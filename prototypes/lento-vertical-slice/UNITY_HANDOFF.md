# Unity 이관 기준

## 권장 프로젝트 설정

- 기준 해상도: 1280x720, 16:9
- Pixel Perfect Camera: Assets PPU 64, Reference Resolution 1280x720, Crop Frame X/Y 사용
- 티크 스프라이트 셀: 128x128, 렌토: 256x192, 새끼쥐: 64x64
- 원형 관로: 외곽 지름 약 244px, 중심 Y 486px, 바닥선 Y 604px에 매립
- 애니메이션 파일: 한 PNG에 한 동작만 배치하고 모든 프레임의 피벗을 bottom-center로 통일
- 입력: 방향키 이동/상호작용, Z 점프, X 공격, C 대시
- Texture Import: Sprite (2D and UI), Filter Mode Point, Compression None, Generate Mip Maps Off
- 물리: Rigidbody2D + CapsuleCollider2D(티크), Rigidbody2D Kinematic + 복수 Collider2D(렌토)

## 컴포넌트 분리

| 컴포넌트 | 책임 |
|---|---|
| `LentoEncounterController` | 페이즈 임계값, 전환, 클리어 시퀀스 |
| `LentoPatternRunner` | 패턴 큐, 전조/활성/회복 타이밍 |
| `LentoHurtboxController` | 방어, 취약, 그로기 배율 |
| `PipeNoiseReceiver` | 티크 공격 소리 이벤트와 출현 배관 선택 |
| `PipeHideInteractable` | 3페이즈 숨기 상호작용과 무적 상태 |
| `RatlingGroupController` | 소환, 명령, 전멸 이벤트 |
| `PurifierControlPanel` | 보스 처치 후 조작, 배수 이벤트 |
| `BossDebugPanel` | 페이즈 이동, 패턴 강제, 시간 배율, 히트박스 |

## 상태 머신

`Hidden -> NoiseHeard -> BiteTell -> BiteActive -> Recovery -> Hidden`

`Phase2Entry -> RatlingCommand/TailSweep/PoisonSpit -> Neutral`

`Phase3Entry -> JumpSlam/SonicWave/Charge -> WallCrashGroggy -> Neutral`

각 패턴은 `telegraph`, `active`, `recovery` 시간을 ScriptableObject로 분리한다. 애니메이션 이벤트는 공격 판정 시작·종료, 발사체 생성, 음파 생성에만 사용하고 페이즈 전환은 EncounterController가 소유한다.

## 데이터 이관

- `data/lento-combat.json`의 수치를 `LentoEncounterData` ScriptableObject 초기값으로 사용한다.
- `data/animation-manifest.json`은 스프라이트 제작과 Animator State 이름의 기준으로 사용한다.
- 웹 프로토타입에서 조정한 전조 속도는 개별 패턴 시간으로 다시 기록한다. 전역 배율을 최종 게임에 그대로 두지 않는다.

## 완료 조건

- 1페이즈 배관 타격 위치와 렌토 출현 위치가 일치한다.
- 모든 공격에 최소 0.6초 이상의 고유 전조가 있고 애니메이션과 히트박스가 일치한다.
- 배관 숨기는 돌진 전조 중 항상 접근 가능한 배관이 카메라 안에 하나 이상 있다.
- 새끼쥐 전멸 이벤트가 렌토 방어 해제와 즉시 동기화된다.
- 처치, 제어반 조작, 배수, 갈고리 획득 경로 개방이 저장 가능한 이벤트 플래그로 이어진다.
- 60fps와 30fps에서 패턴 타이밍 및 물리 결과가 동일하다.
