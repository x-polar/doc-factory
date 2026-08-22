# Diagram Catalog — `layout: diagram` 사용법

기술 다이어그램을 슬라이드에 넣는 방법과 `.dg-*` 컴포넌트 정의.
이 문서는 storyboard ↔ `src/lib/render.py`(diagram 분기) ↔
`brands/_default/diagram.css` 사이의 **계약**이다(AGENTS.md §6 교차 검증).
디자인 기준은 `reference/diagram-refs/`(레퍼런스 8종 + README)를 따른다.

## 사용법

1) storyboard frontmatter:

```yaml
---
title: "환각이 보안을 뚫지 못한다 — …"   # action title
layout: diagram
diagram: diagrams/architecture.html      # 문서 폴더 기준 상대경로
---
```

2) 다이어그램 파일: `docs/<문서>/diagrams/<이름>.html` — HTML fragment
   (루트는 `<div class="dg-canvas">`). 렌더 시 슬라이드 본문에 인라인 삽입되어
   브랜드 CSS 변수(`--c-*`, `--font-*`)와 diagram.css를 그대로 상속한다.
   **브랜드를 바꾸면 다이어그램도 함께 리스킨된다.**

골드스탠다드 예시: `docs/20260822_diagram_gold/` (KORI Answers 아키텍처).

## 좌표계 규약

- 노드/존/칩/스텝: `dg-canvas` 기준 **% 좌표** (`style="left:..%;top:..%"`).
- 연결선: `<svg class="dg-edges" viewBox="0 0 1000 560" preserveAspectRatio="none">`
  — x% = X/10, y% = Y/5.6 로 환산해 노드 좌표와 맞춘다.
- 화살촉은 fragment의 `<defs><marker>`로 정의(브랜드 색 하드코딩 대신
  액센트 색을 직접 지정; CSS 변수는 marker 내부에서 안 먹는 경우가 있음).

## 컴포넌트 (.dg-*)

| 클래스 | 역할 | 비고 |
|--------|------|------|
| `dg-canvas` | 좌표 기준 루트 | `--dots` 변형: 도트 그리드 배경 |
| `dg-zone` | 점선 그룹핑 존 | `--solid`(실선) `--accent`(강조색) 변형 |
| `dg-zone-label` | 존 라벨 | 존의 첫 자식으로. 배경이 선을 가림(z2) |
| `dg-node` | 카드 노드 | `--accent`(강조) `--ghost`(외부 시스템) `--danger` |
| `dg-head` / `dg-ico` / `dg-t` | 노드 헤더 행 / 아이콘 / 제목 | 아이콘: `{{icon:lucide/database}}` 치환 문법 — `brands/_default/assets/icons/README.md` 참고 |
| `dg-s` | 노드 서브텍스트 | |
| `dg-items` | 노드 내 체크리스트 | `<ul class="dg-items"><li>` |
| `dg-chip` | 프로토콜/기술 칩 | 좌표=칩 중심. `--muted` 변형 |
| `dg-step` | 흐름 순서 번호 원 | 좌표=원 중심 |
| `dg-edges` | 연결선 SVG 레이어 | 선 클래스: `e`, `e--accent`, `e--flow`(대시), `e--wide` |

### 아이소메트릭 (.dg-iso-*)

플랫 카드 대신 2:1 iso 투영(x→(0.866,0.5), y→(-0.866,0.5))으로 그리는 모드.
배포 토폴로지·망 분리·인프라 조감도에 쓴다. 골드스탠다드:
`docs/20260823_diagram_iso_gold/` (KORI Answers 3망 배포 토폴로지).

| 클래스 | 역할 | 비고 |
|--------|------|------|
| `dg-iso-plane` | 존 평면(다이아몬드) | `--iso-tint`로 존 색 지정. 좌표+width/height는 iso 변환 전 기준 |
| `dg-iso-zonetag` | 존 이름표 | 좌표=중심. 평면 위/아래 꼭짓점 근처에 |
| `dg-iso-cube` | 3면 큐브 | 자식 `.f-top/.f-left/.f-right` 3개 필수. `--s`(한 변)·`--h`(높이)·`--iso-c`(색). 앵커=윗면 위쪽 꼭짓점 |
| `.f-top > .dg-ico` | 윗면 아이콘 | 역변환으로 서 있게 렌더됨. `{{icon:}}` 문법 그대로 |
| `dg-iso-label` | 흰색 라벨 필 | 좌표=중심. `<small>`로 부제. 큐브 옆에 콜아웃처럼 |

아이소메트릭 규약:
- 좌표는 `in` 단위 권장 (캔버스 약 11.9×5.4in, 16:9 기준).
- 깊이 정렬: **뒤(위쪽) 요소를 먼저, 앞(아래쪽) 요소를 나중에** 쓴다 (DOM 순서=페인트 순서).
- 흐름선은 iso 축 기울기(±30°, dy/dx≈±0.577)를 따라야 바닥에 붙어 보인다.
- 존 배치는 좌상→우하 대각선 흐름이 기본 (레퍼런스 08 문법).

## 품질 체크리스트 (렌더 후 스크린샷으로 반드시 확인)

- [ ] 화살표가 노드 경계에 정확히 닿는가 (떠 있거나 뚫고 들어가지 않게)
- [ ] 선이 라벨·노드를 관통하지 않는가 (경로를 우회시키거나 라벨 배경으로 가림)
- [ ] 주 흐름이 한 줄로 읽히는가 (스텝 번호 ①②③…으로 순서 보강)
- [ ] 위계가 3단 이내인가 (accent 노드 = 핵심, 기본 = 보통, ghost = 외부)
- [ ] 빈 공간이 균형 있게 분배됐는가 (존 높이는 내용물에 맞춤)
- [ ] 폰트 크기 최소 7pt 이상 (인쇄 시 가독성)

## 워크플로

1. 내용 확정(어떤 노드·흐름·존이 필요한가) → 종이 스케치 수준의 배치 결정
2. fragment 작성 → `render.py <문서폴더>` → PDF를 이미지로 떠서 눈으로 비평
3. 접점·정렬·밀도 문제를 고치고 재렌더 — **최소 2회 이상 반복**
4. 확정본은 `release/`로 복사 후 커밋
