# 티크 도트 연출 v4 — 공방 삭제·샷 크기 재편집

공방 장면을 포함한 v3를 그대로 줄인 것이 아니라, **상부 공방/착륙층이 없는 샤프트를 먼저 실제 이미지 생성**하고 전체 연출의 샷 크기를 다시 편집했다. 새로운 사건·인물·캐릭터 포즈는 추가하지 않았다. 기존 낙하 오프닝은 유지한다.

**독립된 세 클립 후보: 기동8초 / 쓰러짐3초 / 엘리베이터7초.** 게임 연동·실행·사운드 동기화는 아직 하지 않았다. 기술 검증과 인간 구도·동작 승인은 별개다.

## 변경 결과

| 구간 | 최신 흐름 |
|---|---|
| 기동 | 복구 미디엄 → 릴레이 CU → 붉은 노심 ECU → 전투 와이드 |
| 쓰러짐 | 몸이 내려앉는 미디엄 → 꺼진 입속 CU → 티크·문지기 와이드 |
| 엘리베이터 | 탑승 미디엄 → 가이드·상태등 인서트 → 탑승자 트래킹 클로즈 → 샤프트 와이드·화면 위로 이탈 |

공방·상부 착륙층·하차·도착음·시계음·마지막 설명 자막은 최신 클립에 없다. 상승만 보여주고6.6초 투 블랙→400ms 홀드로 끝낸다. 세 클립을18초 통짜 영화로 붙이지 않는다.

## 바로 확인

![전체11샷 구도](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/shot-board.png)

문지기 기동8초:

![기동](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/awakening-preview.gif)

문지기 쓰러짐3초:

![쓰러짐](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/guardian-collapse-preview.gif)

엘리베이터 탑승·상승7초:

![상승](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/elevator-ascent-preview.gif)

GIF는 무음 반복 미리보기다. 마지막 투 블랙 다음 첫 프레임 복귀는 GIF 루프이며 게임에서는 엔딩 메뉴로 연결한다.

## 상세 계획·원본·검증

- [전체 게임 구조·11샷 타임라인·카메라 이유](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/storyboard.md)
- [내장 이미지 생성 프롬프트·참조](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/requests.json), [실제 생성 결과](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/generation-results.json), [원본·참조 SHA](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/provenance.json)
- [네이티브 파생·정수2배·기존 승강기 출처](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/Derivation/native-derivation.json), [카메라·발점 등록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/registration.json), [재사용 원본 PNG·해시](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Source/reused-assets.json)
- [클립 프레임·가변 시간](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/Clips/clip-plan.json), [PNG/APNG/Piskel/GIF 검증](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/validation.json), [구도·세계 좌표·소스 재생 검증](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-cinematic-edit-v4/QA/composition-validation.json)

각 `Clips/<name>/`에 PNG·native.apng·Piskel·sheet·pixel-delta가 있고 `Exports/<name>/` PNG는 입력 원본과 바이트 동일하다. Piskel 편집본의 고정fps 대신 `durations`/APNG가 가변 프레임 시간의 기준이다. GIF는 source RGB가 정확한 NEAREST2배이며 개별 노출 경계를10ms 단위로 누적 반올림한다. 총8/3/7초는 그대로다.

티크/문지기 동작은 그대로 두고, 완성된 세계에320×180→2배/160×90→4배 카메라 크롭을 적용한다. **스프라이트 몸체를 따로 늘이지 않지만, 화면에서 보이는 크기는 샷에 따라 커진다.** 새 이미지 생성 스킬이 공방 제거를 실제 생성 편집으로 먼저 처리하도록 제작 순서를 정했다.

## 재현

```text
python tools/art/compose_cinematic_edit_v4.py --inspected-anchors --derive-only
# 실제 native 검수와 registration 뒤:
python tools/art/compose_cinematic_edit_v4.py --inspected-anchors
python tools/art/package_cinematic_edit_v4.py --inspected-anchors
python tools/art/check_cinematic_edit_v4.py
```

기존 출력과 다른 결과는 덮어쓰지 않고 실패한다. 이전v1/v2/v3 파일은 보존하며 현재 소스/클립과 게임 파일을 혼동하지 않는다. `--inspected-anchors`는 생성·확인을 생략하는 자동 승인 플래그가 아니다.
