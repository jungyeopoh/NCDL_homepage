"""Generate NCDL research concept diagrams (SVG)."""
import math
from pathlib import Path

OUT = Path("/home/claude/ncdl/images/research/diagrams")
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#053863"
BLUE = "#0062a8"
TINT = "#e6eef7"
TEAL = "#2a9a96"
VIOLET = "#7b4fa6"
GOLD = "#c9a632"
BRONZE = "#b5844a"
INK = "#17212c"
MUTED = "#56626f"
RULE = "#d4dae0"
PAPER = "#ffffff"

STYLE = f"""<style>
  .t  {{ font-family: var(--font-body, 'Pretendard', 'Apple SD Gothic Neo', Arial, sans-serif); fill: {INK}; }}
  .h  {{ font-family: var(--font-display, Arial, sans-serif); font-weight: 700; fill: {INK}; }}
  .m  {{ fill: {MUTED}; }}
  .w  {{ fill: #fff; }}
  .b  {{ fill: {BLUE}; }}
  .n  {{ fill: {NAVY}; }}
  .sm {{ font-size: 13px; }}
  .md {{ font-size: 15px; }}
  .lg {{ font-size: 18px; }}
  .xl {{ font-size: 22px; }}
  .bold {{ font-weight: 650; }}
  .ln {{ stroke: {MUTED}; stroke-width: 1.4; fill: none; }}
</style>"""


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{STYLE}'
            '<defs>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{MUTED}"/></marker>'
            f'<marker id="arrb" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>'
            f'<linearGradient id="film" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{BRONZE}"/><stop offset=".35" stop-color="{VIOLET}"/><stop offset=".65" stop-color="{BLUE}"/><stop offset="1" stop-color="{TEAL}"/></linearGradient>'
            '</defs>'
            f'{body}</svg>')


def chem(s):
    import re
    def fix(m):
        tok = m.group(0)
        if re.fullmatch(r"M\d+D", tok):
            return tok
        return re.sub(r"([A-Za-z])(\d+)", r'\1<tspan baseline-shift="sub" font-size="72%">\2</tspan>', tok) if re.search(r"\d", tok) else tok
    return re.sub(r"\b(?:[A-Z][a-z]?\d*){2,}\b", fix, s)


def text(x, y, s, cls="t md", anchor="start", extra=""):
    s = chem(s.replace("&", "&amp;").replace("<", "&lt;"))
    return f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" {extra}>{s}</text>'


def lines(x, y, rows, cls="t md", anchor="start", lh=19):
    return "".join(text(x, y + i * lh, r, cls, anchor) for i, r in enumerate(rows))


def pinched_loop(cx, cy, rx, ry, amp=1.0, n=120):
    pts = []
    imax = 0.12 + 0.88 * 0.85
    for k in range(n + 1):
        t = k / n * 2 * math.pi
        v = math.sin(t)
        w = amp * (1 - math.cos(t)) / 2
        i = (0.12 + 0.88 * w) * v / imax
        pts.append(f"{cx + v * rx:.1f},{cy - i * ry:.1f}")
    return "M" + "L".join(pts)


