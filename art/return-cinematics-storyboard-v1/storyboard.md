# 티크 — 복구와 귀환 스토리보드 v1

> **최신 기준은 [연출 v4](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/README.md)와 [전체 구조·11샷 계획](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/storyboard.md)이다.** 공방과 상부 착륙층을 배경에서도 제거하고, 마지막은 엘리베이터 탑승·상승으로만 끝낸다. 기동8초·쓰러짐3초·엘리베이터7초에 미디엄·클로즈업·와이드를 재배치했다. 기존 낙하 오프닝과 게임 플레이는 유지한다. 아래 내용과 v2/v3는 이전 기획·제작 기록으로 보존한다.

> **이전 v3 제작 기록:** 문지기 쓰러짐3초와 엘리베이터 상승·공방 도착7초를 독립된 두 연출로 제작했었다. [엔딩 v3 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/README.md)은 보존하되 현재 엔딩 기준으로 사용하지 않는다. 공방·하차·도착 자막은 최신 v4에서 제외됐다.

> 현재 제작 방식: **실제 이미지 생성 → 네이티브 도트 → 기존 티크/문지기 프레임 재사용·합성 → PNG/Piskel/APNG 내보내기**다. A1–A4·B1–B4 전체 8컷과 기동 8초·귀환 10초 순서 재생본은 [전체 도트 연출 v2](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v2-full/README.md)에 정리했다. 이전 4컷 패키지와 아래 AI 영상 프롬프트·제작 분담은 최초 기획 기록으로 보존한다. AI 영상 변환·게임 연동·실행은 하지 않았고 인간 최종 외형 승인은 대기 중이다.

## 기획 범위

마지막 퍼즐 뒤의 **문지기 기동 8초**, 전투 뒤의 **공방 귀환 10초**를 설계한다. 두 장면 사이에는 실제 보스전이 있으므로, 연속 18초짜리 영상이 아니다. 기존 낙하 오프닝은 변경하지 않으며 이 18초에도 포함하지 않는다.

표의 8컷·18초는 **게임 연결 장면 4컷·8초**와 **AI 영상 계획 4컷(A2·A3·B3·B4)·10초**를 합친 연출상 목표다. B2는 플레이어가 직접 문에 도달해 상호작용할 때까지 기다리므로 실제 소요시간은 더 길어질 수 있다. 각 컷의 초수는 편집 목표이며, 영상 생성 도구의 출력 길이를 보장하는 값이 아니다.

전달할 이야기: **공장을 켰더니 문지기가 깨어났다. 문지기를 멈추고 돌아갈 문을 열었다.** 대사와 세계관 설명을 추가하기보다 빛과 소리의 변화로 전달한다.

생성 시트는 구도와 흐름에 피드백하기 위한 **미승인 시각 기획안**이다. 영상의 실제 시작·끝 프레임, 스프라이트, 런타임 에셋으로 바로 쓰지 않는다. 게임 구현과 영상 변환은 아직 진행하지 않는다.

## A. 문지기 기동 — 마지막 퍼즐에서 전투로

감정: **성공의 안도 → 이상 징후 → 위협 발견 → 내가 대응할 차례**.

![문지기 기동 4컷 시각 기획안](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematics-storyboard-v1/Generated/sequence-a-board.png)

