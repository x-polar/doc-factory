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
        slides.append({**meta, "body": body, "free": free, "notes": notes,
                       "_file": os.path.basename(path)})
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
        cands = [
            os.path.join(self.doc_dir, ref),
            os.path.join(self.brand_dir, ref),
            os.path.join(self.brand_dir, "assets", kind, ref),
        ]
        for ext in ("", ".jpg", ".png", ".webp"):
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
        inner = (
            (f'<img class="logo" src="{cover_logo}">' if cover_logo else "") +
            '<div class="cover-mid">' +
            f'<h1 class="cover-title">{e(sp.get("title",""))}</h1>' +
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
    else:  # title+body
        inner = slide_head(sp) + bullets(sp.get("body"))

    # 푸터: 로고(있으면) + 브랜드/문서명 + 페이지 번호 → 하단을 시각적으로 고정
    foot = ""
    if layout != "title":
        mark = (f'<img class="logo-sm" src="{logo}">' if logo
                else f'<span class="ftr-txt">{e(theme.get("footer") or theme.get("meta",{}).get("name",""))}</span>')
        pg = f'<span class="pg">{page:02d}</span>' if page else ""
        foot = f'<footer class="ftr">{mark}{pg}</footer>'
    return (f'<section class="slide l-{layout}">{bg_div}{veil}'
            f'<div class="body">{inner}{foot}</div></section>')


def build_html(slides, theme, ctx, brand_dir):
    # 공통 디자인 시스템(_default) + 브랜드 오버라이드 순으로 적층
    css = ""
    for cp in (os.path.join(ROOT, "brands", "_default", "slides.css"),
               os.path.join(brand_dir, "slides.css")):
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
