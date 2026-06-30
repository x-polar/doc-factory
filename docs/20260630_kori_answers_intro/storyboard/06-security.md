---
title: "결정론적 보안 레이어가 권한 밖 데이터를 LLM 입력 전에 차단한다"
layout: title+body
source: [src-02]
---

- LLM은 원천 데이터에 직접 접근하지 않는다 (세션 통해서만 전달)
- Document / Row / Column level 권한 필터링
- 비인가 데이터는 Prompt에 구조적으로 미포함 — 랜덤 요소 없는 결정론적 방어
- 요청·조회·필터링·응답 전 과정 기록(End-to-End 감사)

## notes
3축 중 3축: 보안. "환각이 보안을 못 뚫는다" 메시지.
