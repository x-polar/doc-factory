# Storyline — KORI Answers 아키텍처

> 2단계. 결론과 그 논리 구조(Pyramid Principle). **v0.2 — 메인 다이어그램을 1장(히어로)으로 승격, D28~D32 반영.**

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

## Horizontal logic (슬라이드 배열 — 8장)

| # | slug | action title | 시각 자료 |
|---|---|---|---|
| 1 | 01-hero | KORI Answers — 구조가 보장하는 엔터프라이즈 AI 답변 | **플랫 메인 다이어그램** (확정본 — 존 4 + Deterministic Security 밴드 + End User·External Interface) |
| 2 | 02-gateway-agent | 질문은 게이트웨이에서 신원을 얻고, 에이전트 루프가 답을 만든다 | G1+G2 드릴다운 — CG 책임 4종(Authn·Authz·Audit·Observability) · AO 책임 5종(Planning & Re-planning → Tool Orchestration → Context Assembly → Answer Synthesis → Validation) · Grounding Context 슬롯 구조 |
| 3 | 03-security | 환각이 보안을 뚫지 못한다 — 결정론적 보안 레이어 | X 드릴다운 — 권한 판정 + 산출물 검증 (UI 권한 · 플랜 검증 · ACL pre-filter · 인용의 슬롯 단위 검증) |
| 4 | 04-tools | 플랜이 지정한 능력만 실행된다 — 능력별 툴 계층 | G4 드릴다운 — Document Search · Domain Dictionary(OLTP 사전 조회) · Quantitative Query · Document Provider, RRF 융합, Grounding Context 2종 |
| 5 | 05-data | 데이터는 형태별 저장소에, 접근은 권한 필터를 통과한 쿼리만 | G5 드릴다운 — Keyword·Vector Store + OLTP·OLAP + File Store 5노드, 읽기(G4)/쓰기(G6) 경로 분리 |
| 6 | 06-inference | 모델은 교체 가능한 부품 — 단일 추론 관문이 라우팅한다 | G3 드릴다운 — Model Gateway(Routing·Logging) + LLM/SLM, OpenAI Compatible API, 모델 교체 경로 |
| 7 | 07-ingestion | 응답 속도는 등록 시점에 결정된다 — 적재 파이프라인 4단계 | G6 드릴다운 — External Interface 유입 → Conversion(File Store 원본·OLTP 메타) → Semantic Chunking(DD 참조) → Indexing(Keyword·Vector) → Summarization(SLM 배치 → Keyword Store 요약 필드) |
| 8 | 08-closing | 구조가 신뢰를 만든다 — 세 기둥 요약 | 요약 (보안 · 툴 · 추론 관문) |

## So-What 점검
- 각 장이 "그래서 안전한가/정확한가/운영 가능한가"의 답 하나씩 담당.
- 2~7장은 1장(히어로 = 메인 다이어그램)의 영역을 순서대로 확대 — 수평 논리 일관.
  드릴다운 순서 = 메인의 시선 흐름(좌→우→하단): G1+G2(2) → X(3) → G4(4) →
  G5(5) → G3(6) → G6(7).
- 순서 논리: 사용자 진입(2) → 신뢰의 근거(3) → 실행(4) → 데이터(5) →
  모델(6) → 준비(7) → 회수(8).

## v0.1 → v0.2 변경 기록
- 1장: G-레벨 흐름도(구 히어로) → **확정 플랫 메인 다이어그램으로 교체**.
  구 히어로(iso/flat)는 storyboard 01·01b로 보존하되 덱에서 제외.
- 2장: CG·AO 리스트 책임 반영(D29), Context Slots → Grounding Context(D31).
- 4장: 툴 4종 표기·순서 갱신(D29·D32), Domain Dictionary G4 소속.
- 5장: Domain Dictionary 제외(G4로 이동), OLTP/OLAP 분리 5노드(D29).
- 7장: Queue→Worker 표기 폐기 — Conversion→Chunking→Indexing→Summarization
  4단계(D28·D30), External Interface 액터(D29).
