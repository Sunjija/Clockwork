# ID 구현 연결표

구현 전 판단은 [id-work-table.md](id-work-table.md)에 보존한다. 230개 ID는 상태/화면 의미이며 230개 새 클립을 뜻하지 않는다. 아래는 실제 연결처와 생략 근거다. 자동 검사·화면 캡처는 통과 여부를 별도 보고하며 사람의 동작 품질 승인을 대신하지 않는다.

| ID | 단위 | 처리 | 실제 자산 | 소스 연결 | 근거 |
|---|---|---|---|---|---|
| TC01 | 기본 대기 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC02 | 눈 감기 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC03 | 눈 감김 유지 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC04 | 눈 뜨기 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC05 | 방향 전환 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC06 | 이동 접지 A | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC07 | 이동 통과·접지 B | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TC08 | 이동 정지 | 원본+눈 ROI 보정 | Idle/Walk, blink-half/closed | ReworkGame.DrawWorld / CorePuzzle.walkAge | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP01 | 빈 칸 확인 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP02 | 한 칸 디디기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP03 | 벽 앞 멈춤 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP04 | 추 접근·손 닿기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP05 | 추 밀기 지지 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP06 | 추 한 칸 밀기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP07 | 추 멈춤·힘 풀기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP08 | 추 밀기 실패 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP09 | 구슬 접촉 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP10 | 구슬 밀어 내기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP11 | 손 놓기·한 칸 전진 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP12 | 구슬 이동 관찰 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP13 | 구슬 밀기 실패 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP14 | 소켓 접촉 확인 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| TP15 | 잘못된 소켓 확인 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| TP16 | 완성 물체 다시 밀기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP17 | 한 수 되돌리기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP18 | 현재 방 초기화 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP19 | 힌트 확인 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| TP20 | 마지막 연결 대기 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TP21 | 회로 복구 반응 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| TP22 | 다음 공간 진입 | 원본+양손 키 이미지 변환 | push-side/up/down 14노출, push-brace 3종, StateArt | CorePuzzle / ReworkModel.AdvancePuzzleVisual / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB01 | 전투 준비 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB02 | 이동 시작 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB03 | 지속 이동 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB04 | 정지·반대 방향 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB05 | 첫 점프 발 밀기 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB06 | 첫 점프 상승 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB07 | 첫 점프 정점 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB08 | 첫 점프 하강 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB09 | 두 번째 점프 재발동 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB10 | 두 번째 상승·정점 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB11 | 두 번째 하강 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB12 | 발판에서 떨어짐 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB13 | 최초 접지 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB14 | 착지 압축·복귀 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB15 | 지상 대시 출발 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB16 | 대시 진행 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB17 | 공중 대시 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB18 | 대시 종료·복귀 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB19 | 대시 재사용 준비 | 준비 표시 생략 | 기존 대시 복귀 / dashReady 규칙 유지 | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 문서 허용 선택 사항. 작은 캐릭터 주변 추가 표식 혼잡을 피함. 대시의 재사용 규칙은 유지. |
| TB20 | 공격 반응·팔 회수 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB21 | 몸통 준비·힘 전달 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB22 | 주먹 유효 타격 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB23 | 명중 반응 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB24 | 빗나감·장갑 접촉 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB25 | 팔·몸통 회복 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB26 | 공격 회피 취소 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB27 | 기둥 접촉·충전 입력 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB28 | 충전 손 회수·유도 이동 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB29 | 피격 접촉·움찔 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB30 | 피격 보호·복귀 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB31 | 전원 저하·실패 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB32 | 재도전 복귀 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| TB33 | 전투 종료 확인 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| TB34 | 귀환문 조작·신원 확인 | 원본+공용 새 픽셀 보완 | Attack/Jump/DoubleJump/Dash, hurt-pose, power-down, bridge | ReworkModel.MoveHero / DrawWorld / ReturnFeedback | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| GB01 | 전원 없는 정지 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB02 | 전력 수신 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB03 | 지지 다리 잠금 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB04 | 전투 대기 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB05 | 목표 방향 탐색 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| GB06 | 돌진 지지·몸 낮추기 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB07 | 돌진 방향 확정 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB08 | 돌진 준비 유지 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB09 | 지지 발 추진 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB10 | 돌진 진행 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB11 | 티크 접촉 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB12 | 일반 벽 충돌·제동 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB13 | 충전 기둥 접촉 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB14 | 충격 흡수 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB15 | 장갑 잠금 해제·열림 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB16 | 노심 노출 유지 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB17 | 노심 첫 접촉·피격 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB18 | 피격 후 열린 자세 회복 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB19 | 장갑 닫기 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB20 | 다리 재지지·잠금 복구 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB21 | 충격파 힘 모으기 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB22 | 마지막 발동 자세 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB23 | 첫 충격파 방출 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB24 | 방출 후 압축 회수 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB25 | 두 번째 방출 재준비 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB26 | 두 번째 방출 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB27 | 충격파 복귀·대기 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB28 | 이륙 접지·압축 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB29 | 상승·다리 모음 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB30 | 낙하 지점 추적 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB31 | 낙하 지점 확정·공중 유지 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB32 | 하강 발동 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB33 | 하강·접지 준비 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB34 | 바닥 접촉·낙하 타격 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB35 | 강화 착지 파형 방출 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB36 | 착지 압축·무게 회수 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB37 | 마지막 노심 타격 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB38 | 전원 차단·지지 정착 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| GB39 | 정지 유지 | 원본+상태 재생 보완 | WardenAuthored 52, StateArt core 12, boot/shutdown | WardenAnimation.Select / BossTick / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H01 | 티크 동력계 외곽 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H02 | 티크 빈 칸 바탕 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H03 | 티크 정상 칸 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H04 | 티크 피해 접수 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H05 | 티크 소실 잔상 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H06 | 티크 저체력 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H07 | 티크 보호 중 표시 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H08 | 티크 마지막 소실 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H09 | 티크 재도전 채움 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H10 | 보스 계기 외곽 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H11 | 보스 정상·빈 칸 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H12 | 보스 3칸 구획 홈 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H13 | 보스 유효 피해 접수 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H14 | 보스 소실 잔상 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H15 | 보스 강화 경계 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H16 | 보스 최종 소실 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H17 | 장면 전환 숨김 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| H18 | 정지·연속 사건 처리 | 이미지 변환 UI 연결 | heart marker, tique-cell 3, iron 3, protect, native panel | ReworkUi.Cells / hudRefillAt / damage times | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F01 | 주먹 가속 흔적 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F02 | 유효 접촉의 첫 점 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F03 | 노심 명중 확장 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F04 | 노심 명중 소멸 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F05 | 닫힌 장갑 접촉 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F06 | 허공 공격 종료 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F07 | 공격 취소 정리 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F08 | 티크 피해 접점 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F09 | 피격 보호 표현 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F10 | 무적 중 접촉 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F11 | 마지막 노심 타격 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F12 | 티크 마지막 피해 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F13 | 첫 점프 추진 먼지 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F14 | 공중 두 번째 추진 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F15 | 착지 먼지 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F16 | 지상 대시 출발 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F17 | 대시 잔상·진행 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F18 | 대시 종료·준비 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 대시 종료 자세 연결; 별도 준비 VFX는 선택 사항으로 생략. |
| F19 | 기둥 충전 접촉 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F20 | 충전 저장·만료 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F21 | 일반 벽 충돌 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F22 | 충전 기둥 충돌 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F23 | 장갑 개방 신호 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F24 | 노심 노출·종료 표시 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F25 | 돌진 추적→확정 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F26 | 충격파 생성·접촉·소멸 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F27 | 낙하 추적→확정 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F28 | 낙하 바닥 충격 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F29 | 강화 추가 파형 신호 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| F30 | 전원 차단·복구 | 이미지 변환 VFX 또는 원본 파생 | hit/hurt/armor/air/dust/boost/bridge/pylon-impact/slam-dust/dash-ghost | ReturnFeedback / ReworkModel / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P01 | 추 접촉 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P02 | 추 마찰 이동 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P03 | 추 정착 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P04 | 구슬 방출 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P05 | 구슬 정지 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P06 | 막힌 밀기 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P07 | 올바른 접속 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P08 | 잘못된 접속 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P09 | 연결 해제 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P10 | 되돌리기·초기화 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P11 | 힌트 강조 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| P12 | 회로 복구·다음 공간 | 이미지 변환 접촉+원본 상태 | friction/weight-settle/orb-release/stop; StateArt socket 12노출 | AdvancePuzzleVisual / WorldArtState / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U01 | 패널 모서리 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U02 | 패널 변·바탕 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U03 | 버튼 기본 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U04 | 버튼 선택·호버 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U05 | 버튼 눌림 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U06 | 버튼 비활성 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U07 | 섹션별 키 캡 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U08 | 행동 아이콘 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U09 | 퍼즐 복구 아이콘 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U10 | 퍼즐 진행 0~3 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U11 | 충전 시간 프레임 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U12 | 충전 시간 채움·만료 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U13 | 노출 시간 프레임 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U14 | 노출 시간·타수 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U15 | 대시 사용 가능 | 준비 표시 생략 | 기존 대시 복귀 / dashReady 규칙 유지 | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 문서 허용 선택 사항. 작은 캐릭터 주변 추가 표식 혼잡을 피함. 대시의 재사용 규칙은 유지. |
| U16 | 안내·실패·완료 카드 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U17 | 제목·귀환 표식 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U18 | 한글 픽셀 글꼴 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U19 | 숫자·영문·키 글리프 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| U20 | 선택 커서·설정 표식 | 이미지 변환 UI+허용된 픽셀 폰트 | panel/button 4state/keycaps/action icons/381glyph atlas | ReworkUi.LoadPixelUi / Panel / HandleMenuKeys | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A01 | 104×20 / 셀 8×10 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A02 | 136×20 / 셀 8×10 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 136×20 프레임 / 셀10×12, 3·6 구획 홈. 원문 크기는 출발점이며 네이티브 정수 배치로 확정. |
| A03 | 24×24 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A04 | 24×24 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A05 | 20×16 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A06 | 기존 32×8·136×16 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A07 | 글리프 12–16px 후보 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A08 | 모서리 4×4, 타일 4×4, 표식 8–16px | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A09 | 프레임 약 40×6·88×6 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 40/88 네이티브 채움 폭의 정수 클리핑, 공용9px 패널 프레임. |
| A10 | 20×16 이내 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A11 | 24×12 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용32×16 먼지 5노출 / 200ms로 확정. 땅 접점 피벗을 모든 발생처가 공유. |
| A12 | 24×24 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A13 | 32×32 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A14 | 96×24 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A15 | 16×16 / 24×12 | 위 공용 묶음의 자산 인덱스 | Source/Concepts -> Native -> Clips PNG/Piskel/APNG/pixel JSON | art/return-v5-feedback/clip-source-map.json | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| A16 | 워드마크 약 160×32 | 픽셀 글꼴·기존 문으로 구현 | licensed atlas title + StateArt exit | art/return-v5-feedback/clip-source-map.json | 새 생성 글자/대형 워드마크 대신 실제 픽셀 한글과 귀환문을 사용. |
| O01 | 제목 대기·시작 확정 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O02 | 첫 공간·운반 통로 암시 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O03 | 티크 낙하·착지·인지 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O04 | 귀환 기록 표시 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O05 | 단절 회로 식별 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O06 | 희망 반응 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| O07 | 조작 안내 교체 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O08 | 첫 조작권 인계 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O09 | 첫 유효 행동 확인 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O10 | 복구→집행 재가동 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O11 | 전투 확인·재도전 인계 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| O12 | 귀환 문구 회수 | 인게임 상태 연결 | Opening14s / puzzle150-orb270 / clear800 / boot2400 / Enter / exit800 | ReworkModel.Tick / OpeningSequence / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D01 | 통로 낙하 원인 신호 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D02 | 화면 진입 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D03 | 낙하 진행 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D04 | 최초 발 접촉 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D05 | 착지 압축 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D06 | 접지 복귀 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D07 | 낙하 여운 정리 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| D08 | 기록·조작 인계 | 원본 낙하+이미지 변환 통로/먼지 | Jump08/09, Jump10..14 160ms, chute/dust, original Idle | OpeningSequence.DropOffset / LandingFrame / DrawWorld | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A01 | 기존 재사용 우선 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A02 | 기존 재사용 우선, 부족 시 최소 보정 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A03 | 필요, 공용 신규 VFX 후보 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A04 | 필요 여부 실제 화면 판독 후 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| DO-A05 | 조건부 신규 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A06 | 선택·재사용 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| DO-A07 | 선택·재사용 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 새 본체 과장 연기는 생략. 기본형·방향·장치/문구의 기존 상태를 공유함. |
| DO-A08 | 기존 픽셀 가림 재사용 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A09 | 기존 계획 재사용 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A10 | 기존 우선, 픽셀 자산 아님 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
| DO-A11 | 기존 동작/장치 재사용 | 재사용·공용 연결 | 원본 Jump/Idle, chute/dust, pixel overlay, licensed glyphs, original land sound | OpeningSequence / ReturnFeedback / ReworkUi | 공용 노출·상태로 연결. 독립 새 클립 수와 ID 수를 혼동하지 않음. |
