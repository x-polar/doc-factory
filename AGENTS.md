# AGENTS.md — Document Factory

이 저장소는 **비즈니스/기술 문서를 생성하는 작업 공간**입니다. 기본 산출물은
`.pptx`이며, 필요에 따라 `.pdf` 등으로 변환합니다. 모든 AI 에이전트(Claude,
그 외 협업 AI)는 작업 시작 전 이 문서를 먼저 읽고 규칙을 따릅니다.

> Claude Code 사용자는 로컬에 `CLAUDE.md` 파일(내용: `@AGENTS.md`)을 두어
> 이 문서로 자동 연결합니다. `CLAUDE.md`는 `.gitignore`에 포함되어 커밋되지
> 않습니다. 이 파일(`AGENTS.md`)이 모든 에이전트의 단일 기준 문서입니다.

---

## 1. 스킬 (Skills)

재사용 가능한 작업 절차는 `.ai/skills/<skill-name>/SKILL.md`에 정의되어 있습니다.
작업이 아래 스킬에 해당하면 **해당 `SKILL.md`를 먼저 열어 절차를 그대로 따르세요.**

| 스킬 | 위치 | 언제 사용 |
|------|------|-----------|
| `doc-scaffold` | `.ai/skills/doc-scaffold/SKILL.md` | 새 문서 작업 폴더(brief/research/…) 생성 |
| `pptx-builder` | `.ai/skills/pptx-builder/SKILL.md` | 슬라이드 덱(.pptx) 생성·수정 |
| `pdf-export` | `.ai/skills/pdf-export/SKILL.md` | pptx → pdf(또는 기타 포맷) 변환 |

> 새 스킬을 추가하면 위 표와 `.ai/skills/`에 함께 갱신하세요.

---

## 2. 문서 제작 워크플로 (핵심)

문서 1개는 **5단계 파이프라인**으로 만듭니다. 각 단계는 `docs/<문서폴더>/` 안의
산출물로 남고, 단계 사이에는 **검토 게이트**가 있습니다. 슬라이드를 다 만든 뒤
구조를 고치는 건 비쌉니다 — 앞 단계(텍스트)에서 잡으면 쌉니다.

| 단계 | 산출물 | 핵심 질문 |
|------|--------|-----------|
| 0. **brief** | `brief.md` | 누구에게, 무슨 결정을 위해, 어떤 제약으로? |
| 1. **research** | `research/` | 주장을 받칠 근거·출처는? |
| 2. **storyline** | `storyline.md` | 결론과 그 논리 구조는? (Pyramid) |
| 3. **storyboard** | `storyboard/NN-*.md` | 슬라이드별 메시지·레이아웃·자료는? |
| 4. **output** | `output/`(임시)→`release/`(확정) | 최종 .pptx / .pdf |

### 검토 게이트 (반드시 지킬 것)

- **brief → research:** brief의 대상·목적·핵심 질문이 확정되기 전엔 조사 시작 금지.
- **storyline → storyboard:** storyline(논리 구조)을 사용자가 승인하기 전엔
  슬라이드를 만들지 않습니다. "storyline까지 보고 OK → 그다음 생성."
- **storyboard → output:** 각 슬라이드 메시지·자료가 확정된 뒤에만 pptx 생성.

### 방법론 원칙

- **Pyramid Principle (Minto):** storyline은 결론(governing thought)을 맨 위에
  두고 MECE한 근거로 받칩니다.
- **Horizontal logic:** 슬라이드 **제목만 쭉 읽어도 하나의 이야기**가 되도록
  배열합니다(action title = 제목이 곧 메시지).
- **Vertical logic:** 한 슬라이드 안에서 본문·차트가 제목(주장)을 정확히 증명.
- **So-What test:** "그래서?"에 답 못 하는 슬라이드는 제거.
- **Traceability:** storyboard의 각 주장은 `research/sources.md`의 출처로
  역추적 가능해야 합니다.

### 스토리보드: 슬라이드별 1파일

storyboard는 **슬라이드 1장 = 파일 1개**(`storyboard/NN-slug.md`)로 분리합니다.
내용이 길어도 감당되고, diff가 국소적이며, 슬라이드 단위로 작업·재배열이 쉽습니다.

- **순서의 단일 기준은 파일명 숫자 접두**(`01-`, `02-`). frontmatter에 `n:`을 두지
  않습니다(중복·drift 방지). 중간 삽입 시 필요하면 리넘버링합니다.
