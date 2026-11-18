"""Build the V3 design sheets (identity + writeup) as standalone HTML with inline SVG.

Usage: python3 build_v3.py  -> writes ../planches/v3/00-identite.html and 01-writeup.html
All values in the figures are DEMO placeholders until eval/run.py exists.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "planches" / "v3"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palette
VOID, INDIGO, VIOLET, LILAC = "#08071c", "#151340", "#5b5bf0", "#a9a6ff"
AUR, AUR_INK, MAG = "#3df0a8", "#0b8a5f", "#e14bd6"
ERR, ERR_INK = "#ff5c7a", "#c42a45"
PAPER, INK, GREY = "#f6f5fc", "#0f0e26", "#6b6987"

PAL = {
    "glass": ("#3b3894", "#2a2774", "#1c1a56", LILAC),
    "valid": ("#8cf8cf", "#33d996", "#17a571", INK),
    "err":   ("#ff9cae", "#e4496b", "#b5304f", "#fff"),
    "spec":  ("#8d8cff", VIOLET, "#3f3fc4", "#fff"),
    "paper": ("#ffffff", "#e9e8f6", "#d6d4ec", INK),
}

# ---------------------------------------------------------------- glyphs (motif A)
GLYPHS = {
    "EXTRACT": "111000111", "SPEC": "000010000", "SOLVE": "010111010",
    "AUDIT": "101010101", "PROVE": "111101111", "WRITE": "100110111",
    "DONE": "111111111", "LEDGER": "101101101",
}
KERNELS = [  # name, glyph variant, used on the shown dev tasks (demo)
    ("beam-simple", "110110000", True), ("frame-2d", "111100100", False),
    ("truss", "010101010", False), ("section-props", "111010010", False),
    ("buckling-euler", "100100111", False), ("mna-ac", "011110011", True),
    ("three-phase", "100010001", True), ("cable-size", "110011001", False),
    ("thermo-balance", "001011111", False), ("fluid-network", "101111101", False),
]


def glyph(bits, x, y, cell, on, off="none", gap=None, rx=None):
    gap = cell * 0.18 if gap is None else gap
    rx = cell * 0.12 if rx is None else rx
    out = []
    for i, b in enumerate(bits):
        cx, cy = x + (i % 3) * (cell + gap), y + (i // 3) * (cell + gap)
        fill = on if b == "1" else off
        if fill == "none":
            out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{rx:.1f}" fill="none" stroke="{on}" stroke-opacity=".28"/>')
        else:
            out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="{rx:.1f}" fill="{fill}"/>')
    return "".join(out)


def glyph_svg(bits, size=24, on=INK, off="none"):
    cell = size / 3.36
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true">{glyph(bits, 0, 0, cell, on, off)}</svg>'


# ---------------------------------------------------------------- iso (motif B)
C, S = 0.8660, 0.5


class Iso:
    def __init__(self, ox, oy, k=1.0):
        self.ox, self.oy, self.k = ox, oy, k

    def P(self, x, y, z=0):
        k = self.k
        return (self.ox + (x - y) * C * k, self.oy + (x + y) * S * k - z * k)

    def pts(self, *ps):
        return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in ps)

    def tile(self, x, y, w, d, fill, stroke="none", op=1, z=0):
        P = self.P
        return f'<polygon points="{self.pts(P(x,y,z),P(x+w,y,z),P(x+w,y+d,z),P(x,y+d,z))}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="1"/>'

    def block(self, x, y, w, d, h, kind="glass", z=0, left_text=None, right_text=None,
              top_glyph=None, ghost=False, glow=None, right_size=None, left_size=None, sheen=True, spark=None):
        P = self.P
        x1, y1, zt = x + w, y + d, z + h
        out = []
        if ghost:
            st = f'fill="none" stroke="{LILAC}" stroke-width="1.3" stroke-dasharray="4 4" stroke-opacity=".75"'
            out.append(f'<polygon points="{self.pts(P(x,y1,z),P(x1,y1,z),P(x1,y1,zt),P(x,y1,zt))}" {st}/>')
            out.append(f'<polygon points="{self.pts(P(x1,y,z),P(x1,y1,z),P(x1,y1,zt),P(x1,y,zt))}" {st}/>')
            out.append(f'<polygon points="{self.pts(P(x,y,zt),P(x1,y,zt),P(x1,y1,zt),P(x,y1,zt))}" {st}/>')
            return "".join(out)
        top, left, right, tcol = PAL[kind]
        if glow:
            gx, gy = P(x + w / 2, y + d / 2, z + h / 2)
            out.append(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="{w*self.k*1.4:.1f}" ry="{(h*self.k/2+w*self.k*.6):.1f}" fill="{glow}" opacity=".35" filter="url(#blur18)"/>')
        out.append(f'<polygon points="{self.pts(P(x,y1,z),P(x1,y1,z),P(x1,y1,zt),P(x,y1,zt))}" fill="{left}"/>')
        out.append(f'<polygon points="{self.pts(P(x1,y,z),P(x1,y1,z),P(x1,y1,zt),P(x1,y,zt))}" fill="{right}"/>')
        out.append(f'<polygon points="{self.pts(P(x,y,zt),P(x1,y,zt),P(x1,y1,zt),P(x,y1,zt))}" fill="{top}"/>')
        if sheen and h * self.k > 30:  # reflection streak (Psychoactive light)
            out.append(f'<polygon points="{self.pts(P(x,y1,zt),P(x+w*.18,y1,zt),P(x+w*.62,y1,z),P(x+w*.44,y1,z))}" fill="#fff" opacity=".10"/>')
            out.append(f'<polyline points="{self.pts(P(x,y1,zt),P(x1,y1,zt),P(x1,y,zt))}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1"/>')
        k = self.k
        if left_text:
            px, py = P(x + w * .08, y1, zt)
            fs = left_size or max(9, min(13, w * k * .13))
            out.append(f'<g transform="matrix({C},{S},0,1,{px:.1f},{py:.1f})"><text x="0" y="{fs+8:.1f}" font-family="ui-monospace,Menlo,monospace" font-size="{fs:.1f}" letter-spacing="1.2" fill="{tcol}" opacity=".9">{left_text}</text></g>')
        if spark:
            px, py = P(x + w * .08, y1, z + h * .45)
            pts = " ".join(f"{u*w*k*.84:.1f},{-v*h*k*.3:.1f}" for u, v in spark)
            out.append(f'<g transform="matrix({C},{S},0,1,{px:.1f},{py:.1f})"><polyline points="{pts}" fill="none" stroke="{tcol}" stroke-width="1.6" stroke-dasharray="3 3" opacity=".85"/></g>')
        if right_text:
            px, py = P(x1, y1 - d * .1, z + h * .1)
            fs = right_size or max(12, min(34, d * k * .42))
            out.append(f'<g transform="matrix({C},{-S},0,1,{px:.1f},{py:.1f})"><text x="0" y="0" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-weight="600" font-size="{fs:.1f}" letter-spacing="-.5" fill="{tcol}">{right_text}</text></g>')
        if top_glyph:
            # glyph laid flat on top face
            px, py = P(x + w * .2, y + d * .2, zt)
            cell = w * .6 / 3.4
            out.append(f'<g transform="matrix({C},{S},{-C},{S},{px:.1f},{py:.1f})">{glyph(top_glyph, 0, 0, cell, tcol)}</g>')
        return "".join(out)


# ---------------------------------------------------------------- aurora + marks (motifs C, D)
def defs(uid):
    return f'''<defs>
  <filter id="blur18" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="18"/></filter>
  <filter id="smoke{uid}" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency=".004 .011" numOctaves="3" seed="{7+len(uid)}" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="160" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="22"/>
  </filter>
  <filter id="wisp{uid}" x="-20%" y="-50%" width="140%" height="200%">
    <feTurbulence type="fractalNoise" baseFrequency=".008 .03" numOctaves="2" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="40" result="d"/><feGaussianBlur in="d" stdDeviation="3"/>
  </filter>
  <filter id="grain{uid}"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter>
  <pattern id="scan{uid}" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" opacity=".035"/></pattern>
  <linearGradient id="chrome{uid}" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".48" stop-color="#d9d8ee"/><stop offset=".52" stop-color="#8f8cb8"/><stop offset="1" stop-color="#e9e7ff"/>
  </linearGradient>
</defs>'''


def aurora(uid, w, h, variant="full"):
    """Smoky violet field + aurora streaks + light reflection + grain + scanlines."""
    if variant == "band":
        blobs = [(w*.2, h*.6, w*.35, h*1.2, VIOLET, .9), (w*.7, h*.3, w*.4, h, "#2c2a9a", .9), (w*.55, h*.9, w*.25, h*.8, MAG, .35)]
        streaks = [(f"M0 {h*.8} C {w*.3} {h*.2}, {w*.6} {h*1.1}, {w} {h*.3}", AUR, .55, 5)]
    elif variant == "thread":
        blobs = [(w*.5, h*.5, w*.6, h*3, VIOLET, .8)]
        streaks = [(f"M0 {h*.5} C {w*.3} 0, {w*.7} {h}, {w} {h*.5}", AUR, .7, 2)]
    else:
        blobs = [(w*.25, h*.35, w*.32, h*.45, VIOLET, .95), (w*.75, h*.65, w*.38, h*.5, "#3a38c8", .9),
                 (w*.55, h*.15, w*.25, h*.3, MAG, .38), (w*.15, h*.9, w*.3, h*.3, "#2a2890", .9),
                 (w*.9, h*.15, w*.2, h*.3, "#6d6bff", .6)]
        streaks = [(f"M{-w*.05} {h*.95} C {w*.25} {h*.45}, {w*.55} {h*.75}, {w*1.05} {h*.12}", AUR, .55, 7),
                   (f"M{-w*.05} {h*.6} C {w*.3} {h*.2}, {w*.6} {h*.55}, {w*1.05} {h*.35}", MAG, .45, 4),
                   (f"M{w*.1} {h*1.05} C {w*.4} {h*.6}, {w*.7} {h*.9}, {w*1.05} {h*.7}", "#9fe8ff", .25, 3)]
    g = [f'<rect width="{w}" height="{h}" fill="{VOID}"/>', f'<g filter="url(#smoke{uid})">']
    for cx, cy, rx, ry, col, op in blobs:
        g.append(f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="{col}" opacity="{op}"/>')
    g.append("</g>")
    for d, col, op, sw in streaks:
        g.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{sw}" filter="url(#wisp{uid})"/>')
    # specular reflection: a soft diagonal light band
    g.append(f'<path d="M{w*.35} 0 L{w*.47} 0 L{w*.2} {h} L{w*.08} {h} Z" fill="#fff" opacity=".045"/>')
    g.append(f'<rect width="{w}" height="{h}" filter="url(#grain{uid})" opacity=".09"/>')
    g.append(f'<rect width="{w}" height="{h}" fill="url(#scan{uid})"/>')
    return "".join(g)


def marks(pts, col="#fff", op=.6, s=6):
    return "".join(f'<path d="M{x-s} {y}H{x+s}M{x} {y-s}V{y+s}" stroke="{col}" stroke-opacity="{op}" stroke-width="1"/>' for x, y in pts)


def frame(uid, w, h, inner, variant="full", r=26, pad=0, caption=None, tag=None):
    """Rounded aurora card + ambilight bleed + crosshair marks (Psychoactive frame)."""
    W, H = w + 2 * pad, h + 2 * pad
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" role="img">', defs(uid),
           f'<clipPath id="clip{uid}"><rect x="{pad}" y="{pad}" width="{w}" height="{h}" rx="{r}"/></clipPath>']
    if pad:
        out.append(f'<g opacity=".55" filter="url(#blur18)"><g transform="translate({pad-pad*.6},{pad-pad*.6}) scale({(w+pad*1.2)/w:.3f},{(h+pad*1.2)/h:.3f})">{aurora(uid, w, h, variant)}</g></g>')
    out.append(f'<g clip-path="url(#clip{uid})"><g transform="translate({pad},{pad})">{aurora(uid, w, h, variant)}{inner}</g></g>')
    out.append(f'<rect x="{pad+.5}" y="{pad+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="#fff" stroke-opacity=".12"/>')
    if tag:
        out.append(f'<g transform="translate({pad+28},{pad+26})">{glyph(tag[1], 0, 0, 5.2, "#fff")}<text x="26" y="13" font-family="ui-monospace,Menlo,monospace" font-size="12" letter-spacing="1.6" fill="#fff" opacity=".85">{tag[0]}</text></g>')
    if caption:
        out.append(f'<text x="{pad+w-28}" y="{pad+40}" text-anchor="end" font-family="ui-monospace,Menlo,monospace" font-size="11.5" letter-spacing=".8" fill="{LILAC}" opacity=".85">{caption}</text>')
    out.append(marks([(pad + 14, pad + h / 2), (pad + w - 14, pad + h / 2), (pad + w / 2, pad + h - 14)]))
    out.append("</svg>")
    return "".join(out)


MONO = 'font-family="ui-monospace,Menlo,monospace"'
SANS = 'font-family="Helvetica Neue,Helvetica,Arial,sans-serif"'


def floor(iso, nx, ny, T, op=1, x0=0, y0=0):
    """Night version of Baseten's striped floor: diagonal bands, a few tinted tiles."""
    tints = {(1, 0): VIOLET, (4, 2): MAG, (6, 1): VIOLET, (2, 3): AUR, (7, 3): VIOLET}
    out = []
    for i in range(nx):
        for j in range(ny):
            band = (i + j) % 3
            fill = ["#1b1950", "#211f60", "#17154a"][band]
            o = op
            if (i, j) in tints:
                fill, o = tints[(i, j)], .32 * op
            out.append(iso.tile(x0 + i * T, y0 + j * T, T, T, fill, stroke="#3d3a8f", op=o))
    return "".join(out)