# ------------------------------------------------------------------ 1. von Neumann vs in-memory
def von_neumann():
    W, H = 980, 360
    b = []
    # left panel
    b.append(text(40, 40, "Von Neumann computer", "h lg"))
    b.append(text(40, 62, "Processor and memory are separate", "t sm m"))
    b.append(f'<rect x="40" y="96" width="170" height="150" rx="14" fill="{TINT}" stroke="{BLUE}" stroke-width="1.5"/>')
    b.append(text(125, 165, "Processor", "t md bold", "middle"))
    b.append(text(125, 186, "(compute)", "t sm m", "middle"))
    b.append(f'<rect x="330" y="96" width="170" height="150" rx="14" fill="#fff" stroke="{NAVY}" stroke-width="1.5"/>')
    for r in range(5):
        for c in range(6):
            b.append(f'<rect x="{352 + c * 22}" y="{112 + r * 14}" width="16" height="9" rx="2" fill="{NAVY}" opacity="{0.18 + 0.12 * ((r + c) % 3)}"/>')
    b.append(text(415, 210, "Memory", "t md bold", "middle"))
    b.append(text(415, 230, "(data, weights)", "t sm m", "middle"))
    # bus
    b.append(f'<rect x="210" y="156" width="120" height="30" fill="{TINT}" stroke="{RULE}"/>')
    for k in range(9):
        x = 218 + k * 12.5
        b.append(f'<rect x="{x:.1f}" y="164" width="7" height="14" rx="2" fill="{GOLD}"/>')
    b.append(f'<path d="M232,140 L310,140" class="ln" marker-end="url(#arr)"/>')
    b.append(f'<path d="M310,204 L232,204" class="ln" marker-end="url(#arr)"/>')
    b.append(text(270, 282, "Every operation moves data", "t sm", "middle"))
    b.append(text(270, 300, "across the bus: the memory wall", "t sm", "middle"))
    b.append(f'<path d="M270,262 L270,192" stroke="{GOLD}" stroke-width="1.4" fill="none" stroke-dasharray="3 3"/>')

    # divider arrow
    b.append(f'<path d="M545,171 L600,171" stroke="{BLUE}" stroke-width="2.4" fill="none" marker-end="url(#arrb)"/>')

    # right panel: crossbar
    x0, y0 = 720, 100
    b.append(text(640, 40, "Neuromorphic, compute-in-memory", "h lg"))
    b.append(text(640, 62, "Memory arrays compute where data are stored", "t sm m"))
    rows, cols, gap = 5, 6, 30
    for r in range(rows):
        y = y0 + r * gap
        b.append(f'<line x1="{x0 - 30}" y1="{y}" x2="{x0 + (cols - 1) * gap + 18}" y2="{y}" stroke="{BLUE}" stroke-width="2"/>')
        b.append(text(x0 - 36, y + 5, f"V{r + 1}", "t sm b", "end"))
    for c in range(cols):
        x = x0 + c * gap
        b.append(f'<line x1="{x}" y1="{y0 - 18}" x2="{x}" y2="{y0 + (rows - 1) * gap + 30}" stroke="{NAVY}" stroke-width="2"/>')
        b.append(f'<path d="M{x},{y0 + (rows - 1) * gap + 34} l0,18" stroke="{TEAL}" stroke-width="2" marker-end="url(#arr)"/>')
        b.append(text(x, y0 + (rows - 1) * gap + 72, f"I{c + 1}", "t sm", "middle"))
    for r in range(rows):
        for c in range(cols):
            g = 0.35 + 0.6 * (((r * 7 + c * 3) % 5) / 4)
            b.append(f'<circle cx="{x0 + c * gap}" cy="{y0 + r * gap}" r="7" fill="{TEAL}" opacity="{g:.2f}"/>')
    b.append(text(795, 322, "Each cell stores a weight as conductance G; currents sum", "t sm", "middle"))
    b.append(text(795, 340, "on each column (I = Σ G×V), a multiply–accumulate in one step", "t sm", "middle"))
    return svg(W, H, "".join(b), "Von Neumann bottleneck versus compute-in-memory")


# ------------------------------------------------------------------ 2. research stack (overview)
def iso_face(cx, cy, w, d):
    return f"{cx - w / 2},{cy} {cx},{cy - d / 2} {cx + w / 2},{cy} {cx},{cy + d / 2}"


def slab(cx, cy, w, d, t, top, side1, side2):
    s = []
    s.append(f'<polygon points="{cx - w / 2},{cy} {cx},{cy + d / 2} {cx},{cy + d / 2 + t} {cx - w / 2},{cy + t}" fill="{side1}"/>')
    s.append(f'<polygon points="{cx + w / 2},{cy} {cx},{cy + d / 2} {cx},{cy + d / 2 + t} {cx + w / 2},{cy + t}" fill="{side2}"/>')
    s.append(f'<polygon points="{iso_face(cx, cy, w, d)}" fill="{top}"/>')
    return "".join(s)


def on_face(cx, cy, w, d, inner):
    a, bb, c, dd = w / 400, -d / 400, w / 400, d / 400
    return f'<g transform="matrix({a},{bb},{c},{dd},{cx - w / 2},{cy})">{inner}</g>'


