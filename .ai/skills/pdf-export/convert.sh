#!/usr/bin/env bash
# pptx -> pdf 변환 (LibreOffice headless)
# 사용법:
#   convert.sh <file.pptx>     단일 파일 변환
#   convert.sh <dir>           디렉터리 내 모든 *.pptx 변환
set -euo pipefail

if ! command -v soffice >/dev/null 2>&1; then
  echo "오류: soffice(LibreOffice)를 찾을 수 없습니다. 설치 후 다시 시도하세요." >&2
  exit 1
fi

# pptx 변환에는 Impress 모듈이 필요(core만 있으면 'source file could not be loaded').
if [ ! -e /usr/lib/libreoffice/program/simpress.so ] \
   && ! ls /usr/lib/libreoffice/program/*impress* >/dev/null 2>&1; then
  echo "경고: LibreOffice Impress 모듈이 안 보입니다. 변환이 실패하면 설치하세요:" >&2
  echo "      sudo apt-get update && sudo apt-get install -y libreoffice-impress" >&2
fi

if [ "$#" -ne 1 ]; then
  echo "사용법: $0 <file.pptx | dir>" >&2
  exit 1
fi

target="$1"

# 동시 실행/락 충돌을 피하기 위한 전용 프로필 디렉터리
profile="$(mktemp -d)"
trap 'rm -rf "$profile"' EXIT

convert_one() {
  local f="$1"
  local outdir
  outdir="$(dirname "$f")"
  echo "변환 중: $f -> $outdir/$(basename "${f%.*}").pdf"
  soffice --headless -env:UserInstallation="file://$profile" \
    --convert-to pdf --outdir "$outdir" "$f"
}

if [ -d "$target" ]; then
  shopt -s nullglob
  files=("$target"/*.pptx)
  if [ "${#files[@]}" -eq 0 ]; then
    echo "변환할 .pptx 파일이 없습니다: $target" >&2
    exit 1
  fi
  for f in "${files[@]}"; do
    convert_one "$f"
  done
elif [ -f "$target" ]; then
  convert_one "$target"
else
  echo "오류: 경로를 찾을 수 없습니다: $target" >&2
  exit 1
fi

echo "완료."
