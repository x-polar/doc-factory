#!/usr/bin/env python3
"""storyboard(.md) + 브랜드 테마 -> HTML -> PDF (headless Chromium).

디자인은 CSS가 담당한다(브랜드별 `slides.css`). 파이썬은 '내용을 의미 있는 HTML로
바꾸는 일'만 한다. 좌표 계산 없음.

사용법:
  python src/lib/render.py <문서폴더> [--brand NAME] [--html-only]
예:
  python src/lib/render.py docs/20260630_kori_answers_intro
"""
import argparse
import csv
import glob
import html as H
import os
import re
import subprocess

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
]


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isabs(c) and os.path.exists(c):
            return c
        from shutil import which
        if which(c):
            return which(c)
    # 설치된 playwright 브라우저 자동 탐색
    for base in ("/opt/pw-browsers",):
        for p in glob.glob(base + "/chromium*/chrome-linux/chrome"):
            return p
    raise SystemExit("오류: Chromium을 찾을 수 없습니다. (env PLAYWRIGHT_BROWSERS_PATH 확인)")


# ----- 입력 파싱 ---------------------------------------------------------------

def deep_merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def load_doc_meta(doc_dir):
    """문서 메타(title/brand/version/theme)를 brief.md frontmatter에서 읽는다."""
    p = os.path.join(doc_dir, "brief.md")
    if not os.path.exists(p):
        return {}
    return _frontmatter(open(p, encoding="utf-8").read())[0]


def resolve_brand_dir(brand):
    d = os.path.join(ROOT, "brands", brand or "_default")
    return d if os.path.isdir(d) else os.path.join(ROOT, "brands", "_default")


def resolve_theme(doc_dir, brand_override=None):
    meta = load_doc_meta(doc_dir)
    brand = brand_override or meta.get("brand") or "_default"
    bdir = resolve_brand_dir(brand)
    theme = yaml.safe_load(open(os.path.join(bdir, "theme.yaml"), encoding="utf-8"))
    return deep_merge(theme, meta.get("theme")), bdir, meta


def load_slides(storyboard_dir):
    slides = []
    for path in sorted(glob.glob(os.path.join(storyboard_dir, "*.md"))):
        meta, rest = _frontmatter(open(path, encoding="utf-8").read())
        parts = re.split(r"^##\s*notes\s*$", rest, maxsplit=1, flags=re.M)
        lines = parts[0].splitlines()
        body = [l.strip()[1:].strip() for l in lines if l.strip().startswith("- ")]
        free = [l.strip() for l in lines if l.strip() and not l.strip().startswith("- ")]
        notes = parts[1].strip() if len(parts) > 1 else ""
        # 마크다운 본문이 비어 있으면 frontmatter의 body/free 를 그대로 쓴다
        # (구조화 레이아웃은 body를 frontmatter에 적는 경우가 많다)
        slides.append({**meta,
                       "body": body or meta.get("body") or [],
                       "free": free or meta.get("free") or [],
                       "notes": notes, "_file": os.path.basename(path)})
    return slides


def read_csv_chart(path):
    rows = [r for r in csv.reader(open(path, encoding="utf-8")) if r]
    header = rows[0]
    cats = [r[0] for r in rows[1:]]
    series = [(header[i], [float(r[i]) for r in rows[1:]])
              for i in range(1, len(header))]
    return cats, series


# ----- 자산 경로 해석 -----------------------------------------------------------

class Ctx:
    """문서/브랜드 폴더 기준으로 자산 경로를 file:// 절대경로로 해석."""

    def __init__(self, doc_dir, brand_dir):
        self.doc_dir = os.path.abspath(doc_dir)
        self.brand_dir = os.path.abspath(brand_dir)

    def asset(self, ref, kind="backgrounds"):
        if not ref:
            return None
        kinds = [kind] + [k for k in ("screens", "backgrounds", "logos", "images")
                          if k != kind]
        shared = os.path.join(ROOT, "brands", "_default")
        cands = [os.path.join(self.doc_dir, ref), os.path.join(self.brand_dir, ref)]
        for base in (self.brand_dir, shared):      # 브랜드 우선, 없으면 공용
            cands += [os.path.join(base, "assets", k, ref) for k in kinds]
        for ext in ("", ".svg", ".png", ".jpg", ".webp"):   # 벡터 우선
            for c in cands:
                p = c + ext
                if os.path.exists(p):
                    return "file://" + os.path.abspath(p)
        return None


