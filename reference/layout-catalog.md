# Layout Catalog — storyboard `layout:` 값 정의

storyboard 슬라이드 파일(`storyboard/NN-*.md`)의 frontmatter `layout:` 필드가
가질 수 있는 값과, 각 layout이 사용하는 필드를 정의한다. 이 문서는 storyboard와
`deckbuilder`(`src/lib/deckbuilder.py`) 사이의 **계약**이다. 값을 추가/변경하면
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

구조화 필드(YAML frontmatter, 들여쓰기 주의):

```yaml
# columns — 카드 묶음
columns:
  - heading: "하이브리드 검색"
    items: ["벡터+키워드", "출처 표기"]
  - heading: "결정론적 보안"
    items: ["권한 밖 차단"]

# table — 표
table:
  headers: ["고객", "기간", "매출"]
  rows:
    - ["삼성 MARU", "2018~2025", "260억+"]
    - ["KT 로봇", "2022~2023", "25억+"]

# stat — 큰 숫자
stats:
  - value: "93.2%"
    label: "요구사항 만족도"
  - value: "41/44"
    label: "응답 성공"

# two-col — 2단(불릿 좌/우, 또는 우측 이미지)
left:  ["정형: Oracle", "분석: ClickHouse"]
right: ["비정형: ElasticSearch", "벡터: Milvus"]
# right_image: "research/arch.png"   # right 대신 이미지
```

공통 필드(모든 layout):

- `title` — action title(결론을 말하는 제목). **필수.**
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
