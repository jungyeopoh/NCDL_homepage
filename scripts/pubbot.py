#!/usr/bin/env python3
"""NCDL publication bot.

GitHub Actions 에서 실행됩니다. 직접 실행할 일은 거의 없습니다.

  python scripts/pubbot.py event <github-event.json>   이슈 양식/댓글 처리
  python scripts/pubbot.py scan                        새 논문 후보 찾기 (OpenAlex)

결과:
  .pubbot_comment.md     이슈에 남길 댓글
  .pubbot_commit_msg     커밋 메시지
  .pubbot_issue.md       (scan) 새 이슈 본문
종료 코드: 0 = 변경 있음/후보 있음, 2 = 할 일 없음, 1 = 오류 (댓글에 이유)
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PUBS = DATA / "publications.yml"
NEWS = DATA / "news.yml"
SITE = DATA / "site.yml"
IGNORE = ROOT / ".github" / "pubbot-ignore.txt"

STATUSES = ["In preparation", "Submitted", "Under review", "Revision", "Accepted", "Published"]
EMPTY = {"", "_no response_", "none", "n/a", "-"}

yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096
yaml.indent(mapping=2, sequence=4, offset=2)

# news.yml 처럼 최상위가 목록인 파일용 (들여쓰기 없이 "- " 로 시작)
yaml_list = YAML()
yaml_list.preserve_quotes = True
yaml_list.width = 4096
yaml_list.indent(mapping=2, sequence=2, offset=0)


class BotError(Exception):
    """사용자에게 보여줄 오류."""


# ---------------------------------------------------------------- utils

def out(name: str, text: str) -> None:
    (ROOT / name).write_text(text, encoding="utf-8")


def _y(path: Path):
    return yaml_list if path == NEWS else yaml


def load(path: Path):
    with path.open(encoding="utf-8") as f:
        return _y(path).load(f)


def save(path: Path, data) -> None:
    with path.open("w", encoding="utf-8") as f:
        _y(path).dump(data, f)


def clean(v) -> str:
    v = "" if v is None else str(v).strip()
    return "" if v.lower() in EMPTY else v


def norm_doi(v: str) -> str:
    v = clean(v)
    v = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", v, flags=re.I)
    v = re.sub(r"^doi:\s*", "", v, flags=re.I)
    return v.strip().rstrip(".").lower()


def block_seq(parent, key):
    """parent[key] 를 블록 스타일 목록으로 보장 (`[]` 로 비어 있던 경우 포함)."""
    seq = parent.get(key)
    if not isinstance(seq, CommentedSeq):
        seq = CommentedSeq(seq or [])
        parent[key] = seq
    seq.fa.set_block_style()
    return seq


def norm_status(v: str) -> str:
    v = clean(v)
    for s in STATUSES:
        if v.lower() == s.lower():
            return s
    low = v.lower()
    if "revis" in low:
        return "Revision"
    if "review" in low:
        return "Under review"
    if "submit" in low:
        return "Submitted"
    if "prep" in low:
        return "In preparation"
    if "accept" in low:
        return "Accepted"
    if "publish" in low or "게재" in v:
        return "Published"
    raise BotError(f"상태 `{v}` 를 알 수 없습니다. 다음 중 하나로 적어 주세요: {', '.join(STATUSES)}")


def existing_dois(pubs) -> set[str]:
    found = set()
    for key in ("journal", "conference", "in_progress"):
        for p in pubs.get(key) or []:
            for f in ("link", "doi"):
                d = norm_doi(p.get(f, "") or "")
                if d.startswith("10."):
                    found.add(d)
    return found


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", re.sub(r"<[^>]+>", "", str(t or "")).lower())


def existing_titles(pubs) -> set[str]:
    return {norm_title(p.get("title")) for key in ("journal", "conference", "in_progress")
            for p in pubs.get(key) or [] if p.get("title")}


def settings() -> dict:
    site = load(SITE) or {}
    auto = site.get("automation") or {}
    return {
        "orcid": clean(auto.get("orcid")),
        "openalex_id": clean(auto.get("openalex_id")),
        "news_on_publish": auto.get("news_on_publish", True) is not False,
        "email": clean(auto.get("contact_email")) or clean((site.get("contact") or {}).get("email")),
    }


# ---------------------------------------------------------------- web

def http_json(url: str, email: str = ""):
    ua = "ncdl-homepage-pubbot/1.0" + (f" (mailto:{email})" if email else "")
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def crossref(doi: str, email: str = "") -> dict:
    """DOI → 논문 정보. 실패하면 BotError."""
    doi = norm_doi(doi)
    if not doi.startswith("10."):
        raise BotError(f"DOI 형식이 아닙니다: `{doi}` (예: 10.1002/adma.202413640)")
    try:
        msg = http_json("https://api.crossref.org/works/" + urllib.parse.quote(doi), email)["message"]
    except Exception as e:  # noqa: BLE001
        raise BotError(f"Crossref에서 DOI `{doi}` 정보를 가져오지 못했습니다 ({e}). DOI가 맞는지 확인해 주세요.") from e
    return parse_crossref(msg, doi)


def parse_crossref(msg: dict, doi: str) -> dict:
    def strip(t):
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t or ""))).strip()

    date = None
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(k) or {}).get("date-parts") or [[]]
        if parts and parts[0] and parts[0][0]:
            date = parts[0]
            break
    year = int(date[0]) if date else dt.date.today().year
    month = int(date[1]) if date and len(date) > 1 else None

    authors = ", ".join(
        strip(f"{a.get('given', '')} {a.get('family', '')}") if a.get("family") else strip(a.get("name", ""))
        for a in msg.get("author") or []
    )
    venue = strip((msg.get("container-title") or [""])[0])
    vol = clean(msg.get("volume"))
    page = clean(msg.get("article-number")) or clean(msg.get("page"))
    detail = ", ".join(x for x in (vol, page) if x)
    detail = f"{detail} ({year})" if detail else str(year)
    return {
        "title": strip((msg.get("title") or [""])[0]),
        "authors": authors,
        "venue": venue,
        "detail": detail,
        "year": year,
        "month": month,
        "link": f"https://doi.org/{doi}",
    }


# ---------------------------------------------------------------- issue form parsing

def parse_form(body: str) -> dict:
    """GitHub 이슈 양식 본문(### 제목 + 값) → {제목: 값}."""
    fields, key, buf = {}, None, []
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.*)$", line)
        if m:
            if key is not None:
                fields[key] = "\n".join(buf).strip()
            key, buf = m.group(1).strip(), []
        elif key is not None:
            buf.append(line)
    if key is not None:
        fields[key] = "\n".join(buf).strip()
    return fields


