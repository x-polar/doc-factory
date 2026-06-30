---
title: "결정론적 보안 레이어가 권한 밖 데이터를 LLM 입력 전에 차단한다"
layout: two-col
source: [src-02]
left:
  - "LLM은 원천 데이터에 직접 접근 불가"
  - "데이터는 사용자 세션 통해서만 전달"
  - "Document / Row / Column 권한 필터"
right:
  - "비인가 데이터는 Prompt에 구조적 미포함"
  - "랜덤 요소 없는 결정론적(Deterministic) 방어"
  - "요청·조회·필터·응답 전 과정 End-to-End 감사"
---

## notes
3축: 보안. "환각이 보안을 못 뚫는다".
