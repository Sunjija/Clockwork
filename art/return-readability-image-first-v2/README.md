# 퍼즐 에셋 v2 — 이미지 우선 네이티브 도트 후보

생성 원본 2026-10-01, 네이티브 도트·게임 연결 2026-10-02. **게임용 도트 파생, 상태별 애니메이션 출력, Unity 로컬 빌드와 실제 카메라 검증 완료. 사용자 외형 승인과 재미 검증은 대기 중이다.**

사용자는 기존 프로토타입의 벽/추/구슬/소켓이 훨씬 잘 구분된다고 평가했다. 그 형태와 색 역할을 보존하면서, 모든 새 에셋은 실제 이미지 생성부터 시작한다는 제작 순서를 바로잡는다. v1의 코드 도형을 새 이미지 출처인 것처럼 소급해서 기록하지 않는다. v2 생성 원본에서 실제 게임용 에셋을 파생해야 한다.

내장 image_gen으로 대상별 기준 이미지 6장을 생성하고 소켓 2장을 한 번씩 수정했다. 총 8회 생성/편집 호출이며 애니메이션 시트 생성이나 게임용 77프레임 생성이라는 뜻은 아니다. 생성 원본은 변경 없이 보존했다.

## 현재 시안

| 대상 | 생성 원본 | 유지할 구분 |
| --- | --- | --- |
| 벽 | [wall](Source/Generated/rev1/wall.png) | 회색 연결 구조물, 허브·손잡이 없음 |
| 추 | [weight](Source/Generated/rev1/weight.png) | 황동 사각 몸체 + 큰 빈 손잡이 |
| 구슬 | [orb](Source/Generated/rev1/orb.png) | 청록 원형 외곽 + 회전용 큰 이음선 |
| 추 소켓 | [weight socket 수정본](Source/Generated/rev2/weight_socket.png) | 어두운 사각 홈 + 얇은 황동 테두리 |
| 구슬 소켓 | [orb socket 수정본](Source/Generated/rev2/orb_socket.png) | 어두운 원형 홈 + 청록 접점. 금색 제거 |
| 바닥 | [floor](Source/Generated/rev1/floor.png) | 낮은 대비의 어두운 보행 타일 |

소켓 1차 생성본은 테두리가 너무 두껍고 높게 보였고, 구슬 소켓에 금색이 들어갔다. 2차 이미지 편집에서 사각 소켓을 얇게 만들고 원형 소켓의 금색을 청록/철색으로 변경했다. 1차 실패 후보도 보존한다. 실제640×360 게임 화면은 검토했으며 사용자 외형 승인은 아직 받지 않았다.

## 생성 기록

- [실제 프롬프트와 참조](Source/prompts.json)
- [소켓 수정 요청](Source/socket-revision-prompts.json)
- [원본 경로·선택 후보·호출별 출처](Source/provenance.json)

`Source/generation-requests.json`은 초기에 준비한 요청안이다. 실제 호출 프롬프트는 `prompts.json`과 `socket-revision-prompts.json`을 기준으로 한다.

## 실제 네이티브 파생

생성 원본의 형태를 보존해 기존 native 크기(벽/바닥/소켓36×36, 추30×32, 구슬26×26)로 정리했다. 알파128 크롭, premultiplied 면적 평균 축소, 약한 샤픈, 공유 팔레트, 제한적인 저대비 픽셀 정리를 사용했다. 벽/바닥은 셀 전체를 채우고, 추 손잡이·발, 구슬 윤곽과 큰 이음선, 소켓의 빈 중심을 보존했다. 사각 소켓의 얇은 황동 림은 실제 원본의 밝은 픽셀 면적을 반영해 살렸다. 임의 도형으로 다시 그린 것이 아니다.

모든 출력 픽셀의 생성 원본 영역·알파·팔레트·정리 내역과 SHA를 [파생 명세](Source/Derivation/native-derivation.json)에 기록했다. [네이티브 원본](Source/Native), [원본 대조](QA/native-source-comparison.png), [색/실제 크기 미리보기](QA/native-contact.png), [흑백 비교](QA/native-grayscale-contact.png)를 보존한다. 총48색 중47색은 생성 원본에서 파생했고, 빨간 오배치 표시1색은 기존 처리의 변경 없는 재사용이다.

## 애니메이션과 게임 연결

31클립·77프레임을 [Clips](Clips)와 `Assets/Resources/ReturnV2/ReadabilityArtV2`에 내보냈다. 기존 클립명·duration·크기·게임 배치를 유지한다. 추는 손잡이1px 움직임, 구슬은 고정 광원을 유지한 내부 원본 선의 정수 이동, 소켓은 기존 원본 림의 순차 점등, 벽은 연결 방향의 원본 내부 픽셀 연장이다. Piskel·다중 프레임 APNG·프레임 델타·네이티브 원본 대비 편집 내역을 재생 대조했다. [출력 출처](Clips/export-manifest.json)와 [상태 비교](QA/clip-all-state-contact.png)를 참고한다.

게임은 v2를 우선 읽고, v2가 없을 때만 보존된 v1으로 돌아간다. 티크V10·문지기V7 PNG, 퍼즐 규칙, 낙하 반격, 체력·키 입력은 외형 교체에서 변경하지 않았다. v1을 소급해 이미지 우선 제작물로 표시하지 않는다.

## 검증 및 남은 사용자 확인

- [독립 파일 검사](QA/audit-all-report.json):1,075개 통과/실패0. 원본 SHA, 크롭, 픽셀 출처, 팔레트/알파, 크기/시간, 편집 원본 재생, Unity 설정, 벽 연결.
- Mac Unity 빌드 성공: `unity/TiqueReturnPrototype/Builds/MacV10ReadabilityImageFirstV2/TiqueReturn.app` (로컬 산출물, Git 제외).
- [실제 카메라 검증](QA/runtime-validation.json): v2 리소스를 강제 확인한 퍼즐3개 + 낙하 반격 장면13개, 전체 자동 흐름 Ending·HP5/5·106.40초. 이는 자동 공략 시간으로, 사람의 게임 완료 시간/재미 평가가 아니다.
- [이전/현재 실제 화면](QA/runtime-comparison.png), [흑백 실제 화면](QA/runtime-comparison-grayscale.png). PNG는 Unity world-camera640×360 출력이며 IMGUI·데스크톱·물리 키 입력은 검사 범위에서 제외한다.

소켓 점등의 충분한 가시성, 밀기/회전의 자연스러움, 배경과의 조화는 사용자와 플레이하며 확인한다. 파일 검사와 자동 엔딩 통과를 외형 승인/재미 검증으로 취급하지 않는다.

## 재현

저장소 루트에서 Pillow·NumPy가 있는 Python으로 다음을 실행한다. 새 이미지를 생성하는 것이 아니라 보존된 실제 생성 원본을 재파생하는 명령이다.

```sh
python3 tools/art/derive_readability_native_v2.py
python3 tools/art/export_readability_v2.py
python3 tools/art/check_readability_v2.py --phase all
```

생성 원본 캐시와 직접 비교하는 검사는 제작 PC의 추가 증거다. 다른 PC에서는 저장소의 원본 PNG와 `QA/audit-source-baseline.json` SHA를 기준으로 한다. 실제 호출 프롬프트는 위 생성 기록에 있다. [게임 연결 명세](../../unity/TiqueReturnPrototype/Docs/WorkOrderV01/readability-image-first-v2.md)도 참고한다.