def field(fields: dict, *names) -> str:
    for want in names:
        for k, v in fields.items():
            if k.lower().startswith(want.lower()):
                return clean(v)
    return ""


def checked(fields: dict, name: str) -> bool:
    """체크박스 줄 `- [x] ...name...` 이 있으면 True."""
    for v in fields.values():
        for line in (v or "").splitlines():
            if re.match(r"^\s*-\s*\[[xX]\]", line) and name.lower() in line.lower():
                return True
    return False


# ---------------------------------------------------------------- operations

def journal_entry(info: dict, extra: dict, pubs) -> CommentedMap:
    nos = [int(p.get("no")) for p in pubs.get("journal") or [] if str(p.get("no", "")).isdigit()]
    e = CommentedMap()
    e["no"] = (max(nos) + 1) if nos else 1
    e["year"] = int(extra.get("year") or info.get("year") or dt.date.today().year)
    for k in ("title", "authors", "venue", "detail"):
        e[k] = extra.get(k) or info.get(k) or ""
    e["note"] = extra.get("note", "")
    e["link"] = info.get("link", "") or extra.get("link", "")
    if extra.get("role"):
        e["role"] = extra["role"]
    if extra.get("selected"):
        e["selected"] = True
    if not e["title"]:
        raise BotError("논문 제목을 알 수 없습니다. DOI를 넣거나 제목을 직접 적어 주세요.")
    return e