def research_stack():
    W, H = 980, 520
    cx, w, d, t = 300, 360, 180, 26
    ys = [130, 270, 410]
    b = []
    # bottom: process (lattice)
    y = ys[2]
    b.append(slab(cx, y, w, d, t, "#eef1f4", "#c9d0d8", "#b7c0ca"))
    lat = []
    for i in range(9):
        for j in range(9):
            px, py = 12 + i * 22 + (j % 2) * 11, 12 + j * 20
            if px < 196 and py < 196:
                lat.append(f'<circle cx="{px}" cy="{py}" r="3.4" fill="{TEAL if (i + j) % 3 else VIOLET}"/>')
    b.append(on_face(cx, y, w, d, "".join(lat)))
    # middle: memory devices (crossbar)
    y = ys[1]
    b.append(slab(cx, y, w, d, t, "#e9f0f8", "#b9cbe0", "#a5bbd5"))
    cb = []
    for k in range(7):
        p = 28 + k * 24
        cb.append(f'<line x1="14" y1="{p}" x2="186" y2="{p}" stroke="{BLUE}" stroke-width="2.2" vector-effect="non-scaling-stroke"/>')
        cb.append(f'<line x1="{p}" y1="14" x2="{p}" y2="186" stroke="{NAVY}" stroke-width="2.2" vector-effect="non-scaling-stroke"/>')
    for i in range(7):
        for j in range(7):
            cb.append(f'<rect x="{24 + i * 24}" y="{24 + j * 24}" width="8" height="8" fill="{GOLD}"/>')
    b.append(on_face(cx, y, w, d, "".join(cb)))
    # top: neuromorphic (network)
    y = ys[0]
    b.append(slab(cx, y, w, d, t, "#eaf2fb", NAVY, "#0a4a80"))
    nodes = {0: [40, 100, 160], 1: [30, 75, 125, 170], 2: [60, 140]}
    xs = {0: 35, 1: 100, 2: 165}
    net = []
    for L in (0, 1):
        for a_ in nodes[L]:
            for b_ in nodes[L + 1]:
                net.append(f'<line x1="{xs[L]}" y1="{a_}" x2="{xs[L + 1]}" y2="{b_}" stroke="{BLUE}" stroke-width="1.2" opacity=".55" vector-effect="non-scaling-stroke"/>')
    for L, ys_ in nodes.items():
        for yy in ys_:
            net.append(f'<circle cx="{xs[L]}" cy="{yy}" r="9" fill="{BLUE}"/>')
    b.append(on_face(cx, y, w, d, "".join(net)))

    # vertical arrow (left)
    b.append(f'<path d="M70,470 L70,90" stroke="{BLUE}" stroke-width="2.4" fill="none" marker-end="url(#arrb)"/>')
    b.append(text(52, 280, "From atoms to AI", "t md bold b", "middle", 'transform="rotate(-90 52 280)"'))

    labels = [
        ("Neuromorphic Computing", ["Synapse & neuron devices, arrays,", "network-level accuracy and power"]),
        ("Next-generation Memory Devices", ["New memories for the hierarchy,", "modeled from physics to circuits"]),
        ("Advanced Semiconductor Process", ["Next-generation materials, interfaces,", "and monolithic 3D integration"]),
    ]
    for (ttl, sub), y in zip(labels, ys):
        b.append(f'<path d="M{cx + w / 2 + 12},{y + 8} L585,{y + 8}" stroke="{RULE}" stroke-width="1.4"/>')
        b.append(f'<circle cx="{cx + w / 2 + 12}" cy="{y + 8}" r="3.5" fill="{MUTED}"/>')
        b.append(text(600, y + 2, ttl, "h lg"))
        b.append(lines(600, y + 26, sub, "t md m"))
    # modeling bracket
    b.append(f'<path d="M940,250 L950,250 L950,440 L940,440" stroke="{VIOLET}" stroke-width="1.6" fill="none"/>')
    b.append(text(966, 345, "Modeling & simulation", "t sm bold", "middle", f'transform="rotate(90 966 345)" style="fill:{VIOLET}"'))
    return svg(W, H, "".join(b), "NCDL research stack: process, memory devices, neuromorphic computing")


