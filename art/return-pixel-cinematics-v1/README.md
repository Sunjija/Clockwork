# Clockwork — 네이티브 도트 연출 후보 v1

실제 이미지 생성 원본에서 도트화·정리·애니메이션·내보내기를 진행하는 **미승인 후보** 패키지다. AI 영상 변환은 사용하지 않는다. 게임 구현·연동·실행은 이 작업에 포함하지 않으며, 기존 낙하 오프닝과 승인된 티크 동작은 변경하지 않는다.

## 컷 구성

모든 컷의 네이티브 캔버스는 **640×360, 16:9**다. 목표 재생시간은 2초 / 2초 / 3초 / 3초, 합계 10초이며 실제 프레임 수·시간은 내보내기 기록으로 확인한다.

와이드 원본은 320×180 논리 도트 격자를 정수 2배로 출력했다. 근접 공방은 같은 격자의 160×90 영역을 정수 4배로 보여준다. 픽셀 크기를 임의 보간하거나 부품별로 늘리지 않는다. 출력은 12 / 12 / 16 / 16프레임, 총 56프레임이다.

| 컷 | 길이 | 움직임 의도 | 우선 검수 사항 |
| --- | --- | --- | --- |
| A2 · 릴레이 전력 전달 | 2초 | 접점·청록 표시등과 기존 배선의 점등으로 오른쪽 전력 전달을 읽게 한다. | 릴레이·배선의 고정 형태, 점등 방향, 불필요한 광번짐 여부 |
| A3 · 문지기 노심 기동 | 2초 | 입 안의 붉은 노심과 기존 기계 연결부를 통해 조용한 기동을 표현한다. | 눈을 추가하지 않은 기존 정체성, 노심 위치, 턱·피스톤 정렬과 흔들림 |
| B3 · 공방 와이드 | 3초 | 차가운 방 안의 따뜻한 작업등과 작은 먼지 픽셀로 귀환의 정적을 만든다. | 램프·시계·작업대 배치, 먼지 밀도, 배경 픽셀의 안정성 |
| B4 · 동일 공방 근접 | 3초 | B3와 **동일한 원본**을 크롭해 램프·시계·작업대 주변으로 시선을 모은다. | 컷 사이 공간·물건 연속성, 크롭 좌표와 픽셀 배율, 새 공간·인물 추가 여부 |

## 제작·추적 기록

생성 원본을 확인한 뒤 크롭·색상·픽셀 격자·정렬을 네이티브 크기에서 정리한다. B3/B4는 하나의 공방 원본과 파생 경로를 공유한다. 확대 검수에는 nearest-neighbor를 사용하며 부드러운 보간으로 픽셀을 흐리지 않는다.

- [생성 요청·프롬프트·참조 이미지](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/Source/requests.json)
- [수정 생성 요청](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/Source/requests-edits.json)
- [생성 원본·출처 추적](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/Source/provenance.json)
- [네이티브 파생·크롭·정리 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/Source/Derivation/native-derivation.json)
- [내보내기 프레임·재생시간·해시 기록](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/Exports/export-manifest.json)

내보내기 형식은 PNG 프레임, 편집 가능한 Piskel, APNG이며 GIF는 확인용 프리뷰다. 형식별 프레임 순서·크기·시간과 원본→파생→출력 해시 연결을 점검한다.

## 검수용 이미지·프리뷰

아래 링크는 패키지의 검수 출력 위치다. 출력 파일의 존재와 최신 여부는 최종 내보내기 기록으로 확인한다.

![네 컷 동시 애니메이션 미리보기 — 게임 캡처 아님](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/all-cuts-preview.gif)

동시 미리보기는 10fps로 각 클립을 독립 반복한다. 실제 게임 흐름이나 최종 편집 영상이 아니며 정확한 컷별 시간은 개별 APNG·clips.json이 기준이다. 음향·자막은 아직 넣지 않았다.

![4컷 네이티브 도트 후보 — 2배 확대 검수](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/contact-2x.png)

- [A2 릴레이 프리뷰 GIF](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/relay-power-preview.gif)
- [A3 문지기 노심 프리뷰 GIF](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/warden-boot-preview.gif)
- [B3 공방 와이드 프리뷰 GIF](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/workshop-wide-preview.gif)
- [B4 동일 공방 근접 프리뷰 GIF](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/workshop-close-preview.gif)

네이티브 픽셀 정리와 해시·재생 검증은 **인간의 시각 승인과 별개**다. 기술 검수가 통과해도 룩·움직임·서사 연결은 사용자가 직접 확인해야 하며, 승인 전에는 최종 승인 자산으로 표현하지 않는다. 게임에서의 전환·조작 복귀·플레이 검증은 아직 이 패키지의 완료 주장에 포함하지 않는다.

[독립 기술 검증 결과](/Users/daddung/Documents/Codex/2026-09-15/https-github-com-sunjija-clockwork-tree/work/Clockwork-latest-3338c55/art/return-pixel-cinematics-v1/QA/independent-validation.json): 생성 원본·참조·요청 해시, 도트 배율·팔레트, 56프레임의 마스크 밖 픽셀 불변, 원본/프레임 델타 재생, Piskel/APNG 정합, PNG 바이트 복사와 재생시간을 검사한다. 턱·몸체는 고정하고 노심 발광과 기록된 피스톤 삽입부의 정수 이동만 허용한다. 이 검증은 미적 승인이나 실제 게임 플레이 검증을 대신하지 않는다.
