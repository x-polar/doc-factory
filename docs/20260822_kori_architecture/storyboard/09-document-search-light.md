---
title: "Document Search Internals"
lede: "두 검색이 서로의 빈틈을 메운다"
layout: diagram
diagram: diagrams/document-search-light.html
source: [kori-arch]
---

## notes
T1 드릴다운 (search.hybrid 경로). AO → 팬아웃: Lexical Retriever(BM25) ∥ Semantic Retriever(임베딩→Vector Store)
→ Fusion & Rank(RRF 융합·재랭킹) → Document Context 슬롯 → AO 회귀.
스토어·ACL은 3장 소재라 미표기(내부 스테이지에 집중). search.lexical/semantic 단독 툴은 후처리 미경유 — 주석 표기.