# ----- HTML 생성 ---------------------------------------------------------------

def e(s):
    return H.escape(str(s if s is not None else ""))


WEIGHTS = {"thin":100,"extralight":200,"ultralight":200,"light":300,"regular":400,
           "normal":400,"medium":500,"semibold":600,"demibold":600,"bold":700,
           "extrabold":800,"black":900}
FMT = {"ttf":"truetype","otf":"opentype","woff2":"woff2","woff":"woff"}


def font_faces(brand_dir):
    """폰트를 @font-face로 임베드해 시스템 설치 의존을 없앤다.
    공용(brands/_default/assets/fonts) → 브랜드 전용 순으로 적층(뒤가 우선)."""
    dirs = [os.path.join(ROOT, "brands", "_default", "assets", "fonts"),
            os.path.join(brand_dir, "assets", "fonts")]
    out = []
    for fd in dirs:
        if not os.path.isdir(fd):
            continue
        out += _faces_in(fd)
    return "\n".join(out)


def _faces_in(fd):
    out = []
    for fam in sorted(os.listdir(fd)):
        famdir = os.path.join(fd, fam)
        if not os.path.isdir(famdir):
            continue
        files = []
        for ext in FMT:
            files += glob.glob(os.path.join(famdir, "*." + ext))
        for f in sorted(files):
            base = os.path.splitext(os.path.basename(f))[0]
            suf = base.split("-")[-1].lower() if "-" in base else "regular"
            italic = "italic" in suf
            w = WEIGHTS.get(suf.replace("italic", "") or "regular", 400)
            ext = f.rsplit(".", 1)[1].lower()
            out.append(
                f'@font-face{{font-family:"{fam}";'
                f'src:url("file://{os.path.abspath(f)}") format("{FMT[ext]}");'
                f'font-weight:{w};font-style:{"italic" if italic else "normal"};'
                f'font-display:block;}}')
    return out


def css_vars(theme):
    c = theme.get("colors", {})
    f = theme.get("fonts", {})
    s = theme.get("sizes", {})
    sl = theme.get("slide", {})
    out = []
    for k, v in c.items():
        if isinstance(v, str):
            out.append(f"--c-{k.replace('_','-')}:#{v}")
    series = c.get("series") or []
    for i, v in enumerate(series):
        out.append(f"--c-series-{i+1}:#{v}")
    stack = ", ".join(filter(None, [
        f'"{f.get("heading")}"' if f.get("heading") else None,
        f'"{f.get("body")}"' if f.get("body") else None,
        f'"{f.get("fallback")}"' if f.get("fallback") else None,
        '"Noto Sans CJK KR"', '"Noto Sans KR"', "sans-serif"]))
    body_stack = ", ".join(filter(None, [
        f'"{f.get("body")}"' if f.get("body") else None,
        f'"{f.get("fallback")}"' if f.get("fallback") else None,
        '"Noto Sans CJK KR"', '"Noto Sans KR"', "sans-serif"]))
    out.append(f"--font-heading:{stack}")
    out.append(f"--font-body:{body_stack}")
    for k, v in s.items():
        out.append(f"--size-{k}:{v}pt")
    out.append(f"--slide-w:{sl.get('width', 13.333)}in")
    out.append(f"--slide-h:{sl.get('height', 7.5)}in")
    out.append(f"--pad:{sl.get('margin', 0.7)}in")
    return ";\n    ".join(out)


def bullets(items, cls="bullets"):
    if not items:
        return ""
    li = "".join(f"<li>{e(x)}</li>" for x in items)
    return f'<ul class="{cls}">{li}</ul>'