def add_news(entry, month=None) -> None:
    news = load(NEWS)
    if not isinstance(news, CommentedSeq):
        news = CommentedSeq(news or [])
    today = dt.date.today()
    year = int(entry.get("year") or today.year)
    m = month or (today.month if year == today.year else None)
    item = CommentedMap()
    item["date"] = f"{year}.{m:02d}" if m else str(year)
    item["tag"] = "Paper"
    venue = html.escape(str(entry.get("venue") or ""))
    item["text"] = f"Our paper “{html.escape(str(entry['title']))}” was published in <em>{venue}</em>." if venue \
        else f"Our paper “{html.escape(str(entry['title']))}” was published."
    news.insert(0, item)
    save(NEWS, news)


def op_add(fields: dict, cfg: dict) -> tuple[str, str]:
    status = norm_status(field(fields, "상태", "Status") or "Published")
    doi = norm_doi(field(fields, "DOI"))
    extra = {
        "title": field(fields, "제목", "Title"),
        "authors": field(fields, "저자", "Authors"),
        "venue": field(fields, "저널", "학술지", "Journal"),
        "detail": field(fields, "권", "Volume"),
        "year": field(fields, "연도", "Year"),
        "note": field(fields, "IF", "메모"),
        "selected": checked(fields, "대표"),
    }
    if extra["year"] and not extra["year"].isdigit():
        raise BotError(f"연도는 숫자로 적어 주세요 (지금: `{extra['year']}`).")
    pubs = load(PUBS)
    if doi and doi in existing_dois(pubs):
        raise BotError(f"DOI `{doi}` 논문이 이미 목록에 있습니다.")

    if status == "Published":
        info = crossref(doi, cfg["email"]) if doi else {}
        if not doi and not (extra["title"] and extra["venue"]):
            raise BotError("게재된 논문은 DOI를 넣거나, 제목과 저널을 직접 적어 주세요.")
        entry = journal_entry(info, extra, pubs)
        block_seq(pubs, "journal").insert(0, entry)
        save(PUBS, pubs)
        news = ""
        if cfg["news_on_publish"] and not checked(fields, "News에는 올리지"):
            add_news(entry, info.get("month"))
            news = " News에도 소식을 올렸습니다."
        return (f"✅ Journal {entry['no']}번으로 추가했습니다: **{entry['title']}** ({entry['venue']}).{news}\n\n"
                "공동 1저자(†)나 교신저자(*) 표시는 `data/publications.yml` 에서 저자 이름 뒤에 붙여 주세요.",
                f"Add publication #{entry['no']}: {entry['title'][:60]}")

    if not extra["title"]:
        raise BotError("진행 중인 논문은 제목을 적어 주세요 (공개해도 되는 수준으로).")
    e = CommentedMap()
    e["status"] = status
    e["title"] = extra["title"]
    e["authors"] = extra["authors"]
    e["venue"] = extra["venue"]
    if doi:
        e["doi"] = doi
    block_seq(pubs, "in_progress").insert(0, e)
    save(PUBS, pubs)
    return (f"✅ 진행 중인 논문에 추가했습니다: **{e['title']}** — 상태 `{status}`",
            f"Add in-progress paper ({status}): {e['title'][:60]}")


