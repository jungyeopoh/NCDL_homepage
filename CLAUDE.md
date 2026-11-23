# NCDL homepage: notes for Claude

This repo is the lab homepage of Prof. Jungyeop Oh (Neuromorphic Computing & Device Lab, Chung-Ang University).
The professor asks for updates in chat ("add these papers", "a student joined"); Claude edits, pushes, and verifies.
Reply to him in Korean.

## Basics
- Live site: https://jungyeopoh.github.io/NCDL_homepage/ (GitHub Pages, branch `main`, folder `/`). Push to `main` deploys in about 1 minute.
- Static site, no build step. Content lives in `data/*.yml`; `assets/js/site.js` renders every page (js-yaml 1.2 schema, so `no:` is a plain key).
- Content changes: edit `data/*.yml` only.
- CSS/JS changes: bump the `?v=YYYYMMDDx` query on `style.css` and `site.js` in **every** `*.html`, or browsers keep the old files for about 10 minutes.
- After pushing: wait about 60 s, then open the live page (with a fresh query string) and check the change with `get_page_text` or a JS check.
- Check `git fetch` first: the professor or the publication bot may have committed in the meantime.

## Data conventions
- `publications.yml`
  - `journal:` newest first, `no` increments. `note: "IF x, JCR top y%"` only if it differs from `journals.yml`.
  - `in_progress:` with `status` (In preparation / Submitted / Under review / Revision / Accepted). IF/JCR shows for Accepted and published papers only.
  - `role: first | corresponding | "first, corresponding"` when the full author list is not public yet.
  - † = (co-)first author, * = corresponding. "First author" / "Corresponding" badges are derived from marks on "Jungyeop Oh" (or `role`).
  - `cover: true` (or text like "Front Cover") adds a cover badge. `selected: true` shows the paper on the home page.
- `journals.yml`: IF and JCR rank per journal (venue name must match exactly). Update yearly after JCR release (June).
- `members.yml`: groups `postdocs, phd, integrated, ms, interns, alumni`. `aliases:` lets a student be underlined in author lists under another spelling.
- `research.yml`: `overview` (design A), `overview_b` (design B, current), `topics` with one paragraph, one diagram, and `figures` (Selected work; `paper:` = journal number).
- `news.yml`: newest first. `join.yml`: graduate students only; no intern recruitment (CAU students who want grad school may intern after an interview).

## Design
- `site.yml` `design.version: "b"` is live. `?design=a` previews the old version in one browser.
- Home hero: `heroNetwork` (B) / `heroArray` (A) in `site.js`. Research diagrams: `python3 tools/make_svgs.py` writes `images/research/diagrams/*.svg`.
- Palette: CAU blue `#0062a8`, NCDL navy `#053863`; thin-film accents teal/violet/gold.

## Automation
- Issue forms "📄 논문 추가" / "🔄 논문 상태 변경" → `.github/workflows/publications.yml` runs `scripts/pubbot.py` (Crossref by DOI). Only the repo owner's issues are processed.
- Weekly OpenAlex check needs `automation.orcid` in `site.yml` (still empty).

## Open items (ask when relevant)
- Korean names of the undergraduate interns (he says 윤성민; the English name is Seokmin Youn).
- Spelling "Ui Do Ji" on the accepted Materials Horizons paper.
- Bi2O2Se synthesis figure is cited as ACS Nano 19, 638 (from his slides); it may belong to ACS Nano 19, 5406.
- Which papers were journal covers; ORCID iD; school domain (ncdl.cau.ac.kr, CNAME to jungyeopoh.github.io, then Settings → Pages → Custom domain, done by him).
- Which JCR year the current IF values are from.
