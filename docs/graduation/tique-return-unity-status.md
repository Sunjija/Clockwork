# 티크: 귀환 — Unity 구현 상태

2026-09-30. 기획 v0.1에 따른 프로젝트를 `unity/TiqueReturnPrototype`에 작성했다.

- 전자석 퍼즐 → 문지기 액션 → 식별 재검사 → 귀환 엔딩.
- 기존 티크 67프레임 유지. 소품 11개 직접 도트 제작, 배경 2종, 합성 효과음 8종.
- 실제 게임 C# 모델 검사 14개, 일반 입력만 사용한 전체 진행, Unity 라이브러리를 참조한 C# 소스 컴파일, 에셋 파일 검사 통과.
- **Unity Personal 활성화 후 실제 임포트·Windows 빌드·720p 실행 자동 검증 완료.** 퍼즐부터 엔딩까지 체력 4/4로 통과했고 자석 포획도 확인했다. 실행 파일은 `unity/TiqueReturnPrototype/Builds/Windows/TiqueReturn.exe`다.
- **5분 체험 길이 미검증.** 정답을 아는 자동 입력의 약 48.3초 완료 기록은 처음 플레이하는 사람의 소요 시간이 아니다.

프로젝트 실행 방법과 검증 범위는 [README](../../unity/TiqueReturnPrototype/README.md), 과정은 [구현 기록](../../unity/TiqueReturnPrototype/Docs/implementation-log.md), 기계 판독용 상태는 [validation-status.json](../../unity/TiqueReturnPrototype/QA/validation-status.json)에 있다. 실제 실행 캡처와 결과는 [Runtime720Visible](../../unity/TiqueReturnPrototype/QA/Runtime720Visible)에 있다. 이전 배치 검토 이미지는 오프라인 합성 자료이며 실제 실행 캡처와 구분한다.

다음 작업은 사람의 키 입력과 음향을 확인하고, 1080p·창 크기 변경 화면을 검토한 뒤 첫 플레이 테스트로 분량과 난이도를 조정하는 것이다. 기존 본편 및 웹 동작 실험실은 수정하지 않았다.
