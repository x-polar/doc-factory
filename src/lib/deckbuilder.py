#!/usr/bin/env python3
"""storyboard(슬라이드별 .md) + 브랜드 테마 -> .pptx 생성.

문서의 brief.md frontmatter가 브랜드를 고르고(brands/<brand>/theme.yaml), 필요하면
theme: 블록으로 토큰을 오버라이드한다. 마스터 pptx 없이 토큰으로 프로그래밍
스타일링한다(마스터가 생기면 그 위에 얹도록 확장). layout 정의는
reference/layout-catalog.md, 브랜드 구조는 brands/README.md 참고.

사용법:
  python src/lib/deckbuilder.py <문서폴더> [-o out.pptx] [--brand NAME] [--theme path]
예:
  python src/lib/deckbuilder.py docs/20260629_proposal
"""
import argparse
import csv
import glob
import os
import re

import yaml
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ----- 입력 파싱 ---------------------------------------------------------------

def deep_merge(base, over):
    """over의 값으로 base를 재귀 병합(dict는 깊게, 그 외는 덮어씀)."""
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_doc_meta(doc_dir):
    """문서 메타(title/brand/version/theme)를 brief.md frontmatter에서 읽는다."""
    path = os.path.join(doc_dir, "brief.md")
    if not os.path.exists(path):
        return {}
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def resolve_brand_dir(brand):
    brand_dir = os.path.join(ROOT, "brands", brand or "_default")
    if not os.path.isdir(brand_dir):
        brand_dir = os.path.join(ROOT, "brands", "_default")
    return brand_dir


def resolve_theme(doc_dir, brand_override=None, theme_path=None):
    """brief.md frontmatter -> 브랜드 theme 로드 -> theme: 오버라이드 병합.
    반환: (theme dict, brand_dir, meta dict)."""
    meta = load_doc_meta(doc_dir)
    brand = brand_override or meta.get("brand") or "_default"
    brand_dir = resolve_brand_dir(brand)
    theme_file = theme_path or os.path.join(brand_dir, "theme.yaml")
    theme = yaml.safe_load(open(theme_file, encoding="utf-8"))
    theme = deep_merge(theme, meta.get("theme"))
    return theme, brand_dir, meta


