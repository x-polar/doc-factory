# KORI Answers 아키텍처 — 구성 요소·관계 정의 v7.8

다이어그램 작도의 기준 문서. v7.2: KORI Answers는 제품 전체 이름으로 확정. v7.3: R15는 다이어그램 미표기. v7.4: 시각화 이원화 및 아이콘 스타일 토큰 시스템 추가. v7.5: C3.1을 C14에 병합, C14를 Deterministic Security Layer로 개명. v7.6: 마스킹/DLP를 설계 범위에서 제외. v7.7: C9 이원 구현 명시, C17 Domain Dictionary 신설(R21), swappable 배지 도입. **v7.8: G-레벨(큰 컴포넌트) 도입, C18 Tool Registry 신설(G2), C7 계층 소멸 → T1~T3 능력별 툴 그룹, G3=Inference Serving, G5=Data Layer, C9=OLTP/OLAP(제품명은 로고 배지만), C7.3 이중 타겟, R22 동기화 신설, 히어로=레이블 있는 G-레벨 흐름도, 다이어그램 레이블 영어 전용.**

## 0. 큰 컴포넌트 (G-레벨) — 히어로·슬라이드 구성의 기준

| ID | 이름 | 포함 | 정의 |
|---|---|---|---|
| G1 | Service Gateway | C2 | 사용자 접점 — SSO·권한관리 사내 통합 |
| G2 | Agent Core | C3, C18 | 에이전트 루프 + 툴 카탈로그 |
| G3 | Inference Serving | C16, C5, C6 | 추론 요청 단일 관문 + 모델 |
| G4 | Tool Layer | T1, T2, T3 | 툴 실행 (능력별 그룹) |
| G5 | Data Layer | C9, C10, C11, C12, C17 | 저장소 — 읽기: G4 · 쓰기: G6 |
| G6 | Ingestion | C15 | 자료 등록·갱신 → G5 적재 |
| X | Deterministic Security | C14 | cross-cutting — G1·G2·G4 관통 |

C1(End User)은 그룹 밖 액터. 히어로 흐름: End User → G1 → G2 ⇄ (G3 / G4) · G4 → G5 · G6 ⇢ G5 · X 관통.

## 1. 구성 요소