def op_update(fields: dict, cfg: dict) -> tuple[str, str]:
    query = field(fields, "논문 제목", "제목", "Title").lower()
    status = norm_status(field(fields, "새 상태", "상태", "Status"))
    doi = norm_doi(field(fields, "DOI"))
    if not query:
        raise BotError("어떤 논문인지 제목(일부)을 적어 주세요.")
    pubs = load(PUBS)
    prog = block_seq(pubs, "in_progress")
    hits = [i for i, p in enumerate(prog) if query in str(p.get("title", "")).lower()]
    if not hits:
        titles = "\n".join(f"- {p.get('title')}" for p in prog) or "- (진행 중인 논문이 없습니다)"
        raise BotError(f"`{query}` 가 들어간 진행 중 논문을 찾지 못했습니다. 현재 목록:\n{titles}")
    if len(hits) > 1:
        titles = "\n".join(f"- {prog[i].get('title')}" for i in hits)
        raise BotError(f"`{query}` 에 맞는 논문이 여러 개입니다. 제목을 더 길게 적어 주세요:\n{titles}")
    i = hits[0]
    item = prog[i]

    if status != "Published":
        old = item.get("status")
        item["status"] = status
        if doi:
            item["doi"] = doi
        save(PUBS, pubs)
        return (f"✅ 상태를 바꿨습니다: **{item.get('title')}** — `{old}` → `{status}`",
                f"Update paper status to {status}: {str(item.get('title'))[:60]}")

    doi = doi or norm_doi(item.get("doi", "") or "")
    info = crossref(doi, cfg["email"]) if doi else {}
    extra = {
        # 진행 중 목록의 저자 표기(†, *)를 우선 유지
        "authors": item.get("authors") or "",
        "role": item.get("role") or "",
        "note": field(fields, "IF", "메모"),
        "selected": checked(fields, "대표"),
    }
    if not info:
        extra.update(title=item.get("title"), venue=item.get("venue"), detail=str(dt.date.today().year))
    entry = journal_entry(info, extra, pubs)
    del prog[i]
    block_seq(pubs, "journal").insert(0, entry)
    save(PUBS, pubs)
    news = ""
    if cfg["news_on_publish"]:
        add_news(entry, info.get("month"))
        news = " News에도 소식을 올렸습니다."
    return (f"🎉 게재 완료로 옮겼습니다: Journal {entry['no']}번 **{entry['title']}** ({entry['venue']}, {entry['detail']}).{news}",
            f"Publish #{entry['no']}: {entry['title'][:60]}")


CAND_RE = re.compile(r"<!--\s*pubbot-candidates:\s*(\[.*?\])\s*-->", re.S)


def op_candidates(body: str, comment: str, cfg: dict) -> tuple[str, str]:
    m = CAND_RE.search(body or "")
    if not m:
        raise BotError("이 이슈에서 후보 목록을 찾지 못했습니다.")
    cands = json.loads(m.group(1))
    cmd, *args = comment.strip().split()
    nums = [int(x) for a in args for x in re.split(r"[,\s]+", a) if x.isdigit()]
    chosen = [c for k, c in enumerate(cands, 1) if not nums or k in nums]
    if not chosen:
        raise BotError("선택한 번호에 해당하는 후보가 없습니다.")

    if cmd.lower() == "/ignore":
        IGNORE.parent.mkdir(parents=True, exist_ok=True)
        prev = IGNORE.read_text(encoding="utf-8") if IGNORE.exists() else ""
        IGNORE.write_text(prev + "".join(c["doi"] + "\n" for c in chosen), encoding="utf-8")
        return (f"🙈 {len(chosen)}건을 앞으로 후보에서 제외합니다.", f"Ignore {len(chosen)} paper candidate(s)")

    if cmd.lower() != "/approve":
        raise BotError("명령은 `/approve` (전부 추가), `/approve 1 3` (골라서 추가), `/ignore` (제외) 중 하나입니다.")

    pubs = load(PUBS)
    have, titles = existing_dois(pubs), existing_titles(pubs)
    added, failed = [], []
    for c in reversed(chosen):  # 오래된 것부터 넣어 최신이 맨 위로
        if c["doi"] in have:
            continue
        try:
            info = crossref(c["doi"], cfg["email"])
        except BotError as e:
            failed.append(f"- {c.get('title') or c['doi']}: {e}")
            continue
        if norm_title(info.get("title")) in titles:
            continue
        entry = journal_entry(info, {}, pubs)
        block_seq(pubs, "journal").insert(0, entry)
        added.append((entry, info.get("month")))
    if not added:
        raise BotError("추가할 논문이 없습니다 (이미 목록에 있거나 정보를 가져오지 못함).\n" + "\n".join(failed))
    save(PUBS, pubs)
    if cfg["news_on_publish"]:
        for entry, month in added:
            add_news(entry, month)
    lines = "\n".join(f"- {e['no']}. {e['title']} ({e['venue']})" for e, _ in reversed(added))
    fail = ("\n\n가져오지 못한 논문:\n" + "\n".join(failed)) if failed else ""
    return (f"✅ {len(added)}편을 추가했습니다:\n{lines}{fail}\n\n"
            "공동 1저자(†)·교신저자(*) 표시와 IF 메모는 `data/publications.yml` 에서 다듬어 주세요.",
            f"Add {len(added)} publication(s) found by weekly check")