# ================================================================= MODULES
def m_banner():
    w, h = 1200, 600
    iso = Iso(735, 250, 1.0)
    T = 60
    inner = [floor(iso, 8, 8, T, .95, x0=-20, y0=-200)]
    bars = [("LLM ALONE", .11, "err"), ("KERNELS OFF", .17, "glass"), ("LEDGER OFF", .22, "glass"),
            ("AUDIT OFF", .25, "glass"), ("FULL HARNESS", .31, "valid")]
    for n, (name, v, kind) in enumerate(bars):
        x0, y0 = 30 + n * 64, 150 - n * 64
        spark = [(0, .2), (.2, .55), (.4, .8), (.6, .86), (.8, .9), (1, .9)] if kind == "valid" else None
        inner.append(iso.block(x0, y0, 58, 58, v * 820, kind, left_text=name, right_text=f"{v:.2f}",
                               glow=AUR if kind == "valid" else None, right_size=17, spark=spark,
                               top_glyph=GLYPHS["DONE"] if kind == "valid" else None))
    # fact tiles flat on the floor (ledger pins)
    for k, (lab, x, y) in enumerate([("F-03 · 6 000 mm", 70, 300), ("F-07 · 12 kN/m", 210, 160), ("K-1 · 54.0 kN·m", 350, 20)]):
        inner.append(iso.tile(x, y, 120, 34, "#ffffff", op=.92))
        px, py = iso.P(x + 8, y + 34, 0)
        inner.append(f'<g transform="matrix({C},{S},0,1,{px:.1f},{py:.1f})"><text y="-12" {MONO} font-size="11" fill="{INK}">{lab}</text></g>')
    # copy (left)
    inner.append(f'<g transform="translate(56,92)">{glyph(GLYPHS["LEDGER"], 0, 0, 6, "#fff")}<text x="32" y="16" {MONO} font-size="12.5" letter-spacing="2" fill="#fff" opacity=".85">PLE LEDGER KERNELS · KAGGLE WRITEUP</text></g>')
    inner.append(f'<text x="54" y="196" {SANS} font-size="62" font-weight="600" letter-spacing="-2.4" fill="url(#chromeban)">The model never</text>')
    inner.append(f'<text x="54" y="262" {SANS} font-size="62" font-weight="600" letter-spacing="-2.4" fill="url(#chromeban)">reads the drawing.</text>')
    inner.append(f'<text x="56" y="310" {SANS} font-size="19" fill="{LILAC}">It writes a typed spec. Code extracts, computes and audits.</text>')
    stats = [("DEV SCORE", "0.31", AUR, "LLM alone 0.11"), ("TOKENS / TASK", "24 k", "#fff", "LLM alone 62 k"), ("FAILURES", "25 → 7", "#fff", "29 dev tasks")]
    for n, (k, v, col, sub) in enumerate(stats):
        x = 56 + n * 150
        inner.append(f'<text x="{x}" y="400" {MONO} font-size="11" letter-spacing="1.5" fill="{LILAC}">{k}</text>')
        inner.append(f'<text x="{x}" y="440" {MONO} font-size="32" font-weight="600" letter-spacing="-1" fill="{col}">{v}</text>')
        inner.append(f'<text x="{x}" y="462" {MONO} font-size="11.5" fill="{ERR if n == 0 else LILAC}" opacity=".9">{sub}</text>')
    inner.append(f'<text x="56" y="556" {MONO} font-size="11" fill="{LILAC}" opacity=".7">block height = dev-set score · demo values, replaced by eval/run.py</text>')
    return frame("ban", w, h, "".join(inner))


