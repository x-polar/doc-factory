# templates/ — 마스터 pptx

브랜드 마스터 슬라이드(.pptx). 색/폰트/레이아웃이 정의된 빈 덱으로, `pptx-builder`가
이 위에 콘텐츠만 얹어 일관성을 확보한다.

- 예: `corporate-16x9.pptx`
- 마스터의 슬라이드 레이아웃 이름은 `reference/layout-catalog.md`의 `layout:`
  값과 대응시키는 것을 권장.
- **브랜드 확정 전까지는 비어 있어도 된다.** `deckbuilder`는 마스터가 없으면
  `brand/theme.yaml` 토큰으로 빈 16:9 덱을 프로그래밍 방식으로 스타일링한다.
