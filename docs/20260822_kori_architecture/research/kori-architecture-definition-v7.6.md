# KORI Answers 아키텍처 — 구성 요소·관계 정의 v7.6

다이어그램 작도의 기준 문서. v7.2: KORI Answers는 제품 전체 이름으로 확정. v7.3: R15는 다이어그램 미표기. v7.4: 시각화 이원화 및 아이콘 스타일 토큰 시스템 추가. v7.5: C3.1을 C14에 병합, C14를 Deterministic Security Layer로 개명. v7.6: 마스킹/DLP를 설계 범위에서 제외.

## 1. 구성 요소

| ID | 이름 | 유형 | 정의 |
|---|---|---|---|
| C1 | End User | 액터 | 최종 사용자 |
| C2 | Compliance Gateway Server | 애플리케이션 (Java) | SSO 연동·권한관리 등 사내 시스템 통합. 참조 문서 온디맨드 제공. UI 권한 표시 |
| C3 | Agent Orchestrator | 애플리케이션 (Python) | 플랜 수립 → 툴 실행 → 답변 합성의 에이전트 루프. C14 기준으로 플랜·답변 검증 집행 |
| C5 | LLM | 모델 | 온프렘 또는 외부 API |
| C6 | SLM | 모델 | 요약 전용. 온프렘 또는 외부 API |
| C7 | Retrieval Layer | 계층 | 검색·조회 툴 호스트, 결과 병합 |
| C7.1 | Lexical Retriever | C7 하위 | 키워드/BM25 → C10 |
| C7.2 | Semantic Retriever | C7 하위 | 벡터 유사도 → C11 |
| C7.3 | Quantitative Retriever | C7 하위 | 정형 조회·집계 → C9. 권한은 SQL 템플릿 파라미터 바인딩 |
| C7.4 | Fusion & Rank | C7 하위 | RRF 융합 — C7.1 + C7.2 결과만 대상 |
| C7.5 | Document Provider | C7 하위 | 파일 메타 조회(C9) → 원본 페치(C12). SPI 식별자는 `DocumentProvider` |
| C9 | Structured Store | 데이터 저장소 | 정형 데이터 + 권한 + 파일 메타(문서 ID, 물리 경로, 버전, 소유자) |
| C10 | Keyword Store | 데이터 저장소 | 키워드 색인 + 문서별 요약 필드 |
| C11 | Vector Store | 데이터 저장소 | 벡터 색인 |
| C12 | File Store | 데이터 저장소 | 원본 파일. 메타(C9) 경유로만 접근 |
| C14 | Deterministic Security Layer | cross-cutting | 결정론적 보안 규칙의 단일 원천 (PDP): ① 권한 판정 — ACL pre-filter·플랜 권한 범위·UI 권한 정보 ② 산출물 검증 — 플랜 유효성, 답변·인용의 컨텍스트 근거. |
| C15 | Ingestion Pipeline | 파이프라인 | 메인 다이어그램에서는 단일 박스 |
| C15.1 | Summarization Queue | C15 하위 | 등록·갱신 이벤트 적재. 갱신 시 기존 요약 삭제 후 재등록 |
| C15.2 | Summary Worker | C15 하위 | Queue 소비 → C16 경유 C6 호출 → 요약을 C10 필드에 적재 |
| C16 | Model Gateway (LiteLLM) | 게이트웨이 | 모든 모델 호출(LLM·SLM, 런타임·배치)의 단일 관문 — 모델 라우팅·인증·로깅 |

명명 규칙: 리트리버는 능력 기준(Lexical/Semantic/Quantitative), 스토어는 데이터 형태 기준(Keyword/Vector/Structured/File). 구체 구현 기술은 다이어그램에서 로고로 병기한다.

### C7 노출 툴

| 툴 | 실행 | 융합 |
|---|---|---|
| `search.hybrid` | C7.1 + C7.2 팬아웃 → C7.4 RRF | O |
| `search.lexical` | C7.1 단독 | X |
| `search.semantic` | C7.2 단독 | X |
| `query.quantitative` | C7.3 단독 | X — 별도 슬롯 |
| `fetch.document` | C7.5 | — |

## 2. 관계

### 사용자 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R1 | C1 → C2 | Chat Query |
| R2 | C2 → C1 | Chat Response + Reference Links |
| R3 | C2 → C3 | Chat Query + Principal |
| R4 | C3 → C2 | Chat Response |
| R5 | C2 → C7 | `fetch.document` — 참조 문서 다운로드 온디맨드. 플래닝 루프 미경유 |

### 모델 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R6 | C3 → C16 | Planning Prompt / Answer Prompt |
| R7 | C16 → C3 | Proposed Tool Call Plan / Draft Answer + Citations — C3가 C14 기준으로 검증해 Validated로 확정 |
| R8 | C16 ↔ C5 | 프롬프트/응답 |
| R9 | C16 ↔ C6 | 요약 요청/응답 — 호출자는 C3(캐시 미스 폴백, 점선)과 C15.2(배치) |

### 검색 경로
| ID | 방향 | 레이블 |
|---|---|---|
| R10 | C3 → C7 | Tool Invocation — 플랜 지정 툴 + principal |
| R11 | C7 → C3 | Context Slots — ① Document Context (융합·랭킹 문서 + 요약 필드) ② Structured Data (+ 쿼리 ID·대상 테이블 메타 = 답변 출처) |
| R12 | C7.1 ↔ C10 | Keyword Query / Ranked Documents |
| R13 | C7.2 ↔ C11 | Vector Query / Relevant Chunks |
| R14 | C7.3 ↔ C9 | Parameterized SQL (principal 바인딩) / Query Result Data |
| R15 | C7.5 → C9 | File Meta Query — **다이어그램 미표기** (Document Provider 내부 구현) |
| R16 | C7.5 → C12 | File Fetch |