- 파일 형식: YAML frontmatter(`title`/`layout`/`chart`/`source` 등) + Markdown
  본문(불릿) + `## notes`(스피커 노트). 긴 설명은 본문이 아니라 notes에.
- **수평 논리(줄거리)는 `storyline.md`가 spine으로 보유**합니다. 슬라이드 제목은
  storyline에서 승인된 action title을 그대로 따릅니다.
- 콘텐츠와 디자인 분리: `pptx-builder`가 이 파일들을 정렬해 읽어 덱을 생성합니다.

---

## 3. 출력 기본값

- 슬라이드 비율: **16:9** (와이드스크린)
- 문서 작업 폴더: `docs/YYYYMMDD_프로젝트명/` (`doc-scaffold`로 생성)
- 산출물 위치 (2단 분리):
  - `output/` — 작업 중 막 뽑는 **임시본**. git 추적 **제외**.
  - `release/` — **확정·공유용** 버전만 복사해 둠. git **추적**(`main`에 보존).
  - 즉 빌드는 `output/`에 하고, OK 난 버전만 `release/`로 올려 커밋한다.
- 파일 네이밍: `YYYYMMDD_프로젝트명_버전.pptx` (예: `20260629_proposal_v1.pptx`)
- pptx 생성 후 PDF가 필요하면 원본 pptx와 변환본을 **둘 다** 보존

## 4. 작성 원칙

- **한 슬라이드, 한 메시지.** 제목이 결론을 말하도록 작성(action title).
- 슬라이드 본문 텍스트는 과밀하지 않게. 상세 설명은 스피커 노트로.
- 표/차트/도형은 일관된 스타일 사용. 임의 색상·폰트 남용 금지.
- 한글·영문 혼용 시 폰트 깨짐에 유의(폰트 매핑은 스킬 문서 참고).
- 가능하면 처음부터 디자인하지 말고 **템플릿/마스터 슬라이드 위에 콘텐츠만** 채움.
- 상세 작성·디자인 표준은 `reference/style-guide.md`, 색·폰트 값은 **선택한 브랜드의**
  `theme.yaml`(`brands/<brand>/theme.yaml`), 공유 사실·메시지는 `knowledge/`를 따른다.

## 5. 도구 스택 · 공유 리소스

도구:
- `.pptx` 생성: **python-pptx** (공유 빌더 `src/lib/deckbuilder.py`가 storyboard +
  문서 `brief.md` frontmatter가 고른 브랜드 테마를 읽어 자동 생성)
- `.pptx → .pdf` 변환: **LibreOffice headless** (`libreoffice-impress` 필요)
- 차트: python-pptx 네이티브 차트(편집 가능) 또는 이미지 삽입
- 의존성은 `requirements.txt`로 관리

문서 횡단 공유 리소스(모든 문서가 참조):
- `brands/` — **브랜드 레지스트리**. 브랜드마다 1폴더(`theme.yaml`·`brand-guide.md`·
  `assets/`·`templates/`). 문서는 `brief.md` frontmatter의 `brand:`로 선택, `theme:`로 오버라이드.
  색·폰트의 **단일 진실원천**(브랜드별). 구조·해석 순서는 `brands/README.md`.
- `reference/` — 에이전트가 읽는 표준: `style-guide.md`, `layout-catalog.md`(★
  storyboard `layout:` 정의), `chart-style.md`, `examples/`(골드스탠다드).
- `knowledge/` — 여러 문서가 인용하는 사실·메시지(`company-facts.md`, `messaging.md`).
- `src/lib/` — 공유 빌더 코드.

## 6. 일관성 규칙 (파일 수정 후 교차 검증)

**파일을 수정하면, 그 변경에 연관된 파일들을 곧바로 교차 검증하고 필요 시 함께
고칩니다.** 한 곳만 바꾸고 끝내면 문서/설정이 서로 어긋납니다(drift). 커밋 전에
아래 연관 관계를 점검하세요.

