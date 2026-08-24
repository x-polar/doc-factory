---
title: "Retrieval Workflow"
lede: "플랜이 지정한 능력만, 권한 필터를 통과한 데이터만"
layout: diagram
diagram: diagrams/retrieval.html
source: [kori-arch]
---

## notes
G4+G5 통합 드릴다운. 툴 4종(D32 순서) → ACL Pre-filter 게이트 → 스토어 5종.
결과는 Grounding Context 슬롯 2종(Document Context/Structured Data, 인용 단위)으로 조립되어 AO 회귀.
