# 공용 폰트 라이브러리

`brands/_default/assets/fonts/`는 **모든 브랜드가 공유**하는 폰트를 둔다
(디자인 시스템 CSS가 `_default`를 base로 적층되는 것과 같은 모델).
브랜드 전용 폰트는 `brands/<brand>/assets/fonts/`에 두면 위에 얹힌다.

- 렌더러가 `@font-face`로 **자동 임베드**하므로 시스템 설치가 필요 없다.
- 파일명 규칙: `<Family>/<Family>-<Weight>.woff2` (Weight → font-weight 자동 매핑)
- woff2 우선(용량이 OTF의 약 절반, Chromium 네이티브 지원).

| 폰트 | 라이선스 | 용도 |
|------|----------|------|
| Pretendard | SIL OFL 1.1 (`Pretendard/OFL.txt`) | 국·영문 본문/제목 기본 |
