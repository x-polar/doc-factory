---
name: doc-scaffold
description: >
  새 문서 작업 폴더를 표준 골격(brief/research/storyline/storyboard/output)으로
  생성합니다. 사용자가 새 문서·덱·제안서·보고서 작업을 시작할 때 가장 먼저
  사용합니다.
---

# doc-scaffold

`docs/_template/`을 복제해 새 문서 작업 폴더 `docs/YYYYMMDD_<slug>/`를 만듭니다.
이후 작업은 AGENTS.md §2의 5단계 파이프라인(brief → research → storyline →
storyboard → output)을 따릅니다.

## 사용

```bash
# 오늘 날짜로 생성
.ai/skills/doc-scaffold/new.sh proposal

# 날짜를 직접 지정
.ai/skills/doc-scaffold/new.sh proposal 20260629
```

생성 결과:

```
docs/20260629_proposal/
├── brief.md
├── research/sources.md
├── storyline.md
├── storyboard/storyboard.yaml
├── output/    # 임시 export (git 제외)
└── release/   # 확정본 (git 추적)
```

## 생성 후 절차

1. **brief.md 먼저 채운다** — 대상·목적·핵심 질문·제약. (게이트: 확정 전 조사 금지)
2. `research/`에 근거·출처 수집, `sources.md`에 정리.
3. `storyline.md`로 논리 구조 작성 → **사용자 승인**.
4. `storyboard/storyboard.yaml`에 슬라이드별 스펙 작성.
5. `pptx-builder` 스킬로 `output/`에 .pptx 생성, 필요 시 `pdf-export`로 변환.
6. 확정되면 해당 버전을 `release/`로 복사해 커밋(`output/`은 git 제외).

## 주의

- `slug`는 영문·숫자·하이픈 권장(폴더명/파일명에 사용).
- 같은 이름 폴더가 이미 있으면 덮어쓰지 않고 중단합니다.
