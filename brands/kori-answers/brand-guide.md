# KORI Answers — Brand Guide

KORI Answers(= MARU RAG)는 **XENOIMPACT의 온프레미스 RAG 기반 AI 지식 어시스턴트
제품**이다. 이 폴더는 이 제품 문서용 브랜드 엔트리다.

## 디자인 (www.xenoimpact.com 웹/KORI 아이덴티티 기반)
- **다크(블랙 `#000`) 베이스 + 네온 민트 `#22FFBD` 포인트 + Tomorrow 디스플레이 폰트.**
  회사 소개서(오렌지 `#C04F15`/Pretendard)와는 **다른 제품 아이덴티티**다.
- 폰트: 제목 **Tomorrow**(영문 테키, `assets/fonts/Tomorrow/`), 본문 **Pretendard**
  (한글 가독성). 사이트 본문 폰트 **Monda**도 `assets/fonts/Monda/`에 보관(OFL).
  한글은 Tomorrow에 글리프가 없어 폴백 렌더된다.
- 무드: 미니멀·테키, 글래스모피즘(웹). 포인트는 민트 1곳에 절제해 사용.
- 값의 단일 진실원천은 `theme.yaml`. (소스 PDF의 디자인은 참고하지 않음 — 내용만)
- KORI 전용 로고 자산은 아직 없음(웹은 JS 렌더). 입수 시 `assets/logos/`에 두고
  `theme.logo`를 설정한다.

## 제품 내용(콘텐츠)
- 제품 사실·메시지·아키텍처는 `knowledge/kori-answers/`에 정리되어 있다.
  소스 원본은 `refs/`(LFS).

## 표기
- 제품명: **KORI Answers** (구/내부 명칭: MARU RAG).
- 영문 슬로건(소개서 사용): "Next Technology for Human Race".
