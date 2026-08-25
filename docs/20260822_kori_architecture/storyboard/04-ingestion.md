---
title: "Ingestion Pipeline"
layout: diagram
diagram: diagrams/ingestion.html
source: [kori-arch]
---

## notes
G6 드릴다운. 진입 액터 2종(End User 업로드 / External Interface 배치 동기화) → 파이프라인 5단계(D36: Registration 신설 — 원본 먼저 적재).
Summarization 내부 Queue→Worker(D5, 이벤트 구동) → Model Gateway 경유 SLM 배치.
적재: Registration→OLTP·File / Indexing→Keyword·Vector / Worker→Keyword 요약 필드. OLAP는 이 장에서 무연결(분석 적재는 별도 경로).
