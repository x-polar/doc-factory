# icons/ — 다이어그램용 SVG 아이콘 자산 (20,264종)

`layout: diagram` fragment에서 `{{icon:<경로>}}` 로 인라인 삽입된다
(render.py `inline_icons()`가 치환). 전부 벡터(SVG)라 해상도 무손실이고,
`currentColor` 기반이라 **부모 요소의 CSS `color`를 그대로 상속**한다 —
브랜드가 바뀌면 아이콘 색도 따라간다.

## 세트

| 경로 | 개수 | 출처 · 라이선스 | 스타일 | 용도 |
|------|------|-----------------|--------|------|
| `lucide/<name>` | 1,865 | [Lucide](https://lucide.dev) v0.544 · ISC | 스트로크 2px, 둥근 캡 | 기본값. 제네릭 개념 |
| `tabler/<name>` | 4,964 | [Tabler](https://tabler.io/icons) v3.35 · MIT | 스트로크 2px | 최대 커버리지 (lucide에 없을 때) |
| `tabler-filled/<name>` | 999 | Tabler filled 변형 · MIT | 면 채움 | 강조·상태 표시 |
| `phosphor/<weight>/<name>` | 9,072 | [Phosphor](https://phosphoricons.com) v2.1 · MIT | thin/light/regular/bold/fill/duotone 6두께 | 두께 위계 표현 |
| `brands/<name>` | 3,364 | [Simple Icons](https://simpleicons.org) v15.16 · CC0 | 모노크롬 로고 | 기술 브랜드 |

## 사용법

```html
<span class="dg-ico">{{icon:lucide/database}}</span>
<span class="dg-ico">{{icon:tabler/topology-star-ring-3}}</span>
<span class="dg-ico">{{icon:phosphor/duotone/shield-check}}</span>
<span class="dg-ico">{{icon:brands/clickhouse}}</span>
```

- 탐색 순서: `brands/<브랜드>/assets/icons/` → `brands/_default/assets/icons/`
  (브랜드별 오버라이드 가능).
- 색 지정: 감싸는 요소에 `style="color:var(--c-accent)"` 등.
- 없는 이름을 쓰면 렌더에 빨간 `icon? <이름>` 표시 — 오탈자 즉시 발견.
- **이름 검색**: `ls brands/_default/assets/icons/tabler | grep -i network` 처럼
  파일명 grep이 가장 빠르다. 세트별 이름 규칙: lucide/tabler/phosphor는
  kebab-case, brands는 소문자 붙여쓰기(`nextdotjs`, `apachekafka`).

## 한 다이어그램 안에서의 일관성 규칙

- **스트로크 계열(lucide/tabler)과 phosphor를 한 다이어그램에 섞지 않는다**
  (시각 문법이 달라 어색해짐). 기본은 lucide, 부족하면 tabler로 보충
  (둘은 스타일이 거의 같아 혼용 OK). phosphor는 두께 위계가 필요한
  다이어그램에서 단독 사용.
- duotone은 phosphor 전용 — 보조 면이 opacity 0.2로 깔린다.

## 주의

- **Oracle / AWS / Azure / MS Windows 로고는 없음** — 상표권 문제로 Simple Icons에서
  제거됨. 제네릭(lucide/database, lucide/cloud 등)으로 대체할 것.
- simple-icons 원본은 fill 미지정(검정 고정)이라 루트 `<svg>`에
  `fill="currentColor"`를 주입해 두었다. 새로 추가할 때도 동일 처리.
- phosphor 원본 파일명의 `-<weight>` 접미는 제거하고 폴더로 구분했다
  (`regular/database.svg`, 원본은 `database.svg`+`bold/database-bold.svg`).
