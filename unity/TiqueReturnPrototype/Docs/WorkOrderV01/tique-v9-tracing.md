# 티크 V9 — 전신 트레이스와 원본 형태 교정, 사용자 거부 기록

2026-09-30. **V9의 시각 품질은 사용자에게 거부됐으며 재작업이 필요하다.** 사용자는 V8의 점프 손 소실과 많은 도트 뭉개짐을 지적했고, V9에서도 중간 프레임의 찌그러짐과 통일성 저하를 반복해서 지적했다. 이후 원본 형태와 손가락 없는 둥근손을 고정해 다시 교정했지만, 최신 평가에서도 점프를 포함한 전체 모션을 거부했다. 다음 작업은 사용자가 요청한 [sprite-gen](https://github.com/aldegad/sprite-gen) 참고 재작업이다. 아래 자동 검사와 캡처 수집 성공은 이 거부 상태를 바꾸지 않는다.

## 디자인과 제작 기준

V8에서는 생성 전신 포즈가 최종 도트로 충분히 이어지지 않고 원본 조각과 연결선 중심으로 조립됐다. V9는 각 구간의 **독립적인 전신 정지 이미지 → 전체 포즈의 실루엣·관절 트레이스 → 원본 모델에 맞춘 픽셀 교정 → 중간 노출 편집 → 실제 Unity 렌더 검토** 순서로 다시 제작했다. 생성 영상이나 완성 시트를 잘라 쓰지 않았다.

사용자의 최신 정정은 다음과 같이 적용했다.

- 원본 티크 한 장을 고정 모델로 사용한다. 생성 참고는 동작을 정하는 자료이며 새로운 얼굴이나 체형으로 채택하지 않는다.
- 정면 머리 31×27, 몸통 21×16, 시안 하트 13×10을 유지한다. 기준 영역은 머리 `(16,8)-(47,35)`, 몸통 `(23,34)-(44,50)`, 하트 `(30,37)-(43,47)`이다. 좌표의 끝은 제외하며 자세에 따른 위치 이동은 허용하되 크기와 내부 픽셀은 원본 기준으로 교정한다.
- 새 동작의 손은 손가락·엄지 없는 4×4 둥근 공이다. 실루엣 행 폭은 `2/4/4/2`, 색은 INK와 GOLD, 손목 쪽만 연결한다. 원본 대기와 원본 중립 끝점의 손은 다시 그리지 않는다.
- 캔버스 64×64, 발 피벗 `(32,56)`, 원본 13색, 이진 알파, Point·무압축·밉맵 없음. 공중에서는 피벗을 유지한 채 접힌 발이 캔버스 안에서 올라간다.
- 승인 걷기 14장과 원본 대기 8장을 보존한다. 원본 자산 309개와 V8도 비교·실패 기록으로 보존한다. 조작·물리·피해·판정 시간은 이번 그림 교정으로 변경하지 않는다.
- 웅크림은 다리의 접힘으로 표현한다. 몸통이나 하트를 납작하게 줄이거나 팔을 늘려 만들지 않는다.

생성 원본 전체를 그대로 축소한 결과가 최종 PNG인 것은 아니다. 전체 포즈를 머리·허리·발과 손 위치에 맞춰 원본 팔레트로 트레이스한 뒤, 생성 이미지마다 달라진 머리·가슴·하트의 픽셀을 원본과 일치하도록 교정했다. 손가락 잔여, 손목 연결, 어깨와 외곽, 접힌 발도 네이티브 해상도에서 정리했다. 이 교정으로 바뀐 픽셀과 소스·프롬프트·해시를 provenance와 delta 파일에 기록했다. 형태 교정이나 연결 검사 통과가 중간 동작의 자연스러움을 보장하지는 않는다.

## 실제 제작 수량

| 영역 | 생성 전신 정지 이미지 | 최종 내보내기에 사용한 포즈 키 | 근거 |
| --- | ---: | ---: | --- |
| 점프·더블점프 | 16 | 14 | [Jump provenance](../../../../art/return-v9-traced/JumpSource/trace-provenance.json): 긴 팔 준비와 높은 팔 착지 2개 거부 보존 |
| 공격·대시 | 8 | 8 | [Action provenance](../../../../art/return-v9-traced/ActionSource/provenance.json), [validation](../../../../art/return-v9-traced/ActionSource/validation.json) |
| 밀기·피격 | 13 | 5 | 초기 7개와 방향/둥근손 재생성 6개. 최종 키는 side-round-contact, push-up-high-round, push-down-round, hurt-recoil, hurt-settle |
| 합계 | 37 | 27 | 생성 횟수와 선택된 전신 키 수를 분리한다. PNG 노출 수는 포즈 키 수가 아니다. |

Support의 [전체 trace provenance](../../../../art/return-v9-traced/SupportSource/trace-provenance.json)는 이전 키까지 10개를 기록하며, 이 10개를 모두 최종 채택했다고 계산하지 않는다. 추가 생성 6개의 원본은 [방향 provenance](../../../../art/return-v9-traced/SupportSource/round-direction-provenance.json)에 남아 있다. 변경 전 PNG와 제작 스크립트는 각 Source의 BeforeDeformationFix / Iterations / Before-consistency-roundhands에 보존했다.

게임 패키지는 [TiqueV9 manifest](../../Assets/Resources/ReturnV2/TiqueV9/clips.json)의 14클립·134PNG다. Idle 8, Walk 14, Jump 15, DoubleJump 13, Attack 12, Dash 12, hurt 3, 방향별 밀기 각14, 방향별 고정 지지 각1, dash-ghost 12로 구성한다. Jump는 800ms, DoubleJump는 710ms, Attack은 460ms, Dash는 440ms이며 기존 개수와 manifest 시간을 유지했다. 새로 생성한 27키에서 노출 유지와 중간 자세 편집을 통해 이 프레임들을 작성했으므로 독립 생성 이미지 134장으로 표현하지 않는다.

## 자동 검사와 실제 게임 증거

| 종류 | 확인 결과 | 증거와 한계 |
| --- | --- | --- |
| 원본·네이티브 자산 | 1,034검사 통과, 원본309 보존, 134프레임·14클립 | [native-checks.json](../../QA/V9/native-checks.json). 팔레트·알파·연결·단계 구분·패키지 검사이며 모션 승인 제외 |
| 정면 모델 등록 | 93프레임 원본 머리31×27·하트13×10 RGBA 일치 | [identity-registration.json](../../QA/V9/identity-registration.json). Walk는 별도 원본 보존 검사, 후면 위 밀기와 청록 잔상은 방향·팔레트 검사로 구분 |
| 생산 C# 선택기·모델 | 45검사, 3,505선택 통과 | [animation-model-checks.json](../../QA/V9/animation-model-checks.json). 렌더 모양·실제 OS 키·주관 품질 제외 |
| 실제 Unity 렌더 수집 | 14시퀀스·503관찰/전체 화면 PNG, 수집 passed=true | [RuntimeReviewFinal720/result.json](../../QA/V9/RuntimeReviewFinal720/result.json), [시퀀스 미리보기](../../QA/V9/RuntimeReviewFinal720/Preview/index.html). 생산 입력 명령을 주는 자동 fixture이며 사람이 직접 플레이한 품질 승인이 아님 |
| 자동 일반 게임 흐름 | Ending, 체력2/5, breaks3, playSeconds68.38 | [RuntimeFlowFinal720/result.json](../../QA/V9/RuntimeFlowFinal720/result.json). V9 실행 결과이며 V8 스모크 결과를 재사용하지 않음 |

렌더 14시퀀스는 idle, walk, jump, double-jump, moving-landing, dash, moving-dash, air-dash, air-attack, attack, hurt, push-side, push-up, push-down이다. 검토 전용 fixture의 최초 전투 보호 점멸을 해제해 캐릭터가 깜빡이는 교란을 줄였다. 일반 게임의 보호·점멸 규칙은 유지했다. 과거 숨긴 창 실행의 캡처 실패는 실패 기록으로 남기며, 실제 화면 근거는 보이는 창에서 수집한 PNG다.

Final720의 시퀀스 contact와 대표 전체 화면을 눈으로 검토했다. 기존 down의 발 전체소실·침하와 up의 예전 손 잔여를 교정한 상태가 화면에 반영됐고, 낙하 중 Jump09/Double08은 하강 자세, 착지 Jump10/Double09는 접지 후 자세였다. 그러나 이는 관찰 범위에 대한 기록이다. 사용자에게 남은 찌그러짐과 어색한 점프가 지적됐으므로 “자연스러움 완료”나 “모든 구간 해결”로 판정하지 않는다.

## 실제 OS 키 기록과 미검증

[ManualKeysFinal/inputs.jsonl](../../QA/V9/ManualKeysFinal/inputs.jsonl)은 실제 OS 키 경로의 생산 상태 기록이다. Arrival/Dead에서 시도한 Z·X·C·이동 등이 반응하지 않은 초기 실패도 삭제하지 않았다. 이후 Combat에서 Left/Right 이동, Z·Space·Up 점프, X 공격, C 대시, E 상호작용/충전, Escape 정지·재개가 반영됐다. 예를 들어 Z/Space/Up은 `jumps=1`과 상승 위치, X는 `attack=true`, C는 `dash=true`, E는 `charged=0/1`, Escape는 `paused=true/false`를 남겼다.

문서 갱신 시 로그는 423행이며 마지막 기록은 실제 E 입력 후 `phase=Ending`, `clock=122.3588`, `moves=40`이다. Z 입력 후 `jumps=2` 관찰도 있지만, 통제된 실제 키 더블점프·coyote 시험을 따로 완료했다고 판정하지 않는다. coyote와 입력 타이밍의 재현성, 사람의 조작감 평가를 위한 추가 검증은 별도 항목이다. OS 키 성공과 자동 503캡처, 자동 Ending 검사, 사용자의 모션 평가는 서로 대체하지 않는다.

## 남은 문제와 작업 상태

- 사용자 최종 평가: V9 전체와 점프 거부. [sprite-gen](https://github.com/aldegad/sprite-gen)을 참고한 재작업 요청을 다음 작업으로 넘긴다.
- Jump05가 실제 선택기에서 약0.133~0.300초 유지되어 접힌 발 포즈가 오래 정지해 보인다. 원본 형태 일치나 PNG 개수만으로 이 노출 문제를 해결했다고 할 수 없다.
- air-dash/dash의 청록 잔상이 뒤팔과 겹쳐 어깨 주변이 복잡하게 보인다. 현재 검사에서 캐릭터 색과 잔상 색을 구분했어도 최종 가독성 승인으로 계산하지 않는다.
- Final720의 down 오른손은 `push-down-0494-fx-push-down-04.png`에서 손끝 x586~589,y342~343과 해당 상자 윗면 사이에 2화면px(1nativepx) 차이가 남았다. 상자 상단의 오른쪽 투명 여백에 따른 접촉 차이다. 오른손1px 교정 이후 별도 Final720b 재캡처·접촉 검증은 최신 사용자 재작업 요청으로 대기 취소했으며 완료로 기록하지 않는다.
- 통제된 실제 키 더블점프/coyote, 사용자가 수용하는 최종 자연스러움·재미 평가는 미검증/미승인이다.

V9 소스·교정·실패·QA 자료를 보존한다. 자동 passed=true나 독립 검토자의 제한된 관찰을 사용자의 품질 거부보다 우선하는 승인으로 사용하지 않는다.
