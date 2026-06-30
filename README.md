# Document Factory

비즈니스/기술 문서(주로 `.pptx`, 필요 시 `.pdf`)를 AI와 함께 생성하는 작업 공간.
작업 규칙·워크플로·구조는 **[`AGENTS.md`](AGENTS.md)** 를 먼저 읽으세요.

## 시작하기 (Setup)

> ⚠️ **이 repo는 `*.pptx`·`*.pdf`에 Git LFS를 사용합니다.** clone 전에 git-lfs를
> 설치하세요. 안 하면 해당 파일이 **실제 파일이 아니라 작은 포인터 텍스트**로
> 받아집니다.

```bash
# 1) Git LFS (필수 — clone 전에)
#   mac:    brew install git-lfs
#   ubuntu: sudo apt-get install -y git-lfs
git lfs install

# 2) clone (LFS 파일 자동 다운로드)
git clone <repo-url>
#   이미 git-lfs 없이 clone 했다면: git lfs pull 로 복구

# 3) Python 의존성 (pptx 생성)
pip install -r requirements.txt

# 4) (PDF 변환 시) LibreOffice Impress
#   ubuntu: sudo apt-get install -y libreoffice-impress
```

## 빠른 사용

```bash
# 새 문서 골격 생성
.ai/skills/doc-scaffold/new.sh <프로젝트명>

# storyboard 작성 후 덱 생성 (brief.md frontmatter가 브랜드/테마 선택)
python src/lib/deckbuilder.py docs/<문서폴더>

# pptx -> pdf
.ai/skills/pdf-export/convert.sh docs/<문서폴더>/output/<파일>.pptx
```

자세한 절차·브랜드·스킬은 [`AGENTS.md`](AGENTS.md) 참고.