def m_fig1():
    w, h = 1200, 470
    iso = Iso(70, 230, 1.0)
    inner = []
    stages = [("EXTRACT", "glass", "0 tok"), ("SPEC", "spec", "LLM"), ("SOLVE", "glass", "CPU"), ("AUDIT", "glass", "0 tok"),
              ("PROVE", "glass", "2nd parser"), ("WRITE", "glass", "ledger only"), ("DONE", "valid", "frame")]
    step = 74
    for n, (name, kind, sub) in enumerate(stages):
        x, y = 60 + n * step, 20 - n * step
        inner.append(iso.tile(x - 8, y - 8, 76, 76, "#24216a", stroke="#3d3a8f", op=.9))
        hh = 96 if kind == "spec" else 58
        inner.append(iso.block(x, y, 60, 60, hh, kind, top_glyph=GLYPHS[name], glow=VIOLET if kind == "spec" else (AUR if kind == "valid" else None),
                               left_text=name, left_size=10.5))
        bx, by = iso.P(x + 60, y + 60, 0)
        inner.append(f'<text x="{bx:.1f}" y="{by+22:.1f}" {MONO} font-size="11.5" fill="{LILAC}" text-anchor="middle">{sub}</text>')
        if n < 6:
            a, b = iso.P(x + 60, y + 30, 0), iso.P(x + step, y - step + 30, 0)
            inner.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#fff" stroke-opacity=".7" stroke-width="1.5"/>')
    # ledger rail: flat tiles in front
    facts = ["F-03 L = 6 000 mm · S-101 p.2", "F-07 w = 12 kN/m · spec §2.3", "K-1 M = 54.0 kN·m · beam-simple"]
    inner.append(f'<text x="40" y="372" {MONO} font-size="11.5" letter-spacing="1.4" fill="{AUR}">LEDGER · every published number points here</text>')
    x = 40
    for n, f in enumerate(facts):
        wpx = len(f) * 7.1 + 34
        inner.append(f'<rect x="{x}" y="386" width="{wpx:.0f}" height="28" rx="14" fill="#fff"/><circle cx="{x+14}" cy="400" r="4" fill="{AUR_INK}"/><text x="{x+26}" y="404" {MONO} font-size="11.5" fill="{INK}">{f}</text>')
        x += wpx + 10
    # repair loop: AUDIT back to SPEC, drawn above the blocks
    p1, p2 = iso.P(60 + 3 * step + 30, 20 - 3 * step + 30, 58), iso.P(60 + step + 30, 20 - step + 30, 96)
    inner.append(f'<path d="M{p1[0]:.0f} {p1[1]-40:.0f} C {p1[0]-30:.0f} {p1[1]-110:.0f}, {p2[0]+30:.0f} {p2[1]-80:.0f}, {p2[0]:.0f} {p2[1]-40:.0f}" fill="none" stroke="{ERR}" stroke-dasharray="4 5" stroke-width="1.5"/>')
    inner.append(f'<text x="{(p1[0]+p2[0])/2:.0f}" y="{min(p1[1],p2[1])-100:.0f}" text-anchor="middle" {MONO} font-size="11" fill="{ERR}">violation → re-emit only the faulty quantity</text>')
    inner.append(f'<text x="1168" y="450" text-anchor="end" {SANS} font-size="13" fill="#fff" opacity=".85">Only SPEC spends tokens. Every other block is deterministic code.</text>')
    return frame("f1", w, h, "".join(inner), variant="band", tag=("FIGURE 1 · ARCHITECTURE", GLYPHS["SOLVE"]), caption="done / error frame guaranteed · T-12 min finalisation")


