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
