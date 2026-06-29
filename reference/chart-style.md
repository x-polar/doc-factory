# Chart Style — 차트 규칙

## 원칙

- 차트 색은 브랜드 `theme.yaml`의 `colors.series` 팔레트를 **순서대로** 사용.
- 한 차트에 시리즈는 가능하면 4개 이하. 많으면 묶거나 분리.
- 제목은 슬라이드 action title이 담당 → 차트 자체 제목은 보통 생략.
- 축·범례 폰트는 `fonts.body`, 크기는 `sizes.caption` 수준.
- 격자선·테두리 최소화(데이터 잉크 우선).

## 데이터(CSV) 형식

`storyboard`의 `chart:`가 가리키는 CSV는 다음을 따른다(첫 행 헤더, 첫 열 카테고리):

```
year,Revenue,Cost
2024,100,80
2025,150,70
2026,210,60
```

- 시리즈 이름 = 헤더의 2번째 열부터.
- 카테고리 = 각 행의 첫 열.

## 차트 유형 선택

- 시간/추세 → 세로 막대 또는 선
- 구성비 → 누적 막대(파이는 항목 적을 때만)
- 비교 → 가로 막대

deckbuilder는 기본적으로 군집 세로 막대(`COLUMN_CLUSTERED`)를 사용한다. 다른
유형이 필요하면 슬라이드 frontmatter에 `chart_type:`을 추가하는 방식으로 확장한다
(추가 시 `layout-catalog.md`와 `deckbuilder.py`를 함께 갱신).
