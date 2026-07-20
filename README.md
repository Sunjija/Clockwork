# CLOCKWORK

2D 픽셀아트 메트로베니아. 시간이 멈춘 도시, 황금빛으로 굳은 사람들, 그리고 잃어버린 기억을 되찾는 조수 로봇 티크의 이야기.

- **플랫폼:** Steam (PC)
- **분량:** 본편 약 10시간 (ACT1·2·3) / 졸업작품 범위 = ACT1(지하) 약 3시간
- **타깃:** 할로우나이트·데드셀류 메트로베니아 선호층

## 문서 구조

| 경로 | 내용 |
|---|---|
| `docs/00_canon_rules_v5.4.md` | **정본 룰북** — 프로젝트 최상위 정본. 세계관 룰(RUL) · 연표(EVT) · 인물/보스 카드 · 시스템(ABL/WPN/MOD) · 동선 설계 원칙 |
| `docs/rulebook-v5.5-patch.md` | v5.5 패치 제안 — 맵 설계 세션에서 나온 정정·재정의·신설 제안 (A~F 등급 구분) |
| `docs/99_master_context.md` | **LLM 이식용 마스터 컨텍스트** — 프로젝트 전체 맥락 한 장 요약, 룰북 갱신 시 함께 동기화 |
| `docs/reward-system-v0.1.md` | 보상 체계 제안 — 능력·MOD·슬롯·코어 파편·고철 부품·기록의 역할과 맵 데이터 규약 |
| `docs/music/` | 지역별 음악 방향, Suno 기준 실험, ACT1 생성·선별 기록 |
| `docs/art/act1-environment-art-bible.md` | ACT1 지역별 환경 콘셉트·전이 규칙·이미지 생성 순서 |
| `docs/art/tique-character-model-lock.md` | 티크 인게임 외형 고정 규칙 — 짧은 다리, 체형 비율, 피벗, 팔레트 불변 조건 |
| `maps/act1-underground.html` | ACT1 지하 안드레스 — 룸 단위 상세 맵 (49룸, 선택 탐사 지역 포함) + 크리티컬 패스 + 게이트/숏컷 설계 |
| `maps/act2-surface.html` | ACT2 지상 메티아 — 초안 [전부 제안] |
| `maps/act3-tower.html` | ACT3 크로노스 타워 — 십자 5탑·회전 가교 초안 [전부 제안] |
| `maps/world-atlas.html` | **전체 세계 전도** — 옥상~심층 습지 수직 40층 단면, 3막 통합 |
| `prototypes/lento-vertical-slice/index.html` | 렌토 보스전 720P 웹 버티컬 슬라이스 — 3페이즈 전투, 패턴 강제 실행, 티크 PixelLab 애니메이션 검증 |
| `prototypes/limbus-room-slice/index.html` | 림부스 3화면 비주얼 룸 슬라이스 — 방별 생성 배경, 분리 충돌 레이어, 기존 티크 액션 프레임으로 이동·점프·공격·대시 검증 |
| `prototypes/act1-world-slice/index.html` | ACT1 전체 비주얼 월드 슬라이스 — 메인 9구역과 선택 탐사 3구역, 신형 3/4 티크 액션 자산, 지역별 분리 배경 |
| `skills/clockwork-suno-ost/` | CLOCKWORK 지역·보스·기억 음악용 Suno 프롬프트 제작 스킬 |
| `art/concepts/act1/` | ACT1 횡스크롤 환경 콘셉트 이미지 후보 |

맵 HTML은 브라우저에서 바로 열어 볼 수 있습니다 (외부 의존성: Pretendard 폰트 CDN만).
렌토 프로토타입도 `index.html`을 브라우저에서 열거나 로컬 정적 서버로 실행할 수 있습니다.

## 확정/제안 구분 규칙

- 룰북(v5.4)에서 `[제안]`/`[미정]` 표기가 없는 항목은 전부 **확정**.
- 맵 문서의 룸 분할·숏컷·게이트 배치는 `[제안]` — 확정 요소(동선 ①~⑨, 보스, 기억, 보물방, ID)만 정본 준거.
- v5.5 패치는 미머지 상태 — `A(정정)`은 기획자 구두 확정분, `C(신설 제안)`은 채택 결정 필요.

## 팀

기획·스토리·연출 1인 + Unity 개발 1인 (+ 아트 합류 예정)
