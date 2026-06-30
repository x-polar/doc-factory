# KORI Answers — 아키텍처 · 데이터 거버넌스 (Architecture)

> 출처: Technical Details on Implementation 2026.03, KORI Answers Product
> Description 2025.11. 디자인 제외, 내용만 정리.

## 전체 설계
RAG 도구를 연결한 **AI Agent 기반** 시스템. 대화형 UI로 사내 정형/비정형 데이터를
안전·효율적으로 활용. 모든 사내 데이터는 **결정론적 보안 레이어**를 통해 접근하므로
보안 정책 위반 요청을 원천 차단.

처리 흐름(요약):
1. **User → Compliance Gateway Server (Java)** — 채팅 질의 + 권한 정보 수집(SSO 연동/권한관리).
2. **Agent/RAG Server (Python)** — Tool Call Plan 수립 → 검증 → 데이터 조회.
3. **Deterministic Security Layer** — LLM 입력 전 모든 데이터 권한 필터링.
4. **LLM(대형 언어모델)** — 필터링·병합된 Prompt+Context로 답변 생성(출처/인용 포함).
5. 긴 문서는 **SLM(소형 언어모델)**으로 요약/캐싱하여 응답 시간 단축(일배치).

## 데이터 거버넌스 (핵심)
LLM은 정형/비정형 데이터에 **직접 접근하지 않으며**, 모든 데이터는 사용자 세션을
통해 Agent가 전달. 사용자 권한 밖 데이터가 LLM에 노출되는 것을 결정론적으로 차단.

- **접근 제어** — 세션 Role/Level 기반. Document/Row/Column level 필터링. 사용자
  권한과 데이터 권한 간 정합성 보장.
- **결정론적 보안 레이어** — LLM 입력 이전 단계에서 모든 데이터 필터링, 비인가
  데이터는 Prompt에 **구조적으로 미포함**. Rule 기반 일관 결과, 랜덤 요소 없음.
- **감사·추적** — 요청/조회/필터링/응답 전 과정 기록, End-to-End 추적, 이상 응답
  원인 분석 가능.
- **운영·관리** — 데이터 카탈로그 기반 자산 관리, 중앙 Policy Engine으로 정책 일관성.

문서 권한 필터(User Role/Level) + DB 권한 필터(Row/Table/Column/Enum)를 거친
"AI/LLM Free Zone" 데이터만 LLM에 전달.

## 정형 데이터 기반 응답
- LLM은 **SQL을 직접 생성하지 않음**. 전문가가 작성·검증한 SQL이 **MCP Tool**로
  Agent에 제공. LLM 역할은 질의 이해 + **Tool 선택/Parameter 생성**으로 제한.
- **OLTP/OLAP 분리**: 단순 조회는 **Oracle**, 대용량 집계·분석은 **ClickHouse**.
  Oracle을 Source of Truth로 두고 Batch로 ClickHouse 동기화.
- 기준 정보(제품·응용처·거래선·영업그룹·해외법인 총괄 등)와 실적 Fact를 결합해
  의미 있는 분석 단위로 구조화. 자주 쓰는 조합은 사전 Join/View로 Query 복잡도 최소화.
- 기대효과: hallucination에 의한 잘못된 SQL 방지, Oracle 부하 최소화, 고속 분석.

## 비정형 데이터 기반 응답
- **Hybrid Retrieval**: 키워드 검색(**ElasticSearch**, 전체 문서 단위) + 벡터 검색
  (**Milvus**, 문서 Chunk 단위 + 메타데이터 필터링).
- 결과 통합: **Relevance 평가 → Filtering → Reranking**(Customized Pipeline).
- 신뢰성: 출처 기반 응답, Relevance 기반 Context 구성, 불필요 정보 제거로
  hallucination 최소화. 답변 문장에 **In-line 출처** 표기, **Post Validation Chain**.
- 적재 파이프라인: 텍스트는 Chunk 분할 후 Embedding → Milvus 인덱싱. 긴 문서(주간·
  임원 보고 등)는 적재 시 요약문 동반 생성. 도표·이미지는 텍스트 메타데이터화하여
  Chunk에 포함. 신규 데이터는 등록 시점 Queue 기반 비동기 변환.

## 기술 스택 (소개서 명시)
| 구분 | 사용 |
|------|------|
| Gateway | Java (Compliance Gateway Server) |
| Agent/RAG | Python (Agent/RAG Server) |
| 정형 DB | Oracle(OLTP, SoT) + ClickHouse(OLAP) |
| 키워드 검색 | ElasticSearch |
| 벡터 DB | Milvus (RAG Vector DB) |
| Tool 연동 | MCP (Model Context Protocol) 기반 Tool Calling |
| 모델 | LLM(대형) + SLM(요약/캐싱). 오픈소스 LLM 교체 가능 |
| 보안 | Deterministic Security Layer, SSO 연동, 온프레미스/폐쇄망 |
