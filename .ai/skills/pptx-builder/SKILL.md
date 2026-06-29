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
pip install -r requirements.txt   # python-pptx 포함 (없으면: pip install python-pptx)
```

## 작업 원칙

1. **템플릿 우선.** `templates/`에 마스터 `.pptx`가 있으면 그 위에서 시작:
   ```python
   from pptx import Presentation
   prs = Presentation("templates/corporate-16x9.pptx")  # 마스터/레이아웃 상속
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

4. **스피커 노트.** 상세 설명은 `slide.notes_slide.notes_text_frame.text`에.

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
  시 깨지지 않습니다. 폰트는 `assets/fonts/`에 두고 환경에 설치해 사용합니다.
- 런(run) 단위로 폰트 지정: `run.font.name = "Noto Sans KR"`.

## 마무리

- 산출물은 `output/`에 `YYYYMMDD_프로젝트_버전.pptx`로 저장.
- PDF가 필요하면 `pdf-export` 스킬로 변환.
- 생성 후 슬라이드 수·제목·오타·레이아웃 깨짐을 점검.
