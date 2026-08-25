# KORI Answers 아키텍처 — 구성 요소·관계 정의 v0.1

다이어그램 작도의 기준 문서. 본 버전(v0.1)은 G-레벨(큰 컴포넌트) 체계 확정본에서 새로 시작하는 리베이스 판이다 — 이전 v7.x 이력은 결정 이력(§4 D1~D38)으로만 보존한다.

컴포넌트는 **이름으로 참조**한다. 임의 부여 ID(구 C·R 번호)는 D26으로 폐기 — §4 결정 이력 안의 구 ID 표기는 당시 기록 그대로 동결한다. 그룹 키(G1~G6·X, T1~T3)는 유지한다.

## 0. 큰 컴포넌트 (G-레벨) — 히어로·슬라이드 구성의 기준

| ID | 이름 | 포함 | 정의 |
|---|---|---|---|
| G1 | Compliance Gateway | Compliance Gateway Server | 사용자 접점 — SSO·권한관리 사내 통합 |
| G2 | Agent Core | Agent Orchestrator, Tool Registry | 에이전트 루프 + 툴 카탈로그 |
| G3 | Inference Serving | Model Gateway, LLM, SLM | 추론 요청 단일 관문 + 모델 |
| G4 | Tool Layer | T1, T2, T3, Domain Dictionary | 툴 실행 (능력별 그룹) + 사전 참조 |
| G5 | Data Layer | Keyword/Vector Store, OLTP, OLAP, File Store | 저장소(메인 다이어그램 5노드) — 읽기: G4 · 쓰기: G6 |
| G6 | Ingestion | Ingestion Pipeline | 자료 등록·갱신 → G5 적재 |
| X | Deterministic Security | Deterministic Security Layer | cross-cutting — G1·G2·G4 관통 |

End User는 그룹 밖 액터. 히어로 흐름: End User → G1 → G2 ⇄ (G3 / G4) · G4 → G5 · G6 ⇢ G5 · X 관통.

## 1. 구성 요소

