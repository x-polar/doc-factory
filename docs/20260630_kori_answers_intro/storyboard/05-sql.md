---
title: "전문가 SQL Tool로 정형 데이터를 정확·효율적으로 조회한다"
layout: title+body
source: [src-02]
---

- LLM은 SQL을 직접 생성하지 않는다 (환각에 의한 오류 차단)
- 전문가가 검수한 SQL을 MCP Tool로 제공 → LLM은 Tool 선택만
- 조회는 Oracle(OLTP), 대용량 분석은 ClickHouse(OLAP)로 분리
- Context Aware Routing으로 최소 요청·빠른 응답

## notes
3축 중 2축: 정확·효율. "LLM이 SQL을 안 짠다"가 핵심 차별점.