### 보안 (C14 — cross-cutting)
| ID | 방향 | 레이블 |
|---|---|---|
| R17 | C14 → C2 | User Permission Info — UI 표시용 (접근 가능 메뉴·문서) |
| R18 | C14 ⇢ C3 | 플랜·답변 검증 기준 |
| R19 | C14 ⇢ C7 | ACL pre-filter 기준 — Keyword Store 필터 절 / Vector Store 메타데이터 필터 / SQL 파라미터 |

### 적재 (C15)
| ID | 방향 | 레이블 |
|---|---|---|
| R20 | C15 ⇢ C9·C10·C11·C12 | 적재 (점선). 내부 전개는 별도 다이어그램 |

C15 내부 흐름(별도 장): 자료 등록/갱신 → 메타(C9)·원본(C12)·색인(C10)·청킹/임베딩(C11) 적재 → C15.1 enqueue → C15.2 → C16 → C6 → 요약을 C10 문서 필드에 기록. 갱신 시 기존 요약 삭제 후 재등록.

## 3. 다이어그램 표기 지침

- **시각화 이원화**: 히어로 슬라이드(추상 3D 렌더 — 레이블·화살표 없음, 박스 5~6개, 분위기 담당) / 아키텍처 슬라이드(2.5D 아이소메트릭 — 박스만 입체, 선은 전부 바닥 평면 직각 라우팅, 레이블은 수평 빌보드)
- **아이콘 시스템**: 형태 = 유형, 글리프 = 개체. 유형별 기본 형태 — 서버=세로 박스 / 게이트웨이=슬롯 박스 / 계층=플랫폼(모듈 큐브 탑재) / 저장소=원기둥 / 모델=적층 슬래브(크기·층수 = L/S) / cross-cutting=앰버 반투명 평면 / 파이프라인=덕트. 개체 구분은 윗면 평면 글리프로만. 토큰(투영 2:1, 팔레트, 광원 좌상단, 스트로크)은 `kori-icon-style-tokens.html` 참조 — 모든 아이콘은 토큰 단일 소스에서 생성
- **저장소·게이트웨이 레이블**: 역할명을 주 레이블로, 구체 기술 로고를 병기 — 로고는 아이콘이 아니라 전면 하단 고정 배지
- **C14**: C2·C3·C7을 관통하는 세로 밴드(또는 배경 레이어). 화살표 노드로 그리지 않음
- **C15**: 단일 박스 + 저장소 4곳으로 점선. 상세는 별도 장
- **주석 수정**: "사내 폐쇄망에 LLM 운영으로 데이터 유출 없음" → "온프렘/외부 API 선택 배포 (Model Gateway 라우팅)"
- **주석 수정**: SLM 요약 "Daily Batch" → "등록 시 사전 요약·캐싱으로 응답 시간 단축"
- **유지 주석**: SSO 연동/권한관리 사내 통합 · 정형/비정형 데이터 통합 답변 · 답변 출처와 기반 문서 제시

## 4. 확정 결정 이력

| # | 결정 |
|---|---|
| D1 | 검색 계층 명칭 Retrieval Layer, 하위 Lexical/Semantic/Quantitative |
| D2 | Quantitative 결과는 융합하지 않고 별도 컨텍스트 슬롯 |
| D3 | 리트리버 선택은 Tool Call Plan이 지정 (툴 노출) + `search.hybrid` 추가 |
| D4 | 권한은 cross-cutting Authorization Layer로 분리, pre-filter(쿼리 시점) 적용 |
| D5 | 요약은 등록 이벤트 Queue 구동, Keyword Store 문서 필드 적재, 런타임 폴백 유지 |
| D6 | C4는 C3 내부 모듈화, C3 = Agent Orchestrator |
| D7 | 모델 호출은 Model Gateway(LiteLLM) 단일 관문, 유출 통제는 게이트웨이 담당 |
| D8 | Ingestion Pipeline은 별도 다이어그램, 요약 큐는 그 하위로 흡수 |
| D9 | 참조 문서는 C2 → C7 `fetch.document` 직접 호출 |
| D10 | Quantitative 권한 주입은 SQL 템플릿 파라미터 바인딩 |
| D11 | Structured Data에 쿼리 ID·대상 테이블 메타 동봉해 출처 노출 |
| D12 | 저장소는 역할명(*Store 패밀리)으로 명명, 구체 기술은 로고 병기. C7.5는 Document Provider |
| D13 | KORI Answers는 제품 전체 이름 — 컴포넌트 레벨에 KORI 표기 없음 |
| D14 | R15는 다이어그램 미표기 — 관계는 정의에만 존재, 메인 다이어그램 선 교차 0 달성 |
| D15 | 시각화 이원화(히어로 3D + 아키텍처 2.5D) 및 아이콘 스타일 토큰 시스템(형태=유형, 글리프=개체) 채택 |
| D16 | C3.1을 C14에 병합, C14를 Deterministic Security Layer로 개명 — 범위는 권한 판정 + 산출물 검증, 마스킹/DLP는 C16 고유로 범위 외 |
| D17 | 마스킹/DLP는 설계 범위 전체에서 제외 — D7·D16의 관련 문구는 본 결정으로 대체, C16은 라우팅·인증·로깅 전담 |