| 이름 | 그룹 | 유형 | 정의 |
|---|---|---|---|
| End User | 액터 | 액터 | 질문을 던지고 근거 있는 답변을 받는 최종 사용자 |
| External Interface | 액터 | 시스템 액터 | 자료 등록·갱신의 진입점 — 사내 문서 시스템 등 외부 소스가 Ingestion Pipeline(Conversion)으로 자료를 밀어넣는 인터페이스 |
| Compliance Gateway Server | G1 | 애플리케이션 | 사용자와 시스템 사이의 유일한 접점. 책임 4개: **Authentication**(SSO 연동 신원 부여) · **Authorization**(권한관리 사내 통합, UI 권한 반영) · **Audit**(요청·응답 감사 기록) · **Observability**(운영 관측). 참조 문서 다운로드는 플래닝 루프를 거치지 않고 온디맨드로 제공 |
| Agent Orchestrator | G2 | 애플리케이션 | 답변 생성의 지휘자. 책임 5개: **Planning & Re-planning**(플랜 수립·재수립) · **Tool Orchestration**(플랜 지정 툴 실행) · **Context Assembly**(툴 결과를 컨텍스트 슬롯으로 조립) · **Answer Synthesis**(근거 기반 답변 합성) · **Validation**(플랜·답변을 Deterministic Security Layer 기준으로 검증). 다이어그램은 리스트 표기 |
| Tool Registry | G2 | 레지스트리 | 사용 가능한 툴의 카탈로그. 툴의 등록·노출·발견을 담당하며, Agent Orchestrator가 플랜 수립 시 참조한다 |
| Model Gateway | G3 | 게이트웨이 | 모든 모델 호출이 지나는 단일 관문. LLM·SLM, 런타임·배치를 가리지 않고 라우팅·인증·로깅을 일원화한다. 호출 인터페이스는 OpenAI Compatible API. 구현(LiteLLM)은 로고 배지 |
| LLM | G3 | 모델 | 플랜 수립과 답변 생성을 담당하는 주력 모델. 온프렘 또는 외부 API — 배포 형태는 Model Gateway 라우팅으로 교체 가능 |
| SLM | G3 | 모델 | 문서 요약 전용 경량 모델. 온프렘 또는 외부 API — 배포 형태는 Model Gateway 라우팅으로 교체 가능 |
| Document Search | G4 (T1) | 툴 그룹 | 비정형 문서 검색 능력. 노출 툴은 `search.hybrid` / `search.lexical` / `search.semantic` 3종 — hybrid는 리트리버 팬아웃(Lexical·Semantic) 후 Fusion & Rank를 거쳐 Document Context를 만들고, 단독 툴은 후처리 없이 리트리버 결과를 그대로 반환한다 |
| Lexical Retriever | T1 | 리트리버 | 키워드/BM25 기반 검색 — Keyword Store를 조회한다 |
| Semantic Retriever | T1 | 리트리버 | 벡터 유사도 기반 검색 — Vector Store를 조회한다 |
| Fusion & Rank | T1 | 후처리 스테이지 | 두 리트리버 결과의 합류 지점. RRF로 융합·재랭킹해 최종 문서 순위를 만든다. `search.hybrid`에서만 경유하는 T1 내부 스테이지 (리트리버와 동급 아님) |
| Quantitative Query | G4 (T2) | 툴 그룹 | 정형 데이터 조회 능력. 노출 툴은 `query.quantitative` 1종 — 실행은 Quantitative Retriever가 담당 |
| Quantitative Retriever | T2 | 리트리버 | 정형 조회·집계 실행기. Structured Store의 OLTP·OLAP 양쪽에 SQL을 실행하며, 엔진 선택은 SQL 템플릿이, 권한은 principal 파라미터 바인딩이 담당한다 |
| Document Provider | G4 (T3) | 툴 그룹 | 원본 문서 제공 능력. 노출 툴은 `fetch.document` 1종 — 실행은 Document Fetcher가 담당. Compliance Gateway의 참조 문서 온디맨드 경로도 이 그룹을 호출한다 |
| Document Fetcher | T3 | 페처 | 원본 문서 반환기. Structured Store에서 파일 메타를 조회한 뒤 File Store에서 원본을 가져온다. SPI 식별자는 `DocumentProvider` |
| Structured Store | G5 | 데이터 저장소 | 정형 데이터의 논리적 단일 저장소. 물리 구현은 워크로드 기준 이원 — **OLTP**는 마스터 데이터·권한·파일 메타(문서 ID, 물리 경로, 버전, 소유자)·트랜잭션 정형을, **OLAP**은 대용량 조회·집계를 담당한다. 구체 제품은 로고 배지로만 병기 |
| Keyword Store | G5 | 데이터 저장소 | 키워드 색인 저장소. 문서별 요약 필드를 함께 보관해 검색 결과에 사전 요약을 동봉한다 |
| Vector Store | G5 | 데이터 저장소 | 청크 단위 벡터 색인 저장소 — 의미 기반 검색의 기반 |
| File Store | G5 | 데이터 저장소 | 원본 파일 저장소. 직접 접근은 없고 반드시 Structured Store의 파일 메타를 경유해서만 접근한다 |
| Domain Dictionary | G4 | 지원 컴포넌트 | 도메인 용어·동의어·엔티티의 단일 원천. 검색 품질의 도메인 적응 장치로, G4의 쿼리 전처리와 G6의 청킹/색인(Semantic Chunking)을 보조한다. 사전 데이터는 Structured Store(OLTP)에서 조회하며 고객사별 교체. 다이어그램에서는 Tool Layer 존 안에 배치 |
| Ingestion Pipeline | G6 | 파이프라인 | 자료 등록·갱신을 받아 G5의 저장소에 적재하는 준비 경로. 내부는 처리 단계 4개: Conversion → Semantic Chunking → Indexing → Summarization. 메인 다이어그램에서 존으로 표기 |
| Conversion | Ingestion Pipeline | 처리 단계 | 원본(PDF·Office 등) 파싱 — 텍스트·구조 추출, 메타 등록(OLTP)·원본 보존(File Store) |
| Semantic Chunking | Ingestion Pipeline | 처리 단계 | 의미 단위 분할. Domain Dictionary 참조로 도메인 용어 경계 보존 |
| Indexing | Ingestion Pipeline | 처리 단계 | 키워드 색인(Keyword Store)·벡터 색인(Vector Store) 구축 |
| Summarization | Ingestion Pipeline | 처리 단계 | 문서 요약 생성 — Model Gateway 경유 SLM 배치 호출, 요약을 Keyword Store 문서 필드에 적재. 내부 구현은 Queue + Worker(이벤트 구동, 갱신 시 기존 요약 삭제 후 재등록) |
| Deterministic Security Layer | X | cross-cutting | 결정론적 보안 규칙의 단일 원천(PDP). 모델의 확률적 출력과 무관하게 규칙으로 판정한다: ① 권한 판정 — ACL pre-filter·플랜 권한 범위·UI 권한 정보 ② 산출물 검증 — 플랜 유효성, 답변·인용의 컨텍스트 근거 확인 |