| 컷 / 장면 내 시간 | 화면·동작 | 구도·카메라 | 소리·감정 | 제작 담당 |
|---|---|---|---|---|
| A1 · 0–2초 | 마지막 황동 사각 추가 사각 소켓에 들어간다. 연결 표시가 켜진 뒤 완료 창으로 가리지 않고 결과를 보여준다. | 실제 퍼즐의 고정 격자 화면을 유지한다. 플레이어가 방금 조작한 추와 소켓 중심. 시트의 사선 클로즈업은 연결 대상을 설명하는 그림이며 새 게임 카메라가 아니다. | 연결음, 짧은 전원 기동음. “해냈다.” | **게임**: 기존 추·소켓·벽·구슬·연결 표현 재사용. |
| A2 · 2–4초 | 배선 끝의 릴레이가 한 번 닫히며 청록 전력이 기계 내부로 전달된다. | 철·황동 릴레이 클로즈업. v1은 고정 구도. | ‘딸깍’ 후 낮은 전기음. 복구가 더 큰 설비에 영향을 줬다는 암시. | **AI 이미지 → 영상**: 릴레이 활성화 하나만. |
| A3 · 4–6초 | 문지기의 붉은 입속 노심과 턱 연결부. 피스톤이 짧게 움직이며 잠금이 풀린다. | 기존 문지기 형태를 유지한 노심 클로즈업. 눈이나 새 얼굴을 만들지 않는다. | 금속 잠금 해제음, 묵직한 저음. “이건 뭐지?” | **AI 이미지 → 영상**: 피스톤의 작은 작동 하나만. |
| A4 · 6–8초 | 붉은 노심을 기준으로 전투맵에 컷. 왼쪽 티크, 오른쪽 문지기. ‘폐기 대상 감지’가 짧게 표시된다. | 실제 전투맵의 고정 측면 구도. 게임 크기의 티크와 네 다리 문지기 유지. 노심 색으로 연결하며 흰 섬광은 쓰지 않는다. | 영상의 저음이 게임 설비음으로 이어진다. 위협의 대상이 티크임을 명확히 한다. | **게임**: 기존 기동 애니메이션과 픽셀 폰트. 종료 후 조작 안내·전투 시작. |

전환 핵심: A1의 청록 연결광 → A2의 청록 전력 → A3의 붉은 노심 → A4의 같은 붉은 노심. 영상에서 게임으로 넘어올 때 전투 구도와 캐릭터 크기가 갑자기 바뀌지 않게 한다.

## B. 공방 귀환 — 전투의 보상을 보여주기

감정: **위험 해소 → 내가 출구로 이동 → 따뜻한 장소 발견 → 안착**.

![공방 귀환 4컷 시각 기획안](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematics-storyboard-v1/Generated/sequence-b-board.png)

| 컷 / 장면 내 시간 | 화면·동작 | 구도·카메라 | 소리·감정 | 제작 담당 |
|---|---|---|---|---|
| B1 · 0–2초 | 문지기가 바닥에 멈추고 붉은 노심이 꺼진다. 승리 창을 바로 덮지 않고 정지 상태를 보여준다. | 기존 전투맵 고정 측면 구도. 보스 정지·출구 개방이 읽히게. | 구동음이 낮아지다 멈추고 금속이 가라앉는 소리. 긴장 해소. | **게임**: 기존 정지·문 상태 표현 재사용. |
| B2 · 2–4초 | 열린 오른쪽 문에 따뜻한 빛이 보인다. 티크가 승인된 Walk 동작으로 문에 접근한다. | 같은 전투 화면 유지. 이동 방향을 한눈에 읽게. | 티크 발소리, 문 작동음. 귀환을 내가 선택한다는 느낌. | **게임**: 출구까지 직접 이동. 표의 2초는 연출상 목표이며 입력이 늦으면 영상이 자동 시작하지 않는다. |
| B3 · 4–7초 | 문 너머의 빈 공방. 작업대·황동 시계·기어에 따뜻한 작업등이 닿는다. | 공방 전체를 읽을 수 있는 고정 와이드 구도. 새로운 사람이나 NPC 없음. | 거친 공장 소음이 사라지고 작은 시계 소리가 등장. 돌아갈 장소 발견. | **AI 이미지 → 영상**: 빛과 미세한 먼지 중심. |
| B4 · 7–10초 | 같은 작업대와 작업등, 벽 시계를 더 가까이 본다. 마지막에 ‘돌아갈 곳이 있어.’가 표시된다. | B3와 물건 배치를 맞춘 더 좁은 고정 구도. 과한 줌·팬 없음. | 조용한 시계 소리와 여운. 이후 엔딩 메뉴. | **AI 이미지 → 영상** + **게임 폰트 자막**. |

전환 핵심: B2 문의 따뜻한 빛 → B3 작업등의 같은 색 → B4 조용한 작업대. 티크의 걷기를 AI로 다시 만들지 않는다. 공방에 들어온 뒤 새 인물이나 추가 사건을 넣지 않는다.

## 이미지 → 영상 변환용 동작 프롬프트 초안

