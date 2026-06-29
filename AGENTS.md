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
| 3. **storyboard** | `storyboard/` | 슬라이드별 메시지·레이아웃·자료는? |
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

### 콘텐츠와 디자인 분리

storyboard는 구조화된 데이터(`storyboard/storyboard.yaml`)로 관리합니다. 같은
콘텐츠로 pptx·pdf 요약본 등을 뽑을 수 있고, 수정은 데이터 한 곳만 고칩니다.
`pptx-builder`는 이 파일을 읽어 덱을 생성합니다.

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

## 5. 도구 스택

- `.pptx` 생성: **python-pptx**
- `.pptx → .pdf` 변환: **LibreOffice headless** (`soffice --headless --convert-to pdf`)
- 차트: python-pptx 네이티브 차트(편집 가능) 또는 이미지 삽입
- 의존성은 `requirements.txt`로 관리

## 6. Git 워크플로

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

## 7. 폴더 구조 (확정분)

```
doc-factory/
├── AGENTS.md            # 이 문서 — 모든 에이전트의 기준
├── CLAUDE.md            # (로컬 전용, gitignore) -> @AGENTS.md
├── requirements.txt     # python 의존성 (python-pptx 등)
├── .ai/
│   └── skills/          # 재사용 작업 절차
│       ├── doc-scaffold/
│       ├── pptx-builder/
│       └── pdf-export/
└── docs/                # 문서별 작업 폴더 (문서 1개 = 폴더 1개)
    ├── _template/       # 새 문서 골격 (doc-scaffold가 복제)
    │   ├── brief.md
    │   ├── research/
    │   ├── storyline.md
    │   ├── storyboard/
    │   ├── output/      # 임시 export (git 제외)
    │   └── release/     # 확정본 (git 추적)
    └── YYYYMMDD_프로젝트명/   # 실제 문서 작업 폴더
```

> `templates/`(마스터 pptx), `assets/`(폰트·로고), `brand/`(색·폰트 토큰) 등은
> 브랜드 자산이 정해질 때 추가합니다. 추가 시 이 섹션을 갱신하세요.
