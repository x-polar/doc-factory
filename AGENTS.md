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
| `pptx-builder` | `.ai/skills/pptx-builder/SKILL.md` | 슬라이드 덱(.pptx) 생성·수정 |
| `pdf-export` | `.ai/skills/pdf-export/SKILL.md` | pptx → pdf(또는 기타 포맷) 변환 |

> 새 스킬을 추가하면 위 표와 `.ai/skills/`에 함께 갱신하세요.

---

## 2. 출력 기본값

- 슬라이드 비율: **16:9** (와이드스크린)
- 산출물 위치: `output/` (git 추적 제외)
- 파일 네이밍: `YYYYMMDD_프로젝트명_버전.pptx` (예: `20260629_proposal_v1.pptx`)
- pptx 생성 후 PDF가 필요하면 원본 pptx와 변환본을 **둘 다** 보존

## 3. 작성 원칙

- **한 슬라이드, 한 메시지.** 제목이 결론을 말하도록 작성(action title).
- 슬라이드 본문 텍스트는 과밀하지 않게. 상세 설명은 스피커 노트로.
- 표/차트/도형은 일관된 스타일 사용. 임의 색상·폰트 남용 금지.
- 한글·영문 혼용 시 폰트 깨짐에 유의(폰트 매핑은 스킬 문서 참고).
- 가능하면 처음부터 디자인하지 말고 **템플릿/마스터 슬라이드 위에 콘텐츠만** 채움.

## 4. 도구 스택

- `.pptx` 생성: **python-pptx**
- `.pptx → .pdf` 변환: **LibreOffice headless** (`soffice --headless --convert-to pdf`)
- 차트: python-pptx 네이티브 차트(편집 가능) 또는 이미지 삽입
- 의존성은 `requirements.txt`로 관리

## 5. 폴더 구조 (확정분)

```
doc-factory/
├── AGENTS.md            # 이 문서 — 모든 에이전트의 기준
├── CLAUDE.md            # (로컬 전용, gitignore) -> @AGENTS.md
├── .ai/
│   └── skills/          # 재사용 작업 절차
│       ├── pptx-builder/
│       └── pdf-export/
└── output/              # 산출물 (git 추적 제외)
```

> `templates/`, `assets/`, `brand/`, `briefs/`, `src/` 등 나머지 폴더는
> 작업 흐름을 보며 점진적으로 추가합니다. 추가 시 이 섹션을 갱신하세요.