# ---------------------------------------------------------------- commands

def cmd_event(path: str) -> int:
    ev = json.loads(Path(path).read_text(encoding="utf-8"))
    issue = ev.get("issue") or {}
    labels = {l["name"] for l in issue.get("labels") or []}
    comment = ((ev.get("comment") or {}).get("body") or "").strip()
    cfg = settings()
    try:
        if "paper-candidates" in labels and comment.startswith("/"):
            msg, commit = op_candidates(issue.get("body", ""), comment, cfg)
        elif "add-paper" in labels and (not comment or comment.startswith("/retry")):
            msg, commit = op_add(parse_form(issue.get("body", "")), cfg)
        elif "update-paper" in labels and (not comment or comment.startswith("/retry")):
            msg, commit = op_update(parse_form(issue.get("body", "")), cfg)
        else:
            return 2
    except BotError as e:
        out(".pubbot_comment.md", f"⚠️ 처리하지 못했습니다.\n\n{e}\n\n"
            "이슈 본문을 **Edit** 으로 고친 뒤 댓글로 `/retry` 를 남기면 다시 시도합니다.")
        return 1
    out(".pubbot_comment.md", msg + "\n\n1~2분 뒤 홈페이지에 반영됩니다.")
    out(".pubbot_commit_msg", commit)
    return 0


def cmd_scan() -> int:
    cfg = settings()
    if cfg["openalex_id"]:
        flt = f"author.id:{cfg['openalex_id']}"
    elif cfg["orcid"]:
        flt = f"author.orcid:{cfg['orcid']}"
    else:
        print("site.yml 의 automation.orcid 가 비어 있어 건너뜁니다.")
        return 2
    since = (dt.date.today() - dt.timedelta(days=730)).isoformat()
    url = ("https://api.openalex.org/works?per-page=50&sort=publication_date:desc"
           f"&filter={flt},from_publication_date:{since}")
    if cfg["email"]:
        url += "&mailto=" + urllib.parse.quote(cfg["email"])
    works = http_json(url, cfg["email"]).get("results", [])
    pubs = load(PUBS)
    have = existing_dois(pubs)
    titles = existing_titles(pubs)
    ignored = set(IGNORE.read_text(encoding="utf-8").split()) if IGNORE.exists() else set()
    cands = []
    for w in works:
        doi = norm_doi(w.get("doi") or "")
        if not doi.startswith("10.") or doi in have or doi in ignored:
            continue
        if norm_title(w.get("title") or w.get("display_name")) in titles:
            continue
        if w.get("type") not in (None, "article", "review", "letter"):
            continue
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
        cands.append({"doi": doi, "title": w.get("title") or w.get("display_name") or "", "venue": src,
                      "date": w.get("publication_date") or ""})
    if not cands:
        print("새 논문 후보가 없습니다.")
        return 2
    rows = "\n".join(f"{k}. **{c['title']}**  \n   {c['venue']}, {c['date']} — https://doi.org/{c['doi']}"
                     for k, c in enumerate(cands, 1))
    out(".pubbot_issue.md",
        f"홈페이지에 아직 없는 논문 {len(cands)}편을 찾았습니다.\n\n{rows}\n\n"
        "---\n댓글로 답해 주세요:\n"
        "- `/approve` → 전부 홈페이지에 추가\n"
        "- `/approve 1 3` → 고른 번호만 추가\n"
        "- `/ignore` 또는 `/ignore 2` → 앞으로 후보에서 제외\n\n"
        f"<!-- pubbot-candidates: {json.dumps(cands, ensure_ascii=False)} -->\n")
    out(".pubbot_commit_msg", f"Found {len(cands)} candidate(s)")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "event":
        return cmd_event(argv[1])
    if argv and argv[0] == "scan":
        return cmd_scan()
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
