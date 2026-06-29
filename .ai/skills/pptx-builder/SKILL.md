---
name: pptx-builder
description: >
  비즈니스/기술 문서용 슬라이드 덱(.pptx)을 python-pptx로 생성·수정합니다.
  사용자가 슬라이드, 덱, 프레젠테이션, 제안서, 보고서 덱을 만들거나 수정해
  달라고 할 때 사용합니다.
---

# pptx-builder

`python-pptx`로 `.pptx`를 프로그래밍 방식으로 생성/수정하는 절차입니다.

## 준비

```bash
pip install -r requirements.txt   # python-pptx, PyYAML 포함
```

## 권장 경로: deckbuilder

대부분의 경우 직접 python을 짜지 말고 공유 빌더를 씁니다. storyboard와
**선택된 브랜드 테마**를 읽어 자동으로 덱을 생성합니다.

```bash
python src/lib/deckbuilder.py docs/20260629_proposal
# -> docs/20260629_proposal/output/20260629_proposal_v1.pptx
```

- **브랜드/테마 선택은 문서의 `doc.yaml`**: `brand:`로 `brands/<brand>/theme.yaml`을
  고르고, `theme:` 블록으로 이 덱만의 토큰을 오버라이드(deep-merge). 해석 순서·구조는
  `brands/README.md` 참고. 빌더에 `--brand NAME`으로 강제 지정도 가능.
- 색·폰트·여백은 브랜드 `theme.yaml` 토큰을 따릅니다(임의 지정 금지).
- 슬라이드 `layout:` 값의 의미·필드는 `reference/layout-catalog.md` 참고.
- 차트 CSV 형식·차트 규칙은 `reference/chart-style.md` 참고.
- 새 layout/차트유형이 필요하면 `deckbuilder.py`와 `layout-catalog.md`를 **함께**
  확장합니다(AGENTS.md §6 교차 검증).

아래 내용은 deckbuilder를 확장하거나 특수 슬라이드를 손으로 만들 때의 참고입니다.

## 입력: 스토리보드 읽기

덱은 `docs/<문서>/storyboard/`의 **슬라이드별 파일**에서 생성합니다. 파일 하나가
슬라이드 하나이고, **파일명 숫자 접두(`01-`, `02-`) 순서가 곧 슬라이드 순서**입니다.
각 파일은 YAML frontmatter(구조) + Markdown 본문(불릿) + `## notes`(스피커 노트)
구성입니다.

```python
import glob, os, re, yaml

def load_slides(storyboard_dir):
    slides = []
    for path in sorted(glob.glob(os.path.join(storyboard_dir, "*.md"))):
        text = open(path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        meta = yaml.safe_load(m.group(1)) if m else {}
        rest = m.group(2) if m else text
        # 본문과 notes 분리
        parts = re.split(r"^##\s*notes\s*$", rest, maxsplit=1, flags=re.M)
        body  = [l[1:].strip() for l in parts[0].splitlines() if l.strip().startswith("-")]
        notes = parts[1].strip() if len(parts) > 1 else ""
        slides.append({**meta, "body": body, "notes": notes, "_file": path})
    return slides

slides = load_slides("docs/20260629_proposal/storyboard")
```

`meta`에는 `title`(action title), `layout`, `chart`, `image`, `source` 등이 담깁니다.
이 리스트를 순회하며 아래 패턴으로 슬라이드를 만듭니다.

## 작업 원칙

1. **템플릿 우선.** 브랜드의 `templates/`에 마스터 `.pptx`가 있으면 그 위에서 시작:
   ```python
   from pptx import Presentation
   prs = Presentation("brands/acme/templates/acme-16x9.pptx")  # 마스터/레이아웃 상속
   ```
   템플릿이 없으면 빈 16:9로 시작:
   ```python
   from pptx import Presentation
   from pptx.util import Inches
   prs = Presentation()
   prs.slide_width  = Inches(13.333)   # 16:9
   prs.slide_height = Inches(7.5)
   ```

2. **레이아웃 재사용.** 직접 도형을 그리기보다 `slide_layouts`의 플레이스홀더에
   텍스트를 채워 일관성을 유지합니다.

3. **Action title.** 각 슬라이드 제목은 결론/주장을 담습니다(예: "매출은 3년간
   2배 성장" — "매출 추이"가 아니라).

4. **스피커 노트.** 상세 설명은 `slide.notes_slide.notes_text_frame.text`에
   (스토리보드 각 파일의 `## notes` 내용을 그대로 넣음).

## 기본 패턴

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation("templates/corporate-16x9.pptx")  # 없으면 위 빈 16:9 사용

# 제목 슬라이드
layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(layout)
slide.shapes.title.text = "프로젝트 제안서"
slide.placeholders[1].text = "2026 Q3 · Xenoimpact"

# 본문(불릿) 슬라이드
layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(layout)
slide.shapes.title.text = "핵심 결론: 도입 시 비용 30% 절감"
body = slide.placeholders[1].text_frame
body.text = "현행 대비 운영 비용 30% 절감"
for line in ["배포 자동화로 리드타임 단축", "유지보수 인력 재배치 가능"]:
    p = body.add_paragraph()
    p.text = line
    p.level = 1

prs.save("output/20260629_proposal_v1.pptx")
```

## 표 / 차트

- 표: `slide.shapes.add_table(rows, cols, left, top, width, height)`
- 네이티브 차트(편집 가능):
  ```python
  from pptx.chart.data import CategoryChartData
  from pptx.enum.chart import XL_CHART_TYPE
  data = CategoryChartData()
  data.categories = ["2024", "2025", "2026"]
  data.add_series("매출", (100, 150, 210))
  slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, data)
  ```
- 복잡한 시각화는 matplotlib로 PNG 생성 후 `add_picture`로 삽입.

## 한글 폰트

- 시스템에 한글 폰트(예: Noto Sans KR / Pretendant 등)가 설치돼 있어야 PDF 변환
  시 깨지지 않습니다. 폰트는 브랜드의 `assets/fonts/`에 두고 환경에 설치해 씁니다.
- 런(run) 단위로 폰트 지정: `run.font.name = "Noto Sans KR"`.

## 마무리

- 산출물은 `output/`에 `YYYYMMDD_프로젝트_버전.pptx`로 저장(작업 중 임시본).
- PDF가 필요하면 `pdf-export` 스킬로 변환.
- 생성 후 슬라이드 수·제목·오타·레이아웃 깨짐을 점검.
- 확정된 버전은 `release/`로 복사해 커밋한다(`output/`은 git 제외, `release/`는 추적).