def m_fig2():
    w, h = 1200, 520
    X0, Y0, PW, PH = 110, 90, 700, 340
    def X(t): return X0 + t / 70 * PW
    def Y(v): return Y0 + PH - v / .4 * PH
    g = [f'<rect x="{X0-40}" y="{Y0-30}" width="{PW+90}" height="{PH+90}" rx="16" fill="{INDIGO}" opacity=".72"/>']
    for v in (.1, .2, .3, .4):
        g.append(f'<line x1="{X0}" x2="{X0+PW}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#fff" stroke-opacity=".08"/>')
        g.append(f'<text x="{X0-12}" y="{Y(v)+4:.1f}" text-anchor="end" {MONO} font-size="12" fill="{LILAC}">{v:.1f}</text>')
    for t in (20, 40, 60):
        g.append(f'<text x="{X(t):.1f}" y="{Y0+PH+24}" text-anchor="middle" {MONO} font-size="12" fill="{LILAC}">{t} k</text>')
    g.append(f'<text x="{X0+PW/2}" y="{Y0+PH+48}" text-anchor="middle" {SANS} font-size="13" fill="#fff">tokens per task (mean, 29 dev tasks)</text>')
    g.append(f'<path d="M{X0} {Y0}V{Y0+PH}H{X0+PW}" fill="none" stroke="#fff" stroke-opacity=".5"/>')
    g.append(f'<line x1="{X0}" x2="{X0+PW}" y1="{Y(.138):.1f}" y2="{Y(.138):.1f}" stroke="{LILAC}" stroke-dasharray="3 5"/>')
    g.append(f'<text x="{X0+PW-4}" y="{Y(.138)-8:.1f}" text-anchor="end" {MONO} font-size="11.5" fill="{LILAC}">0.138 · Pareto entry (Stage 2)</text>')
    curve = [(12, .24), (18, .29), (24, .31), (36, .32), (48, .32)]
    pts = " ".join(f"{X(t):.1f},{Y(v):.1f}" for t, v in curve)
    g.append(f'<polyline points="{pts}" fill="none" stroke="{AUR}" stroke-width="8" stroke-opacity=".25" filter="url(#blur18)"/>')
    g.append(f'<polyline points="{pts}" fill="none" stroke="{AUR}" stroke-width="2.5"/>')
    for t, v in curve:
        g.append(f'<circle cx="{X(t):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{AUR}"/>')
    g.append(f'<circle cx="{X(24):.1f}" cy="{Y(.31):.1f}" r="9" fill="{AUR}" stroke="#fff" stroke-width="2"/>')
    g.append(f'<text x="{X(24)+14:.1f}" y="{Y(.31)-14:.1f}" {SANS} font-size="14" font-weight="600" fill="#fff">full harness 0.31</text>')
    g.append(f'<text x="{X(48):.1f}" y="{Y(.32)-14:.1f}" text-anchor="middle" {MONO} font-size="11.5" fill="{LILAC}">plateau → the cost left is CPU</text>')
    # ablations: point + glyph of the removed brick (motif A as data marker)
    abl = [("audit off", 23, .25, "AUDIT", -1), ("ledger off", 31, .22, "LEDGER", 1), ("kernels off", 38, .17, "SOLVE", 1), ("gemma-4-26b", 27, .21, None, -1)]
    for name, t, v, gl, side in abl:
        x, y = X(t), Y(v)
        if gl:
            g.append(f'<rect x="{x-11:.1f}" y="{y-11:.1f}" width="22" height="22" rx="5" fill="{VOID}" stroke="{LILAC}"/>{glyph(GLYPHS[gl], x-7.5, y-7.5, 4.3, LILAC)}')
        else:
            g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="none" stroke="#fff" stroke-width="1.6"/>')
        tx = x + 18 if side > 0 else x - 18
        g.append(f'<text x="{tx:.1f}" y="{y+4:.1f}" text-anchor="{"start" if side > 0 else "end"}" {SANS} font-size="13" fill="#fff">{name}</text>')
    x, y = X(62), Y(.11)
    g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{ERR}"/><text x="{x-14:.1f}" y="{y+26:.1f}" text-anchor="end" {SANS} font-size="13" font-weight="600" fill="{ERR}">LLM alone 0.11</text>')
    # legend (right column)
    L = 930
    leg = [("line", "full harness at 5 token budgets"), ("glyph", "one brick switched off (its glyph)"), ("err", "model answers directly"), ("txt", "up-left = higher score, fewer tokens")]
    for n, (k, t) in enumerate(leg):
        y = 130 + n * 40
        if k == "line":
            g.append(f'<line x1="{L}" x2="{L+22}" y1="{y-4}" y2="{y-4}" stroke="{AUR}" stroke-width="2.5"/>')
        elif k == "glyph":
            g.append(f'<rect x="{L}" y="{y-15}" width="22" height="22" rx="5" fill="{VOID}" stroke="{LILAC}"/>{glyph(GLYPHS["AUDIT"], L+3.5, y-11.5, 4.3, LILAC)}')
        elif k == "err":
            g.append(f'<circle cx="{L+11}" cy="{y-4}" r="7" fill="{ERR}"/>')
        g.append(f'<text x="{L+34 if k != "txt" else L}" y="{y}" {SANS} font-size="13" fill="#fff" opacity=".9">{t}</text>')
    return frame("f2", w, h, "".join(g), variant="band", tag=("FIGURE 2 · SCORE VS COST", GLYPHS["AUDIT"]), caption="demo values · FrontierKit-lite")


