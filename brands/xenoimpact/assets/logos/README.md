# XENOIMPACT 로고 자산

| 파일 | 용도 |
|------|------|
| `xenoimpact_white_typo.svg` | 공식 벡터(화이트 워드마크) — 다크 배경용 |
| `xenoimpact_black_typo.svg` | 공식 벡터(블랙 워드마크) — 밝은 배경용 |
| `xenoimpact_white_typo.png` | 위 SVG의 래스터(투명, 1744×176) — **deckbuilder가 사용** |
| `xenoimpact_black_typo.png` | 〃 (밝은 배경용) |

## 빌더 연동

`theme.yaml`의 `logo.cover`/`logo.footer`가 PNG를 가리킨다(표지 상단·푸터 자동 삽입).
python-pptx가 SVG를 직접 못 넣어서 PNG를 쓴다.

## SVG → PNG 재생성

로고가 바뀌면 아래로 PNG를 다시 만든다(빌드 시점엔 PNG만 쓰므로 cairosvg는 런타임
의존성이 아님):

```bash
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='xenoimpact_white_typo.svg', \
  write_to='xenoimpact_white_typo.png', scale=4.0)"
```

> 심볼('X' 셰브론)만 분리된 버전이 있으면 추가해 두면 좋다(아이콘/파비콘용).