def slide_head(sp):
    """kicker / title / lede 헤더 블록."""
    h = []
    if sp.get("kicker"):
        h.append(f'<p class="kicker">{e(sp["kicker"])}</p>')
    if sp.get("title"):
        h.append(f'<h2 class="title">{e(sp["title"])}</h2>')
    if sp.get("lede"):
        h.append(f'<p class="lede">{e(sp["lede"])}</p>')
    return f'<header class="head">{"".join(h)}</header>' if h else ""


def chart_html(path, theme):
    cats, series = read_csv_chart(path)
    vals = [v for _, s in series for v in s]
    mx = max(vals) if vals else 1
    groups = []
    for i, cat in enumerate(cats):
        bars = "".join(
            f'<div class="bar" style="height:{(s[i]/mx*100):.1f}%;'
            f'--i:{k}" data-v="{s[i]:g}"></div>'
            for k, (_, s) in enumerate(series))
        groups.append(f'<div class="grp"><div class="bars">{bars}</div>'
                      f'<div class="cat">{e(cat)}</div></div>')
    legend = ""
    if len(series) > 1:
        legend = '<div class="legend">' + "".join(
            f'<span style="--i:{k}">{e(n)}</span>' for k, (n, _) in enumerate(series)
        ) + "</div>"
    return f'<div class="chart">{legend}<div class="plot">{"".join(groups)}</div></div>'


def numbered_html(items):
    """01/02/03 번호 리스트. items: [str] 또는 [{num,heading,text}]"""
    out = []
    for i, it in enumerate(items or [], 1):
        if isinstance(it, dict):
            num = it.get("num") or f"{i:02d}"
            head = it.get("heading", "")
            text = it.get("text", "")
        else:
            num, head, text = f"{i:02d}", str(it), ""
        out.append(f'<li><span class="n">{e(num)}</span>'
                   f'<div class="t"><b>{e(head)}</b>'
                   + (f'<span>{e(text)}</span>' if text else "") + "</div></li>")
    return f'<ol class="numbered">{"".join(out)}</ol>' if out else ""


def strips_html(paths):
    cells = "".join(f'<div class="strip"><img src="{p}"></div>' for p in paths if p)
    return f'<div class="strips">{cells}</div>' if cells else ""


def inline_icons(frag, ctx):
    """fragment 내 {{icon:<set>/<name>}} 을 아이콘 SVG 내용으로 치환.
    탐색: 브랜드 assets/icons/ → _default assets/icons/ (브랜드 오버라이드 가능).
    SVG는 currentColor를 쓰므로 부모의 CSS color를 상속한다."""
    def _sub(m):
        rel = m.group(1).strip()
        for base in (ctx.brand_dir, os.path.join(ROOT, "brands", "_default")):
            p = os.path.join(base, "assets", "icons", rel + ".svg")
            if os.path.exists(p):
                s = open(p, encoding="utf-8").read()
                return re.sub(r"<\?xml[^>]*\?>|<!--.*?-->", "", s, flags=re.S).strip()
        return f'<span class="dg-missing">icon? {H.escape(rel)}</span>'
    return re.sub(r"\{\{icon:([^}]+)\}\}", _sub, frag)


