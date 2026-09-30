# 티크 V10 — sprite-gen 기반 재제작

V8/V9는 사용자에게 거절된 시안이다. 파일 검사 통과를 자연스러운 모션의 완료 판정으로 사용하지 않는다. V10은 기존 결과의 원인을 수정하는 별도 제작본이며, 원본과 실패 이력은 보존한다.

## 기준과 제작 방법

사용자가 요청한 [aldegad/sprite-gen](https://github.com/aldegad/sprite-gen)의 SKILL.md와 workflow, pixel-unfake, motion QA 문서를 직접 읽었다. 참조 버전은 `bc64939c6e46a9679bb6569f40524d8a84c88160`, 스킬2.11.0이다. 외부 복제본과 가상환경은 게임 저장소 밖에 두었다.

이전 방식은 머리·몸·다리 구간을 서로 다른 높이로 맞추고 머리/몸 사각형을 덮어썼다. 발 길이와 관절이 프레임마다 바뀌고, 손이 얇거나 사라져 보이는 결과를 만들었다. 이 구현은 V10에 사용하지 않는다.

1. 승인된 원본64×64 PNG를 유일한 디자인/픽셀 밀도 기준으로 사용한다. 참고 첨부만 정수 NEAREST16배 확대한다.
2. 각 동작의 중요한 전신 자세를 **한 장씩** 실제 이미지 생성한다. 영상이나 완성 애니메이션 시트를 생성하지 않는다.
3. 실제 sprite-gen `prepare`/`extract`의 전신 분리와 pixel-unfake를 사용한다. 팔레트는 원본13색으로 고정한다. 감지 오류·물리캡 경고를 그대로 성공 판정하지 않는다.
4. 손 끝/손목, 작은 입·눈·하트 클러스터와 발 윤곽을 네이티브 픽셀에서 수정한다. 수정 전후 픽셀과 입력 PNG를 기록한다. 머리/가슴 전체 사각형 덮기나 부위별 리사이즈를 하지 않는다.
5. 중간 자세는 선택된 전신 이미지에서 직접 도트를 수정해 작성한다. 둥근 손은 원래 손의5px 폭 안에서 통일하며 손가락/엄지/장갑을 추가하지 않는다.
6. 실제 C# 선택기와 Unity 화면에서 전환과 접촉을 확인한다. 정적 연결성 검사는 주관적인 자연스러움 판정과 구분한다.

## 보존·연결

대기와 승인된 걷기14장은 원본 PNG 바이트를 유지한다. 양손·양발을 갖춘 Jump15장, DoubleJump13장, Attack12장, Dash12장 및 밀기/피격/잔상 상태를 별도 `TiqueV10` 리소스로 연결한다. 원본 manifest duration 배열과 이동·점프·대시·코요테·입력 버퍼 규칙은 유지한다. 화면에 표시할 프레임은 기존 공격/대시 창과 공중 속도에 맞춰 선택하므로, manifest 시간이 실제 게임의 모든 표시 시간과 같다는 뜻은 아니다.

점프 힘이 적용된 뒤 공중에서 대기·준비 자세를 다시 보이던 선택을 수정한다. 첫45ms에는 이륙/부스트 해제 자세를 보여주고, 상승 속도·정점·하강과 실제 착지에 따라 프레임을 고른다. 준비 자세는 접지에서 사용할 수 있는 제작 프레임으로 보존한다.

눈 깜박임과 동력 꺼짐은 원본 중립 이미지에서 만들어진 기존 상태를 재사용한다. 전체 실루엣은 원본 그대로이며 새 팔레트와 섞이지 않도록 색상만 원본13색으로 고정했다.

## 제작 파일

- [단일 자세 및 네이티브 입력](../../../../art/return-v10-spritegen/identity-contract.json)
- [점프 생성 이력](../../../../art/return-v10-spritegen/jump/generation-provenance.json)
- [점프 픽셀 수정](../../../../art/return-v10-spritegen/jump/native-cleanup.json)
- [점프 전프레임 비교](../../../../art/return-v10-spritegen/jump/qa/jump-contact-5x.png)
- [더블점프 비교](../../../../art/return-v10-spritegen/jump/qa/doublejump-contact-5x.png)
- [대기 기반 상태 재사용](../../../../art/return-v10-spritegen/neutral-state-reuse.json)
- [공격·대시 생성/수정 기록](../../../../art/return-v10-spritegen/actions/qa-notes.md)
- [밀기·피격 생성/수정 기록](../../../../art/return-v10-spritegen/support/qa-notes.md)
- [위쪽 밀기 접촉 오류 수정](../../../../art/return-v10-spritegen/support/up-contact-correction.json)

실제 단일 전신 이미지 생성은 점프10장, 공격/대시11장, 밀기/피격12장, 총33장이다. 그중22개 자세를 선택해 원본 재사용과 중간 픽셀 편집으로17클립·139PNG를 패키징했다. 독립 이미지139장을 생성했다고 표현하지 않는다. 폐기·감지 실패본과 실제 호출 프롬프트도 함께 보존한다.

## 실제 화면에서 다시 찾은 문제

최종 게임 카메라에서 점프 상승·정점·하강·착지, 더블점프, 공중 공격/대시, 지상 회복과 밀기 세 방향을 비교했다. 점프 도중 양손 소실, 기존 얼굴 사각형 경계와 부위별 눌림을 만드는 제작 방식을 제거했다. 새 공격/대시의 작은 입과 하트는 원본 의미 픽셀만 교정했으며 얼굴/몸 사각형을 덮어쓰지 않는다. 실제 앞팔에 가려진 공격 하트3픽셀은 가림으로 기록했다.

첫 전체 GPU 수집에서는 위쪽 밀기 손이 상자 밑면보다4도트 아래에 있었다. root가 타일36px를 실제 상자 높이로 잘못 계산한 것이 원인이다. 실제 battery-moving은30×32이며 밑면은 캐릭터 네이티브 y20 경계다. 손 윗줄을20, 중심 x16/47로 고쳐 밑면 모서리 x17/46에 닿게 했다. 위 밀기14장과 brace-up1장만 수정하고 다른33개 support PNG의 해시는 유지했다. 이전 잘못된15PNG와 비교 이미지를 보존한다. 재빌드의 [최종 위 밀기 캡처](../../QA/V10/FinalWorldCameraV2/Preview/push-up-contact.png)에서 기존4도트 간격이 사라진 것을 확인했다.

아래 밀기는 새로 생성한 실제 웅크린 전신 자세를 사용한다. 고개가 가슴을 가리는 만큼 하트가 작게 보이며, 이를 서 있는 하트 크기로 강제 확대하지 않았다. 어두운 손 테두리와 금빛 상자 경계의 접촉은 작은 화면에서 대비가 낮고, 옆 밀기의 교차한 앞팔은 대기보다 길어 보일 수 있다. 이 두 인상과 전체 자연스러움은 사용자 평가가 남아 있다.

## 검증 결과

| 구분 | 결과와 근거 | 범위 |
|---|---|---|
| 원본·네이티브·패키지 자동 검사 | [native-checks.json](../../QA/V10/native-checks.json):1,062검사, 원본309개 보존,17클립139PNG | 실제 파일·팔레트·알파·연결성·Walk 보존·패키지 일치. 자연스러움 승인 제외 |
| 생산 C# 선택기·모델 | [animation-model-checks.json](../../QA/V10/animation-model-checks.json):45검사,3,505선택 통과 | 실제 선택기·공중/착지/공격/대시 우선순위·기존 규칙 보존. OS 입력과 렌더 모양 제외 |
| Windows Unity 빌드 | Unity6000.5.3f1, `Builds/WindowsV10/TiqueReturn.exe` 생성 | 실제 에디터 batch build 성공. 실행 파일은 로컬 산출물로 Git 제외 |
| 최종 Unity GPU 렌더 수집 | [FinalWorldCameraV2/result.json](../../QA/V10/FinalWorldCameraV2/result.json):14시퀀스503관찰, `ReturnV2/TiqueV10/` 확인 | 생산 입력 명령 fixture와 실제 게임 worldCamera.RenderTexture. IMGUI·데스크톱 창·물리 키 제외 |
| 실제 모션 화면 검토 | [시퀀스 미리보기](../../QA/V10/FinalWorldCameraV2/Preview/index.html)와 프레임 비교 이미지 | 실제 GPU PNG의 위치 추적 크롭. 파일 검사를 자연스러움 판정으로 사용하지 않음 |
| 자동 일반 게임 흐름 | [최종 흐름 결과](../../QA/V10/FinalFlowWorldCameraV2/result.json):Ending, 체력2/5, breaks3, playSeconds68.38 | 최종 빌드의 오프닝→퍼즐→문지기→Ending 자동 진행. 동일한 GPU 캡처 범위 |
| 직접 물리 키 입력 | [direct-input-status.json](../../QA/V10/direct-input-status.json):미검증 | 사용자 Escape로 Computer Use 중단. 이 턴에서 이후 창/키 조작 없음. V9 입력 기록을 V10 증거로 재사용하지 않음 |

[검증 종합 기록](../../QA/V10/validation-summary.json)은 최종 빌드·리소스·생산 소스의 해시와 검증 범위를 기록한다. 전체503개 캡처 PNG는 로컬에 보존하며 Git에는 시퀀스 미리보기, 대표 전체 PNG, 결과/전체 PNG 해시를 포함한다. 이전 V8/V9는 실패 이력의 결과와 비교본을 보존한다.

재현은 [원본 제작 README](../../../../art/return-v10-spritegen/README.md)와 `Tools/Review-TiqueV10.py`, `Tools/Check-Source.ps1`, `Tools/Build-Windows.ps1`을 사용한다. 정상 플레이는 프로젝트의 `Play.cmd`로 시작한다. 이 턴에서는 시작 화면을 사람이 직접 연 상태나 최종 모션의 사용자 승인을 주장하지 않는다.

외부 sprite-gen의 `inspect-motion`은 발 접촉과 일부 부위 ROI가 수동 확인 대상이라는 `needs-review` 결과를 유지한다. 자동 증거를 늘려도 물리 입력이나 주관적인 완성도를 통과 처리하지 않는다.
