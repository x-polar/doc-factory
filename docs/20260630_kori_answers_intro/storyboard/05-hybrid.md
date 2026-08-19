---
title: "의미와 키워드를 동시에 검색해 근거를 고른다"
kicker: "Pillar 01 · 정확성"
lede: "두 검색을 병렬로 돌린 뒤 Relevance 평가로 통합해 최적의 배경지식만 남깁니다."
layout: two-col
source: [src-01, src-02]
left:
  - "벡터 검색 — 의미·문맥 기반 유사도"
  - "Milvus, 문서 Chunk 단위 저장"
  - "메타데이터 필터로 후보군 축소"
right:
  - "키워드 검색 — 정확한 용어 매칭"
  - "ElasticSearch, 전체 문서 단위"
  - "1차 후보군 확보에 강함"
---

## notes
두 축을 병렬 수행 → Relevance 평가 → Filtering → Reranking → In-line 출처 + Post Validation Chain.
