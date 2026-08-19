---
name: deck-render
description: >
  storyboard(.md)를 슬라이드 덱(PDF)으로 렌더합니다. HTML/CSS로 디자인하고 헤드리스
  Chromium으로 출력합니다. 덱·발표자료·소개서를 만들거나 다시 렌더할 때 사용합니다.
---

# deck-render (주력 렌더 경로)

`src/lib/render.py`가 storyboard + 브랜드 테마를 읽어 **HTML → PDF**를 생성합니다.
디자인은 **CSS가 담당**합니다. 파이썬은 좌표를 계산하지 않습니다.

```bash
python src/lib/render.py docs/20260630_proposal            # → output/*.html, *.pdf
python src/lib/render.py docs/20260630_proposal --html-only # 빠른 확인용
python src/lib/render.py docs/20260630_proposal --brand xenoimpact
```

## 왜 HTML/CSS인가
- 풀블리드 배경·그라디언트·정밀 그리드·웹폰트가 전부 CSS 한 줄. pptx 좌표 계산 불가능한 영역.
- 의존성 1개(Chromium, 이 환경에 사전 설치). LibreOffice/python-pptx 불필요.
- 브랜드 토큰(`theme.yaml`) → CSS 변수로 자동 주입.

## 디자인이 사는 곳
| 파일 | 역할 |
|------|------|
| `brands/_default/slides.css` | 공통 디자인 시스템(모든 브랜드가 상속) |
| `brands/<brand>/slides.css` | 브랜드 고유 오버라이드만 |
| `brands/<brand>/theme.yaml` | 색·폰트·비율·로고·기본 배경 토큰 |

- 모든 치수는 슬라이드 폭 기준 `--u`(폭의 1%)라 **비율이 바뀌어도 레이아웃이 무너지지 않습니다.**
- 폰트는 `assets/fonts/<Family>/*.ttf`를 **@font-face로 자동 임베드** → 시스템 설치에
  의존하지 않습니다. (이전 실패: 브랜드가 Pretendard를 지정했으나 설치가 없어 계속 폴백 렌더됨)

## 자주 하는 일
- **배경 바꾸기**: 슬라이드 frontmatter `bg: cosmos-network` (브랜드 `assets/backgrounds/`).
  끄려면 `bg: none`. 미지정 시 `theme.backgrounds`의 레이아웃별 기본값 사용.
- **레이아웃 추가**: `render.py`의 `render_slide()`에 분기 + `_default/slides.css`에 스타일,
  그리고 `reference/layout-catalog.md`를 **같은 커밋에서** 갱신(AGENTS.md §6).
- **디자인만 손보기**: CSS만 고치고 재렌더. 파이썬을 건드릴 필요 없음.

## 주의
- Chromium 경로는 자동 탐색(`/opt/pw-browsers/...`). 못 찾으면 명확히 실패합니다.
- 이미지는 `file://` 절대경로로 삽입되므로 **HTML만 따로 옮기면 이미지가 깨집니다**(PDF는 무관).
