# 티크 엔딩 v3 — 쓰러짐과 엘리베이터 귀환

마지막 연출을 **독립된 두 클립**으로 분리했다. 이전 문으로 걸어 나가는 B1–B4 대신 아래3초·7초 후보를 사용한다. 기존 낙하 오프닝과 A1–A4 문지기 기동8초는 변경하지 않았다.

상태: **오프라인 도트 애니메이션 후보 제작·기술 검증 완료 / 사용자 외형·동작 승인 대기 / 게임 연동·실행 안 함.** AI 영상 변환 결과나 실제 플레이 캡처가 아니다.

## 1. 문지기 쓰러짐 — 3초

![문지기 쓰러짐 미리보기](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/guardian-collapse-preview.gif)

서 있는 문지기300ms → 기존 defeat00–04 각110ms → defeat05 정지2150ms. 입속 노심이 꺼지며 위험이 끝났다는 것을 보여준다. 문을 열거나 승리창을 덮지 않고 전투맵에서 끝낸다. 티크는 왼쪽에서 기존 Idle00을 유지한다.

원래6프레임 defeat 동작의 형태·순서는 그대로다. 마지막 정지 홀드만 엔딩용으로 늘렸으며, 회전·신체 부위 확대·재생성·보간 변형은 하지 않았다.

## 2. 엘리베이터로 공방 귀환 — 7초

![엘리베이터 귀환 미리보기](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/elevator-homecoming-preview.gif)

| 클립 시간 | 장면 | 동작 |
|---|---|---|
| 0–0.76초 | 아래층 탑승 | 기존 Walk14프레임·760ms. 왼쪽에서 승강기 중앙까지 이동. |
| 0.76–1.2초 | 탑승 확인 | 기존 Idle00, 발판 정지. |
| 1.2–3.8초 | 상승 | 승강기와 티크가 같이 y282→172로 수직 이동. 중간에 기존80/100/80ms 눈 깜빡임 한 번. |
| 3.8–4.2초 | 위층 도착 | 발판·티크 정지. 층 높이 확인. |
| 4.2–5초 | 하차 | 기존 Walk760ms로 오른쪽의 따뜻한 공방 입구까지 이동, 짧은 정지. |
| 5–7초 | 공방 안착 | 기존 같은 공방 와이드 소스 재사용. 티크가 바닥에 서 있다. 마지막1초만 ‘돌아갈 곳이 있어.’ |

상승은 고정 카메라의 두 층·수직 레일로 읽힌다. 승강기·티크는 정수 좌표로만 이동하며 실루엣을 변형하지 않는다. 승강기 앞면과 내부는 실제 알파로 열려 있어 탑승자가 보인다. 새로운 문 열기·버튼 누르기·인물·사건은 넣지 않았다.

최종 공방은 승강기 배경 생성 때 참조했던 기존 공방과 같은 소품 구도다. 따뜻한 작업등과 작업대·벽 시계를 연결 단서로 삼고, 새 방이나 NPC를 추가하지 않는다.

## 이미지 우선 제작과 원본 추적

내장 이미지 생성으로 `shaft-workshop-plate` 배경과 `open-lift-carriage` 투명 승강기를 **먼저 실제 생성**했다. 생성 원본을 메인 에이전트가 확인·사용자에게 표시한 뒤 도트로 파생하고, 파생 배경·승강기·공방 바닥 위치를 다시 확인했다. 이 스킬은 새 승강기를 코드 도형으로 만드는 대신 실제 생성 원본에서 파생하도록 제작 순서를 정했다.

- [전체 프롬프트·참조·내장 생성 방식](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/requests.json)
- [실제 생성 결과 경로·메타데이터](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/generation-results.json)
- [생성 원본·복사본·참조 SHA 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/provenance.json)
- [네이티브 파생 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/Derivation/native-derivation.json)
- [층·발판·캐릭터 등록값](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/registration.json)
- [그대로 재사용한 원본·해시](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Source/reused-assets.json)

배경은 균일16:9 source crop→premultiplied BOX320×180→기존64색 팔레트→NEAREST2배640×360. 승강기는 alpha≥128 전체 바운딩 박스→몸체 전체를 논리52px 폭으로 균일 샘플→고정 팔레트·binary alpha→논리64×64 패딩→NEAREST2배128×128. 파츠별 크기 조절·임의 윤곽 재도색·새 형상 코드 페인팅은 없다. 팔레트 인덱스 맵에서 native RGBA를 정확히 복원했다.

