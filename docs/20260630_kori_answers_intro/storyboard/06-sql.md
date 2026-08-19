---
title: "LLM은 SQL을 쓰지 않는다 — 전문가가 검수한 쿼리를 호출할 뿐"
kicker: "Pillar 02 · 효율"
lede: "환각이 만든 잘못된 SQL이 DB에 닿을 경로 자체를 없앴습니다."
layout: numbered
source: [src-02]
items:
  - heading: "필요한 Tool 판별"
    text: "질의를 이해해 어떤 조회 도구가 필요한지 결정"
  - heading: "Parameter 생성 · 호출 검증"
    text: "LLM의 역할은 여기까지 — 쿼리문 자체는 만들지 않는다"
  - heading: "MCP Tool 호출"
    text: "전문가가 작성·검증한 SQL이 실행. 단순 조회는 Oracle, 대용량 분석은 ClickHouse"
  - heading: "조회 후처리"
    text: "Relevance 검증과 사용자 권한 필터링을 거쳐 시각화 데이터로 전달"
---

## notes
Context Aware Routing으로 최소 요청·빠른 응답. Oracle 부하도 최소화.