| ID | 이름 | 그룹 | 유형 | 정의 |
|---|---|---|---|---|
| C1 | End User | 액터 | 액터 | 최종 사용자 |
| C2 | Compliance Gateway Server | G1 | 애플리케이션 (Java) | SSO 연동·권한관리 등 사내 시스템 통합. 참조 문서 온디맨드 제공(플래닝 루프 미경유). UI 권한 표시 |
| C3 | Agent Orchestrator | G2 | 애플리케이션 (Python) | 플랜 수립 → 툴 실행 → 답변 합성의 에이전트 루프. C14 기준으로 플랜·답변 검증 집행 |
| C18 | Tool Registry | G2 | 레지스트리 | 툴 등록·노출·발견 — 플랜 수립의 참조원. 소비 주체는 C3 |
| C16 | Model Gateway | G3 | 게이트웨이 | 모든 모델 호출(LLM·SLM, 런타임·배치)의 단일 관문 — 라우팅·인증·로깅. 구현(LiteLLM)은 로고 배지 |
| C5 | LLM | G3 | 모델 | 플랜·답변 생성. 온프렘 또는 외부 API |
| C6 | SLM | G3 | 모델 | 요약 전용. 온프렘 또는 외부 API |
| T1 | Document Search | G4 | 툴 그룹 | `search.hybrid` / `search.lexical` / `search.semantic` — 실행 흐름: 리트리버 팬아웃(C7.1·C7.2) → 후처리(C7.4) → Document Context. 단독 툴은 후처리 미경유 |
| C7.1 | Lexical Retriever | T1 | 리트리버 | 키워드/BM25 → C10 |
| C7.2 | Semantic Retriever | T1 | 리트리버 | 벡터 유사도 → C11 |
| C7.4 | Fusion & Rank | T1 | 후처리 스테이지 | RRF 융합·랭킹 — C7.1 + C7.2 결과 합류 지점. `search.hybrid` 시에만 경유 (리트리버와 동급 아님) |
| T2 | Quantitative Query | G4 | 툴 그룹 | `query.quantitative` — 하위 C7.3 |
| C7.3 | Quantitative Retriever | T2 | T2 하위 | 정형 조회·집계 → C9의 OLTP·OLAP 양쪽 실행. 권한은 SQL 템플릿 파라미터 바인딩 |
| T3 | Document Provider | G4 | 툴 그룹 | `fetch.document` — 하위 C7.5 |
| C7.5 | Document Fetcher | T3 | T3 하위 | 파일 메타 조회(C9) → 원본 페치(C12). SPI 식별자는 `DocumentProvider` |
| C9 | Structured Store | G5 | 데이터 저장소 | 논리적 단일 역할, 물리 구현 이원: **OLTP**(마스터 데이터·권한·파일 메타[문서 ID, 물리 경로, 버전, 소유자]·트랜잭션 정형) + **OLAP**(대용량 조회·집계). 구체 제품은 로고 배지로만 병기 |
| C10 | Keyword Store | G5 | 데이터 저장소 | 키워드 색인 + 문서별 요약 필드 |
| C11 | Vector Store | G5 | 데이터 저장소 | 벡터 색인 |
| C12 | File Store | G5 | 데이터 저장소 | 원본 파일. 메타(C9) 경유로만 접근 |
| C17 | Domain Dictionary | G5 | 지원 컴포넌트 | 도메인 용어·동의어·엔티티의 단일 원천. G4 쿼리 전처리·G6 청킹/색인 보조. 사전 데이터는 고객사별 교체 |
| C15 | Ingestion Pipeline | G6 | 파이프라인 | 메인 다이어그램에서는 단일 박스 |
| C15.1 | Summarization Queue | C15 | C15 하위 | 등록·갱신 이벤트 적재. 갱신 시 기존 요약 삭제 후 재등록 |
| C15.2 | Summary Worker | C15 | C15 하위 | Queue 소비 → C16 경유 C6 호출 → 요약을 C10 필드에 적재 |
| C14 | Deterministic Security Layer | X | cross-cutting | 결정론적 보안 규칙의 단일 원천 (PDP): ① 권한 판정 — ACL pre-filter·플랜 권한 범위·UI 권한 정보 ② 산출물 검증 — 플랜 유효성, 답변·인용의 컨텍스트 근거 |

명명 규칙: 툴 그룹은 능력 기준(Document Search / Quantitative Query / Document Provider), 스토어는 데이터 형태 기준(Keyword/Vector/Structured/File), C9 내부는 워크로드 기준(OLTP/OLAP). 구체 구현 기술·제품명은 다이어그램에서 로고 배지로만 병기. **다이어그램 레이블은 영어 전용** — 한글은 정의서·발표 노트에만.

### G4 노출 툴

| 툴 | 그룹 | 실행 | 융합 |
|---|---|---|---|
| `search.hybrid` | T1 | C7.1 + C7.2 팬아웃 → 후처리 C7.4 (RRF·랭킹) | O |
| `search.lexical` | T1 | C7.1 단독 — 후처리 미경유 | X |
| `search.semantic` | T1 | C7.2 단독 — 후처리 미경유 | X |
| `query.quantitative` | T2 | C7.3 단독 (OLTP·OLAP 라우팅) | X — 별도 슬롯 |
| `fetch.document` | T3 | C7.5 | — |

## 2. 관계

### 사용자 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R1 | C1 → C2 | Chat Query |
| R2 | C2 → C1 | Chat Response + Reference Links |
| R3 | C2 → C3 | Chat Query + Principal |
| R4 | C3 → C2 | Chat Response |
| R5 | C2 → T3 | `fetch.document` — 참조 문서 다운로드 온디맨드. 플래닝 루프 미경유 |