| 무언가를 바꾸면 | 함께 확인/수정할 것 |
|----------------|----------------------|
| `docs/_template/` 구조 | `doc-scaffold` SKILL의 폴더 예시, AGENTS.md §8 폴더 구조 |
| `.ai/skills/` 추가·삭제·개명 | AGENTS.md §1 스킬 표, §8 폴더 구조 |
| 폴더 구조·산출물 규칙 | AGENTS.md(§2/§3/§8), 관련 SKILL, `.gitignore` |
| storyboard 파일 형식/필드 | `pptx-builder` SKILL 파싱 로직, `deckbuilder.py`, `_template` 예시 |
| `layout:` 값 추가/변경 | `reference/layout-catalog.md` ↔ `src/lib/deckbuilder.py`(렌더 함수) |
| 브랜드 `theme.yaml` 토큰 키 | `deckbuilder.py`가 참조하는 키, `reference/chart-style.md` |
| `brands/` 구조·새 브랜드 추가 | `brands/README.md`, `deckbuilder.py` 해석 로직, AGENTS.md §5/§8 |
| `brief.md` frontmatter(brand/theme/version) | `deckbuilder.py` 해석 로직, `_template/brief.md`, `doc-scaffold` SKILL |
| 새 의존성 사용(import) | `requirements.txt` |
| `storyline.md`의 제목(흐름) | `storyboard/NN-*.md`의 각 `title`(action title 일치) |
| storyboard의 `source:` ID | `research/sources.md`에 해당 ID가 실제 존재하는지 |
| storyboard의 `chart:`/`image:` 경로 | 해당 자료 파일이 `research/` 등에 실제 있는지 |
| `knowledge/`의 사실·메시지 | 이를 인용하는 문서들의 `research/`·storyboard |

원칙:
- **변경의 파급을 먼저 떠올리고**(누가 이 파일/규칙을 참조하는가?), 연관 파일을
  열어 일치시킨다. 모르면 검색해서 참조처를 찾는다.
- 표/구조를 바꾸면 그걸 **설명하는 문서(AGENTS.md·SKILL.md)도 같은 커밋에서** 갱신.
- 불일치를 발견했는데 고치기 애매하면 임의로 바꾸지 말고 사용자에게 알린다.

## 7. Git 워크플로

- 작업은 작업 브랜치에서 진행하고, **작업이 끝나면 `main`에 머지 후 푸시**합니다.
  문서 작업 단위마다 `main`이 항상 최신 결과를 담도록 유지합니다.
- 절차:
  1. 작업 단위를 의미 있는 메시지로 커밋
  2. `main`으로 전환 → 작업 브랜치를 머지(가능하면 fast-forward)
  3. `git push origin main`
  4. (선택) 작업 브랜치도 푸시해 이력 보존
- 충돌이 나면 자동 머지하지 말고 사용자에게 알린 뒤 해결합니다.
- 임시 산출물(`output/`)은 `.gitignore`로 제외됩니다. **확정본은 `release/`에**
  복사해 커밋하면 `main`에 보존됩니다.

## 8. 폴더 구조 (확정분)

```
doc-factory/
├── AGENTS.md            # 이 문서 — 모든 에이전트의 기준
├── CLAUDE.md            # (로컬 전용, gitignore) -> @AGENTS.md
├── requirements.txt     # python 의존성 (python-pptx, PyYAML)
├── .ai/
│   └── skills/          # 재사용 작업 절차 (doc-scaffold/pptx-builder/pdf-export)
├── brands/              # 브랜드 레지스트리 (브랜드마다 1폴더)
│   └── _default/        # 폴백 브랜드
│       ├── theme.yaml   #   디자인 토큰 (색·폰트·여백)
│       ├── brand-guide.md
│       ├── assets/      #   fonts / logos / icons
│       └── templates/   #   마스터 pptx (브랜드 확정 시)
├── reference/           # 표준·예시 (style-guide / layout-catalog / chart-style / examples)
├── knowledge/           # 공유 사실·메시지 (company-facts / messaging)
├── src/
│   └── lib/             # 공유 빌더 (deckbuilder.py)
└── docs/                # 문서별 작업 폴더 (문서 1개 = 폴더 1개)
    ├── _template/       # 새 문서 골격 (doc-scaffold가 복제)
    │   ├── brief.md     # frontmatter(brand·theme·version) + 본문(대상·목적…)
    │   ├── research/
    │   ├── storyline.md
    │   ├── storyboard/  # NN-slug.md (슬라이드 1장 = 파일 1개)
    │   ├── output/      # 임시 export (git 제외)
    │   └── release/     # 확정본 (git 추적)
    └── YYYYMMDD_프로젝트명/   # 실제 문서 작업 폴더
```

> 새 브랜드는 `brands/_default`를 복제해 값만 교체합니다(`brands/README.md`). 실제
> 마스터 pptx·폰트·로고는 브랜드 확정 시 각 `brands/<brand>/`에 채웁니다. 현재
> `_default` 테마는 중립 기본값이며, 빌더는 마스터가 없어도 토큰으로 덱을 생성합니다.
