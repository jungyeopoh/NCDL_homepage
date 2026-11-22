/* ==========================================================
   NCDL site renderer
   내용은 data/*.yml 파일에서 읽어옵니다. 보통은 이 파일을 고칠 필요가 없습니다.
   메뉴를 바꾸려면 아래 NAV 목록만 수정하세요.
   ========================================================== */

const NAV = [
  { id: "home",         label: "Home",         href: "index.html" },
  { id: "people",       label: "People",       href: "people.html" },
  { id: "research",     label: "Research",     href: "research.html" },
  { id: "publications", label: "Publications", href: "publications.html" },
  { id: "news",         label: "News",         href: "news.html" },
  { id: "join",         label: "Join us",      href: "join.html" },
  { id: "contact",      label: "Contact",      href: "contact.html" },
];

/* ---------- helpers ---------- */

const $ = (sel, root = document) => root.querySelector(sel);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const list = (v) => (Array.isArray(v) ? v : []);
const has = (v) => v !== undefined && v !== null && String(v).trim() !== "";

async function loadYaml(name) {
  const res = await fetch(`data/${name}.yml`, { cache: "no-cache" });
  if (!res.ok) throw new Error(`data/${name}.yml 파일을 불러오지 못했습니다 (HTTP ${res.status}).`);
  const text = await res.text();
  try {
    return jsyaml.load(text);
  } catch (e) {
    const err = new Error(`data/${name}.yml 파일의 형식에 오류가 있습니다: ${e.reason || e.message}` + (e.mark ? ` (${e.mark.line + 1}번째 줄)` : ""));
    err.yaml = true;
    throw err;
  }
}

// MoS2, Bi2O2Se 같은 화학식의 숫자를 아래첨자로 표시
function chem(html) {
  return String(html ?? "").replace(/\b((?:[A-Z][a-z]?\d*){2,})\b/g, (tok) =>
    /\d/.test(tok) && !/^M\d+D$/.test(tok) ? tok.replace(/([A-Za-z])(\d+)/g, "$1<sub>$2</sub>") : tok);
}

function initials(name) {
  return String(name || "?").split(/\s+/).filter(Boolean).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
}

function avatar(p, folder = "images/people/") {
  if (has(p.photo)) return `<div class="avatar"><img src="${folder}${esc(p.photo)}" alt="${esc(p.name)}" loading="lazy"></div>`;
  return `<div class="avatar" aria-hidden="true">${esc(initials(p.name))}</div>`;
}

// 연구실 학생 이름 (publications 페이지에서 members.yml 로 채움) → 밑줄 표시
let LAB_AUTHORS = [];

function boldAuthors(authors, names) {
  let out = esc(authors);
  const rx = (n) => esc(n).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  list(names).forEach((n) => {
    out = out.replace(new RegExp(`(${rx(n)}[†*]*)`, "g"), "<strong>$1</strong>");
  });
  LAB_AUTHORS.forEach((n) => {
    out = out.replace(new RegExp(`(^|, )(${rx(n)}[†*]*)`, "g"), '$1<span class="lab-author">$2</span>');
  });
  return out;
}

function labAuthorsFrom(m) {
  const groups = ["postdocs", "phd", "integrated", "ms", "interns", "alumni"];
  return groups.flatMap((g) => list(m && m[g])).flatMap((p) => [p.name, ...list(p.aliases)]).filter(has);
}

// 교수(highlight_authors)가 1저자(맨 앞 또는 †)·교신(*)인지
function authorRole(p, site) {
  if (has(p.role)) {
    const r = String(p.role).toLowerCase();
    const first = r.includes("first"), corr = r.includes("corr");
    return { first, corr, lead: first || corr };
  }
  const names = list(site.highlight_authors).map((n) => String(n).toLowerCase());
  const parts = String(p.authors || "").split(/\s*,\s*/);
  let first = false, corr = false;
  parts.forEach((a, i) => {
    const bare = a.replace(/[†*‡\d\s]+$/u, "").trim().toLowerCase();
    if (!names.includes(bare)) return;
    if (i === 0 || a.includes("†")) first = true;
    if (a.includes("*")) corr = true;
  });
  return { first, corr, lead: first || corr };
}

function roleBadges(p, site) {
  const r = authorRole(p, site);
  return (r.first ? `<span class="badge badge-first">First author</span>` : "") +
         (r.corr ? `<span class="badge badge-corr">Corresponding</span>` : "");
}

