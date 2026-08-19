# Layout Catalog — storyboard `layout:` 값 정의

storyboard 슬라이드 파일(`storyboard/NN-*.md`)의 frontmatter `layout:` 필드가
가질 수 있는 값과, 각 layout이 사용하는 필드를 정의한다. 이 문서는 storyboard와
렌더러(`src/lib/render.py`) + 디자인 시스템(`brands/*/slides.css`) 사이의 **계약**이다. 값을 추가/변경하면
양쪽을 함께 고친다(AGENTS.md §6 교차 검증).

| layout | 용도 | 사용 필드 | 본문(`-` 불릿) |
|--------|------|-----------|----------------|
| `title` | 표지 | `title`(제목) | 첫 줄들 = 부제/작성자/날짜 |
| `section` | 섹션 구분 | `title` | (없음) |
| `title+body` | 메시지+근거 불릿 | `title` | 불릿 = 본문 |
| `title+chart` | 메시지+차트 | `title`, `chart`(CSV 경로) | 불릿 = 차트 해설(선택) |
| `title+image` | 메시지+이미지 | `title`, `image`(이미지 경로) | 불릿 = 캡션(선택) |
| `columns` | N개 카드(예: 3대 특징) | `title`, `columns:`(아래) | (미사용) |
| `table` | 표 | `title`, `table:`(아래) | (미사용) |
| `stat` | 큰 숫자 강조 | `title`, `stats:`(아래) | 불릿 = 보조 설명(선택) |
| `two-col` | 2단 구성 | `title`, `left:`/`right:` 또는 `right_image:` | (미사용) |
| `image-split` | 사선 이미지 패널 + 텍스트 | `title`, `image`, `side`(left/right), `items:` 또는 본문 | 불릿(=items 없을 때) |
| `numbered` | 01/02/03 번호 리스트 | `title`, `items:` | (미사용) |
| `process` | 단계 진행(셰브론 연결) | `title`, `steps:` | (미사용) |
| `gallery` | 사선 이미지 스트립 | `title`, `images:`(2~4) | 캡션 |
| `team` | 인물 카드 | `title`, `people:` | (미사용) |
| `device` | 브라우저 프레임 속 스크린샷 | `title`, `image`, `url`(선택), `side`(선택) | 캡션 |
| `compare` | 좌우 대비 (VS) | `title`, `left:`/`right:`(각 tag·heading·items) | (미사용) |
| `timeline` | 가로 연혁 | `title`, `events:`(when·heading·text) | (미사용) |
| `quote` | 큰 인용문 | `quote`, `cite`(선택) | (미사용) |
| `mosaic` | 이미지 그리드(첫 장 강조) | `title`, `images:` | 캡션 |
| `contact` | 마무리 연락처 | `title`, `lede`, `contacts:`(label·value) | (미사용) |

구조화 필드(YAML frontmatter, 들여쓰기 주의):

```yaml
# columns — 카드 묶음
columns:
  - num: "01"                    # 선택: 카드 번호
    heading: "하이브리드 검색"
    items: ["벡터+키워드", "출처 표기"]
  - heading: "결정론적 보안"
    items: ["권한 밖 차단"]

# table — 표
table:
  headers: ["고객", "기간", "매출"]
  rows:
    - ["삼성 MARU", "2018~2025", "260억+"]
    - ["KT 로봇", "2022~2023", "25억+"]

# stat — 큰 숫자 (note는 선택)
stats:
  - value: "93.2%"
    label: "요구사항 만족도"
    note: "예상질문 44종 기준"
  - value: "41/44"
    label: "응답 성공"

# image-split / numbered / process — 번호 항목 공통 형태
items:                          # numbered, image-split 에서 사용
  - heading: "온프레미스 운영"
    text: "외부 전송 0건, SSO 연동"     # text 는 선택
  - num: "05"                   # num 은 선택(기본은 자동 01,02,…)
    heading: "…"
steps:                          # process 에서 사용 (items 와 같은 형태)
  - num: "01"
    heading: "세션 권한 확인"
    text: "Role / Level 기반 접근 제어"

# gallery — 사선 이미지 스트립 (2~4장 권장)
images: [kori-code, amos-ai, kt-robot, hscode-result]

# team — 인물 카드
people:
  - photo: leader-byun
    name: "변정민"
    role: "AI Lead · Ph.D (KAIST)"
    items: ["Kori AI 제품 설계", "Elice 공동창업"]

# compare — 좌우 대비 (right 를 우리 쪽으로 두면 액센트 강조됨)
left:  { tag: "기존 방식", heading: "클라우드 LLM", items: ["데이터 반출 필요"] }
right: { tag: "KORI Answers", heading: "온프레미스 RAG", items: ["폐쇄망 내 완결"] }

# timeline — 가로 연혁 (3~5개 권장)
events:
  - when: "2018"
    heading: "삼성전자 MARU 착수"
    text: "메모리 전략마케팅실 플랫폼"

# device — 브라우저 프레임. side 를 주면 텍스트와 2단으로 배치
image: maru-platform
url: "maru.samsung.net"      # 선택: 주소창 텍스트
side: right                  # 선택: left|right (없으면 전체 폭)

# contact — 마무리
contacts:
  - { label: "Email", value: "jy.choi@xenoimpact.com" }

# two-col — 2단(불릿 좌/우, 또는 우측 이미지)
left:  ["정형: Oracle", "분석: ClickHouse"]
right: ["비정형: ElasticSearch", "벡터: Milvus"]
# right_image: "research/arch.png"   # right 대신 이미지
```

공통 필드(모든 layout):

- `title` — action title(결론을 말하는 제목). **필수.**
- `kicker` — 제목 위 작은 라벨(섹션/축 표시). 액센트색·대문자. 권장.
- `lede` — 제목 아래 한 줄 요약. 슬라이드 밀도를 올려준다. 권장.
- `bg` — 배경 이미지 이름(브랜드 `assets/backgrounds/`) 또는 문서 상대경로.
  미지정 시 `theme.backgrounds`의 레이아웃별 기본값. 끄려면 `bg: none`.

이미지 참조(`image`, `images`, `photo`, `bg`)는 확장자 없이 이름만 적으면 된다.
탐색 순서: 문서 폴더 → 브랜드 `assets/{screens,backgrounds,logos,images}` →
공용 `brands/_default/assets/…`. 제품 스크린샷은 공용에 있다.
- `source` — 근거 출처 ID 목록(`research/sources.md`와 일치). 권장.
- `## notes` — 스피커 노트(본문 아래 별도 섹션).

경로 규칙:

- `chart:`·`image:` 경로는 **문서 폴더 기준 상대경로**(예: `research/cost.csv`).

CSV 형식(`chart:`): 첫 행은 헤더, 첫 열은 카테고리, 이후 열은 시리즈.

```
year,Revenue,Cost
2024,100,80
2025,150,70
2026,210,60
```

## 페이지 규격

브랜드 기본값은 `theme.yaml > slide`. 렌더 시 `--page a4|16:9|4:3|letter|WxH`로
**일회성 오버라이드**가 가능하며 출력 파일명에 접미사가 붙는다(화면용/인쇄용 두 벌).
치수가 슬라이드 폭 기준 상대값이라 규격이 바뀌어도 레이아웃은 리플로우된다.
