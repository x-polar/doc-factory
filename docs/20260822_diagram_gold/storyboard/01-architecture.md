---
title: "환각이 보안을 뚫지 못한다 — 결정론적 보안 레이어가 LLM 입력 전에 차단"
layout: diagram
diagram: diagrams/architecture.html
source: [kori-arch]
---

## notes
knowledge/kori-answers/architecture.md의 처리 흐름 1~5를 시각화.
LLM은 사내 데이터에 직접 접근하지 않고, Agent가 보안 레이어를 거쳐
필터링된 컨텍스트만 전달받는 구조를 강조.
