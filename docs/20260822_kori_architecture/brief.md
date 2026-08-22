---
title: "KORI Answers 아키텍처"
brand: kori-answers
version: v1
theme: {}
---

# Brief — KORI Answers 아키텍처

## 대상 (Audience)
- 고객/파트너의 기술 의사결정자·아키텍트 (사전지식: 엔터프라이즈 IT 일반,
  LLM/RAG 개념은 개요 수준)

## 목적 (Objective)
- KORI Answers의 아키텍처가 **보안·정합성·운영 유연성을 구조로 보장**함을
  납득시켜 기술 검토/도입 논의를 다음 단계로 진전시킨다.

## 핵심 질문 (Key Question)
- "LLM 제품을 사내 데이터에 붙여도 안전하고 정확한가? 그 근거는 구조에 있는가?"

## 제약 (Constraints)
- 다이어그램 중심 5~8장, 16:9 (kori-answers 브랜드)
- 시각화 이원화: 히어로 슬라이드 = 추상 3D 렌더(ComfyUI 이미지, 레이블 없음),
  아키텍처 슬라이드 = 2.5D 아이소메트릭 (v7.6 §3)
- 아이콘 스타일 토큰 시스템(`kori-icon-style-tokens.html`) 신규 구축 — 형태=유형,
  글리프=개체, 토큰 단일 소스
- 작도 기준: `research/kori-architecture-definition-v7.7.md` (단일 출처).
  R15 미표기, C14는 관통 밴드, 마스킹/DLP 범위 외 (D14·D16·D17).
  교체 가능 컴포넌트는 swappable 배지 + 하단 범례 (D20)

## 성공 기준 (Definition of Done)
- 메인 아키텍처 2.5D 다이어그램이 v7.7의 컴포넌트·관계 정의와 1:1 대조 통과
- 선 교차 0 (D14), vision 비평 루프 2회 이상 통과
- release/에 PDF 확정본

## 메모
- 기존 플랫 골드(20260822_diagram_gold)는 v7.5 이전 기준 — 참고만, 재사용 금지
