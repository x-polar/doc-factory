---
name: pdf-export
description: >
  생성된 .pptx 파일을 .pdf(또는 기타 포맷)로 변환합니다. 사용자가 덱을 PDF로
  내보내거나 변환·export 해달라고 할 때 사용합니다.
---

# pdf-export

LibreOffice headless로 `.pptx`를 `.pdf`로 변환합니다. 레이아웃·폰트 보존이
가장 안정적인 무료 방식입니다.

## 사전 조건

- LibreOffice + **Impress 모듈** 필요(`soffice` 사용 가능해야 함).
  - 확인: `soffice --version`
  - **pptx 변환에는 `libreoffice-impress`가 반드시 필요**합니다. core만 설치돼
    있으면 `Error: source file could not be loaded`로 실패합니다.
  - 설치(데비안/우분투): `sudo apt-get update && sudo apt-get install -y libreoffice-impress`
  - 주의: 원격/임시 컨테이너는 세션마다 초기화될 수 있어 매번 설치가 필요할 수 있음.
- 한글 등 멀티바이트 폰트는 **변환 실행 환경에 설치**돼 있어야 깨지지 않습니다.

## 단일 파일 변환

```bash
soffice --headless --convert-to pdf --outdir output output/20260629_proposal_v1.pptx
```

## 헬퍼 스크립트

`convert.sh`로 파일/디렉터리를 변환합니다.

```bash
# 단일 파일
.ai/skills/pdf-export/convert.sh output/20260629_proposal_v1.pptx

# output/ 의 모든 pptx 일괄 변환
.ai/skills/pdf-export/convert.sh output/
```

## 주의

- 변환 결과는 원본과 같은 디렉터리에 `.pdf`로 생성됩니다(원본 pptx는 유지).
- 변환 후 PDF를 열어 폰트 깨짐·잘림이 없는지 확인하세요.
- 다른 포맷이 필요하면 `--convert-to` 값을 바꿉니다(예: `png`, `docx`).