def load_slides(storyboard_dir):
    """storyboard/*.md 를 파일명 순으로 읽어 슬라이드 dict 목록 반환."""
    slides = []
    for path in sorted(glob.glob(os.path.join(storyboard_dir, "*.md"))):
        text = open(path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        meta = (yaml.safe_load(m.group(1)) if m else {}) or {}
        rest = m.group(2) if m else text
        parts = re.split(r"^##\s*notes\s*$", rest, maxsplit=1, flags=re.M)
        lines = parts[0].splitlines()
        body = [l.strip()[1:].strip() for l in lines if l.strip().startswith("-")]
        free = [l.strip() for l in lines
                if l.strip() and not l.strip().startswith("-")]
        notes = parts[1].strip() if len(parts) > 1 else ""
        slides.append({**meta, "body": body, "free": free,
                       "notes": notes, "_file": os.path.basename(path)})
    return slides


def read_csv_chart(path):
    """첫 행 헤더·첫 열 카테고리 CSV -> (categories, [(series_name, values)])."""
    with open(path, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r]
    header = rows[0]
    series_names = header[1:]
    categories = [r[0] for r in rows[1:]]
    series = []
    for i, name in enumerate(series_names, start=1):
        series.append((name, [float(r[i]) for r in rows[1:]]))
    return categories, series


# ----- 렌더 헬퍼 ---------------------------------------------------------------

class Deck:
    def __init__(self, theme):
        self.t = theme
        self.c = theme["colors"]
        self.f = theme["fonts"]
        self.s = theme["sizes"]
        self.sl = theme["slide"]
        self.prs = Presentation()
        self.prs.slide_width = Inches(self.sl["width"])
        self.prs.slide_height = Inches(self.sl["height"])
        self.blank = self.prs.slide_layouts[6]  # 기본 템플릿의 Blank 레이아웃

    def rgb(self, key):
        return RGBColor.from_string(self.c[key])

    def _add_text(self, slide, text, left, top, width, height, *,
                  size, color, bold=False, align=PP_ALIGN.LEFT,
                  anchor=MSO_ANCHOR.TOP, font=None):
        box = slide.shapes.add_textbox(Inches(left), Inches(top),
                                       Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        para = tf.paragraphs[0]
        para.alignment = align
        run = para.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.name = font or self.f["body"]
        run.font.color.rgb = RGBColor.from_string(color)
        return box

    def _bg(self, slide, color_key):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = self.rgb(color_key)

    def _notes(self, slide, text):
        if text:
            slide.notes_slide.notes_text_frame.text = text

    # --- layout 별 렌더 ---
    def render(self, sp):
        layout = sp.get("layout", "title+body")
        fn = getattr(self, "_l_" + layout.replace("+", "_"), None)
        if fn is None:
            fn = self._l_title_body  # 알 수 없는 layout은 본문형으로 폴백
        slide = self.prs.slides.add_slide(self.blank)
        fn(slide, sp)
        self._notes(slide, sp.get("notes", ""))
        return slide

    def _title_band(self, slide, text):
        m = self.sl["margin"]
        self._add_text(slide, text, m, m, self.sl["width"] - 2 * m, 1.0,
                       size=self.s["title"], color=self.c["primary"],
                       bold=True, font=self.f["heading"])

    def _l_title(self, slide, sp):
        self._bg(slide, "primary")
        w, h = self.sl["width"], self.sl["height"]
        self._add_text(slide, sp["title"], 1.0, h / 2 - 1.0, w - 2.0, 1.5,
                       size=self.s["title"] + 8, color=self.c["on_primary"],
                       bold=True, align=PP_ALIGN.LEFT, font=self.f["heading"])
        sub = " · ".join(sp.get("free", []))
        if sub:
            self._add_text(slide, sub, 1.0, h / 2 + 0.3, w - 2.0, 1.0,
                           size=self.s["subtitle"], color=self.c["on_primary"],
                           font=self.f["body"])

    def _l_section(self, slide, sp):
        self._bg(slide, "accent")
        w, h = self.sl["width"], self.sl["height"]
        self._add_text(slide, sp["title"], 1.0, h / 2 - 0.6, w - 2.0, 1.2,
                       size=self.s["title"] + 4, color=self.c["on_primary"],
                       bold=True, anchor=MSO_ANCHOR.MIDDLE, font=self.f["heading"])

    def _l_title_body(self, slide, sp):
        self._title_band(slide, sp["title"])
        m = self.sl["margin"]
        box = slide.shapes.add_textbox(Inches(m), Inches(1.7),
                                       Inches(self.sl["width"] - 2 * m),
                                       Inches(self.sl["height"] - 2.4))
        tf = box.text_frame
        tf.word_wrap = True
        for i, line in enumerate(sp.get("body", [])):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            run = para.add_run()
            run.text = "•  " + line
            run.font.size = Pt(self.s["body"])
            run.font.name = self.f["body"]
            run.font.color.rgb = RGBColor.from_string(self.c["text"])
            para.space_after = Pt(8)

    def _l_title_chart(self, slide, sp):
        self._title_band(slide, sp["title"])
        chart_path = sp.get("_chart_abspath")
        if not chart_path or not os.path.exists(chart_path):
            self._add_text(slide, f"[차트 누락: {sp.get('chart')}]",
                           self.sl["margin"], 1.8, 6, 0.5,
                           size=self.s["caption"], color=self.c["muted"])
            return
        categories, series = read_csv_chart(chart_path)
        data = CategoryChartData()
        data.categories = categories
        for name, vals in series:
            data.add_series(name, vals)
        gframe = slide.shapes.add_chart(
            XL_CHART_TYPE.COLUMN_CLUSTERED,
            Inches(self.sl["margin"]), Inches(1.8),
            Inches(self.sl["width"] - 2 * self.sl["margin"]), Inches(4.6), data)
        chart = gframe.chart
        chart.has_title = False
        for i, plot_series in enumerate(chart.series):
            palette = self.c["series"]
            plot_series.format.fill.solid()
            plot_series.format.fill.fore_color.rgb = \
                RGBColor.from_string(palette[i % len(palette)])

    def _l_title_image(self, slide, sp):
        self._title_band(slide, sp["title"])
        img = sp.get("_image_abspath")
        if img and os.path.exists(img):
            slide.shapes.add_picture(img, Inches(self.sl["margin"]), Inches(1.8),
                                     height=Inches(4.6))
        else:
            self._add_text(slide, f"[이미지 누락: {sp.get('image')}]",
                           self.sl["margin"], 1.8, 6, 0.5,
                           size=self.s["caption"], color=self.c["muted"])

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.prs.save(path)


# ----- 엔트리포인트 ------------------------------------------------------------

def build(doc_dir, out=None, brand=None, theme_path=None):
    theme, brand_dir, meta = resolve_theme(doc_dir, brand, theme_path)
    slides = load_slides(os.path.join(doc_dir, "storyboard"))
    # chart/image 경로를 문서폴더 기준 절대경로로 해석
    for sp in slides:
        if sp.get("chart"):
            sp["_chart_abspath"] = os.path.join(doc_dir, sp["chart"])
        if sp.get("image"):
            sp["_image_abspath"] = os.path.join(doc_dir, sp["image"])
    deck = Deck(theme)
    deck.brand_dir = brand_dir  # 자산(로고 등) 해석 기준
    for sp in slides:
        deck.render(sp)
    if out is None:
        name = os.path.basename(os.path.normpath(doc_dir))
        version = meta.get("version")
        fname = f"{name}_{version}.pptx" if version else f"{name}.pptx"
        out = os.path.join(doc_dir, "output", fname)
    deck.save(out)
    print(f"생성: {out}  (슬라이드 {len(slides)}장, 브랜드: {os.path.basename(brand_dir)})")
    return out


def main():
    ap = argparse.ArgumentParser(description="storyboard -> pptx")
    ap.add_argument("doc_dir", help="문서 폴더 (storyboard/ 포함)")
    ap.add_argument("-o", "--out", help="출력 pptx 경로")
    ap.add_argument("--brand", help="brands/<NAME> 강제 지정(brief.md frontmatter보다 우선)")
    ap.add_argument("--theme", help="theme.yaml 경로 직접 지정")
    args = ap.parse_args()
    build(args.doc_dir, args.out, args.brand, args.theme)


if __name__ == "__main__":
    main()
