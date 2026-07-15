# PixelLab 동작별 생성 명세

## 현재 작업 상태

- PixelLab 티크 캐릭터 ID: `9580e2b4-d66e-40e4-8d38-5458f63397ee`
- 생성 완료: 티크 8방향 회전 원본, `Breathing Idle`, `Running (8 frames)`, `Two-Footed Jump`, `Cross Punch (beta)`, `Slide (beta)`, `Taking Punch (beta)`
- 로컬 보관 위치: `assets/tique/pixellab/rotations/`
- 정리된 런타임 프레임: `assets/tique/animations/{idle,run,jump,attack,dash,hit}/`
- 동작별 스프라이트 시트: `assets/tique/animations/{idle,run,jump,attack,dash,hit}.png`
- 웹 런타임 현재 사용: 대기 4프레임, 달리기 8프레임, 점프 7프레임, 수평 공격 6프레임, 대시 6프레임, 피격 6프레임
- 교체 규칙: 생성 완료된 각 동작은 128x128 셀과 하단 중앙 피벗으로 정규화한 뒤 해당 동작만 교체한다.

PixelLab 갤러리 API가 일시적으로 `Failed to fetch`를 반환할 경우 작업을 재제출하지 않는다. 백그라운드 작업은 서버 큐에 남아 있으므로 캐릭터 상세 화면이 복구된 뒤 완료 결과만 회수한다.

## 공통 규칙

- 한 PNG에는 한 동작만 배치한다.
- 모든 프레임은 동일한 셀 크기와 `bottom-center` 피벗을 사용한다.
- 캐릭터가 셀 경계에 닿지 않도록 좌우 12%, 상단 8%, 하단 4%의 안전 여백을 둔다.
- 배경은 투명, 그림자는 별도 레이어, 프레임 배열은 가로 1행이다.
- 티크는 128x128 셀, 렌토는 256x192 셀, 새끼쥐는 64x64 셀을 사용한다.
- 색상표와 외형은 참조 시트에 고정하고 동작 생성마다 새 캐릭터를 재생성하지 않는다.

## 티크 참조 고정 문구

`Side-view warm brass wind-up robot named Tique, large cyan glass eyes, cyan heart core in the chest, round head and torso, short mechanical limbs, wind-up key on the back. Preserve exact proportions, palette, facial design, core shape and key silhouette from the reference. Pixel art, transparent background, fixed bottom-center pivot.`

## 티크 동작

| 파일 | PixelLab 동작 설명 | 프레임 |
|---|---|---:|
| `animations/idle.png` | subtle breathing through core pulse, tiny key movement, feet remain planted | 4 |
| `animations/run.png` | readable side-view run cycle, brass limbs swing, no body redesign | 8 |
| `animations/jump.png` | crouch, compression, upward takeoff and fall | 7 |
| `jump-fall.png` | airborne falling loop, legs lowered, arms balancing | 4 |
| `land.png` | impact squash, small recoil, return to planted stance | 4 |
| `animations/attack.png` | fast horizontal punch with short anticipation and recovery | 6 |
| `attack-up.png` | upward melee slash, feet and body remain centered | 8 |
| `attack-down.png` | downward aerial melee slash, clear pogo impact frame | 8 |
| `animations/dash.png` | short forward burst, compact silhouette, no teleport effect | 6 |
| `animations/hit.png` | brief backward recoil, core flicker | 6 |
| `down.png` | mechanical collapse onto the floor, settle completely | 8 |
| `pipe-enter.png` | turn and squeeze into a circular pipe opening | 6 |
| `panel-interact.png` | reach forward and operate an industrial control panel | 6 |

## 렌토 참조 고정 문구

`Huge mutated sewer rat boss named Lento, wet charcoal fur, amber eyes, dirty-gold Lentium crystal exposed in a cracked rib cavity, rusted purifier debris embedded in the back, long cable-like tail with metal rings. Preserve the exact silhouette and material design from the reference. Side-view boss sprite, transparent background, fixed bottom-center pivot.`

## 렌토 동작

각 패턴은 `data/action-assets.json`에 정의된 별도 PNG로 생성한다. 물기·꼬리 휩쓸기·점프 찍기·음파·돌진은 전조, 활성, 회복이 한 파일 안에서 시간 순서로 이어져야 하며 다른 패턴 프레임을 섞지 않는다.
