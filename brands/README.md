# brands/ — 브랜드 레지스트리

브랜드(클라이언트/제품/사내)마다 하위 폴더 1개. 각 문서는 `brief.md` frontmatter의
`brand:`로 어떤 브랜드를 쓸지 고른다. 색·폰트가 다른 문서를 한 공장에서 찍는 구조.

```
brands/
├── _default/                 # 폴백 브랜드 (brand 미지정/없을 때)
│   ├── theme.yaml            #   디자인 토큰 (색·폰트·여백) — 단일 진실원천
│   ├── brand-guide.md        #   로고·색 사용 규칙
│   ├── assets/{fonts,logos,icons}/
│   └── templates/            #   (선택) 마스터 pptx
└── <brand>/                  # 새 브랜드는 _default를 복제해 값만 교체
    └── ...
```

## 문서가 브랜드를 고르는 법 (`docs/<문서>/brief.md` frontmatter)

```yaml
---
brand: acme        # brands/acme 사용. 폴더가 없으면 _default로 폴백.
theme:             # (선택) 이 문서만의 토큰 오버라이드 → 브랜드 theme에 deep-merge
  colors:
    accent: "0F9D58"
---
```

## 테마 해석 순서 (구체적인 것이 우선)

1. `brands/<brand>/theme.yaml` (없으면 `brands/_default/theme.yaml`)
2. `brief.md` frontmatter의 `theme:` 블록을 deep-merge로 덮어씀

`src/lib/deckbuilder.py`가 이 순서로 테마를 합성한다. 자산(로고·폰트)은 선택된
브랜드의 `assets/`에서 찾는다.

## 새 브랜드 추가

```bash
cp -R brands/_default brands/<brand>
# 이후 theme.yaml 색·폰트, assets/logos, (선택) templates/ 마스터 교체
```