def m_fig3():
    w, h = 1200, 540
    iso = Iso(60, 290, 1.0)
    cats = [("callout mistyped", 7, 2, "LEDGER", "ledger"), ("wrong scale", 4, 1, "AUDIT", "audit"), ("inconsistent dim.", 6, 1, "AUDIT", "audit"),
            ("invalid solid", 3, 2, "PROVE", "prove"), ("missing deliverable", 3, 0, "WRITE", "write"), ("timeout", 2, 1, "DONE", "done guard")]
    U = 26
    inner = []
    step = 88
    for n, (name, before, after, gl, brick) in enumerate(cats):
        x, y = 60 + n * step, 20 - n * step
        inner.append(iso.tile(x - 8, y - 8, 68, 68, "#2a2774", stroke="#4b48a8", op=.9))
        if after:
            inner.append(iso.block(x, y, 52, 52, after * U, "err", right_text=str(after), right_size=18, sheen=True))
        inner.append(iso.block(x, y, 52, 52, before * U, ghost=True))
        tx, ty = iso.P(x + 26, y + 26, before * U)
        inner.append(f'<text x="{tx:.1f}" y="{ty-22:.1f}" text-anchor="middle" {MONO} font-size="12.5" fill="#fff">{before} → {after}</text>')
        bx, by = iso.P(x + 52, y + 52, 0)
        inner.append(f'<g transform="translate({bx-50:.1f},{by+24:.1f})">{glyph(GLYPHS[gl], 0, 0, 4.3, AUR)}<text x="20" y="11" {MONO} font-size="11" fill="{AUR}">{brick}</text><text x="0" y="32" {SANS} font-size="13" fill="#fff">{name}</text></g>')
    inner.append(f'<text x="56" y="480" {SANS} font-size="14" fill="#fff"><tspan font-weight="600">25 → 7 failures</tspan> on 29 dev tasks · dashed = LLM alone · red = left with the harness · glyph = the brick that removed them</text>')
    return frame("f3", w, h, "".join(inner), variant="band", tag=("FIGURE 3 · DEV-SET FAILURES", GLYPHS["PROVE"]), caption="demo counts · S2 measurement campaign")


