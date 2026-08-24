# Storyline — KORI Answers 아키텍처

> 2단계. 결론과 그 논리 구조(Pyramid Principle). **v0.3 — 4장 압축 구성(아키텍처 / 에이전트 루프 / Retrieval / Ingestion).**

## Governing thought (한 줄 결론)
> KORI Answers는 보안·정합성·응답 품질을 사람의 운영이 아니라 **아키텍처
> 구조로 보장**한다 — 결정론적 보안 레이어, 능력별 툴 계층, 단일 추론 관문이
> 그 세 기둥이다.

## 구성 원칙 (v0.2)
- **1장(히어로) = 확정된 플랫 메인 다이어그램**: 전 컴포넌트 개요(존 4개 +
  앰버 밴드 + 액터 2종). 다크가 마스터, 라이트는 파생본(인쇄·제안서용).
- **이후 = 영역 1개씩 드릴다운**: 같은 플랫 스타일·같은 팔레트. 메인에서
  생략한 관계 레이블·내부 배선을 드릴다운에서 전부 표기.
- **다이어그램 레이블은 영어 전용** — 한글은 본문·노트에만 (D24).
- **표기 표준은 `reference/diagram-rules.md`** — 무향 데이터 접근선, 트렁크
  존 경계 종단, 교차 0, 리스트형 노드 설명 등.

## Horizontal logic (슬라이드 배열 — 4장)

| # | slug | action title | 시각 자료 |
|---|---|---|---|
| 1 | 01-hero | KORI Answers Architecture | **플랫 메인 다이어그램** (확정본 — 존 4 + Deterministic Security 밴드 + 액터 2종) |
| 2 | 02-agent-loop | Agent Loop *(lede: 신원 없이 실행되지 않고, 검증 없이 답하지 않는다)* | Agent Loop 다이어그램 — CG(Authn·Authz·Audit·Observability) → AO 루프 5단계(Planning & Re-planning → Tool Orchestration → Context Assembly → Answer Synthesis → Validation) + Deterministic Security 검증 접점 |
| 3 | 03-retrieval | Retrieval Workflow *(lede: 모든 답의 근거는 권한 필터를 통과한 데이터에서만 나온다)* | Retrieval 다이어그램 — 툴 4종(Document Search·Domain Dictionary·Quantitative Query·Document Provider) → 스토어 5종, RRF 융합, ACL pre-filter, Grounding Context 슬롯 조립 |
| 4 | 04-ingestion | Ingestion Pipeline *(lede: 응답 속도는 등록 시점에 결정된다)* | Ingestion 다이어그램 — External Interface → Conversion(File Store·OLTP) → Semantic Chunking(DD 참조) → Indexing(Keyword·Vector) → Summarization(SLM 배치 → Keyword Store) |

## 제목 정책 (v0.3)
- 슬라이드 제목 = **간결한 명사형** (Agent Loop / Retrieval Workflow / Ingestion Pipeline).
- 전달 메시지는 **lede(리드 문장)**로 제목 아래 배치 — storyboard frontmatter `lede:` 사용.

## So-What 점검
- 1장: 전체 구조 한 장 — "구조가 보장한다"는 결론의 시각적 증거.
- 2장: 런타임 질의 경로 — 신원·검증(보안 스토리 흡수). "그래서 안전한가."
- 3장: 검색·근거 — 능력 제한 + 권한 필터 + 슬롯 근거(툴·데이터 스토리 통합). "그래서 정확한가."
- 4장: 사전 준비 — 적재 4단계와 사전 요약. "그래서 빠른가."
- 모델(G3)은 별도 장 없이 1장 Model Zone + 2장 모델 호출 접점으로 표현.

## v0.2 → v0.3 변경 기록
- 8장 → **4장 압축**: 구 2(G1+G2)·3(X) → 2장 Agent Loop로 통합 /
  구 4(G4)·5(G5) → 3장 Retrieval로 통합 / 구 6(G3)·8(요약) 삭제(1·2장에 흡수) /
  구 7(G6) → 4장 Ingestion.
- 라이트 변형(01b)은 부속 유지.

## v0.1 → v0.2 변경 기록
- 1장: G-레벨 흐름도(구 히어로) → **확정 플랫 메인 다이어그램으로 교체**.
  구 히어로(iso/flat)는 storyboard 01·01b로 보존하되 덱에서 제외.
- 2장: CG·AO 리스트 책임 반영(D29), Context Slots → Grounding Context(D31).
- 4장: 툴 4종 표기·순서 갱신(D29·D32), Domain Dictionary G4 소속.
- 5장: Domain Dictionary 제외(G4로 이동), OLTP/OLAP 분리 5노드(D29).
- 7장: Queue→Worker 표기 폐기 — Conversion→Chunking→Indexing→Summarization
  4단계(D28·D30), External Interface 액터(D29).
