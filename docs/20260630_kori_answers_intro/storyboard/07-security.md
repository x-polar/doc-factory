---
title: "권한 밖 데이터는 LLM 입력 이전에 차단된다"
kicker: "Pillar 03 · 보안"
lede: "필터링이 프롬프트 구성 앞단에 있어, 환각이 보안을 뚫을 구조적 여지가 없습니다."
layout: process
source: [src-02]
steps:
  - num: "01"
    heading: "세션 권한 확인"
    text: "사용자 Role / Level 기반 접근 제어"
  - num: "02"
    heading: "데이터 조회"
    text: "LLM은 원천 데이터에 직접 접근하지 못한다"
  - num: "03"
    heading: "권한 필터링"
    text: "Document · Row · Column · Enum 단위 Rule 기반 차단"
  - num: "04"
    heading: "프롬프트 구성"
    text: "인가된 데이터만 병합되어 LLM에 전달"
---

## notes
결정론적(Deterministic) — 랜덤 요소 없음. 전 과정 End-to-End 감사 추적.
