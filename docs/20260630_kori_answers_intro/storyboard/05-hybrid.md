---
title: "하이브리드 검색과 출처 표기로 '신뢰할 수 있는 답'을 만든다"
layout: title+body
source: [src-01, src-02]
---

- 의미(벡터) + 키워드 검색을 병렬 수행하는 Hybrid Retrieval
- 결과를 Relevance 평가 → Filtering → Reranking으로 정밀 선별
- 답변 문장에 In-line 출처 표기, Post Validation Chain으로 검증
- 비정형: ElasticSearch(전체 문서) + Milvus(Chunk 단위 벡터)

## notes
1축: 정확성·신뢰성.