승인된 개별 기준 이미지가 준비된 뒤 사용한다. 아래 문장은 동작 지시이며, 아직 영상 생성 결과가 아니다. 입력 이미지로 형태·색·구도를 고정하고 클립마다 한 가지 작은 동작만 요구한다. 픽셀 경계나 캐릭터 동일성이 자동 보장되는 것은 아니다.

### A2 — 릴레이 활성화 / 2초

> Locked camera. The single steel-and-brass relay in the input image closes once, carrying a small cyan activation pulse into the existing cable. Keep the original composition, hard pixel edges, palette, and all mechanical parts unchanged. No new components, camera shake, lens effects, lettering, or morphing.

### A3 — 문지기 잠금 해제 / 2초

> Locked close-up. The existing guardian jaw piston makes one short mechanical activation stroke and settles. Preserve the input image's angular jaws and red mouth core, with no eyes and no new facial features. Keep the red core steady, the silhouette unchanged, and the pixel grid crisp. No lunge, transformation, camera shake, bloom, or text.

### B3 — 조용한 공방 / 3초

> Locked wide shot of the exact empty workshop in the input image. A few fine dust motes drift slowly through the steady warm task-lamp light. Preserve the workbench, bronze clock, gears, palette, and pixel grid. No character enters, no object moves or appears, no camera pan, flicker, bloom, or text.

### B4 — 귀환의 여운 / 3초

> Locked tighter shot of the exact workbench, task lamp, and wall clock in the input image. A few fine dust motes drift gently through the steady warm light. Keep every object, its position, and its pixel silhouette unchanged. No people, new props, camera movement, clock deformation, soft-focus effect, or generated lettering.

자막과 음향은 생성 영상에 포함시키지 않고 별도로 편집·게임 적용한다. 이미지 내 시계 숫자나 글자도 연출 전달의 필수 정보로 사용하지 않는다.

## 시각·연출 불변 조건

- 기존 낙하 오프닝, 티크의 이동·기동 애니메이션, 전투 패턴은 이번 기획에서 변경하지 않는다.
- 티크는 작은 황동 몸체와 청록 눈·심장. 문지기는 얼굴 없는 어두운 네 다리 기계, 각진 턱과 붉은 입속 노심. 눈·인간 표정·새 얼굴을 추가하지 않는다.
- 연결된 회색 벽, 손잡이 달린 황동 사각 추, 청록 원형 구슬, 사각·원형의 들어간 소켓을 유지한다.
- 전투 복귀 프레임은 실제 측면 아레나와 기존 게임 크기를 기준으로 맞춘다. 현재 문지기 런타임 셀은 192×176, 티크는 기존 셀·발끝 정렬을 유지한다. 에셋 재사용과 인간 최종 외형 승인은 따로 기록한다.
- 공장은 차가운 회색·청록, 경고는 붉은 노심, 공방은 따뜻한 황동색. 과한 광택·3D 깊이·렌즈 효과로 도트 톤을 바꾸지 않는다.
- ‘폐기 대상 감지’, ‘돌아갈 곳이 있어.’는 게임의 실제 픽셀 폰트로 표시한다. 생성 이미지·영상에 한글을 그리게 하지 않는다.
- 첫째·둘째 퍼즐 완료는 짧은 게임 내 점등·설비음으로 처리한다. 별도 영상을 추가하지 않는다.

## 승인 후 제작 순서

1. 이 시트에서 **구도·컷 흐름·감정**에 먼저 피드백한다. 시트를 승인해도 개별 영상 에셋의 품질 승인이 자동으로 이루어진 것은 아니다.
2. A2·A3·B3·B4 각각의 실제 시작·끝 기준 이미지를 이미지 생성으로 만든다. 시트의 작은 패널을 확대해 최종 프레임으로 대신하지 않는다.
3. 생성 원본과 프롬프트·참조·메타데이터를 보존하고, 개별 기준 이미지를 사용자에게 보여 검토한다.
4. 승인된 정체성을 유지하며 네이티브 픽셀 정리·정렬·팔레트·등록을 맞춘다. 티크/문지기의 기존 editable-source·export 검증 과정을 재사용한다.
5. 영상 변환은 **A2 하나부터** 시험한다. 작은 화면과 실제 게임 표시 크기에서 픽셀 흔들림·부품 뒤틀림을 확인한 뒤 나머지를 제작한다.
6. 자막·음향을 별도로 얹고 게임 화면과 매치 컷을 검수한다. 프레임·색·동작의 기술 검증과 사용자의 시각 승인을 따로 기록한다.