명명 규칙: 툴 그룹은 능력 기준(Document Search / Quantitative Query / Document Provider), 스토어는 데이터 형태 기준(Keyword/Vector/Structured/File), Structured Store 내부는 워크로드 기준(OLTP/OLAP). 구체 구현 기술·제품명은 다이어그램에서 로고 배지로만 병기. **다이어그램 레이블은 영어 전용** — 한글은 정의서·발표 노트에만.

### G4 노출 툴

| 툴 | 그룹 | 실행 | 융합 |
|---|---|---|---|
| `search.hybrid` | T1 | Lexical + Semantic 팬아웃 → 후처리 Fusion & Rank (RRF·랭킹) | O |
| `search.lexical` | T1 | Lexical Retriever 단독 — 후처리 미경유 | X |
| `search.semantic` | T1 | Semantic Retriever 단독 — 후처리 미경유 | X |
| `query.quantitative` | T2 | Quantitative Retriever 단독 (OLTP·OLAP 라우팅) | X — 별도 슬롯 |
| `fetch.document` | T3 | Document Fetcher | — |

## 2. 관계

### 사용자 경로
| 방향 | 레이블 |
|---|---|
| End User → Compliance Gateway | Chat Query |
| Compliance Gateway → End User | Chat Response + Reference Links |
| Compliance Gateway → Agent Orchestrator | Chat Query + Principal |
| Agent Orchestrator → Compliance Gateway | Chat Response |
| Compliance Gateway → T3 Document Provider | `fetch.document` — 참조 문서 다운로드 온디맨드. 플래닝 루프 미경유 |

### 모델 경로
| 방향 | 레이블 |
|---|---|
| Agent Orchestrator ↔ Model Gateway | **OpenAI Compatible API** — 단일 양방향 연결. 요청: Planning Prompt / Answer Prompt. 응답: Proposed Tool Call Plan / Draft Answer + Citations (Orchestrator가 Deterministic Security 기준으로 검증해 Validated로 확정) |
| Model Gateway ↔ LLM | 프롬프트/응답 |
| Model Gateway ↔ SLM | 요약 요청/응답 — 호출자는 Agent Orchestrator(캐시 미스 폴백, 점선)와 Summarization 단계(배치) |

### 툴 경로
| 방향 | 레이블 |
|---|---|
| Agent Orchestrator → G4 | Tool Invocation — 플랜 지정 툴 + principal |
| G4 → Agent Orchestrator | Grounding Context — ① Document Context (융합·랭킹 문서 + 요약 필드) ② Structured Data (+ 쿼리 ID·대상 테이블 메타 = 답변 출처). 답변 합성 프롬프트의 정해진 슬롯에 구조화 주입되어 인용 검증의 단위가 된다 |
| Agent Orchestrator ↔ Tool Registry | Tool Discovery — 플랜 수립 시 툴 카탈로그 참조 (G2 내부, 다이어그램 표기는 드릴다운만) |
| Lexical Retriever ↔ Keyword Store | Keyword Query / Ranked Documents |
| Semantic Retriever ↔ Vector Store | Vector Query / Relevant Chunks |
| Quantitative Retriever ↔ Structured Store | Parameterized SQL (principal 바인딩) — OLTP·OLAP 양쪽 / Query Result Data |
| Document Fetcher → Structured Store | File Meta Query — **다이어그램 미표기** (T3 내부 구현) |
| Document Fetcher → File Store | File Fetch |