# ------------------------------------------------------------------ 3. neuromorphic flow
def neuromorphic_flow():
    W, H = 1000, 360
    b = []
    stages = [
        ("Synapse & neuron", "devices"),
        ("Arrays", "on chip"),
        ("Measured", "device data"),
        ("State-of-the-art", "networks"),
        ("Accuracy", "& power"),
    ]
    bx, by, bw, bh, gap = 30, 70, 160, 150, 37
    # focus band behind stages 3-5
    fx = bx + 2 * (bw + gap) - 14
    b.append(f'<rect x="{fx}" y="34" width="{3 * bw + 2 * gap + 28}" height="296" rx="18" fill="{TINT}"/>')
    b.append(text(fx + 18, 58, "Our focus: what real devices do inside real networks", "t sm bold b"))
    for k, (lab1, lab2) in enumerate(stages):
        x = bx + k * (bw + gap)
        b.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="#fff" stroke="{RULE}" stroke-width="1.4"/>')
        b.append(f'<circle cx="{x + 22}" cy="{by + 22}" r="12" fill="{NAVY}"/>')
        b.append(text(x + 22, by + 27, str(k + 1), "t sm bold w", "middle"))
        icx, icy = x + bw / 2, by + bh / 2 + 10
        if k == 0:
            b.append(f'<line x1="{icx - 52}" y1="{icy}" x2="{icx + 52}" y2="{icy}" stroke="{RULE}"/><line x1="{icx}" y1="{icy - 44}" x2="{icx}" y2="{icy + 44}" stroke="{RULE}"/>')
            b.append(f'<path d="{pinched_loop(icx, icy, 50, 40)}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
        elif k == 1:
            for r in range(5):
                b.append(f'<line x1="{icx - 52}" y1="{icy - 40 + r * 20}" x2="{icx + 52}" y2="{icy - 40 + r * 20}" stroke="{BLUE}" stroke-width="1.8"/>')
                b.append(f'<line x1="{icx - 40 + r * 20}" y1="{icy - 52}" x2="{icx - 40 + r * 20}" y2="{icy + 52}" stroke="{NAVY}" stroke-width="1.8"/>')
            for r in range(5):
                for c in range(5):
                    b.append(f'<circle cx="{icx - 40 + c * 20}" cy="{icy - 40 + r * 20}" r="4.5" fill="{TEAL}" opacity="{0.4 + 0.15 * ((r + 2 * c) % 4)}"/>')
        elif k == 2:
            b.append(f'<path d="M{icx - 54},{icy + 44} L{icx - 54},{icy - 46} M{icx - 54},{icy + 44} L{icx + 54},{icy + 44}" stroke="{MUTED}" stroke-width="1.2" fill="none"/>')
            pts = []
            for i in range(26):
                u = i / 25
                yv = icy + 40 - 78 * (1 - math.exp(-3.2 * u)) + (5 * math.sin(i * 2.7))
                pts.append((icx - 50 + u * 100, yv))
            b.append("".join(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="2.6" fill="{VIOLET}"/>' for p in pts))
            b.append(text(icx + 52, icy + 60, "pulses", "t sm m", "end"))
            b.append(text(icx - 62, icy, "G", "t sm m", "middle"))
        elif k == 3:
            for j, (lbl, col) in enumerate([("Attention", BLUE), ("Feed-forward", NAVY), ("Attention", BLUE)]):
                yy = icy - 50 + j * 30
                b.append(f'<rect x="{icx - 56}" y="{yy}" width="112" height="22" rx="6" fill="{col}" opacity="{0.9 if j != 2 else 0.35}"/>')
                b.append(text(icx, yy + 15, lbl, "t sm w", "middle"))
            b.append(f'<rect x="{icx - 56}" y="{icy + 42}" width="50" height="20" rx="6" fill="#fff" stroke="{TEAL}" stroke-width="1.4"/>')
            b.append(text(icx - 31, icy + 56, "G", "t sm bold", "middle"))
            b.append(f'<rect x="{icx + 6}" y="{icy + 42}" width="50" height="20" rx="6" fill="#fff" stroke="{TEAL}" stroke-width="1.4"/>')
            b.append(text(icx + 31, icy + 56, "D", "t sm bold", "middle"))
            b.append(f'<path d="M{icx - 6},{icy + 52} L{icx + 4},{icy + 52}" stroke="{TEAL}" stroke-width="1.4" marker-end="url(#arr)"/>')
        else:
            base = icy + 44
            for j, (hv, col, lbl) in enumerate([(80, BLUE, "accuracy"), (34, GOLD, "energy")]):
                xx = icx - 44 + j * 52
                b.append(f'<rect x="{xx}" y="{base - hv}" width="36" height="{hv}" rx="4" fill="{col}"/>')
                b.append(text(xx + 18, base + 18, lbl, "t sm m", "middle"))
            b.append(f'<line x1="{icx - 56}" y1="{base}" x2="{icx + 56}" y2="{base}" stroke="{MUTED}"/>')
        b.append(text(x + bw / 2, by + bh + 30, lab1, "t md bold", "middle"))
        b.append(text(x + bw / 2, by + bh + 50, lab2, "t md", "middle"))
        if k < 4:
            b.append(f'<path d="M{x + bw + 6},{by + bh / 2} L{x + bw + gap - 6},{by + bh / 2}" class="ln" marker-end="url(#arr)"/>')
    b.append(text(fx + 3 * bw + 2 * gap + 12, 318, "GAN and Transformer networks with in-memory hardware", "t sm m", "end"))
    return svg(W, H, "".join(b), "Neuromorphic computing workflow from devices to network-level evaluation")


# ------------------------------------------------------------------ 4. memory hierarchy
def memory_hierarchy():
    W, H = 980, 470
    b = []
    cx = 310
    levels = [
        ("SRAM", "cache", 70, NAVY),
        ("DRAM / HBM", "main memory", 140, "#0a4a80"),
        ("NAND flash", "storage", 210, BLUE),
        ("HDD", "archive", 270, "#5b8fc4"),
    ]
    top_y, lh, gap = 40, 70, 34
    for k, (name, role, half, col) in enumerate(levels):
        y = top_y + k * (lh + gap)
        tw = half - 40 if k else 30
        b.append(f'<polygon points="{cx - tw},{y} {cx + tw},{y} {cx + half},{y + lh} {cx - half},{y + lh}" fill="{col}"/>')
        b.append(text(cx, y + lh / 2 + 2, name, "t md bold w", "middle"))
        b.append(text(cx, y + lh / 2 + 21, role, "t sm w", "middle", 'opacity=".85"'))
    # gaps with new memory insertions
    ins = [
        (top_y + lh + gap / 2, TEAL, "On-chip, M3D memory", ["2T (capacitor-less) DRAM", "oxide- and 2D-channel memory transistors"]),
        (top_y + 2 * (lh + gap) - gap / 2, VIOLET, "Storage-class memory", ["RRAM", "transistor-based non-volatile memory"]),
    ]
    for (y, col, ttl, sub) in ins:
        b.append(f'<rect x="{cx - 170}" y="{y - 6}" width="340" height="12" rx="6" fill="{col}"/>')
        b.append(f'<path d="M{cx + 176},{y} L600,{y}" stroke="{col}" stroke-width="1.6" stroke-dasharray="4 3"/>')
        b.append(f'<circle cx="600" cy="{y}" r="4" fill="{col}"/>')
        b.append(text(615, y - 8, ttl, "h lg", extra=f'style="fill:{col}"'))
        b.append(lines(615, y + 16, sub, "t md"))
    # axis
    b.append(f'<path d="M20,440 L20,50" stroke="{MUTED}" stroke-width="1.4" marker-end="url(#arr)"/>')
    b.append(text(34, 60, "faster", "t sm m"))
    b.append(text(34, 438, "denser, cheaper per bit", "t sm m"))
    b.append(text(615, 330, "Goal: reinforce the hierarchy", "t md bold"))
    b.append(text(615, 352, "where DRAM and NAND fall short", "t md m"))
    return svg(W, H, "".join(b), "Memory hierarchy and where NCDL's next-generation memories fit")


# ------------------------------------------------------------------ 5. modeling hierarchy
def modeling_stack():
    W, H = 1000, 300
    b = []
    steps = [
        ("DFT", ["atoms & defects"]),
        ("TCAD", ["device physics"]),
        ("Monte Carlo", ["physics-based", "model"]),
        ("Behavioral", ["compact model"]),
        ("Circuit", ["simulation & design"]),
    ]
    bw, gap, y = 160, 36, 70
    x0 = 24
    # core highlight (MC + behavioral)
    hx = x0 + 2 * (bw + gap) - 12
    b.append(f'<rect x="{hx}" y="{y - 30}" width="{2 * bw + gap + 24}" height="168" rx="16" fill="{TINT}"/>')
    b.append(text(hx + 14, y - 10, "Core of our modeling work", "t sm bold b"))
    for k, (ttl, sub) in enumerate(steps):
        x = x0 + k * (bw + gap)
        col = VIOLET if k < 2 else (BLUE if k < 4 else NAVY)
        b.append(f'<rect x="{x}" y="{y}" width="{bw}" height="96" rx="14" fill="#fff" stroke="{col}" stroke-width="1.8"/>')
        b.append(text(x + bw / 2, y + 38, ttl, "h lg", "middle"))
        b.append(lines(x + bw / 2, y + 62, sub, "t sm m", "middle", lh=17))
        if k < 4:
            b.append(f'<path d="M{x + bw + 6},{y + 48} L{x + bw + gap - 6},{y + 48}" class="ln" marker-end="url(#arr)"/>')
    # match arrow between MC and behavioral
    mx = x0 + 3 * (bw + gap) - gap / 2
    b.append(text(mx, y + 120, "matched", "t sm b", "middle"))
    # measurement feedback
    fy = 236
    b.append(f'<path d="M{x0 + 2 * (bw + gap) + bw / 2},{fy} L{x0 + 2 * (bw + gap) + bw / 2},{y + 100}" stroke="{TEAL}" stroke-width="1.6" fill="none" marker-end="url(#arr)"/>')
    b.append(f'<path d="M{x0 + 3 * (bw + gap) + bw / 2},{fy} L{x0 + 3 * (bw + gap) + bw / 2},{y + 100}" stroke="{TEAL}" stroke-width="1.6" fill="none" marker-end="url(#arr)"/>')
    b.append(f'<line x1="{x0 + 2 * (bw + gap) + bw / 2}" y1="{fy}" x2="{x0 + 3 * (bw + gap) + bw / 2}" y2="{fy}" stroke="{TEAL}" stroke-width="1.6"/>')
    b.append(text(x0 + 2 * (bw + gap) + bw + gap / 2, fy + 24, "calibrated with our fabricated devices", "t sm", "middle", f'style="fill:{TEAL}"'))
    b.append(f'<path d="M{x0},{y + 110} L{x0},{y + 120} L{x0 + 2 * bw + gap},{y + 120} L{x0 + 2 * bw + gap},{y + 110}" stroke="{VIOLET}" stroke-width="1.5" fill="none"/>')
    b.append(text(x0 + bw + gap / 2, y + 142, "linked when atomistic or", "t sm m", "middle"))
    b.append(text(x0 + bw + gap / 2, y + 160, "device-level detail matters", "t sm m", "middle"))
    return svg(W, H, "".join(b), "Simulation hierarchy from DFT and TCAD to circuit design")


# ------------------------------------------------------------------ 6. process / M3D
def process_m3d():
    W, H = 980, 470
    b = []
    x0, x1 = 60, 560
    # substrate
    b.append(f'<rect x="{x0}" y="380" width="{x1 - x0}" height="60" fill="#c9ced6"/>')
    b.append(text(x0 + 14, 418, "Silicon substrate", "t sm bold"))
    # FEOL transistors
    for k in range(6):
        gx = x0 + 40 + k * 80
        b.append(f'<rect x="{gx}" y="352" width="34" height="28" rx="3" fill="#8b95a3"/>')
        b.append(f'<rect x="{gx - 14}" y="376" width="62" height="6" fill="#aab3bf"/>')
    # BEOL
    for layer, y in enumerate([300, 248, 196]):
        b.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="40" fill="#f1f3f6"/>')
        for k in range(5 - layer % 2):
            lx = x0 + 30 + k * (95 + layer * 6)
            if lx + 60 < x1:
                b.append(f'<rect x="{lx}" y="{y + 14}" width="60" height="12" fill="{BRONZE}" opacity=".85"/>')
                b.append(f'<rect x="{lx + 24}" y="{y + 26}" width="10" height="{(352 - y - 26) if layer == 0 else 26}" fill="{BRONZE}" opacity=".6"/>')
    # upper tier
    ty = 70
    b.append(f'<rect x="{x0}" y="{ty + 90}" width="{x1 - x0}" height="36" fill="#e9eef5"/>')  # isolation
    for k in range(3):
        dx = x0 + 50 + k * 160
        # gate (bottom gate)
        b.append(f'<rect x="{dx + 20}" y="{ty + 70}" width="80" height="16" rx="2" fill="{NAVY}"/>')
        # dielectric
        b.append(f'<rect x="{dx}" y="{ty + 56}" width="120" height="14" fill="{VIOLET}" opacity=".8"/>')
        # channel
        b.append(f'<rect x="{dx}" y="{ty + 46}" width="120" height="10" fill="{TEAL}"/>')
        # contacts
        b.append(f'<rect x="{dx - 6}" y="{ty + 24}" width="34" height="22" rx="2" fill="{GOLD}"/>')
        b.append(f'<rect x="{dx + 92}" y="{ty + 24}" width="34" height="22" rx="2" fill="{GOLD}"/>')
    # tier brackets
    b.append(f'<path d="M{x0 - 14},{ty + 20} L{x0 - 24},{ty + 20} L{x0 - 24},{ty + 126} L{x0 - 14},{ty + 126}" class="ln"/>')
    b.append(text(x0 - 32, ty + 73, "Upper tier", "t sm bold", "middle", f'transform="rotate(-90 {x0 - 32} {ty + 73})"'))
    b.append(f'<path d="M{x0 - 14},196 L{x0 - 24},196 L{x0 - 24},340 L{x0 - 14},340" class="ln"/>')
    b.append(text(x0 - 32, 268, "Interconnects", "t sm bold", "middle", f'transform="rotate(-90 {x0 - 32} 268)"'))
    b.append(f'<path d="M{x0 - 14},348 L{x0 - 24},348 L{x0 - 24},440 L{x0 - 14},440" class="ln"/>')
    b.append(text(x0 - 32, 394, "Si CMOS", "t sm bold", "middle", f'transform="rotate(-90 {x0 - 32} 394)"'))
    # callouts
    calls = [
        (ty + 35, GOLD, "Metal contacts", ["low-resistance, reliable", "contact engineering"]),
        (ty + 51, TEAL, "Thin-film growth & synthesis", ["2D (MoS2, Bi2O2Se) and oxide", "(IGZO) semiconductor channels"]),
        (ty + 63, VIOLET, "Dielectric interfaces", ["metal-oxide dielectrics on", "new channel materials"]),
        (ty + 108, NAVY, "Monolithic 3D integration", ["low-temperature, BEOL-compatible", "processes on finished silicon"]),
    ]
    ys = [60, 150, 240, 330]
    for (py, col, ttl, sub), ly in zip(calls, ys):
        b.append(f'<path d="M{x1 + 4},{py} L{x1 + 40},{py} L{x1 + 70},{ly + 4} L{x1 + 84},{ly + 4}" stroke="{col}" stroke-width="1.5" fill="none"/>')
        b.append(f'<circle cx="{x1 + 4}" cy="{py}" r="3.5" fill="{col}"/>')
        b.append(text(x1 + 92, ly + 8, ttl, "h md", extra=f'style="fill:{col if col != GOLD else "#8a6d12"}"'))
        b.append(lines(x1 + 92, ly + 30, sub, "t sm m", lh=18))
    return svg(W, H, "".join(b), "Monolithic 3D integration of new-material devices on silicon")


files = {
    "von-neumann.svg": von_neumann(),
    "research-stack.svg": research_stack(),
    "neuromorphic-flow.svg": neuromorphic_flow(),
    "memory-hierarchy.svg": memory_hierarchy(),
    "modeling-stack.svg": modeling_stack(),
    "process-m3d.svg": process_m3d(),
}
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print("wrote", name, len(content))
