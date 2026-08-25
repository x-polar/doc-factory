---
title: "Document Search Internals"
lede: "두 검색이 서로의 빈틈을 메운다"
layout: diagram
diagram: diagrams/document-search.html
source: [kori-arch]
---

## notes
T1 드릴다운 (search.hybrid 경로). AO → Query Preprocessing(정규화·확장·검색어 분리, DD 참조) → 팬아웃: Lexical Retriever(BM25→Keyword Store) ∥ Query Embedding(MG 경유 text→vector)→Semantic Retriever(top-k→Vector Store)
→ Fusion & Rank(RRF 융합·재랭킹) → Document Context 슬롯 → AO 회귀.
스토어 조회는 ACL PRE-FILTER 관통(3장 문법). search.lexical/semantic 단독 툴은 후처리 미경유 — 주석 표기.
