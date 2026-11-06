#!/usr/bin/env python3
"""README visuals for dsh-contract-suite, derived from what the suite really does.

Two figures, read off `package.json`, `cordis.patch.yml`,
`samples/quickstart/input/profile.json` and the one runtime module
`src/members.mjs` -- not from a generic install template.

  hero 1440x576 (Pillow, zh/en x light/dark, four WebP files)
      Left column: kicker / wordmark / two value lines / one subtitle / one meta
      line / footer.  Right side: two member stubs, each carrying the exact
      version pinned for it, clasped together by ONE VERSION SET, a
      reconciliation strip that holds `cordis.patch.yml`'s two insert rows
      against `package.json`'s two exact pins, and a 2/2 resolved seal over
      `0.1.0-alpha.10`.

  flow 1100x660 (hand-written SVG, light/dark)
      Grammar: a RECONCILIATION SHEET -- a contract comparison grid, not a row
      of arrowed boxes.  Each member is one row; the columns are the surfaces it
      must satisfy in order: ASSEMBLY (`cordis.patch.yml` insert rows), VERSIONS
      (`package.json#dependencies` exact pins), RESOLVED (`node_modules` or the
      manifest pin plus the profile row), VERDICT.  Stitch marks bind the same
      member across cells; a footer margin notes the failure code each surface
      raises, and the bottom line counts 2 rows = 2 pins = 2 resolved rows.

Every name, version and count is read from the checked-in manifests; every
label is measured before it is drawn, and an overflowing label aborts the run
instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import json
import os
import re
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-contract-suite"
SUITE_VERSION = "0.1.0-alpha.10"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42", band="#202839",
        grid="#262f42", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: int, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def shadow_card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
                radius: int = RADIUS, shadow: int = SHADOW,
                fill: str | None = None, edge: str | None = None,
                width: int = 2) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=s["shadow"] + (int(10 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=width)
    return base.convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: float, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(int(round(size)), kind))


def require_w(text: str, size: float, kind: str, max_w: float,
              what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum and measure(text, size, kind) > max_w:
        size -= 1
    if measure(text, size, kind) > max_w:
        raise SystemExit(f"FATAL: {text!r} cannot fit {max_w}px even at "
                         f"{minimum}px")
    return size


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    size = start
    while size > minimum and any(measure(l, size, kind) > max_w for l in lines):
        size -= 1
    if any(measure(l, size, kind) > max_w for l in lines):
        raise SystemExit(f"FATAL: value line cannot fit {max_w}px at "
                         f"{minimum}px")
    return size


def pill(img: Image.Image, x: int, top: int, label: str, s: dict,
         size: float = 16, kind: str = "cjk", height: int | None = None,
         pad: int = 15, fg: str | None = None, bg: str | None = None,
         edge: str | None = None) -> tuple[Image.Image, int]:
    f = font(int(round(size)), kind)
    h = height or int(size * 2.1)
    w = measure(label, size, kind) + pad * 2
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, top, x + w, top + h], radius=h / 2,
                        fill=hx(bg or s["pill"]),
                        outline=hx(edge) if edge else None,
                        width=2 if edge else 0)
    d.text((x + pad, top + h / 2 + 1), label, font=f,
           fill=hx(fg or s["accent"]), anchor="lm")
    return img, int(w)


# ---------------------------------------------------------------------------
# suite data: manifests are the source of truth.  The picture fails loudly if
# it would describe a suite that is not on disk.
# ---------------------------------------------------------------------------
ERROR_CODES = (
    "E_SUITE_MANIFEST_MISSING",
    "E_SUITE_PATCH_MISMATCH",
    "E_SUITE_VERSION_MISMATCH",
)


def load_suite() -> dict:
    with open(os.path.join(ROOT, "package.json"), encoding="utf-8") as fh:
        pkg = json.load(fh)
    patch_path = os.path.join(ROOT, "cordis.patch.yml")
    with open(patch_path, encoding="utf-8") as fh:
        patch_text = fh.read()
    with open(os.path.join(ROOT, "samples", "quickstart", "input",
                           "profile.json"), encoding="utf-8") as fh:
        profile = json.load(fh)
    with open(os.path.join(ROOT, "src", "members.mjs"), encoding="utf-8") as fh:
        members_src = fh.read()

    if pkg.get("name") != NAME:
        raise SystemExit("FATAL: package.json name changed")
    if pkg.get("version") != SUITE_VERSION:
        raise SystemExit(f"FATAL: package version is {pkg.get('version')}, "
                         f"script expects {SUITE_VERSION}")
    if pkg.get("dsh", {}).get("bundle", {}).get("patch") != "./cordis.patch.yml":
        raise SystemExit("FATAL: dsh.bundle.patch changed")

    rows = []
    current = None
    for line in patch_text.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^\s*-\s+id:\s*([^\s#]+)\s*$", line)
        if m:
            current = {"id": m.group(1), "name": None}
            rows.append(current)
            continue
        m = re.match(r"^\s+name:\s*([^\s#]+)\s*$", line)
        if m and current is not None:
            current["name"] = m.group(1)
    if len(rows) != 2:
        raise SystemExit(f"FATAL: cordis.patch.yml has {len(rows)} members, "
                         "expected 2")
    deps = pkg.get("dependencies", {})
    if len(deps) != 2:
        raise SystemExit(f"FATAL: package.json has {len(deps)} deps, expected 2")
    if {r["id"] for r in rows} != set(deps):
        raise SystemExit("FATAL: patch member set != dependency set")
    for row in rows:
        if row["name"] != row["id"]:
            raise SystemExit(f"FATAL: patch row {row['id']} lacks a matching "
                             "name")
    for code in ERROR_CODES:
        if code not in members_src:
            raise SystemExit(f"FATAL: {code} is not raised by src/members.mjs")

    sample_rows = {row["id"]: row for row in profile.get("rows", [])}
    members = []
    for row in rows:
        member = row["id"]
        version = deps[member]
        sample = sample_rows.get(member)
        if sample is None:
            raise SystemExit(f"FATAL: profile sample lacks {member}")
        if sample.get("version") != version:
            raise SystemExit(f"FATAL: profile sample pins {member} at "
                             f"{sample.get('version')}, manifest pins {version}")
        if sample.get("enabled") is not True:
            raise SystemExit(f"FATAL: profile sample does not enable {member}")
        members.append({"id": member, "version": version})
    return {"version": pkg["version"], "members": members}


HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 安装型套件",
        value=["一条命令装齐合同法务两件套", "两行成员、两个版本，逐行对账"],
        sub="只安装，不审合同：锁版本、插行、核对解析。",
        meta="2/2 resolved · 2 pins · 0 tools · network: false",
        foot="Apache-2.0 · 零工具面 · 不读合同 · 不调用模型",
        cmd_note="一条命令 · 2 个成员",
        strip_note="同名、同版本，缺一行都不算装全",
        seal_word="resolved",
        note="卸载只移除套件行，成员保持安装",
        member_label="MEMBER",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · install-only suite",
        value=["Two members, one install", "two rows, two exact pins"],
        sub="Install-only: pin, insert, verify both resolve.",
        meta="2/2 resolved · 2 pins · 0 tools · network: false",
        foot="Apache-2.0 · zero tool surface · no model calls",
        cmd_note="one command · 2 members",
        strip_note="same ids, same versions — no silent mixing",
        seal_word="resolved",
        note="uninstall removes the suite row; members stay",
        member_label="MEMBER",
    ),
}


# ---------------------------------------------------------------------------
# hero 1440x576
# ---------------------------------------------------------------------------
def draw_lock(d: ImageDraw.ImageDraw, cx: int, cy: int, s: dict,
              size: int = 1.0) -> None:
    """A small padlock glyph used on the clasp."""
    accent = hx(s["accent"])
    body_w = int(22 * size)
    body_h = int(16 * size)
    d.rounded_rectangle([cx - body_w // 2, cy - 2, cx + body_w // 2,
                         cy - 2 + body_h], radius=4, fill=accent)
    r = int(8 * size)
    d.arc([cx - r, cy - 14 * size, cx + r, cy + 6 * size], 180, 360,
          fill=accent, width=max(2, int(3 * size)))
    d.ellipse([cx - 2 * size, cy + 3 * size, cx + 2 * size, cy + 7 * size],
              fill=hx(s["pill"]))


def check_mark(d: ImageDraw.ImageDraw, cx: int, cy: int, scale: float,
               color: str, width: int) -> None:
    d.line([(cx - 9 * scale, cy - 1 * scale),
            (cx - 2 * scale, cy + 6 * scale),
            (cx + 11 * scale, cy - 9 * scale)],
           fill=hx(color), width=width, joint="curve")


def hero(lang: str, skin: str, suite: dict) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    members = suite["members"]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1140, 80, 430, s["accent"], s["glow"])
    img = glow(img, 170, 560, 320, s["accent"], max(8, s["glow"] // 3))
    d = ImageDraw.Draw(img)
    m = 56
    col_w = 556

    # ---- left column --------------------------------------------------------
    img, _ = pill(img, m, 66, h["kicker"], s, size=15.5)
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", col_w, 58, 50)
    if title_size < 48:
        raise SystemExit("FATAL: hero title below 48px")
    d.text((m - 1, 126), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))
    require_w(NAME, title_size, "mono_bold", col_w, "hero title")

    value_size = fit_lines(h["value"], "cjk_bold", col_w, 38, 31)
    for i, line in enumerate(h["value"]):
        d.text((m, 226 + i * 54), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")

    sub_size = fit(h["sub"], "cjk", col_w, 22, 18)
    require_w(h["sub"], sub_size, "cjk", col_w, "hero subtitle")
    d.text((m, 344), h["sub"], font=font(sub_size, "cjk"), fill=hx(s["sub"]))

    require_w(h["meta"], 18, "mono", col_w, "hero meta")
    d.text((m + 1, 398), h["meta"], font=font(18, "mono"), fill=hx(s["faint"]))

    d.line([m + 1, 452, m + col_w - 4, 452], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 470), h["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- right: install command --------------------------------------------
    cmd = "dsh plugin --profile <profile> add dsh-contract-suite"
    img, cmd_w = pill(img, 632, 64, cmd, s, size=13, kind="mono",
                      height=36, pad=16, fg=s["text"], bg=s["card"],
                      edge=s["edge"])
    d = ImageDraw.Draw(img)
    require_w(h["cmd_note"], 12.5, "cjk", 1384 - (632 + cmd_w + 16),
              "hero command note")
    d.text((632 + cmd_w + 16, 85), h["cmd_note"], font=font(12.5, "cjk"),
           fill=hx(s["faint"]))

    # ---- right: two member stubs -------------------------------------------
    stub_y, stub_h, stub_w, gap = 140, 228, 235, 66
    xs = [632, 632 + stub_w + gap]
    for i, (x, member) in enumerate(zip(xs, members)):
        d.rounded_rectangle([x, stub_y, x + stub_w, stub_y + stub_h],
                            radius=20, fill=hx(s["card"]),
                            outline=hx(s["edge"]), width=2)
        # contract-stub accent tab + perforation
        d.rounded_rectangle([x + 18, stub_y + 16, x + 62, stub_y + 20],
                            radius=2, fill=hx(s["accent"]))
        d.text((x + 18, stub_y + 28), f"{h['member_label']} {i + 1:02d}",
               font=font(10.5, "cjk_bold"), fill=hx(s["accent"]))
        # resolved dot at top-right
        d.ellipse([x + stub_w - 92, stub_y + 31, x + stub_w - 84,
                   stub_y + 39], fill=hx(s["ok"]))
        d.text((x + stub_w - 78, stub_y + 27), h["seal_word"],
               font=font(10.5, "mono"), fill=hx(s["ok"]))

        require_w(member["id"], 15.5, "mono_bold", stub_w - 36,
                  "hero member id")
        d.text((x + 18, stub_y + 58), member["id"],
               font=font(15.5, "mono_bold"), fill=hx(s["text"]))
        d.text((x + 18, stub_y + 92), "EXACT VERSION",
               font=font(10.5, "cjk_bold"), fill=hx(s["faint"]))
        require_w(member["version"], 22, "mono_bold", stub_w - 36,
                  "hero member version")
        d.text((x + 18, stub_y + 112), member["version"],
               font=font(22, "mono_bold"), fill=hx(s["text"]))

        for dash_x in range(x + 18, x + stub_w - 16, 12):
            d.line([dash_x, stub_y + 162, min(dash_x + 6, x + stub_w - 16),
                    stub_y + 162], fill=hx(s["grid"]), width=2)

        d.text((x + 18, stub_y + 176), "[manifest pin]",
               font=font(11, "mono"), fill=hx(s["sub"]))
        d.text((x + 18, stub_y + 198), "profile: enabled",
               font=font(11, "cjk"), fill=hx(s["ok"]))

    # ---- right: one-version-set clasp --------------------------------------
    cx0, cx1 = xs[0] + stub_w, xs[1]
    clasp_top, clasp_bot = 200, 316
    d.rounded_rectangle([cx0 + 8, clasp_top, cx1 - 8, clasp_bot],
                        radius=20, fill=hx(s["pill"]),
                        outline=hx(s["accent"]), width=2)
    ccx = (cx0 + cx1) // 2
    draw_lock(d, ccx, clasp_top + 38, s, 0.9)
    for j, word in enumerate(("ONE", "VERSION", "SET")):
        require_w(word, 9.5, "cjk_bold", cx1 - cx0 - 18, "hero clasp label")
        d.text((ccx, clasp_top + 74 + j * 14), word,
               font=font(9.5, "cjk_bold"), fill=hx(s["accent"]),
               anchor="mm")

    # ---- right: reconciliation strip ---------------------------------------
    ry0, ry1 = 386, 464
    d.rounded_rectangle([632, ry0, 1168, ry1], radius=16, fill=hx(s["card"]),
                        outline=hx(s["edge"]), width=2)
    d.text((648, ry0 + 16), "RECONCILIATION",
           font=font(10.5, "cjk_bold"), fill=hx(s["accent"]))
    d.line([648, ry0 + 24, 1152, ry0 + 24], fill=hx(s["grid"]), width=1)
    left = "cordis.patch.yml · 2 rows"
    right = "package.json · 2 pins"
    require_w(left, 11.5, "mono", 300, "hero strip left")
    require_w(right, 11.5, "mono", 300, "hero strip right")
    d.text((648, ry0 + 38), left, font=font(11.5, "mono"), fill=hx(s["text"]))
    d.text((1152, ry0 + 38), right, font=font(11.5, "mono"),
           fill=hx(s["text"]), anchor="ra")
    # a drawn identity mark ("≡") reads cleaner than a glyph at this size
    d.ellipse([886, ry0 + 26, 914, ry0 + 54], fill=hx(s["pill"]),
              outline=hx(s["accent"]), width=2)
    for j in range(3):
        d.line([892, ry0 + 34 + j * 5, 908, ry0 + 34 + j * 5],
               fill=hx(s["accent"]), width=2)
    require_w(h["strip_note"], 11, "cjk", 504, "hero strip note")
    d.text((648, ry0 + 60), h["strip_note"], font=font(11, "cjk"),
           fill=hx(s["sub"]))

    reads = ("reads: profile.json (synthetic) · package.json · "
             "cordis.patch.yml")
    require_w(reads, 11, "mono", 536, "hero reads")
    d.text((632, 484), reads, font=font(11, "mono"), fill=hx(s["sub"]))
    require_w(h["note"], 11.5, "cjk", 536, "hero uninstall note")
    d.text((632, 506), h["note"], font=font(11.5, "cjk"), fill=hx(s["sub"]))

    # ---- right: 2/2 resolved seal -----------------------------------------
    scx, scy, sr = 1294, 252, 68
    for a in range(0, 360, 12):
        if (a // 12) % 2:
            d.arc([scx - sr - 10, scy - sr - 10, scx + sr + 10,
                   scy + sr + 10], a, a + 7, fill=hx(s["ok"]), width=3)
    d.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=hx(s["card"]),
              outline=hx(s["grid"]), width=2)
    check_mark(d, scx, scy - 28, 1.25, s["ok"], 6)
    d.text((scx, scy + 12), "2/2", font=font(30, "mono_bold"),
           fill=hx(s["ok"]), anchor="mm")
    d.text((scx, scy + 44), h["seal_word"], font=font(12, "cjk_bold"),
           fill=hx(s["ok"]), anchor="mm")
    d.text((scx, 338), "suite", font=font(10, "cjk_bold"),
           fill=hx(s["faint"]), anchor="mm")
    d.text((scx, 356), suite["version"], font=font(11, "mono"),
           fill=hx(s["sub"]), anchor="mm")

    path = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.relpath(path, ROOT)}  {W}x{H}")


# ---------------------------------------------------------------------------
# flow SVG (light + dark): the reconciliation sheet
# ---------------------------------------------------------------------------
FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = "Consolas,'Microsoft YaHei',ui-monospace,monospace"

COLUMNS = [
    dict(x=100, w=232, num="1", label="ASSEMBLY",
         file="cordis.patch.yml", sub="2 insert rows · id = name",
         fail="rows != deps", code="E_SUITE_PATCH_MISMATCH"),
    dict(x=366, w=246, num="2", label="VERSIONS",
         file="package.json#dependencies", sub="2 exact pins · no drift",
         fail="pin drift", code="E_SUITE_VERSION_MISMATCH"),
    dict(x=646, w=240, num="3", label="RESOLVED",
         file="node_modules/ · profile.json", sub="manifest pin · enabled row",
         fail="manifest / sample missing", code="E_SUITE_MANIFEST_MISSING"),
    dict(x=920, w=112, num="4", label="VERDICT",
         file="2 / 2", sub="both rows", fail="all agree", code="exit 0"),
]


def flow_svg(skin: str, suite: dict) -> str:
    s = SKIN[skin]
    W, H = 1100, 660
    members = suite["members"]
    p: list[str] = []

    def add(line: str) -> None:
        p.append(line)

    def text(x: float, y: float, body: str, size: float, fill: str,
             kind: str = "sans", weight: str | None = None,
             anchor: str | None = None, ls: float | None = None) -> None:
        family = FONT_CSS_MONO if kind == "mono" else FONT_CSS_SANS
        attrs = [f'x="{x:g}"', f'y="{y:g}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size:g}"']
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor:
            attrs.append(f'text-anchor="{anchor}"')
        if ls:
            attrs.append(f'letter-spacing="{ls:g}"')
        add(f'<text {" ".join(attrs)}>{escape(body)}</text>')

    def rect(x0: float, y0: float, x1: float, y1: float, fill: str,
             rx: float = 12, stroke: str | None = None,
             width: float = 1.5, opacity: float | None = None,
             shadow: bool = False) -> None:
        attrs = [f'x="{x0:g}"', f'y="{y0:g}"', f'width="{x1 - x0:g}"',
                 f'height="{y1 - y0:g}"', f'rx="{rx:g}"', f'fill="{fill}"']
        if stroke:
            attrs.append(f'stroke="{stroke}" stroke-width="{width:g}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity:g}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        add(f'<rect {" ".join(attrs)}/>')

    def line(x0: float, y0: float, x1: float, y1: float, color: str,
             width: float = 1, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x1="{x0:g}"', f'y1="{y0:g}"', f'x2="{x1:g}"',
                 f'y2="{y1:g}"', f'stroke="{color}"', f'stroke-width="{width:g}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity:g}"')
        add(f'<line {" ".join(attrs)}/>')

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    add('<title id="title">dsh-contract-suite reconciliation sheet</title>')
    add('<desc id="desc">A contract comparison sheet, not an arrow pipeline. '
        'Each of the two members is one row. The columns are the surfaces the '
        'suite reconciles, numbered in check order: (1) ASSEMBLY, the two '
        'insert rows of cordis.patch.yml where id must equal name; '
        '(2) VERSIONS, the two exact pins in package.json dependencies; '
        '(3) RESOLVED, the node_modules source or the manifest pin plus the '
        'profile row enabled in the synthetic profile.json; (4) VERDICT. '
        'Stitch marks bind the same member across the cells, so no row can '
        'pass on one surface only. The margin band under the rows names the '
        'failure code each surface raises: rows differ from dependencies -> '
        'E_SUITE_PATCH_MISMATCH, an installed version drifts from the pin -> '
        'E_SUITE_VERSION_MISMATCH, a manifest or sample is missing or not '
        'valid JSON -> E_SUITE_MANIFEST_MISSING. The summary counts 2 rows = '
        '2 pins = 2 resolved rows, with network false, zero writes and zero '
        'tools. Every name, version and count is read from package.json, '
        'cordis.patch.yml and the checked-in quickstart sample.</desc>')
    add('<defs>')
    add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.2" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    shadow_hex = "#2b2440" if skin == "light" else "#000000"
    add('<filter id="soft" x="-30%" y="-30%" width="160%" height="180%">'
        '<feDropShadow dx="0" dy="8" stdDeviation="10" '
        f'flood-color="{shadow_hex}" flood-opacity="0.13"/>'
        '</filter>')
    add(f'<pattern id="dots" width="24" height="24" '
        f'patternUnits="userSpaceOnUse"><circle cx="1.2" cy="1.2" r="1.2" '
        f'fill="{s["grid"]}"/></pattern>')
    add(f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    add('</defs>')
    add(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    add(f'<rect width="{W}" height="{H}" fill="url(#dots)" opacity="0.55"/>')

    # ---- header -------------------------------------------------------------
    text(44, 58, NAME, 30, s["text"], "mono", "700")
    subtitle = ("Two members, three surfaces, one fixed version set; "
                "the suite counts as installed only at 2/2.")
    require_w(subtitle, 14.5, "cjk", 754, "flow subtitle")
    text(44, 88, subtitle, 14.5, s["sub"])
    top = "manifest v1 · install-only"
    tw = measure(top, 11.5, "mono") + 24
    rect(1056 - tw, 30, 1056, 58, s["pill"], rx=14)
    text(1056 - tw + 12, 48, top, 11.5, s["accent"], "mono")
    ins = "IN · package.json + cordis.patch.yml + profile.json (synthetic)"
    outs = "OUT · 2/2 resolved · 0 tools · network false"
    require_w(ins, 11, "mono", 560, "flow IN")
    require_w(outs, 11, "mono", 340, "flow OUT")
    text(44, 116, ins, 11, s["faint"], "mono")
    text(1056, 116, outs, 11, s["faint"], "mono", anchor="end")
    line(44, 128, 1056, 128, s["grid"], 1, opacity=0.75)

    # ---- install band -------------------------------------------------------
    rect(44, 138, 1056, 180, s["band"], rx=14)
    text(58, 164, "INSTALL", 11, s["accent"], "sans", "700", ls=1.2)
    command = "dsh plugin --profile <profile> add dsh-contract-suite"
    require_w(command, 12.5, "mono", 430, "flow install command")
    text(132, 164, command, 12.5, s["text"], "mono")
    add(f'<path d="M520 159h24" stroke="{s["accent"]}" stroke-width="1.5" '
        'marker-end="url(#arr)"/>')
    channels = "bundle patch → 2 insert rows · npm / git / tarball / 1024"
    require_w(channels, 11.5, "cjk", 420, "flow channels")
    text(560, 164, channels, 11.5, s["sub"])

    # ---- sheet --------------------------------------------------------------
    rect(44, 190, 1056, 600, s["card"], rx=22, stroke=s["edge"], shadow=True)
    # bound-ledger spine: accent rule + binding holes
    line(56, 216, 56, 574, s["accent"], 4, opacity=0.5)
    for hy in (248, 304, 360, 416, 472, 528):
        add(f'<circle cx="70" cy="{hy}" r="4" fill="none" '
            f'stroke="{s["edge"]}" stroke-width="1.5"/>')
        add(f'<circle cx="70" cy="{hy}" r="1.6" fill="{s["edge"]}"/>')
    text(100, 222, "RECONCILIATION SHEET", 11.5, s["accent"], "sans", "700",
         ls=1.3)
    text(1032, 222, f"{NAME} {suite['version']}", 11, s["faint"], "mono",
         anchor="end")
    line(100, 236, 1032, 236, s["grid"], 1)

    # ---- column headers -----------------------------------------------------
    for col in COLUMNS:
        x = col["x"]
        cx = x + 9
        add(f'<circle cx="{cx:g}" cy="258" r="8" fill="{s["accent"]}"/>')
        text(cx, 261.5, col["num"], 11, s["card"], "mono", "700",
             anchor="middle")
        require_w(col["label"], 13, "cjk_bold", col["w"] - 24,
                  f"flow header {col['label']}")
        text(x + 24, 263, col["label"], 13, s["text"], "sans", "700")
        require_w(col["file"], 11, "mono", col["w"], f"flow file {col['label']}")
        text(x, 282, col["file"], 11, s["sub"], "mono")
        require_w(col["sub"], 11, "cjk", col["w"], f"flow sub {col['label']}")
        text(x, 300, col["sub"], 11, s["faint"])

    # ---- rows ---------------------------------------------------------------
    for i, member in enumerate(members):
        base = 314 + i * 102
        # row label band
        rect(100, base, 124, base + 22, s["pill"], rx=8)
        text(112, base + 15, f"{i + 1:02d}", 11, s["accent"], "mono", "700",
             anchor="middle")
        text(134, base + 15, "MEMBER", 11, s["faint"], "sans", "700", ls=1.2)
        require_w(member["id"], 14, "mono_bold", 420, "flow member id")
        text(210, base + 16, member["id"], 14, s["text"], "mono", "700")
        text(1032, base + 15, "declared", 11, s["faint"], "sans", "700",
             anchor="end", ls=1.2)
        line(100, base + 26, 1032, base + 26, s["grid"], 1)

        cy0 = base + 32
        rect(96, cy0, 1036, cy0 + 62, s["band"], rx=12)
        # stitch marks in the gaps: the same member bound across surfaces
        for gx in (349, 629, 903):
            line(gx - 3, cy0 + 18, gx - 3, cy0 + 44, s["accent"], 1.2,
                 opacity=0.5)
            line(gx + 3, cy0 + 18, gx + 3, cy0 + 44, s["accent"], 1.2,
                 opacity=0.5)

        # ASSEMBLY
        text(108, cy0 + 24, f"- id: {member['id']}", 12, s["text"], "mono")
        text(118, cy0 + 48, f"name: {member['id']}", 12, s["text"], "mono")
        # VERSIONS
        text(374, cy0 + 24, f'"{member["id"]}"', 11, s["sub"], "mono")
        text(374, cy0 + 49, member["version"], 16.5, s["text"], "mono", "700")
        vw = measure(member["version"], 16.5, "mono_bold")
        rect(374 + vw + 10, cy0 + 35, 374 + vw + 52, cy0 + 53, s["pill"],
             rx=9)
        text(374 + vw + 31, cy0 + 47.5, "pin", 11, s["accent"], "mono", "700",
             anchor="middle")
        # RESOLVED
        text(654, cy0 + 24, "[manifest pin]", 11, s["sub"], "mono")
        text(654, cy0 + 48, "profile: enabled", 11, s["ok"])
        # VERDICT
        add(f'<circle cx="938" cy="{cy0 + 27:g}" r="10" fill="{s["ok_bg"]}" '
            f'stroke="{s["ok"]}" stroke-width="1.5"/>')
        add(f'<path d="M933 {cy0 + 27:g}l4 4 8-9" fill="none" '
            f'stroke="{s["ok"]}" stroke-width="2.2" stroke-linecap="round" '
            'stroke-linejoin="round"/>')
        text(956, cy0 + 31, "resolved", 11.5, s["ok"], "sans", "700")

    # ---- margin band: the failure code of each surface ----------------------
    line(100, 512, 1032, 512, s["grid"], 1)
    for col in COLUMNS:
        x = col["x"]
        require_w(col["fail"], 11, "cjk", col["w"], f"flow fail {col['label']}")
        fail_color = s["ok"] if col["code"] == "exit 0" else s["sub"]
        text(x, 528, col["fail"], 11, fail_color)
        code_color = s["ok"] if col["code"] == "exit 0" else s["mark"]
        require_w(col["code"], 11, "mono", col["w"],
                  f"flow code {col['code']}")
        text(x, 546, col["code"], 11, code_color, "mono", "700")

    # ---- summary ------------------------------------------------------------
    rect(96, 558, 1036, 592, s["pill"], rx=12, stroke=s["accent"], width=1.5)
    summary = "2 rows = 2 pins = 2 resolved rows"
    require_w(summary, 12, "mono_bold", 430, "flow summary")
    text(110, 580, summary, 12, s["text"], "mono", "700")
    facts = "network: false · writes 0 · 0 tools"
    require_w(facts, 11, "mono", 270, "flow facts")
    text(560, 580, facts, 11, s["faint"], "mono")
    rect(884, 564, 1024, 586, s["ok_bg"], rx=11)
    text(954, 579, "2/2 resolved", 12, s["ok"], "mono", "700",
         anchor="middle")

    # ---- footer -------------------------------------------------------------
    reads = ("READS · package.json + cordis.patch.yml + "
             "profile.json (synthetic)")
    require_w(reads, 11, "mono", 520, "flow reads")
    text(44, 626, reads, 11, s["faint"], "mono")
    run = "RUN · node samples/quickstart/run.mjs --json"
    require_w(run, 11, "mono", 320, "flow run")
    text(1056, 626, run, 11, s["faint"], "mono", anchor="end")

    add('</svg>')
    return "\n".join(p) + "\n"


def main() -> None:
    suite = load_suite()
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin, suite)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin, suite))
        print(f"wrote {os.path.relpath(path, ROOT)}  1100x660")


if __name__ == "__main__":
    main()