def render_slide(sp, theme, ctx, page=None, total=None):
    layout = (sp.get("layout") or "title+body").replace("+", "-")
    # 배경: 슬라이드가 지정하면 그것, 없으면 브랜드 기본값(레이아웃별)
    bgs = theme.get("backgrounds", {}) or {}
    kind = {"title": "cover", "section": "section"}.get(layout, "content")
    ref = sp.get("bg", bgs.get(kind))
    if ref in (False, "none"):
        ref = None
    bg = ctx.asset(ref)
    bg_div = f'<div class="bg" style="background-image:url(\'{bg}\')"></div>' if bg else ""
    veil = '<div class="veil"></div>' if bg else ""
    logo = ctx.asset(theme.get("logo", {}).get("footer"), kind="logos")
    cover_logo = ctx.asset(theme.get("logo", {}).get("cover"), kind="logos")

    inner = ""
    if layout == "title":
        sub = "<br>".join(e(x) for x in sp.get("free", []))
        # 제목이 없으면 로고 자체가 표제 역할(회사명 중복 방지)
        hero = not sp.get("title")
        inner = (
            ("" if hero or not cover_logo else f'<img class="logo" src="{cover_logo}">') +
            '<div class="cover-mid">' +
            (f'<img class="logo-hero" src="{cover_logo}">' if hero and cover_logo else "") +
            (f'<h1 class="cover-title">{e(sp["title"])}</h1>' if sp.get("title") else "") +
            '<div class="rule"></div>' +
            (f'<p class="cover-sub">{sub}</p>' if sub else "") +
            "</div>" +
            (f'<p class="date">{e(sp["date"])}</p>' if sp.get("date") else "")
        )
    elif layout == "section":
        n = sp.get("num")
        inner = ('<div class="sec-mid">' +
                 (f'<span class="sec-num">{e(n)}</span>' if n else "") +
                 f'<h2 class="sec-title">{e(sp.get("title",""))}</h2>' +
                 (f'<p class="lede">{e(sp["lede"])}</p>' if sp.get("lede") else "") +
                 "</div>")
    elif layout == "columns":
        cards = ""
        for c in sp.get("columns", []) or []:
            cards += ('<div class="card">' +
                      (f'<span class="card-num">{e(c["num"])}</span>' if c.get("num") else "") +
                      f'<h3>{e(c.get("heading",""))}</h3>' +
                      bullets(c.get("items")) + "</div>")
        n = len(sp.get("columns", []) or [])
        inner = slide_head(sp) + f'<div class="cards cols-{n}">{cards}</div>'
    elif layout == "stat":
        cells = ""
        for s in sp.get("stats", []) or []:
            cells += ('<div class="stat">' +
                      f'<div class="stat-v">{e(s.get("value",""))}</div>' +
                      f'<div class="stat-l">{e(s.get("label",""))}</div>' +
                      (f'<div class="stat-n">{e(s["note"])}</div>' if s.get("note") else "") +
                      "</div>")
        inner = (slide_head(sp) +
                 f'<div class="stats cols-{len(sp.get("stats",[]) or [])}">{cells}</div>' +
                 bullets(sp.get("body")))
    elif layout == "table":
        t = sp.get("table", {}) or {}
        th = "".join(f"<th>{e(x)}</th>" for x in t.get("headers", []))
        tr = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in row) + "</tr>"
                     for row in t.get("rows", []))
        inner = (slide_head(sp) +
                 f'<table class="tbl"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>')
    elif layout == "two-col":
        rimg = ctx.asset(sp.get("right_image"))
        right = (f'<div class="col"><img class="fig" src="{rimg}"></div>' if rimg
                 else f'<div class="col">{bullets(sp.get("right"))}</div>')
        inner = (slide_head(sp) + '<div class="two">' +
                 f'<div class="col">{bullets(sp.get("left"))}</div>' + right + "</div>")
    elif layout == "title-chart":
        cp = os.path.join(ctx.doc_dir, sp.get("chart", ""))
        body = chart_html(cp, theme) if os.path.exists(cp) else \
            f'<p class="missing">[차트 없음: {e(sp.get("chart"))}]</p>'
        inner = slide_head(sp) + body + bullets(sp.get("body"))
    elif layout == "title-image":
        img = ctx.asset(sp.get("image"))
        body = (f'<img class="fig" src="{img}">' if img
                else f'<p class="missing">[이미지 없음: {e(sp.get("image"))}]</p>')
        inner = slide_head(sp) + body + bullets(sp.get("body"))
    elif layout == "image-split":
        img = ctx.asset(sp.get("image"), kind="screens")
        side = sp.get("side", "right")
        content = slide_head(sp)
        content += numbered_html(sp["items"]) if sp.get("items") else bullets(sp.get("body"))
        panel = (f'<div class="split-img side-{side}"><img src="{img}"></div>'
                 if img else "")
        inner = f'{panel}<div class="split-text side-{side}">{content}</div>'
    elif layout == "numbered":
        inner = slide_head(sp) + numbered_html(sp.get("items"))
    elif layout == "gallery":
        paths = [ctx.asset(x, kind="screens") for x in (sp.get("images") or [])]
        inner = slide_head(sp) + strips_html(paths) + bullets(sp.get("body"))
    elif layout == "team":
        shape = sp.get("shape", "banner")      # banner(기본) | circle
        orient = sp.get("orient", "cols")      # cols(기본) | rows
        cards = ""
        for pr in sp.get("people", []) or []:
            ph = ctx.asset(pr.get("photo"), kind="screens")
            cards += (f'<div class="person shape-{shape}">' +
                      (f'<div class="ph"><img src="{ph}"></div>' if ph else '<div class="ph"></div>') +
                      '<div class="p-body">' +
                      f'<h3>{e(pr.get("name",""))}</h3>' +
                      (f'<p class="role">{e(pr["role"])}</p>' if pr.get("role") else "") +
                      bullets(pr.get("items")) + "</div></div>")
        n = len(sp.get("people", []) or [])
        cls = f'people orient-{orient} ' + (f"cols-{n}" if orient == "cols" else "")
        inner = slide_head(sp) + f'<div class="{cls}">{cards}</div>'
    elif layout == "process":
        steps = ""
        for i, st in enumerate(sp.get("steps", []) or [], 1):
            steps += ('<div class="step">' +
                      f'<span class="s-num">{e(st.get("num") or f"{i:02d}")}</span>' +
                      f'<h3>{e(st.get("heading",""))}</h3>' +
                      (f'<p>{e(st["text"])}</p>' if st.get("text") else "") + "</div>")
        n = len(sp.get("steps", []) or [])
        inner = slide_head(sp) + f'<div class="steps cols-{n}">{steps}</div>'
    elif layout == "device":
        img = ctx.asset(sp.get("image"), kind="screens")
        frame = (f'<div class="device"><div class="chrome">'
                 f'<span></span><span></span><span></span>'
                 + (f'<em>{e(sp["url"])}</em>' if sp.get("url") else "") +
                 f'</div><div class="screen"><img src="{img}"></div></div>'
                 ) if img else f'<p class="missing">[이미지 없음: {e(sp.get("image"))}]</p>'
        side = sp.get("side")
        if side in ("left", "right"):   # 텍스트와 나란히
            txt = f'<div class="col">{numbered_html(sp["items"]) if sp.get("items") else bullets(sp.get("body"))}</div>'
            cells = (f'<div class="col">{frame}</div>' + txt) if side == "left" else (txt + f'<div class="col">{frame}</div>')
            inner = slide_head(sp) + f'<div class="two dev-two">{cells}</div>'
        else:
            inner = slide_head(sp) + frame + bullets(sp.get("body"))
    elif layout == "compare":
        def _panel(d, cls):
            return ('<div class="cmp ' + cls + '">' +
                    (f'<span class="cmp-tag">{e(d.get("tag"))}</span>' if d.get("tag") else "") +
                    f'<h3>{e(d.get("heading",""))}</h3>' + bullets(d.get("items")) + "</div>")
        a, b = sp.get("left", {}) or {}, sp.get("right", {}) or {}
        inner = (slide_head(sp) + '<div class="compare">' +
                 _panel(a, "cmp-a") + '<div class="vs">VS</div>' + _panel(b, "cmp-b") +
                 "</div>")
    elif layout == "timeline":
        pts = ""
        for i, ev in enumerate(sp.get("events", []) or []):
            pts += ('<li>' +
                    f'<span class="tl-when">{e(ev.get("when",""))}</span>'
                    '<span class="tl-dot"></span>'
                    f'<div class="tl-body"><b>{e(ev.get("heading",""))}</b>' +
                    (f'<span>{e(ev["text"])}</span>' if ev.get("text") else "") +
                    "</div></li>")
        n = len(sp.get("events", []) or [])
        inner = slide_head(sp) + f'<ul class="timeline cols-{n}">{pts}</ul>'
    elif layout == "quote":
        inner = ('<div class="quote-wrap">'
                 f'<blockquote>{e(sp.get("quote") or sp.get("title",""))}</blockquote>' +
                 (f'<p class="cite">{e(sp["cite"])}</p>' if sp.get("cite") else "") +
                 "</div>")
    elif layout == "mosaic":
        imgs = [ctx.asset(x, kind="screens") for x in (sp.get("images") or [])]
        cells = "".join(f'<div class="tile"><img src="{p}"></div>' for p in imgs if p)
        inner = slide_head(sp) + f'<div class="mosaic">{cells}</div>' + bullets(sp.get("body"))
    elif layout == "contact":
        rows = ""
        for c in sp.get("contacts", []) or []:
            rows += ('<div class="ct">' +
                     f'<span class="ct-k">{e(c.get("label",""))}</span>' +
                     f'<span class="ct-v">{e(c.get("value",""))}</span></div>')
        inner = ('<div class="contact-wrap">'
                 f'<h2 class="sec-title">{e(sp.get("title",""))}</h2>' +
                 (f'<p class="lede">{e(sp["lede"])}</p>' if sp.get("lede") else "") +
                 f'<div class="contacts">{rows}</div></div>')
    elif layout == "pie":
        import math
        # 좌표계 = 슬라이드 자체(가로 100, 세로 100*h/w). 원본 회사소개서 3p를
        # 실측한 값이라 그리드 폭에 흔들리지 않고 원본과 같은 크기로 나온다.
        sl_ = theme.get("slide", {})
        VBH = 100.0 * float(sl_.get("height", 7.5)) / float(sl_.get("width", 13.333))
        pie = sp.get("pie", {}) or {}
        sl = pie.get("slices", []) or []
        total = sum(float(x.get("value", 0)) for x in sl) or 1.0
        palette = theme.get("colors", {}).get("series", ["888888"])
        acc_col = theme.get("colors", {}).get("accent", "888888")
        g = pie.get("geometry", {}) or {}
        RX, RY, RR = g.get("ring", [30.4, 34.2, 21.9])      # 정규직 점선 원
        CX, CY, R = g.get("pie", [30.9, 33.7, 14.1])        # 파이
        SX, SY, SR = g.get("satellite", [52.8, 47.8, 9.4])  # 계약직 점선 원
        # 세로 비율이 다른 규격(16:9 등)에서도 화면 안에 들어오도록 y 를 스케일
        ys = VBH / 69.26
        RY, CY, SY = RY * ys, CY * ys, SY * ys

        def pt(cx, cy, r, frac):
            a = math.radians(frac * 360 - 90)
            return cx + math.cos(a) * r, cy + math.sin(a) * r * (100.0 / VBH) * (VBH / 100.0)

        paths, labels, acc = "", "", 0.0
        for i2, x in enumerate(sl):
            frac = float(x.get("value", 0)) / total
            col = "#" + palette[i2 % len(palette)]
            x1, y1 = pt(CX, CY, R, acc)
            x2, y2 = pt(CX, CY, R, acc + frac)
            large = 1 if frac > 0.5 else 0
            if frac >= 0.999:
                paths += f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="{col}"/>'
            else:
                paths += (f'<path d="M{CX} {CY} L{x1:.3f} {y1:.3f} '
                          f'A{R} {R} 0 {large} 1 {x2:.3f} {y2:.3f} Z" fill="{col}"/>')
            mid = acc + frac / 2
            lr = R * 0.62 if frac > 0.12 else R * 0.74
            lx, ly = pt(CX, CY, lr, mid)
            cls = "pl" + ("" if frac > 0.12 else " thin")
            labels += (f'<span class="{cls}" style="left:{lx:.2f}%;top:{ly/VBH*100:.2f}%">'
                       f'<b>{e(x.get("label",""))}</b>'
                       + (f'<i>{e(x["note"])}</i>' if x.get("note") else "") + "</span>")
            acc += frac

        dots = (f'stroke="#{acc_col}" stroke-width="0.32" fill="none" '
                f'stroke-linecap="round" stroke-dasharray="0.01 1.5"')
        sat = pie.get("satellite") or {}
        svg = (f'<svg class="pie-svg" viewBox="0 0 100 {VBH:.3f}" preserveAspectRatio="none">'
               f'<circle cx="{RX}" cy="{RY}" r="{RR}" {dots}/>'
               + (f'<circle cx="{SX}" cy="{SY}" r="{SR}" {dots}/>' if sat else "")
               + paths + "</svg>")

        over = ""
        if pie.get("label"):
            over += (f'<span class="pie-ring-label" style="left:{RX:.2f}%;'
                     f'top:{(RY-RR+4.2)/VBH*100:.2f}%">{e(pie["label"])}</span>')
        over += labels
        if sat:
            over += (f'<span class="sat-l" style="left:{SX:.2f}%;top:{(SY-3.2)/VBH*100:.2f}%">'
                     f'{e(sat.get("label",""))}</span>'
                     f'<span class="sat-v" style="left:{SX:.2f}%;top:{(SY+2.4)/VBH*100:.2f}%">'
                     f'{e(sat.get("value",""))}</span>')

        logos = ""
        for lg in sp.get("logos", []) or []:
            src = ctx.asset(lg.get("image"), kind="logos")
            logos += ('<div class="lg">' +
                      (f'<img src="{src}">' if src else "") +
                      (f'<span>{e(lg["caption"])}</span>' if lg.get("caption") else "") + "</div>")
        aside = (f'<div class="aside"><h3 class="aside-t">{e(sp.get("aside_title",""))}</h3>'
                 f'<div class="logos">{logos}</div></div>') if logos else ""
        inner = slide_head(sp) + f'<div class="pie-abs">{svg}{over}</div>{aside}'
    elif layout == "diagram":
        # 다이어그램: 별도 파일(HTML fragment 또는 SVG)을 인라인으로 삽입.
        # 파일 안에서 diagram.css 클래스(.dg-*)와 CSS 변수(--c-*)를 그대로 쓴다.
        # {{icon:lucide/database}} / {{icon:brands/python}} 은 아이콘 SVG로 치환.
        ref = sp.get("diagram")
        frag = ""
        if ref:
            p = os.path.join(ctx.doc_dir, ref)
            if not os.path.exists(p):
                p = os.path.join(ctx.brand_dir, ref)
            if os.path.exists(p):
                frag = inline_icons(open(p, encoding="utf-8").read(), ctx)
            else:
                frag = f'<p class="dg-missing">diagram not found: {e(ref)}</p>'
        inner = slide_head(sp) + f'<div class="dg-stage">{frag}</div>'
    else:  # title+body
        inner = slide_head(sp) + bullets(sp.get("body"))

    # 푸터: 로고(있으면) + 브랜드/문서명 + 페이지 번호 → 하단을 시각적으로 고정
    foot = ""
    if layout != "title":
        mark = (f'<img class="logo-sm" src="{logo}">' if logo
                else f'<span class="ftr-txt">{e(theme.get("footer") or theme.get("meta",{}).get("name",""))}</span>')
        pg = f'<span class="pg">{page:02d}</span>' if page else ""
        foot = f'<footer class="ftr">{mark}{pg}</footer>'
    extra = f" img-{sp.get('side','right')}" if layout in ("image-split", "device") else ""
    return (f'<section class="slide l-{layout}{extra}">{bg_div}{veil}'
            f'<div class="body">{inner}{foot}</div></section>')