// "IF 26.8, JCR top 5%" → 강조 표시
function metricChips(note) {
  const t = String(note || "");
  const ifm = t.match(/IF\s*([\d.]+)/i);
  const jcr = t.match(/top\s*([\d.]+)\s*%/i);
  if (!ifm && !jcr) return has(t) ? `<span class="pub-note">${esc(t)}</span>` : "";
  const tier = jcr ? Number(jcr[1]) : 100;
  return `<span class="metrics">${ifm ? `<span class="metric metric-if">IF ${esc(ifm[1])}</span>` : ""}${jcr ? `<span class="metric metric-jcr" data-tier="${tier <= 5 ? "top" : tier <= 10 ? "high" : "mid"}">JCR top ${esc(jcr[1])}%</span>` : ""}</span>`;
}

function coverBadge(p) {
  return p.cover ? `<span class="badge badge-cover">${esc(typeof p.cover === "string" ? p.cover : "Cover")}</span>` : "";
}

function pubItem(p, site, opts = {}) {
  const title = has(p.link) ? `<a href="${esc(p.link)}" target="_blank" rel="noopener">${chem(esc(p.title))}</a>` : chem(esc(p.title));
  const type = has(p.type) ? `<span class="pub-type">${esc(p.type)}</span>` : "";
  const status = has(p.status) ? `<span class="pub-status" data-status="${esc(String(p.status).toLowerCase().replace(/[^a-z]+/g, "-"))}">${esc(p.status)}</span>` : "";
  const badges = (opts.compact ? "" : roleBadges(p, site)) + coverBadge(p);
  const metrics = opts.compact ? "" : metricChips(p.note);
  const venue = has(p.venue) || has(p.detail)
    ? `<div class="pub-venue">${has(p.venue) ? `<em>${esc(p.venue)}</em>` : ""}${has(p.venue) && has(p.detail) ? ", " : ""}${has(p.detail) ? esc(p.detail) : ""}</div>` : "";
  const lead = authorRole(p, site).lead;
  return `<li class="pub${lead && !opts.compact && !has(p.status) ? " pub-lead" : ""}">
    <div class="pub-no">${esc(p.no ?? "")}</div>
    <div>
      ${status}<div class="pub-title">${title}${type}</div>
      ${has(p.authors) ? `<div class="pub-authors">${boldAuthors(p.authors, site.highlight_authors)}</div>` : ""}
      ${venue}
      ${badges || metrics ? `<div class="pub-tags">${badges}${metrics}</div>` : ""}
    </div>
  </li>`;
}

/* ---------- figures (SVG) ---------- */

// Pinched hysteresis loop of a memristor: I = G(w)·V, w follows ∫V dt.
function loopPoints(amp, cx, cy, rx, ry, iMax) {
  const pts = [];
  const N = 220;
  for (let k = 0; k <= N; k++) {
    const t = (k / N) * Math.PI * 2;
    const v = Math.sin(t);
    const w = amp * (1 - Math.cos(t)) / 2;
    const g = 0.12 + 0.88 * w;
    const i = (g * v) / iMax;
    pts.push(`${(cx + v * rx).toFixed(1)},${(cy - i * ry).toFixed(1)}`);
  }
  return "M" + pts.join("L");
}

