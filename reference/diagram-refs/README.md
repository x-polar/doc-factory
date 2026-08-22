# diagram-refs — 기술 다이어그램 디자인 레퍼런스

기술 다이어그램 시스템(diagram.css + 컴포넌트 라이브러리) 구축의 기준이 되는
디자인 레퍼런스 8종. 2026-08-22 웹에서 수집·선별(사용자 픽 확정).
새 다이어그램을 만들 때 이 수준·문법을 기준으로 삼는다.

> 저작권 주의: 학습/스타일 참고용으로만 사용. 이미지 자체를 산출물에 넣지 않는다.

| # | 파일 | 출처 | 스타일 | 차용 포인트 |
|---|------|------|--------|-------------|
| 1 | `01-cloudflare-zone-grouping.png` | [Cloudflare Reference Architecture](https://developers.cloudflare.com/reference-architecture/diagrams/serverless/fullstack-application/) | 플랫 라이트, 존 그룹핑 | 점선 존 박스, 아이콘+라벨 노드, 번호 스텝 주석 — 정보구조의 교과서 |
| 2 | `02-vercel-glass-cards.png` | [Vercel Infrastructure Blog](https://vercel.com/blog/behind-the-scenes-of-vercels-infrastructure) | 다크 글래스 카드 | 아이콘 카드 노드, 체크리스트 내장, 중첩 컨테이너(외부 클라우드 존), 직교 화살표 |
| 3 | `03-alcion-light-isometric.png` | Dribbble (Alcion Agency) | 라이트 아이소메트릭 | 웜톤 미니멀 블록 스택 + 라벨 콜아웃 |
| 4 | `04-kris-dark-isometric.png` | Dribbble (Kris Anfalova) | 다크 아이소메트릭 | 다크 그리드 + 아이소 블록 + 코드 패널 콜아웃 |
| 5 | `05-gt-isometric-diagram-kit.png` | Dribbble (GT Diagram Kit) | 라이트 아이소메트릭 킷 | 재사용 블록 팔레트 + 곡선 화살표 + 라벨 필 — 컴포넌트 라이브러리의 모델 |
| 6 | `06-kamer-isometric-platform-map.png` | Dribbble (Kamer) | 아이소메트릭 플랫폼 맵 | 다수 컴포넌트를 한 장의 맵으로 배치하는 구도 |
| 7 | `07-cloudcraft-aws-isometric.png` | [Cloudcraft](https://www.cloudcraft.co/) | 아이소메트릭 인프라 구성도 | VPC 존 평면 + 서브넷 라벨 + 실무 수준 정보밀도 — 밀도의 상한 기준 |
| 8 | `08-isoflow-network-topology.png` | [Isoflow](https://isoflow.io/) | 아이소메트릭 네트워크 토폴로지 | 색상 존 평면으로 망 구분 + 장비 노드 + 상세 라벨 필 |

## 방향 요약 (선별 기준)

- **두 축**: ① 플랫 다크/라이트 카드+존 문법(1,2) — 문서 본문용 표준.
  ② 아이소메트릭(3~8) — 표지·개요·임팩트 슬라이드용.
- 공통 요구: "한눈에 들어오되 단순하지 않게" — 존 그룹핑으로 구조를 잡고,
  노드 안에 아이콘·라벨·부가정보를 층층이 넣어 밀도를 확보한다.
- 후속 작업: 이 레퍼런스들을 실측·분석해 `brands/*/diagram.css` +
  SVG 컴포넌트 라이브러리 + `reference/diagram-catalog.md`를 구축한다.