def m_cube():
    w, h = 1200, 500
    iso = Iso(330, 150, 1.0)
    inner = [floor(iso, 6, 6, 50, .6)]
    s, gap = 46, 6
    lit = {(0, 2, 2), (1, 2, 1), (2, 2, 2), (2, 0, 2), (2, 1, 0), (0, 0, 2)}
    order = sorted([(i, j, k) for i in range(3) for j in range(3) for k in range(3)], key=lambda t: (t[0] + t[1], t[2]))
    for i, j, k in order:
        if i < 2 and j < 2 and k < 2:
            continue  # hidden
        kind = "valid" if (i, j, k) in lit else "glass"
        inner.append(iso.block(40 + i * (s + gap), 40 + j * (s + gap), s, s, s, kind, z=k * (s + gap), sheen=True,
                               top_glyph=KERNELS[(i * 3 + j) % 10][1] if k == 2 else None))
    a, b = iso.P(40 + 1.5 * (s + gap), 40 + 1.5 * (s + gap), 0)
    inner.append(f'<line x1="{a:.0f}" y1="0" x2="{a:.0f}" y2="{h}" stroke="{AUR}" stroke-width="2" opacity=".75"/><line x1="{a:.0f}" y1="0" x2="{a:.0f}" y2="{h}" stroke="{AUR}" stroke-width="16" opacity=".18" filter="url(#blur18)"/>')
    # kernel list with their glyph variants
    X = 700
    inner.append(f'<text x="{X}" y="96" {SANS} font-size="26" font-weight="600" letter-spacing="-.6" fill="#fff">Ten kernels, one pack</text>')
    inner.append(f'<text x="{X}" y="122" {SANS} font-size="14" fill="{LILAC}">Each kernel: one formula or small solver, tested, with a declared domain.</text>')
    for n, (name, bits, used) in enumerate(KERNELS):
        cx, cy = X + (n % 2) * 230, 160 + (n // 2) * 52
        col = AUR if used else LILAC
        inner.append(f'<rect x="{cx}" y="{cy}" width="30" height="30" rx="7" fill="{VOID}" stroke="{col}" stroke-opacity=".7"/>{glyph(bits, cx+5.5, cy+5.5, 5.5, col)}')
        inner.append(f'<text x="{cx+42}" y="{cy+20}" {MONO} font-size="13" fill="{"#fff" if used else LILAC}">{name}</text>')
    inner.append(f'<text x="{X}" y="452" {MONO} font-size="11.5" fill="{AUR}">lit = used on the dev tasks shown (demo)</text>')
    return frame("cb", w, h, "".join(inner), variant="full", tag=("SOLVE · KERNEL PACK", GLYPHS["SOLVE"]))


# chrome gradient for banner text needs its own id
def fix_chrome(svg, uid):
    return svg.replace("url(#chromeban)", f"url(#chrome{uid})")


BANNER = fix_chrome(m_banner(), "ban")
FIG1, FIG2, FIG3, CUBE = m_fig1(), m_fig2(), m_fig3(), m_cube()

# ================================================================= shared CSS
BASE_CSS = f"""
:root{{--void:{VOID};--indigo:{INDIGO};--violet:{VIOLET};--lilac:{LILAC};--aur:{AUR};--aur-ink:{AUR_INK};--mag:{MAG};
--err:{ERR};--err-ink:{ERR_INK};--paper:{PAPER};--ink:{INK};--grey:{GREY};--rule:#e2e0f0;
--sans:"Helvetica Neue",Helvetica,Arial,sans-serif;--serif:Charter,"Bitstream Charter",Georgia,serif;--mono:ui-monospace,"SF Mono",Menlo,"DejaVu Sans Mono",monospace}}
*{{box-sizing:border-box}}html,body{{margin:0}}
.demo{{font:11px/1 var(--mono);border:1px dashed currentColor;border-radius:4px;padding:5px 8px;opacity:.8}}
"""

# ================================================================= 00 identity sheet
def swatch(name, hexv, role, dark=True):
    fg = "#fff" if dark else INK
    return f'<div class="sw"><div class="chip" style="background:{hexv};color:{fg}">{hexv}</div><b>{name}</b><span>{role}</span></div>'


def glyph_card(name, bits, note):
    return f'<div class="gc"><div class="gd">{glyph_svg(bits, 54, "#fff")}</div><div class="gl">{glyph_svg(bits, 20, INK)}</div><b>{name}</b><span>{note}</span></div>'


def mini(svg_body, w, h, uid, variant="band"):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">{defs(uid)}<clipPath id="clip{uid}"><rect width="{w}" height="{h}" rx="14"/></clipPath><g clip-path="url(#clip{uid})">{aurora(uid, w, h, variant)}{svg_body}</g></svg>'


def iso_demo():
    iso = Iso(110, 160, .9)
    a = iso.block(0, 0, 50, 50, 110, "valid", right_text="0.31", right_size=20, left_text="FULL", top_glyph=GLYPHS["DONE"], glow=AUR)
    iso2 = Iso(270, 160, .9)
    b = iso2.block(0, 0, 50, 50, 60, "glass", right_text="0.22", right_size=18, left_text="ABLATION")
    iso3 = Iso(420, 160, .9)
    c = iso3.block(0, 0, 50, 50, 90, ghost=True) + iso3.block(0, 0, 50, 50, 30, "err", right_text="2", right_size=16)
    iso4 = Iso(580, 170, .9)
    d = iso4.tile(0, 0, 120, 34, "#fff", op=.95)
    px, py = iso4.P(8, 34, 0)
    d += f'<g transform="matrix({C},{S},0,1,{px:.1f},{py:.1f})"><text y="-12" {MONO} font-size="10.5" fill="{INK}">F-03 · 6 000 mm</text></g>'
    iso5 = Iso(800, 150, .9)
    e = "".join(iso5.block(i * 34, j * 34, 30, 30, 30, "valid" if (i, j, k) == (1, 1, 1) else "glass", z=k * 34, sheen=False)
                for k in range(2) for i in range(2) for j in range(2) if not (i == 0 and j == 0 and k == 0))
    labels = [(110, "barre de score"), (270, "barre d'ablation"), (420, "bloc fantôme / erreur"), (600, "tuile de fait"), (820, "cube de noyaux")]
    lab = "".join(f'<text x="{x}" y="305" text-anchor="middle" {MONO} font-size="12" fill="{LILAC}">{t}</text>' for x, t in labels)
    return mini(a + b + c + d + e + lab, 960, 330, "isod", "band")


def aurora_demo():
    full = mini("", 380, 220, "au1", "full")
    band = mini("", 380, 90, "au2", "band")
    thread = mini("", 380, 16, "au3", "thread")
    return f'<div class="au"><div>{full}<b>pleine</b><span>bannière, fond du cube</span></div><div>{band}<b>bande</b><span>fond des figures</span></div><div>{thread}<b>filet</b><span>séparateur, README, pied</span></div></div>'


def app_row():
    # each surface shown with the motifs it carries
    items = [("Bannière (image 0)", BANNER, "aurore pleine · barres iso · glyphe LEDGER · chiffres chrome"),
             ("Figure 1", FIG1, "aurore bande · blocs iso + glyphes · tuiles de faits"),
             ("Figure 2", FIG2, "aurore bande · glyphes comme marqueurs de données"),
             ("Figure 3", FIG3, "aurore bande · blocs fantômes / erreurs · glyphes"),
             ("Module noyaux", CUBE, "aurore pleine · cube iso · 10 variantes de glyphe")]
    cells = "".join(f'<figure class="ap"><div class="apv">{svg}</div><figcaption><b>{t}</b>{d}</figcaption></figure>' for t, svg, d in items)
    readme = f'''<figure class="ap"><div class="apv readme"><div class="rh">{mini(f'<g transform="translate(22,26)">{glyph(GLYPHS["LEDGER"],0,0,6,"#fff")}</g><text x="58" y="44" {SANS} font-size="22" font-weight="600" fill="#fff">ple-ledger-kernels</text>', 600, 76, "rm", "band")}</div>
      <div class="rb"><p><b>The model never reads the drawing.</b> An engineering agent harness…</p><code>uv run python eval/run.py</code><div class="rt">{mini("", 600, 10, "rm2", "thread")}</div><p class="rs">{glyph_svg(GLYPHS["EXTRACT"],14,INK)} EXTRACT {glyph_svg(GLYPHS["SPEC"],14,INK)} SPEC {glyph_svg(GLYPHS["SOLVE"],14,INK)} SOLVE {glyph_svg(GLYPHS["AUDIT"],14,INK)} AUDIT</p></div></div>
      <figcaption><b>README GitHub</b>bande en en-tête · filet · glyphes inline dans le texte</figcaption></figure>'''
    return cells + readme


IDENT = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=1440">
<title>V3-00 · Système visuel — PLE Ledger Kernels</title>
<style>{BASE_CSS}
body{{background:var(--paper);color:var(--ink);font:16px/1.55 var(--sans)}}
.wrap{{width:1440px;margin:0 auto;padding:0 64px 120px}}
header{{display:flex;justify-content:space-between;align-items:center;height:70px;border-bottom:1px solid var(--rule);font:13px var(--mono);color:var(--grey)}}
header b{{font:600 15px var(--sans);color:var(--ink);display:flex;gap:10px;align-items:center}}
h1{{font:600 54px/1.04 var(--sans);letter-spacing:-.035em;margin:64px 0 10px}}
.lede{{font:19px/1.55 var(--serif);color:#34324f;max-width:860px;margin:0}}
h2{{font:600 26px/1.2 var(--sans);letter-spacing:-.02em;margin:84px 0 6px;display:flex;align-items:center;gap:14px}}
h2 small{{font:500 12px var(--mono);letter-spacing:.12em;color:var(--grey);text-transform:uppercase}}
.why{{font:15px/1.55 var(--sans);color:var(--grey);margin:0 0 22px;max-width:900px}}
.pal{{display:grid;grid-template-columns:repeat(6,1fr);gap:16px}}
.sw .chip{{height:96px;border-radius:12px;display:flex;align-items:flex-end;padding:10px 12px;font:12px var(--mono)}}
.sw b{{display:block;margin-top:10px;font:600 14px var(--sans)}} .sw span{{font:13px/1.4 var(--sans);color:var(--grey)}}
.gly{{display:grid;grid-template-columns:repeat(8,1fr);gap:14px}}
.gc .gd{{background:var(--void);border-radius:12px;height:110px;display:grid;place-items:center}}
.gc .gl{{margin-top:10px}} .gc b{{display:block;font:600 13px var(--mono);margin-top:6px}} .gc span{{font:12.5px/1.35 var(--sans);color:var(--grey)}}
.kg{{display:flex;gap:18px;flex-wrap:wrap;margin-top:18px;font:12px var(--mono);color:var(--grey)}}
.kg div{{display:flex;gap:8px;align-items:center}}
.au{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;align-items:end}} .au b{{display:block;font:600 14px var(--sans);margin-top:10px}} .au span{{font:13px var(--sans);color:var(--grey)}}
.type{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px}}
.type > div{{background:#fff;border:1px solid var(--rule);border-radius:12px;padding:22px}}
.type .t1{{font:600 44px/1 var(--sans);letter-spacing:-.03em}} .type .t2{{font:19px/1.5 var(--serif)}} .type .t3{{font:600 30px var(--mono);color:var(--aur-ink)}}
.type small{{display:block;font:12px var(--mono);color:var(--grey);margin-top:12px}}
.chrome{{font:600 64px/1 var(--sans);letter-spacing:-.04em;background:linear-gradient(180deg,#fff 0,#d9d8ee 48%,#8f8cb8 52%,#e9e7ff 100%);-webkit-background-clip:text;background-clip:text;color:transparent}}
.chromebox{{background:var(--void);border-radius:12px;padding:22px}}
.marks{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} .marks > div{{background:var(--void);color:#fff;border-radius:12px;padding:22px;font:13px var(--mono);position:relative;min-height:120px}}
.pin{{display:inline-flex;gap:8px;align-items:center;background:#fff;color:var(--ink);border-radius:999px;padding:6px 12px 6px 8px;font:12px var(--mono);margin:4px 6px 0 0}}
.pin i{{width:8px;height:8px;border-radius:50%;background:var(--aur)}} .pin.e i{{background:var(--err)}} .pin.u{{background:transparent;color:var(--lilac);border:1px dashed var(--lilac)}} .pin.u i{{background:none;border:1px dashed var(--lilac)}}
.cross{{position:absolute;color:var(--lilac);opacity:.7;font:18px var(--mono)}}
.apps{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}}
.ap{{margin:0}} .ap figcaption{{font:13px/1.4 var(--sans);color:var(--grey);margin-top:10px}} .ap figcaption b{{display:block;color:var(--ink);font-size:14px}}
.readme{{background:#fff;border:1px solid var(--rule);border-radius:12px;overflow:hidden}} .readme .rb{{padding:14px 18px;font:13px/1.5 var(--sans)}} .readme code{{font:12px var(--mono);background:var(--paper);padding:2px 6px;border-radius:4px}}
.readme .rs{{display:flex;gap:6px;align-items:center;font:11px var(--mono);color:var(--grey)}}
.rules li{{margin-bottom:8px}}
</style></head><body><div class="wrap">
<header><b>{glyph_svg(GLYPHS["LEDGER"],22,INK)} ple-ledger-kernels · système visuel V3</b><span>Baseten → 3D · Psychoactive → couleurs, lumière, reflets, textures</span><span class="demo">chiffres de démo</span></header>
<h1>Un harness qui prouve ses chiffres.<br>Quatre motifs pour le montrer.</h1>
<p class="lede">Le livrable n'est pas un deck : c'est un Writeup Kaggle (texte mis en forme par Kaggle) et un repo GitHub. L'identité vit donc dans les <b>images</b> du Writeup et dans le README. Ces quatre motifs reviennent sur chacune, avec des variantes.</p>

<h2>{glyph_svg(GLYPHS["DONE"],22,INK)} Couleurs <small>Psychoactive · nuit violette, aurores, reflets</small></h2>
<p class="why">Le violet est la matière (fond, verre des blocs), pas un accent. Un seul accent porte du sens : le vert aurore = chiffre validé par le ledger. Le corail = erreur, jamais en décor. Le magenta n'apparaît que dans la lumière (reflets, fumée).</p>
<div class="pal">{swatch("Nuit", VOID, "fond des images")}{swatch("Violet", VIOLET, "matière : fumée, verre")}{swatch("Lilas", LILAC, "texte secondaire sur nuit", False)}{swatch("Aurore", AUR, "chiffre validé · seul accent", False)}{swatch("Corail", ERR, "erreur uniquement")}<div class="sw"><div class="chip" style="background:{PAPER};color:{INK};border:1px solid #d9d7ea">{PAPER}</div><b>Papier</b><span>README, impression</span></div></div>
<div class="kg"><div>sur fond clair : aurore → <b style="color:{AUR_INK}">{AUR_INK}</b></div><div>corail → <b style="color:{ERR_INK}">{ERR_INK}</b></div><div>magenta {MAG} : lumière seulement</div></div>

<h2>{glyph_svg(GLYPHS["SOLVE"],22,INK)} Motif A · le glyphe 3×3 <small>Baseten · icônes en pixels</small></h2>
<p class="why">Chaque brique de la chaîne a un glyphe de 9 cases. Il sert d'icône de section, de marqueur de données (Figure 2 : le point d'une ablation porte le glyphe de la brique retirée), d'étiquette sur le dessus des blocs et de logo. SPEC est un point seul : c'est le seul appel au LLM.</p>
<div class="gly">{"".join(glyph_card(n, b, t) for (n, b), t in zip(GLYPHS.items(), ["lire en lignes", "un seul appel LLM", "calcul", "contrôle croisé", "re-mesure en cadre", "document qui monte", "trame finale", "colonnes du registre"]))}</div>
<div class="kg">Variantes noyaux : {"".join(f'<div>{glyph_svg(b,18,AUR_INK if u else GREY)}{n}</div>' for n,b,u in KERNELS)}</div>

<h2>{glyph_svg(GLYPHS["WRITE"],22,INK)} Motif B · le bloc isométrique <small>Baseten · volumes, texte imprimé sur les faces</small></h2>
<p class="why">Un seul volume, projeté à 30°, décliné en cinq rôles. La valeur est imprimée sur la face droite, le nom sur la face gauche, le glyphe sur le dessus. Arête claire + bande de reflet sur la face avant (lumière Psychoactive).</p>
{iso_demo()}

<h2>{glyph_svg(GLYPHS["EXTRACT"],22,INK)} Motif C · l'aurore <small>Psychoactive · fumée, aurores, grain, trames</small></h2>
<p class="why">Fumée violette déplacée par du bruit, deux traînées de lumière (aurore + magenta), une bande de reflet en diagonale, du grain et des lignes de balayage. Tout est en filtres SVG : exportable en PNG, sans 3D lourde.</p>
{aurora_demo()}

<h2>{glyph_svg(GLYPHS["AUDIT"],22,INK)} Motif D · repères et provenance <small>Psychoactive · croix « + » · Kivo · pastilles</small></h2>
<p class="why">Chaque image est un cadre arrondi avec un halo de sa propre lumière, trois croix « + » sur les bords, l'étiquette glyphe + titre en haut à gauche. Les faits du ledger apparaissent en pastilles : plein = prouvé, pointillé = UNKNOWN.</p>
<div class="marks"><div><span class="cross" style="left:10px;top:48%">+</span><span class="cross" style="right:10px;top:48%">+</span><span class="pin"><i></i>F-03 · L = 6 000 mm · S-101 p.2</span><span class="pin"><i></i>K-1 · 54.0 kN·m</span><span class="pin e"><i></i>6000 read as m</span><span class="pin u"><i></i>K-2 · UNKNOWN</span></div>
<div class="chromebox"><div class="chrome">0.31</div><div style="font:12px var(--mono);color:var(--lilac);margin-top:8px">chiffre « chrome » : titres et chiffres-clés sur nuit uniquement</div></div></div>

<h2>{glyph_svg(GLYPHS["PROVE"],22,INK)} Typographie <small>polices système, zéro réseau</small></h2>
<div class="type"><div><div class="t1">Titre linéale</div><small>Helvetica / Arial · 600 · approche −3 %</small></div><div><div class="t2">Corps en serif pour les longues lectures du README.</div><small>Charter / Georgia · 19 px</small></div><div><div class="t3">54.0 kN·m</div><small>mono · valeurs, unités, ids de faits</small></div></div>

<h2>{glyph_svg(GLYPHS["LEDGER"],22,INK)} Sur chaque surface <small>les motifs et leurs variantes</small></h2>
<p class="why">Ce sont les vraies images du Writeup (démo), en miniature.</p>
<div class="apps">{app_row()}</div>

<h2>Règles</h2>
<ul class="rules"><li>Aurore pleine : une seule par surface (bannière ou module noyaux). Les figures prennent la bande.</li>
<li>Le vert aurore ne sert qu'aux chiffres validés ; une image sans chiffre validé n'en contient pas.</li>
<li>Lisibilité : une image de 1200 px affichée dans la colonne Kaggle (~760 px, largeur à vérifier) est réduite d'un tiers ; il faut donc ≥ 17 px de texte dans le fichier pour lire ≥ 11 px. <b>Les figures V3 n'y sont pas encore</b> (11–14 px) : à corriger à la déclinaison.</li>
<li>Les blocs iso portent des données (hauteur = valeur) ; jamais de bloc décoratif sans chiffre ni glyphe.</li></ul>
<p style="font:12px var(--mono);color:var(--grey);margin-top:60px">V3 · 2026-11-18 · généré par G-DESIGN/tools/build_v3.py</p>
</div></body></html>"""

# ================================================================= 01 writeup (as read on Kaggle)
WRITEUP = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1440">
<title>V3-01 · Writeup — PLE Ledger Kernels</title>
<style>{BASE_CSS}
body{{background:#eceaf5;color:var(--ink);font:16px/1.6 var(--sans)}}
.note{{width:1440px;margin:0 auto;padding:18px 64px;display:flex;justify-content:space-between;font:12.5px var(--mono);color:var(--grey)}}
.page{{width:1000px;margin:0 auto 120px;background:#fff;border-radius:6px;padding:48px 100px 80px;box-shadow:0 1px 3px rgba(15,14,38,.08)}}
.page h1{{font:700 34px/1.2 var(--sans);margin:0 0 6px}}
.page .meta{{font:13px var(--mono);color:var(--grey);margin-bottom:28px}}
.page h2{{font:700 23px/1.3 var(--sans);margin:44px 0 12px;display:flex;align-items:center;gap:10px}}
.page p{{margin:0 0 14px}}
.page code{{font:14px var(--mono);background:#f2f1f8;padding:1px 5px;border-radius:3px}}
.img{{margin:22px -60px}} .img + .cap{{font:13px/1.5 var(--sans);color:var(--grey);margin:-10px 0 18px}}
table{{border-collapse:collapse;width:100%;font:14px var(--mono);margin:8px 0 18px}}
th,td{{border:1px solid #e2e0f0;padding:7px 10px;text-align:left}} th{{background:#f6f5fc;font-family:var(--sans)}}
td.v{{color:var(--aur-ink);font-weight:600}} tr.e td{{color:var(--err-ink)}}
.finding{{border-left:4px solid var(--aur-ink);background:#f3fbf7;padding:12px 16px;margin:18px 0}}
@media print{{@page{{size:A4;margin:12mm}} body{{background:#fff}} .note{{display:none}} .page{{width:auto;padding:0;box-shadow:none}} .img{{margin:8mm 0;break-inside:avoid}}}}
</style></head><body>
<div class="note"><span>Simulation de lecture : le texte prendra le style de Kaggle (non maîtrisé). Seules les images portent l'identité.</span><span class="demo">chiffres de démo · eval/run.py</span></div>
<article class="page">
<h1>The model never reads the drawing</h1>
<div class="meta">github.com/GaiaSG94/ple-ledger-kernels · commit ········ (SHA 40 car. au commit final) · CC BY 4.0</div>
<div class="img">{BANNER}</div>
<div class="finding"><b>Main finding.</b> Taking reading and arithmetic away from the model raises the dev-set score from 0.11 to 0.31 while tokens per task fall from 62 k to 24 k. The cost moves from tokens to CPU.</div>
<h2>{glyph_svg(GLYPHS["EXTRACT"],20,INK)} 1. Why reading and arithmetic break agents</h2>
<p>On the dev set, the two heaviest failure families are not reasoning errors: they are <b>misread drawing callouts</b> and <b>unit errors</b>. A callout like <code>6000</code> means millimetres; read as metres, the moment is off by a factor of a million. Models are good at deciding <i>what</i> to compute and poor at small print and units, so the model only writes a typed spec and code does the rest.</p>
<h2>{glyph_svg(GLYPHS["SOLVE"],20,INK)} 2. Architecture</h2>
<div class="img">{FIG1}</div>
<p class="cap">Figure 1. One LLM call (SPEC). Every number in the deliverable points to the ledger.</p>
<h2>{glyph_svg(GLYPHS["LEDGER"],20,INK)} 3. One number, end to end</h2>
<table><tr><th>id</th><th>quantity</th><th>value</th><th>source</th><th>audit</th></tr>
<tr><td>F-03</td><td>span L</td><td class="v">6 000 mm</td><td>S-101 p.2</td><td>length ✓</td></tr>
<tr><td>F-07</td><td>load w</td><td class="v">12 kN/m</td><td>spec §2.3</td><td>force/length ✓</td></tr>
<tr><td>K-1</td><td>M = wL²/8</td><td class="v">54.0 kN·m</td><td>beam-simple</td><td>torque ✓ range ✓</td></tr>
<tr class="e"><td>—</td><td>LLM alone</td><td>54 000 000 kN·m</td><td>6000 read as m</td><td>range ✗</td></tr>
<tr><td>K-2</td><td>deflection δ</td><td>—</td><td>E·I missing</td><td>UNKNOWN</td></tr></table>
<div class="img">{CUBE}</div>
<h2>{glyph_svg(GLYPHS["AUDIT"],20,INK)} 4. Score vs cost</h2>
<div class="img">{FIG2}</div>
<p class="cap">Figure 2. Each ablation point carries the glyph of the brick switched off.</p>
<h2>{glyph_svg(GLYPHS["PROVE"],20,INK)} 5. Where it fails</h2>
<div class="img">{FIG3}</div>
<p class="cap">Figure 3. Failure families before / after; the glyph names the brick that removed them.</p>
<h2>{glyph_svg(GLYPHS["WRITE"],20,INK)} 6. Two models, same chain</h2>
<table><tr><th>model</th><th>LLM alone</th><th>harness</th><th>tokens / task</th></tr><tr><td>claude-opus-5-5</td><td>0.11</td><td class="v">0.31</td><td>24 k</td></tr><tr><td>gemma-4-26b (local)</td><td>0.06</td><td class="v">0.21</td><td>27 k</td></tr></table>
<h2>{glyph_svg(GLYPHS["DONE"],20,INK)} 7. Limits</h2>
<p>Twelve kernels at most; no paid code tables; raster drawings depend on OCR confidence; replicating public verify scripts was dropped as it reads as hard-coded output.</p>
</article></body></html>"""

(OUT / "00-identite.html").write_text(IDENT, encoding="utf-8")
(OUT / "01-writeup.html").write_text(WRITEUP, encoding="utf-8")
print("ok", [p.name for p in OUT.iterdir()])