### 모델 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R6 | C3 → C16 | Planning Prompt / Answer Prompt |
| R7 | C16 → C3 | Proposed Tool Call Plan / Draft Answer + Citations — C3가 C14 기준으로 검증해 Validated로 확정 |
| R8 | C16 ↔ C5 | 프롬프트/응답 |
| R9 | C16 ↔ C6 | 요약 요청/응답 — 호출자는 C3(캐시 미스 폴백, 점선)과 C15.2(배치) |

### 툴 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R10 | C3 → G4 | Tool Invocation — 플랜 지정 툴 + principal |
| R11 | G4 → C3 | Context Slots — ① Document Context (융합·랭킹 문서 + 요약 필드) ② Structured Data (+ 쿼리 ID·대상 테이블 메타 = 답변 출처) |
| R23 | C3 ↔ C18 | Tool Discovery — 플랜 수립 시 툴 카탈로그 참조 (G2 내부, 다이어그램 표기는 드릴다운만) |
| R12 | C7.1 ↔ C10 | Keyword Query / Ranked Documents |
| R13 | C7.2 ↔ C11 | Vector Query / Relevant Chunks |
| R14 | C7.3 ↔ C9 | Parameterized SQL (principal 바인딩) — OLTP·OLAP 양쪽 / Query Result Data |
| R15 | C7.5 → C9 | File Meta Query — **다이어그램 미표기** (T3 내부 구현) |
| R16 | C7.5 → C12 | File Fetch |

### 보안 (X — cross-cutting)
| ID | 방향 | 레이블 |
|---|---|---|
| R17 | C14 → C2 | User Permission Info — UI 표시용 (접근 가능 메뉴·문서) |
| R18 | C14 ⇢ C3 | 플랜·답변 검증 기준 |
| R19 | C14 ⇢ G4 | ACL pre-filter 기준 — Keyword Store 필터 절 / Vector Store 메타데이터 필터 / SQL 파라미터 |

### 적재·동기화 (G6·G5)
| ID | 방향 | 레이블 |
|---|---|---|
| R20 | C15 ⇢ C9·C10·C11·C12 | 적재 (점선). 내부 전개는 별도 다이어그램 |
| R21 | C17 ⇢ G4·C15 | Domain Term Reference — 쿼리 전처리(G4)·청킹/색인 보조(G6). 참조 관계(점선) |
| R22 | C9 내부 OLTP → OLAP | 정형 데이터 동기화 (CDC/배치) — **다이어그램 미표기** (C9 내부 구현, R15와 동일 원칙) |

C15 내부 흐름(별도 장): 자료 등록/갱신 → 메타(C9)·원본(C12)·색인(C10)·청킹/임베딩(C11) 적재 → C15.1 enqueue → C15.2 → C16 → C6 → 요약을 C10 문서 필드에 기록. 갱신 시 기존 요약 삭제 후 재등록.

## 3. 다이어그램 표기 지침

- **레이블 언어**: 다이어그램 내 모든 레이블·주석은 **영어 전용**. 한글 설명은 슬라이드 본문·스피커 노트에만
- **히어로 슬라이드**: G-레벨 큰 컴포넌트(G1~G6 + X)만으로 전체 흐름이 읽히는 레이블 있는 흐름도. 박스 6개 + cross-cutting 밴드 1개. 스타일은 임팩트 우선(아이소 허용)
- **드릴다운 슬라이드**: 큰 컴포넌트 1개씩 확대 — 플랫 다크(존 그룹핑 + 글래스 카드) 문법, 관계 레이블 전부 표기
- **아이콘 시스템**: 형태 = 유형, 글리프 = 개체. 토큰은 `kori-icon-style-tokens.html` 단일 소스
- **저장소·게이트웨이 레이블**: 역할명 주 레이블 + 구체 기술 로고는 전면 하단 고정 배지. C9는 OLTP/OLAP 2배지
- **교체 가능(swappable) 배지**: C5·C6·C9·C10·C11·C12·C16·C17 — ⇄ 마커 + 하단 한 줄 범례
- **X(C14)**: G1·G2·G4를 관통하는 밴드(배경 레이어). 화살표 노드로 그리지 않음
- **G6(C15)**: 메인/히어로에서 단일 박스 + G5로 점선. 상세는 별도 장
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