생성 배경의 실제 위층 바닥은 요청 프롬프트의 y128이 아니라 **y172**였다. 이를 원본의 실제 기하 기준으로 등록했으며 이미지를 뒤틀어 요청값에 강제로 맞추지 않았다. 승강기 뒤쪽 가로대 y84와 실제 발판 y94도 구분했다.

티크64×64·발점(32,56), 문지기192×176·발점(96,164)을 그대로 사용한다. 티크의 이동·눈 깜빡임, 문지기의 쓰러짐 프레임과 PNG bytes를 보존했다. 현재 런타임에서 쓰이는 에셋 재사용이며, 이것이 전체 에셋의 인간 최종 승인을 뜻하지는 않는다.

## 전달 파일과 검증

각 `Clips/<name>/`에는 개별 PNG, `native.apng`, 편집용 `<name>.piskel`, `sheet.png`, frame별 pixel-delta JSON, 별도 `sound.wav`가 있다. `Exports/<name>/` PNG는 입력 PNG와 byte-identical이며 [프레임 시간](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/Exports/clips.json)을 같이 제공한다.

- PNG/APNG는 정확한 variable frame timing의 기준이다. 쓰러짐7프레임·3000ms, 귀환116프레임·7000ms.
- GIF는 무음 반복 미리보기다. source RGB와 동일한 직접 팔레트·NEAREST2배이며 경계를10ms 단위로 반올림한다. 이번 총 재생시간3/7초는 그대로다.
- Piskel은 편집을 위해 최대30프레임 horizontal chunk를 사용한다. 설정된 고정 fps가 variable frame timing을 대신하지는 않으므로 내보낼 때 `durations`/APNG를 기준으로 한다.
- [원본·팔레트·구도·탑승자 정렬 재구성 검사](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/composition-validation.json), [PNG/APNG/Piskel/GIF replay 검사](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/validation.json), [WAV 재구성 검사](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/audio-validation.json) 통과. 시각 승인·실제 게임 연동 검사는 아니다.
- [주요9프레임 한눈에 보기](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-ending-elevator-v3/QA/two-ending-contact.png)

음향은 기존 `land/switch`로 만든 별도48kHz PCM16 스테레오 임시 배치본이다. 쓰러짐0.85초, 탑승0.76초, 상승1.2초, 도착3.8초에 작은 접점음;5.5/6.5초에 시계 대용음. 전용 승강기 모터·시계 녹음은 아직 없다. 무음 GIF에 소리가 합쳐진 것이 아니며 MP4/AI 영상은 만들지 않았다.

## 게임에 연결할 때 — 아직 미구현

1. 보스 처치 확정 후 쓰러짐3초를 한 번 재생한다. 기존 defeat가 이중 재생되지 않게 상태를 하나로 관리한다.
2. 이후 조작을 돌려주고 엘리베이터를 사용 가능하게 한다. 플레이어가 접근·상호작용하면 귀환7초를 시작한다. 두 클립 사이 대기시간은 플레이어 선택이며 자동10초 통짜 영화로 붙이지 않는다.
3. 귀환 종료 뒤 엔딩 메뉴. 재시도나2페이즈 단독 시작에서 엔딩을 재생하지 않는다.
4. 두 클립은 각각 스킵 가능하게 하되 확정 입력을 소비하고 키가 놓인 뒤 조작을 재개한다. 승강기·영상 실패 시 준비된 종료 프레임/게임 상태로 정상 진행한다.
5. 실제 맵과 첫·마지막 프레임 위치를 일치시키고, 영상 자막은 게임 UI 계층에서 같은 픽셀 폰트로 표시한다. 연동 시 충돌·입력·HP는 재생 동안 의도적으로 고정한다.

## 재현 명령

```text
python tools/art/compose_ending_elevator_v3.py --inspected-anchors --derive-only
# native를 직접 확인한 뒤 Source/registration.json 기준으로:
python tools/art/compose_ending_elevator_v3.py --inspected-anchors
python tools/art/package_ending_elevator_v3.py --inspected-anchors
python tools/art/check_ending_elevator_v3.py
python tools/art/mix_ending_elevator_v3_audio.py --check-only
```

`--inspected-anchors`는 직접 원본을 확인·표시한 이후의 증빙 게이트이며 확인 없이 붙여 쓰는 자동 승인 옵션이 아니다. 기존 파일과 다른 결과는 덮어쓰지 않고 실패한다. 이전v1/v2 패키지와 게임 파일을 수정하지 않는다.
