# knowledge/kori-answers/ — KORI Answers 제품 지식

XENOIMPACT 제품 **KORI Answers**(= MARU RAG)의 공유 사실·메시지. 이 제품 관련
문서(`docs/...`)는 여기를 인용한다. 소스 원본은 `brands/kori-answers/refs/`(LFS).

| 파일 | 내용 |
|------|------|
| `product.md` | 정의·3대 특징·기능·사용법·도입효과·PoC 결과(93.2%) |
| `architecture.md` | Agent 설계·데이터 거버넌스·정형/비정형 응답·기술 스택 |
| `roadmap.md` | 4단계 발전 로드맵 + STT 부록 |

## 핵심 메시지 (positioning)
- **"안전하게, 정확하게, 사내에서."** 폐쇄망(온프레미스) RAG로 데이터 유출 없이
  정형·비정형 사내 데이터를 활용하는 대화형 AI.
- **신뢰할 수 있는 답** — 모든 답변에 출처(인용)와 근거 문서를 함께 제시.
- **환각이 보안을 못 뚫는다** — LLM은 데이터에 직접 접근하지 않고, 결정론적 보안
  레이어가 권한 밖 데이터를 LLM 입력 이전에 차단.
- **전문가 SQL + 하이브리드 검색** — LLM은 SQL을 생성하지 않고, 전문가가 검수한
  Tool을 호출. 정형은 Oracle/ClickHouse, 비정형은 ElasticSearch+Milvus.
- **계속 똑똑해진다** — 프롬프트 개선·오픈소스 LLM 신버전 교체로 품질 지속 향상.

## 표기 규칙
- 제품명: **KORI Answers** (구/내부: MARU RAG). 외부 문서엔 KORI Answers 권장.
- 영문 태그라인: "Next Technology for Human Race".