## 생성 시트 검수와 남은 보정

- 두 시트 모두 실제 이미지 생성 결과다. 기존 캐릭터·전투 화면을 참조했지만 실제 플레이 캡처는 아니다. 생성 원본은 그대로 보존했다.
- A1은 연결 대상을 설명하는 사선 구도다. A1·A4·B1·B2의 실제 제작은 기존 게임 화면과 승인된 애니메이션을 재사용하며 생성 그림으로 교체하지 않는다.
- 문지기의 붉은 노심은 입속에 있고 새 눈·인간 얼굴은 추가되지 않았다. 실루엣·상대 크기의 정확한 일치는 개별 기준 이미지와 실제 게임 합성에서 다시 검수한다.
- 생성 시트에는 도트 블록과 미세 질감·일부 부드러운 배경이 섞여 있다. 현재는 네이티브 픽셀 정리 전 미승인 기획안이며 최종 도트 에셋으로 간주하지 않는다.
- B3·B4는 공방의 분위기와 구도를 보여주지만 일부 소품 배치·종류가 다르다. 실제 기준 이미지에서는 **B3를 공간 기준으로 고정하고 B4는 같은 작업대의 가까운 구도**로 맞춘다. 새 소품을 추가하지 않는다.
- [전체 이미지 생성 프롬프트와 참조](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematics-storyboard-v1/Source/requests.json), [원본·복사본 해시와 검수 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematics-storyboard-v1/Source/generation-results.json)을 보존한다. 생성 방식은 내장 이미지 생성 도구이며 영상 생성·게임 파일 변경은 하지 않았다.

## 게임 연동 시 체크

- 전투 재도전·전투만 시작에서는 A 영상을 다시 강제 재생하지 않는다. B는 실제 클리어 후 출구를 통과했을 때만 진입한다.
- 영상은 건너뛰기 가능하게 한다. 스킵·확인 입력은 소비하고 키가 놓인 뒤 게임 입력을 재개해, 컷 종료 직후 점프나 공격이 튀어나오지 않게 한다.
- 영상은 전환 전에 미리 로드한다. 마지막 게임 프레임과 영상 첫 프레임, 영상 끝과 복귀 게임 프레임을 준비해 검은 화면·첫 프레임 대기를 피한다.
- 재생 실패 시 준비된 정지 기준 프레임과 게임 연출로 연결한다. 실패 때문에 퍼즐 완료나 보스전 진행이 막히지 않게 한다.
- 전환 동안 게임 상태를 의도적으로 고정하고, 복귀 시 전투 시작 시점·입력·메뉴 상태를 명확히 재개한다. 영상 시간에 플레이어가 피격되지 않는다.
- 모든 안내 자막은 게임 UI 계층에서 표시한다. 음향은 영상과 별도로 볼륨 설정을 적용하고, 자막이 소리에만 의존한 정보를 보충하게 한다.

## 지금 받을 피드백

- A1 → A2 → A3만 봐도 **내가 복구한 전원이 문지기를 깨웠다**고 읽히는가?
- 문지기 클로즈업이 기존 보스와 같은 기계로 보이는가? 눈이나 새 얼굴처럼 읽히는 부분은 없는가?
- A4가 더 큰 영화 화면이 아니라 **곧 내가 조작할 전투 화면**으로 자연스럽게 느껴지는가?
- B2에서 플레이어가 문까지 이동하는 시간이 필요한가, 더 짧게 이어지는 게 좋은가?
- 공방이 안전하고 익숙한 장소로 느껴지는가? 빈 작업대만으로 충분한가?
- 두 자막은 필요한가? 특히 엔딩 문장은 **유지 / 더 담백하게 / 삭제** 중 어느 방향이 좋은가?

상태: **시각 기획 v1 / 사용자 피드백 대기 / 영상 변환·게임 연동 미실행**.