// 홈 첫 화면 그림: 멤리스터 크로스바 어레이 (등각 투영).
// 교차점마다 메모리 셀이 있고, 셀 색은 박막 간섭색처럼 저장된 가중치에 따라 달라진다.
function heroArray() {
  const W = 1000, H = 640, ox = 1010, oy = 36, ax = 26, ay = 13, h = 15, N = 26, M = 37;
  const P = (i, j, z = 0) => [ox + (i - j) * ax, oy + (i + j) * ay - z];
  const f = (n) => n.toFixed(1);
  const stops = [[224, 167, 101], [169, 123, 224], [91, 141, 255], [63, 208, 201], [240, 205, 74]];
  const color = (v) => {
    const t = Math.min(0.9999, Math.max(0, v)) * (stops.length - 1), k = Math.floor(t), u = t - k;
    const c = stops[k].map((a, n) => Math.round(a + (stops[k + 1][n] - a) * u));
    return `rgb(${c[0]},${c[1]},${c[2]})`;
  };
  const weight = (i, j) => 0.5 + 0.5 * Math.sin(i * 0.31 + j * 0.17 + 0.6) * Math.cos(j * 0.23 - i * 0.11);
  const seen = ([x, y]) => x > -40 && x < W + 40 && y > -40 && y < H + 40;
  const line = (a, b, cls) => `<line class="${cls}" x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(b[0])}" y2="${f(b[1])}"/>`;

  let bottom = "", top = "", cells = "", pulses = "";
  for (let j = 0; j <= M; j++) bottom += line(P(-1, j), P(N, j), "bl");
  for (let i = 0; i <= N; i++) top += line(P(i, -1, h), P(i, M + 1, h), "wl-shadow") ;
  for (let i = 0; i <= N; i++) top += line(P(i, -1, h + 2.5), P(i, M + 1, h + 2.5), "wl");
  for (let j = 0; j <= M; j++) for (let i = 0; i <= N; i++) {
    const a = P(i, j, 2.5), b = P(i, j, h - 1);
    if (!seen(a)) continue;
    const v = weight(i, j), depth = Math.min(1, Math.max(0, (a[1] - 60) / 420));
    cells += `<line x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(b[0])}" y2="${f(b[1])}" stroke="${color(v)}" opacity="${(0.35 + 0.65 * depth * (0.55 + 0.45 * v)).toFixed(2)}" style="--d:${Math.round(Math.max(0, a[0]) * 1.3)}ms"/>`;
  }
  [9, 16, 22, 29].forEach((j, n) => {
    const a = P(-1, j, 0), b = P(N, j, 0);
    pulses += `<path class="pulse" pathLength="1" d="M${f(a[0])},${f(a[1])}L${f(b[0])},${f(b[1])}" style="animation-delay:${n * 1.7 + 2}s"/>`;
  });
  const tip = P(0, 14, h + 2.5);
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMinYMin slice" role="img" aria-labelledby="arrayTitle">
    <title id="arrayTitle">A memristor crossbar array: every crossing of two electrodes is a memory cell that stores one synaptic weight</title>
    <defs><filter id="cellGlow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter></defs>
    <g class="arr-bottom">${bottom}</g>
    <g class="arr-pulses">${pulses}</g>
    <g class="arr-cells arr-glow" filter="url(#cellGlow)">${cells}</g>
    <g class="arr-cells">${cells}</g>
    <g class="arr-top">${top}</g>
    <g class="arr-note">
      <path d="M${f(tip[0] - 3)},${f(tip[1] - 5)} L${f(tip[0] - 30)},${f(tip[1] - 46)} L${f(tip[0] - 44)},${f(tip[1] - 46)}"/>
      <circle cx="${f(tip[0])}" cy="${f(tip[1])}" r="5"/>
      <text x="${f(tip[0] - 52)}" y="${f(tip[1] - 52)}" text-anchor="end">Each crossing is a memory cell</text>
      <text x="${f(tip[0] - 52)}" y="${f(tip[1] - 30)}" text-anchor="end">that stores one synaptic weight</text>
    </g>
  </svg>`;
}

function brandMark(size = 34) {
  const d = loopPoints(1, 20, 20, 15, 13, 0.12 + 0.88 * 0.85);
  return `<svg width="${size}" height="${size}" viewBox="0 0 40 40" aria-hidden="true">
    <rect x="0.5" y="0.5" width="39" height="39" rx="9" fill="var(--blue)"/>
    <path d="${d}" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>
  </svg>`;
}

function glyph(kind, size = 56) {
  const s = `width="${size}" height="${size}" viewBox="0 0 56 56" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="glyph"`;
  if (kind === "spikes") {
    return `<svg ${s}><path d="M4 40h8l3-28 3 28h8l3-20 3 20h8l3-28 3 28h4"/><path d="M4 48h48" opacity=".35"/></svg>`;
  }
  if (kind === "layers") {
    return `<svg ${s}><path d="M28 8 50 18 28 28 6 18z"/><path d="M6 27l22 10 22-10" opacity=".7"/><path d="M6 36l22 10 22-10" opacity=".45"/></svg>`;
  }
  // hysteresis
  return `<svg ${s}><path d="M6 28h44M28 6v44" opacity=".35"/><path d="${loopPoints(1, 28, 28, 21, 19, 0.12 + 0.88 * 0.85)}"/></svg>`;
}

/* ---------- layout ---------- */

function applyDesign(site) {
  const d = site.design || {};
  document.documentElement.dataset.theme = d.theme || "paper";
}

// navy 테마처럼 헤더가 어두우면 흰색 로고를 사용
function logoFor(d, key, darkHeader) {
  const dark = d[`${key}_on_dark`];
  return darkHeader && has(dark) ? dark : d[key];
}

function renderChrome(site, page) {
  const d = site.design || {};
  const darkHeader = d.theme === "navy";
  const labLogo = logoFor(d, "logo", darkHeader);
  const uniLogo = logoFor(d, "university_logo", darkHeader);
  const brand = has(labLogo)
    ? `<img class="brand-logo" src="images/${esc(labLogo)}" alt="${esc(site.lab_short)}">`
    : `${brandMark()}<span class="brand-text"><span class="brand-short">${esc(site.lab_short)}</span><span class="brand-uni">${esc(site.university)}</span></span>`;
  const header = $("#site-header");
  header.className = "site-header";
  header.innerHTML = `<div class="wrap">
    <a class="brand" href="index.html" aria-label="${esc(site.lab_name)}, ${esc(site.university)} home">
      ${brand}
      ${has(uniLogo) ? `<span class="brand-sep" aria-hidden="true"></span><img class="brand-uni-logo" src="images/${esc(uniLogo)}" alt="${esc(site.university)}">` : ""}
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">Menu</button>
    <nav class="nav" id="nav" aria-label="Main"><ul>
      ${NAV.map((n) => `<li><a href="${n.href}"${n.id === page ? ' aria-current="page"' : ""}>${n.label}</a></li>`).join("")}
    </ul></nav>
  </div>`;
  const btn = $(".nav-toggle", header), nav = $("#nav", header);
  btn.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    btn.setAttribute("aria-expanded", open);
    btn.textContent = open ? "Close" : "Menu";
  });

  const c = site.contact || {};
  const footer = $("#site-footer");
  footer.className = "site-footer";
  const footUni = logoFor(d, "university_logo", true);
  footer.innerHTML = `<div class="wrap">
    ${has(footUni) ? `<img class="footer-uni" src="images/${esc(footUni)}" alt="${esc(site.university)}">` : ""}
    <div class="footer-text">
      <p><strong>${esc(site.lab_name)}</strong></p>
      <p>${esc(site.school)}, ${esc(site.college)}, ${esc(site.university)}</p>
      <p>${esc(c.office)}, ${esc(c.address)}</p>
    </div>
    <div>
      <p><a href="mailto:${esc(c.email)}">${esc(c.email)}</a></p>
      <p>${esc(c.phone)}</p>
      <p>© ${new Date().getFullYear()} ${esc(site.lab_short)}</p>
    </div>
  </div>`;
}

function pageHead(title, text) {
  return `<section class="page-head"><div class="wrap"><h1>${esc(title)}</h1>${has(text) ? `<p>${text}</p>` : ""}</div></section>`;
}

/* ---------- pages ---------- */

const PAGES = {
  async home(site) {
    const [research, news, pubs] = await Promise.all([loadYaml("research"), loadYaml("news"), loadYaml("publications")]);
    const selected = list(pubs.journal).filter((p) => p.selected).slice(0, 4);
    const latest = list(news).slice(0, 5);
    return `
      <section class="hero${has(site.design?.hero_image) ? " has-image" : ""}"${has(site.design?.hero_image) ? ` style="--hero-photo:url('images/${esc(site.design.hero_image)}')"` : ""}>
        <div class="wrap"><div class="hero-text">
          <p class="affil">${esc(site.school)}, ${esc(site.university)}</p>
          <h1>${esc(site.lab_name)}</h1>
          <p class="lede">${esc(site.tagline)}</p>
          <p class="sub">${esc(site.intro)}</p>
          <div class="actions">
            <a class="btn btn-primary" href="research.html">Explore our research</a>
            <a class="btn btn-ghost" href="join.html">Join the lab</a>
          </div>
        </div></div>
        ${has(site.design?.hero_image) ? "" : `<div class="hero-art">${heroArray()}</div>`}
      </section>

      ${site.recruiting ? `<section class="recruit" aria-label="Recruitment"><div class="wrap">
        <p>${esc(site.recruiting_text)}</p><a href="join.html">How to apply</a>
      </div></section>` : ""}

      <section class="section"><div class="wrap">
        <div class="section-head"><h2>Research</h2><a href="research.html">All research topics</a></div>
        <ul class="topic-rows">
          ${list(research.topics || research).map((r) => `<li><a href="research.html#${esc(r.id)}">
            ${glyph(r.icon)}
            <h3>${esc(r.title)}</h3>
            <p>${esc(r.summary)}</p>
          </a></li>`).join("")}
        </ul>
      </div></section>

      <section class="section"><div class="wrap split">
        <div>
          <div class="section-head"><h2>News</h2><a href="news.html">All news</a></div>
          ${newsList(latest)}
        </div>
        <div>
          <div class="section-head"><h2>Selected publications</h2><a href="publications.html">All publications</a></div>
          <ul class="pub-list">${selected.map((p) => pubItem(p, site, { compact: true })).join("")}</ul>
        </div>
      </div></section>`;
  },

  async people(site) {
    const m = await loadYaml("members");
    const p = m.professor || {};
    const cvBlock = (title, items) => list(items).length ? `<div><h3>${title}</h3><ul>${list(items).map((e) =>
      `<li><span class="yrs">${esc(e.years)}</span><span>${esc(e.text)}</span></li>`).join("")}</ul></div>` : "";

    const groups = [
      ["postdocs", "Postdoctoral researchers"],
      ["phd", "Ph.D. students"],
      ["integrated", "Integrated M.S.–Ph.D. students"],
      ["ms", "M.S. students"],
      ["interns", "Undergraduate interns"],
    ];
    const anyStudents = groups.some(([k]) => list(m[k]).length);
    const groupHtml = groups.filter(([k]) => list(m[k]).length).map(([k, label]) => `
      <section class="group"><h2>${label}</h2><div class="people-grid">
        ${list(m[k]).map((s) => `<article class="person${has(s.photo) ? "" : " compact"}">
          ${avatar(s)}
          <div class="person-info">
          <h3>${esc(s.name)}</h3>
          ${has(s.name_ko) ? `<div class="ko">${esc(s.name_ko)}${has(s.since) ? `, since ${esc(s.since)}` : ""}</div>` : ""}
          <dl>
            ${has(s.education) ? `<dt>Education</dt><dd>${esc(s.education)}</dd>` : ""}
            ${has(s.interests) ? `<dt>Research interests</dt><dd>${esc(s.interests)}</dd>` : ""}
            ${has(s.email) ? `<dt>Email</dt><dd><a href="mailto:${esc(s.email)}">${esc(s.email)}</a></dd>` : ""}
          </dl>
          </div>
        </article>`).join("")}
      </div></section>`).join("");

    const alumni = list(m.alumni).length ? `<section class="group"><h2>Alumni</h2><ul class="alumni-list">
      ${list(m.alumni).map((a) => `<li><strong>${esc(a.name)}</strong><span>${esc(a.degree)}</span><span>${esc(a.now)}</span></li>`).join("")}
    </ul></section>` : "";

    return pageHead("People", "Our team of researchers working on neuromorphic devices and AI semiconductors.") + `
      <section class="section"><div class="wrap">
        <div class="pi">
          ${avatar(p)}
          <div>
            <h2 class="pi-name">${esc(p.name)}${has(p.name_ko) ? `<span>${esc(p.name_ko)}</span>` : ""}</h2>
            <p class="pi-title">${esc(p.title)}, ${esc(p.affiliation)}</p>
            <ul class="contact-lines">
              ${has(p.email) ? `<li><span>Email</span> <a href="mailto:${esc(p.email)}">${esc(p.email)}</a></li>` : ""}
              ${has(p.phone) ? `<li><span>Phone</span> ${esc(p.phone)}</li>` : ""}
              ${has(p.office) ? `<li><span>Office</span> ${esc(p.office)}</li>` : ""}
              ${has(site.links?.google_scholar) ? `<li><span>Scholar</span> <a href="${esc(site.links.google_scholar)}" target="_blank" rel="noopener">Google Scholar profile</a></li>` : ""}
            </ul>
            <div class="bio"><p>${esc(p.bio)}</p></div>
          </div>
        </div>
        <div class="cv">
          ${cvBlock("Education", p.education)}
          ${cvBlock("Career", p.career)}
          ${cvBlock("Honors and awards", p.honors)}
        </div>

        ${anyStudents ? groupHtml : `<section class="group"><h2>Students</h2>
          <div class="empty"><p><strong>We are building our first cohort.</strong></p>
          <p>Graduate students and undergraduate interns who join now will shape the lab's research direction from the start. See <a href="join.html">Join us</a> for how to apply.</p></div>
        </section>`}
        ${alumni}
      </div></section>`;
  },

  async research(site) {
    const [research, pubs] = await Promise.all([loadYaml("research"), loadYaml("publications")]);
    const topics = list(research.topics || research);
    const ov = research.overview || {};
    const byNo = new Map(list(pubs.journal).map((p) => [Number(p.no), p]));
    const ABBR = {
      "Advanced Materials": "Adv. Mater.", "Advanced Functional Materials": "Adv. Funct. Mater.",
      "Advanced Science": "Adv. Sci.", "Materials Horizons": "Mater. Horiz.", "Nano Letters": "Nano Lett.",
      "Advanced Intelligent Systems": "Adv. Intell. Syst.", "Science Advances": "Sci. Adv.",
      "ACS Applied Materials & Interfaces": "ACS Appl. Mater. Interfaces",
    };
    const cite = (p) => {
      const detail = String(p.detail || "").replace(/\s*\(\d{4}\)\s*$/, "");
      const t = `<em>${esc(ABBR[p.venue] || p.venue)}</em> <strong>${esc(p.year)}</strong>${detail ? `, ${esc(detail)}` : ""}`;
      return has(p.link) ? `<a href="${esc(p.link)}" target="_blank" rel="noopener">${t}</a>` : t;
    };

    // SVG 개념도는 페이지 글꼴이 적용되도록 본문에 직접 넣는다
    const svgSrcs = [ov.diagram, ...topics.map((t) => t.diagram)].filter((d) => d && /\.svg$/i.test(d.image)).map((d) => d.image);
    const svgText = new Map(await Promise.all([...new Set(svgSrcs)].map(async (src) => {
      try { const r = await fetch(`images/research/${src}`, { cache: "no-cache" }); return [src, r.ok ? await r.text() : ""]; }
      catch { return [src, ""]; }
    })));
    const diagram = (d, cls = "") => {
      if (!d || !has(d.image)) return "";
      const art = svgText.get(d.image) || `<img src="images/research/${esc(d.image)}" alt="${esc(d.caption || "")}">`;
      return `<figure class="diagram ${cls}"><div class="diagram-art">${art}</div>${has(d.caption) ? `<figcaption>${chem(esc(d.caption))}</figcaption>` : ""}</figure>`;
    };
    const work = (f) => {
      const p = byNo.get(Number(f.paper));
      return `<figure class="work">
        <div class="work-img"><img src="images/research/${esc(f.image)}" alt="${esc(f.caption)}"></div>
        <figcaption>
          ${p ? `<div class="work-tags">${metricChips(p.note)}${roleBadges(p, site)}${coverBadge(p)}</div>` : ""}
          <span class="work-cap">${chem(esc(f.caption))}</span>
          ${p ? `<span class="fig-cite">${cite(p)}</span>` : ""}
        </figcaption>
      </figure>`;
    };

    const overview = has(ov.description) ? `
      <section class="section overview"><div class="wrap">
        <div class="ov-text">
          ${has(ov.title) ? `<h2>${esc(ov.title)}</h2>` : ""}
          <p class="lead">${chem(esc(ov.description))}</p>
        </div>
        ${diagram(ov.diagram, "diagram-stack")}
        <nav class="topic-jump" aria-label="Research topics">${topics.map((r) => `<a href="#${esc(r.id)}">${esc(r.title)}</a>`).join("")}</nav>
      </div></section>` : "";

    return pageHead("Research", "Neuromorphic computing, next-generation memory devices, and advanced semiconductor processes.") +
      overview +
      topics.map((r) => `
        <section class="section topic-sec" id="${esc(r.id)}"><div class="wrap">
          <header class="topic-head">
            <h2>${esc(r.title)}</h2>
            ${has(r.title_ko) ? `<p class="ko">${esc(r.title_ko)}</p>` : ""}
          </header>
          ${has(r.description) ? `<p class="lead topic-lead">${chem(esc(r.description))}</p>` : ""}
          ${diagram(r.diagram)}
          ${list(r.figures).length ? `<div class="selected-work"><h3>Selected work</h3><div class="work-row">${list(r.figures).map(work).join("")}</div></div>` : ""}
        </div></section>`).join("");
  },

  async publications(site) {
    const [pubs, members] = await Promise.all([loadYaml("publications"), loadYaml("members").catch(() => ({}))]);
    LAB_AUTHORS = labAuthorsFrom(members);
    const STATUS_ORDER = ["accepted", "revision", "under review", "submitted", "in preparation"];
    const rank = (p) => { const i = STATUS_ORDER.indexOf(String(p.status || "").toLowerCase()); return i < 0 ? 99 : i; };
    const progress = list(pubs.in_progress).slice().sort((a, b) => rank(a) - rank(b));
    const cats = [["journal", "Journal"], ["conference", "Conference"], ["patents", "Patents"]]
      .filter(([k]) => list(pubs[k]).length || (k === "journal" && progress.length));
    const nJ = list(pubs.journal).length;
    const firstYear = Math.min(...list(pubs.journal).map((p) => Number(p.year) || 9999));
    const nLead = list(pubs.journal).filter((p) => authorRole(p, site).lead).length;
    const headText = nJ ? `${nJ} journal articles since ${firstYear}, ${nLead} as first or corresponding author` + (progress.length ? `, and ${progress.length} more in progress.` : ".") : "";
    const html = pageHead("Publications", headText) + `
      <section class="section"><div class="wrap">
        <div class="pub-tools">
          <div class="tabs" role="tablist">
            ${cats.map(([k, label], i) => `<button class="tab" role="tab" data-cat="${k}" aria-selected="${i === 0}">${label}<span class="count">${list(pubs[k]).length}</span></button>`).join("")}
          </div>
          <div class="pub-filters">
            <label class="toggle"><input type="checkbox" id="lead-only"> First or corresponding author only</label>
            <input class="search" type="search" placeholder="Search title, author, journal" aria-label="Search publications">
          </div>
        </div>
        <p class="legend">† equal contribution, * corresponding author, <span class="lab-author">underlined</span>: NCDL students. Papers led by our lab are marked.</p>
        <div id="pub-body"></div>
      </div></section>`;

    setTimeout(() => {
      let cat = cats[0]?.[0];
      const body = $("#pub-body"), input = $(".search");
      const leadBox = $("#lead-only");
      const match = (q) => (p) => (!leadBox.checked || authorRole(p, site).lead || has(p.status)) &&
        (!q || [p.title, p.authors, p.venue, p.year, p.status].join(" ").toLowerCase().includes(q));
      const draw = () => {
        const q = input.value.trim().toLowerCase();
        const items = list(pubs[cat]).filter(match(q));
        const prog = cat === "journal" ? progress.filter(match(q)) : [];
        if (!items.length && !prog.length) { body.innerHTML = `<p class="empty">No publications match “${esc(input.value)}”. Try a different word or clear the search.</p>`; return; }
        const years = [...new Set(items.map((p) => p.year))];
        body.innerHTML =
          (prog.length ? `<div class="year-group in-progress"><h3>In progress</h3><ul class="pub-list">${prog.map((p) => pubItem(p, site)).join("")}</ul></div>` : "") +
          years.map((y) => `<div class="year-group"><h3>${esc(y)}</h3><ul class="pub-list">${items.filter((p) => p.year === y).map((p) => pubItem(p, site)).join("")}</ul></div>`).join("");
      };
      document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((x) => x.setAttribute("aria-selected", x === t));
        cat = t.dataset.cat; draw();
      }));
      input.addEventListener("input", draw);
      leadBox.addEventListener("change", draw);
      if (cat) draw();
    });
    return html;
  },

  async news() {
    const news = await loadYaml("news");
    return pageHead("News", "Papers, awards, and events from the lab.") +
      `<section class="section"><div class="wrap">${newsList(list(news))}</div></section>`;
  },

  async join(site) {
    const j = await loadYaml("join");
    const c = site.contact || {};
    const subject = encodeURIComponent("[NCDL 지원] 이름_지원과정");
    return pageHead("Join us", esc(site.recruiting_text)) + `
      <section class="section" lang="ko"><div class="wrap">
        <p class="join-lead">${esc(j.lead)}</p>
        <p class="join-lead-en" lang="en">${esc(j.lead_en)}</p>
      </div></section>
      <section class="section" lang="ko"><div class="wrap join-grid">
        <div><h2>모집 과정</h2><ul class="positions">${list(j.positions).map((p) => `<li><strong>${esc(p.title)}</strong><span>${esc(p.text)}</span></li>`).join("")}</ul></div>
        <div><h2>이런 분을 찾습니다</h2><ul class="ticks">${list(j.looking_for).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
        <div><h2>연구실 지원 사항</h2><ul class="ticks">${list(j.we_offer).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
        <div><h2>지원 방법</h2><ol class="steps">${list(j.how_to_apply).map((x) => `<li>${esc(x)}</li>`).join("")}</ol></div>
      </div>
      <div class="wrap"><div class="apply-box">
        <p>지원 및 문의: <strong>${esc(c.pi)}</strong>, <a href="mailto:${esc(c.email)}">${esc(c.email)}</a></p>
        <a class="btn btn-primary" href="mailto:${esc(c.email)}?subject=${subject}">지원 메일 보내기</a>
      </div></div></section>
      ${list(j.faq).length ? `<section class="section" lang="ko"><div class="wrap faq"><div class="section-head"><h2>자주 묻는 질문</h2></div>
        ${list(j.faq).map((f) => `<details><summary>${esc(f.q)}</summary><p>${esc(f.a)}</p></details>`).join("")}
      </div></section>` : ""}`;
  },

  async contact(site) {
    const c = site.contact || {};
    const q = encodeURIComponent(c.map_query || c.address || "");
    return pageHead("Contact", "Visit us at Chung-Ang University's Seoul campus in Heukseok-dong.") + `<section class="section"><div class="wrap contact-grid">
      <dl>
        <dt>Principal investigator</dt><dd>${esc(c.pi)}</dd>
        <dt>Email</dt><dd><a href="mailto:${esc(c.email)}">${esc(c.email)}</a></dd>
        <dt>Phone</dt><dd>${esc(c.phone)}</dd>
        <dt>Office</dt><dd>${esc(c.office)}</dd>
        ${has(c.lab_room) ? `<dt>Lab</dt><dd>${esc(c.lab_room)}</dd>` : ""}
        <dt>Address</dt><dd>${esc(site.school)}, ${esc(site.university)}<br>${esc(c.address)}</dd>
        ${has(c.address_ko) ? `<dt>주소</dt><dd lang="ko">${esc(c.address_ko)}</dd>` : ""}
      </dl>
      <iframe class="map" title="Map of ${esc(c.map_query)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
        src="https://maps.google.com/maps?q=${q}&z=17&output=embed"></iframe>
    </div></section>`;
  },
};

function newsList(items) {
  if (!items.length) return `<p class="empty">News will be posted here.</p>`;
  return `<ul class="news-list">${items.map((n) => `<li>
    <span class="news-date">${esc(n.date)}</span>
    <p>${has(n.tag) ? `<span class="news-tag">${esc(n.tag)}</span>` : ""}${chem(n.text ?? "")}</p>
  </li>`).join("")}</ul>`;
}

/* ---------- boot ---------- */

(async function boot() {
  const page = document.body.dataset.page || "home";
  const main = $("#main");
  main.innerHTML = `<div class="loading">Loading…</div>`;
  try {
    const site = await loadYaml("site");
    applyDesign(site);
    renderChrome(site, page);
    const render = PAGES[page] || PAGES.home;
    main.innerHTML = await render(site);
    if (location.hash) { const t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
  } catch (e) {
    console.error(e);
    const local = location.protocol === "file:";
    main.innerHTML = `<div class="wrap"><div class="load-error" role="alert">
      <p><strong>페이지 내용을 불러오지 못했습니다.</strong></p>
      <p>${esc(e.message)}</p>
      ${local ? `<p>파일을 직접 열면(file://) 데이터 파일을 읽을 수 없습니다. GitHub Pages 주소로 접속하거나 README의 "내 컴퓨터에서 미리보기"를 참고하세요.</p>`
              : e.yaml ? `<p>해당 줄의 들여쓰기(스페이스 2칸), 따옴표, 콜론(:) 뒤 띄어쓰기를 확인해 주세요.</p>` : ""}
    </div></div>`;
  }
})();
