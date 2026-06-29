#!/usr/bin/env bash
# 새 문서 작업 폴더 생성: docs/_template -> docs/YYYYMMDD_<slug>
# 사용법:
#   new.sh <slug> [YYYYMMDD]
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "사용법: $0 <slug> [YYYYMMDD]" >&2
  exit 1
fi

slug="$1"
date_str="${2:-$(date +%Y%m%d)}"

# 저장소 루트 기준으로 경로 고정
root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
template="$root/docs/_template"
dest="$root/docs/${date_str}_${slug}"

if [ ! -d "$template" ]; then
  echo "오류: 템플릿을 찾을 수 없습니다: $template" >&2
  exit 1
fi

if [ -e "$dest" ]; then
  echo "오류: 이미 존재합니다(덮어쓰지 않음): $dest" >&2
  exit 1
fi

cp -R "$template" "$dest"
echo "생성됨: $dest"
echo "다음 단계: brief.md를 먼저 작성하세요 (AGENTS.md §2 참고)."