### 보안 (X — cross-cutting)
| 방향 | 레이블 |
|---|---|
| Deterministic Security Layer → Compliance Gateway | User Permission Info — UI 표시용 (접근 가능 메뉴·문서) |
| Deterministic Security Layer ⇢ Agent Orchestrator | 플랜·답변 검증 기준 |
| Deterministic Security Layer ⇢ G4 | ACL pre-filter 기준 — Keyword Store 필터 절 / Vector Store 메타데이터 필터 / SQL 파라미터 |

### 적재·동기화 (G6·G5)
| 방향 | 레이블 |
|---|---|
| External Interface → Ingestion Pipeline (Conversion) | 자료 등록·갱신 유입 |
| Ingestion Pipeline ⇢ Data Layer | Load (점선·민트) — 종단은 개별 스토어가 아닌 Data Stores 존 경계. 실제 적재 대상은 Structured·Keyword·Vector·File Store 전체 |
| Domain Dictionary → Structured Store (OLTP) | Dictionary Lookup — 사전 데이터 조회 |
| Domain Dictionary ⇢ G4·Ingestion Pipeline | Domain Term Reference — 쿼리 전처리(G4)·청킹/색인 보조(G6 Semantic Chunking). 참조 관계 |
| Structured Store 내부 OLTP → OLAP | 정형 데이터 동기화 (CDC/배치) — **다이어그램 미표기** (Structured Store 내부 구현, File Meta Query와 동일 원칙) |

Ingestion Pipeline 내부 흐름(별도 장): 자료 등록/갱신 → Conversion(메타 OLTP·원본 File Store) → Semantic Chunking(Domain Dictionary 참조) → Indexing(Keyword·Vector Store) → Summarization(Queue enqueue → Worker → Model Gateway → SLM → 요약을 Keyword Store 문서 필드에 기록, 갱신 시 기존 요약 삭제 후 재등록).

## 3. 다이어그램 표기 지침

- **레이블 언어**: 다이어그램 내 모든 레이블·주석은 **영어 전용**. 한글 설명은 슬라이드 본문·스피커 노트에만
- **히어로 슬라이드**: G-레벨 큰 컴포넌트(G1~G6 + X)만으로 전체 흐름이 읽히는 레이블 있는 흐름도. 박스 6개 + cross-cutting 밴드 1개. 스타일은 임팩트 우선(아이소 허용)
- **드릴다운 슬라이드**: 큰 컴포넌트 1개씩 확대 — 플랫 다크(존 그룹핑 + 글래스 카드) 문법, 관계 레이블 전부 표기
- **아이콘 시스템**: 형태 = 유형, 글리프 = 개체. 토큰은 `kori-icon-style-tokens.html` 단일 소스
- **저장소·게이트웨이 레이블**: 역할명 주 레이블 + 구체 기술 로고는 전면 하단 고정 배지. Structured Store는 OLTP/OLAP 2배지
- **교체 가능(swappable) 배지**: LLM·SLM·Structured/Keyword/Vector/File Store·Model Gateway·Domain Dictionary — ⇄ 마커 + 하단 한 줄 범례
- **X(Deterministic Security Layer)**: G1·G2·G4를 관통하는 밴드(배경 레이어). 화살표 노드로 그리지 않음
- **G6(Ingestion Pipeline)**: 메인/히어로에서 단일 박스 + G5로 점선. 상세는 별도 장
- **주석**: "온프렘/외부 API 선택 배포 (Model Gateway 라우팅)" · "등록 시 사전 요약·캐싱으로 응답 시간 단축" → 영어로 표기 (예: "On-prem / External API — routed via Model Gateway", "Pre-summarized at ingestion for fast response")
- **유지 주석**(영어 변환): SSO·권한 사내 통합 / 정형·비정형 통합 답변 / 답변 출처·기반 문서 제시

## 4. 확정 결정 이력