def build_html(slides, theme, ctx, brand_dir):
    # 공통 디자인 시스템(_default) + 브랜드 오버라이드 순으로 적층
    css = ""
    for cp in (os.path.join(ROOT, "brands", "_default", "slides.css"),
               os.path.join(ROOT, "brands", "_default", "diagram.css"),
               os.path.join(brand_dir, "slides.css"),
               os.path.join(brand_dir, "diagram.css")):
        if os.path.exists(cp) and os.path.abspath(cp) not in (os.path.abspath(x) for x in []):
            css += "\n/* ---- " + os.path.relpath(cp, ROOT) + " ---- */\n"
            css += open(cp, encoding="utf-8").read()
    sl = theme.get("slide", {})
    faces = font_faces(brand_dir)
    n = len(slides)
    body = "\n".join(render_slide(s, theme, ctx, page=i, total=n)
                     for i, s in enumerate(slides, 1))
    return f"""<!doctype html><html lang="ko"><meta charset="utf-8">
<title>{e(theme.get('meta',{}).get('name',''))}</title>
<style>
{faces}
  :root {{
    {css_vars(theme)};
  }}
  @page {{ size: {sl.get('width',13.333)}in {sl.get('height',7.5)}in; margin: 0; }}
{css}
</style>
<body>
{body}
</body></html>"""


