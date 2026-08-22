# icons/ — 다이어그램용 SVG 아이콘 자산

`layout: diagram` fragment에서 `{{icon:<set>/<name>}}` 으로 인라인 삽입된다
(render.py `inline_icons()`가 치환). 전부 벡터(SVG)라 해상도 무손실이고,
`currentColor` 기반이라 **부모 요소의 CSS `color`를 그대로 상속**한다 —
브랜드가 바뀌면 아이콘 색도 따라간다.

## 세트

| 세트 | 개수 | 출처 · 라이선스 | 용도 |
|------|------|-----------------|------|
| `lucide/` | 128 | [Lucide](https://lucide.dev) v0.544 · ISC | 제네릭 개념 (서버·DB·보안·사용자·흐름…) |
| `brands/` | 50 | [Simple Icons](https://simpleicons.org) v15.16 · CC0 | 기술 브랜드 로고 (Python·Docker·ClickHouse…) |

## 사용법

```html
<div class="dg-head">
  <span class="dg-ico">{{icon:lucide/database}}</span>
  <span class="dg-t">Oracle</span>
</div>
<span class="dg-ico">{{icon:brands/python}}</span>
```

- 탐색 순서: `brands/<브랜드>/assets/icons/` → `brands/_default/assets/icons/`
  (브랜드별 오버라이드 가능).
- 색 지정: 감싸는 요소에 `style="color:var(--c-accent)"` 등.
- 없는 이름을 쓰면 렌더에 빨간 `icon? <이름>` 표시가 나온다 — 오탈자 즉시 발견.

## 주의

- **Oracle / AWS / Azure / MS Windows 로고는 없음** — 상표권 문제로 Simple Icons에서
  제거됨. 제네릭(lucide/database, lucide/cloud 등)으로 대체할 것.
- 새 아이콘 추가: lucide-static / simple-icons npm 패키지에서 SVG를 복사.
  simple-icons는 루트 `<svg>`에 `fill="currentColor"`를 추가해서 넣는다
  (원본은 fill 미지정 → 검정 고정이 되므로).
- 아이콘 이름 규칙은 원본 패키지 그대로 (lucide: kebab-case, simple-icons:
  소문자 붙여쓰기 예: `nextdotjs`, `apachekafka`).

## 선정 기준 (2026-08)

- lucide: 아키텍처 다이어그램 빈출 개념 위주 128종 — 인프라(server/database/network),
  보안(shield/lock/fingerprint/funnel), AI(bot/brain-circuit/sparkles), 데이터·차트,
  흐름·상태, 디바이스, 비즈니스·산업 카테고리.
- brands: KORI 스택(clickhouse/elasticsearch/milvus/python/openjdk) + 주요
  인프라·AI·프레임워크·협업 도구.