| # | 결정 |
|---|---|
| D1 | 검색 계층 명칭 Retrieval Layer, 하위 Lexical/Semantic/Quantitative *(D21로 개정)* |
| D2 | Quantitative 결과는 융합하지 않고 별도 컨텍스트 슬롯 |
| D3 | 리트리버 선택은 Tool Call Plan이 지정 (툴 노출) + `search.hybrid` 추가 |
| D4 | 권한은 cross-cutting Authorization Layer로 분리, pre-filter(쿼리 시점) 적용 |
| D5 | 요약은 등록 이벤트 Queue 구동, Keyword Store 문서 필드 적재, 런타임 폴백 유지 |
| D6 | C4는 C3 내부 모듈화, C3 = Agent Orchestrator |
| D7 | 모델 호출은 Model Gateway 단일 관문 |
| D8 | Ingestion Pipeline은 별도 다이어그램, 요약 큐는 그 하위로 흡수 |
| D9 | 참조 문서는 C2 → T3 `fetch.document` 직접 호출 |
| D10 | Quantitative 권한 주입은 SQL 템플릿 파라미터 바인딩 |
| D11 | Structured Data에 쿼리 ID·대상 테이블 메타 동봉해 출처 노출 |
| D12 | 저장소는 역할명(*Store 패밀리)으로 명명, 구체 기술은 로고 병기 |
| D13 | KORI Answers는 제품 전체 이름 — 컴포넌트 레벨에 KORI 표기 없음 |
| D14 | R15는 다이어그램 미표기 — 메인 다이어그램 선 교차 0 지향 |
| D15 | 시각화 이원화 및 아이콘 스타일 토큰 시스템 채택 *(D24로 개정)* |
| D16 | C3.1을 C14에 병합, C14 = Deterministic Security Layer — 권한 판정 + 산출물 검증 |
| D17 | 마스킹/DLP는 설계 범위 전체에서 제외 — C16은 라우팅·인증·로깅 전담 |
| D18 | C9는 논리적 단일 Structured Store, 물리 이원 **OLTP + OLAP** (워크로드 기준 명명, 제품명은 로고 배지만). C7.3은 양쪽 모두 실행, 엔진 라우팅은 SQL 템플릿이 담당 |
| D19 | C17 Domain Dictionary 신설 — G4·G6에 참조 제공(R21, 점선). 고객사별 교체 |
| D20 | 교체 가능 컴포넌트(C5·C6·C9·C10·C11·C12·C16·C17)는 ⇄ 배지 + 하단 범례 |
| D21 | G-레벨 큰 컴포넌트 도입(G1~G6+X). C7 계층 소멸 → T1 Document Search(리트리버 C7.1·C7.2 + 후처리 C7.4) / T2 Quantitative Query(C7.3) / T3 Document Provider(C7.5) 능력별 툴 그룹으로 재편 |
| D22 | C18 Tool Registry 신설, G2(Agent Core) 소속 — 툴 카탈로그는 플래너의 참조원. G4는 실행 전담 |
| D23 | G3 = Inference Serving, G5 = Data Layer로 명명. OLTP→OLAP 동기화는 R22로 정의하되 다이어그램 미표기 |
| D24 | 히어로 = G-레벨 레이블 흐름도(추상 3D 폐기), 드릴다운 = 플랫 다크. 다이어그램 레이블은 영어 전용 |
| D25 | C7.4 Fusion & Rank는 리트리버와 동급이 아니라 T1 내부 후처리 스테이지 — 다이어그램에서 리트리버 병렬 아래 합류 지점으로 표기 |
| D26 | 임의 부여 ID(C·R 번호) 폐기 — 컴포넌트·관계는 이름으로 참조. 그룹 키(G1~G6·X, T1~T3)는 유지. 설명문에서 구현 언어(Java·Python) 표기 삭제. §4 이력의 구 ID는 기록 그대로 동결 |
| D27 | Agent Orchestrator ↔ Model Gateway는 단일 양방향 연결로 표기, 레이블은 **OpenAI Compatible API** — 요청/응답 상세는 정의서에만 |
| D28 | Ingestion Pipeline 내부를 처리 단계 4개로 재정의: Conversion → Semantic Chunking → Indexing → Summarization *(명명은 D30으로 공정 명사 통일)*. Queue·Worker는 Summarization 내부 구현으로 흡수(D8 취지 유지). 메인 다이어그램에서 존+4노드 표기 |
| D29 | 메인 다이어그램 확정 사항 일괄 반영 — Compliance Gateway 책임 4종(Authn·Authz·Audit·Observability)·Agent Orchestrator 책임 5종(Planning & Re-planning·Tool Orchestration·Context Assembly·Answer Synthesis·Validation) 리스트 표기 / Structured Store를 메인에서 OLTP·OLAP 2노드로 분리 표기 / Domain Dictionary는 G4(Tool Layer) 소속·OLTP 조회·실선 / External Interface 액터 신설(적재 진입점, End User와 동레벨) / Load는 Data Stores 존 경계 종단·민트 화살표 / 호출 순서 번호·관계선 상세 라벨·범례 제거(상세는 드릴다운) |
| D30 | Ingestion 단계명 공정 명사로 통일 — Converter를 **Conversion**으로 개명 (Conversion·Chunking·Indexing·Summarization) |
| D31 | 툴 결과 반환 레이블을 **Grounding Context**로 개명(구 Context Slots) — 고객 문서 가독성. 슬롯 구조 의미는 관계 설명에 유지 |
| D32 | 메인 다이어그램 Tool Layer 표기 순서 = Document Search → Domain Dictionary → Quantitative Query → Document Provider (스토어 타깃 순서와 일치시켜 관계선 교차 제거). MG↔Orchestrator 선은 민트(런타임 경로 일관) |
| D33 | Agent Loop 드릴다운(2장): Tool Layer·Model Gateway는 AO 존 밖 고스트 — Model Gateway 호출선은 AO 존 경계에서 출발(특정 단계 아닌 오케스트레이터 레벨 호출, 거의 모든 단계가 모델을 호출하므로). 성공 경로 'Verified answer' 라벨을 AO→CG 리턴선에 표기, 실패 경로 'Re-planning on failure'와 대구 |
| D34 | Agent Loop 구성: End User·Compliance Gateway는 AO 존 좌측(수평 왕복: Principal-bound request→ / ←Verified answer), Tool Layer·Model Gateway는 상단 고스트. AO 존 내 루프 5칩에 ①~⑤ 뱃지(⑤만 앰버)+영문 캡션 1줄, CG는 책임 4종 리스트(Authn·Authz·Audit·Observability). Deterministic Security 밴드 미표시(3장 소재) — Validation 앰버 테두리·뱃지로만 암시. Tool Layer↕Tool Orchestration 무향, MG 호출선은 AO 존 경계 출발 |
| D35 | Ingestion 진입 액터 2종: External Interface(배치 동기화) 외에 End User 직접 업로드 경로 추가 — 두 액터가 Conversion으로 합류. 4장 드릴다운에서 Queue·Worker(D5·D28 Summarization 내부 구현) 명시 표기, 스토어 배열은 적재 순서(OLTP·File·Vector·Keyword·OLAP), OLAP는 무연결(적재 대상 아님) |
| D36 | Ingestion 단계 5개로 재정의: Registration(원본 File Store·메타 OLTP 선 적재) → Conversion(파싱·추출) → Semantic Chunking → Indexing → Summarization. 원본 보존이 파싱보다 선행 — 인풋 수신 즉시 저장 후 가공. Conversion의 적재 역할은 Registration으로 이관 |
| D37 | 5단계를 Summarization & Classification으로 확장: 등록 시점 SLM 배치가 요약과 자동 분류(문서 유형·주제 태그)를 함께 생성, 분류 태그는 Keyword Store 메타데이터로 적재(패싯·필터 검색 및 권한 정책 매핑 기반). Queue·Worker는 두 배치 작업의 공용 인프라 |
| D38 | External Interface의 정형 데이터 직접 적재 경로 추가: 문서형 자료는 Ingestion Pipeline(Registration)으로, 정형 데이터(DB 동기화 등)는 파이프라인을 거치지 않고 OLTP·OLAP에 직접 적재 |