def html_to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    cmd = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
           "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}",
           "file://" + os.path.abspath(html_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not os.path.exists(pdf_path):
        raise SystemExit("PDF 생성 실패:\n" + r.stderr[-1500:])


PAGE_PRESETS = {           # inch (width, height)
    "a4":    (10.833, 7.5),    # PowerPoint A4 인쇄 프리셋 (sldSz type="A4")
    "16:9":  (13.333, 7.5),
    "4:3":   (10.0, 7.5),
    "letter": (11.0, 8.5),
}


def parse_page(spec):
    """--page a4 | 16:9 | 4:3 | letter | 12x7.5(inch) -> (w, h)"""
    if not spec:
        return None
    key = spec.strip().lower()
    if key in PAGE_PRESETS:
        return PAGE_PRESETS[key]
    m = re.match(r"^([\d.]+)\s*[x×]\s*([\d.]+)$", key)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    raise SystemExit(f"오류: --page 값을 해석할 수 없습니다: {spec}\n"
                     f"  사용 가능: {', '.join(PAGE_PRESETS)} 또는 'WxH'(인치)")


def build(doc_dir, brand=None, html_only=False, out=None, page=None):
    theme, brand_dir, meta = resolve_theme(doc_dir, brand)
    # 일회성 페이지 규격 오버라이드(브랜드 파일은 건드리지 않음)
    size = parse_page(page)
    if size:
        theme.setdefault("slide", {})
        theme["slide"]["width"], theme["slide"]["height"] = size
    slides = load_slides(os.path.join(doc_dir, "storyboard"))
    ctx = Ctx(doc_dir, brand_dir)
    html_doc = build_html(slides, theme, ctx, brand_dir)

    name = os.path.basename(os.path.normpath(doc_dir))
    ver = meta.get("version")
    stem = f"{name}_{ver}" if ver else name
    if page:
        stem += "_" + re.sub(r"[^a-z0-9]+", "", page.lower())
    outdir = os.path.join(doc_dir, "output")
    os.makedirs(outdir, exist_ok=True)
    hp = os.path.join(outdir, stem + ".html")
    open(hp, "w", encoding="utf-8").write(html_doc)
    print(f"HTML: {hp}  (슬라이드 {len(slides)}장, 브랜드: {os.path.basename(brand_dir)})")
    if html_only:
        return hp
    pp = out or os.path.join(outdir, stem + ".pdf")
    html_to_pdf(hp, pp)
    print(f"PDF : {pp}")
    return pp


def main():
    ap = argparse.ArgumentParser(description="storyboard -> HTML -> PDF")
    ap.add_argument("doc_dir")
    ap.add_argument("--brand", help="brands/<NAME> 강제 지정")
    ap.add_argument("--html-only", action="store_true", help="PDF 없이 HTML만")
    ap.add_argument("-o", "--out", help="출력 PDF 경로")
    ap.add_argument("--page", help="페이지 규격 일회성 오버라이드: a4 | 16:9 | 4:3 | letter | WxH(인치)")
    a = ap.parse_args()
    build(a.doc_dir, a.brand, a.html_only, a.out, a.page)


if __name__ == "__main__":
    main()
