# ACT1 비주얼 월드 슬라이스

ACT1의 메인 진행 9구역과 선택 탐사 3구역을 각각 독립된 1280×720 플레이 화면으로 구성한 비주얼 검증용 프로토타입이다.

## 지역 구성

- 메인: 림부스 → 림부스-칼리고 교량 → 칼리고 → 칼리고 하강 정비축 → 교차로 대공동 → 정수장치 → B24 배수 구간 → 지하심층·사냥꾼 영역 → 터미너스
- 선택: 구 폐기물 선별장(갈고리), 폐쇄 송수로(갈고리), 심층 굴착지(더블점프)

화면 좌우 끝을 통과하면 인접한 메인 지역으로 이동한다. 선택 지역의 왼쪽 출구는 해당 분기점으로 복귀한다. 하단 지역 탭은 비주얼 검증을 위한 직접 이동 기능이다.

## 캐릭터

- 기본: `lento-vertical-slice/reference/tique-3q-generated-source.png`
- 공격: `lento-vertical-slice/assets/tique/generated/attack-source.png`
- 점프: `lento-vertical-slice/assets/tique/generated/jump-source.png`
- 대시: `lento-vertical-slice/assets/tique/generated/dash-source.png`
- 배경 제거: 중립 체크 패턴과 크로마키 초록색을 외곽 연결 영역에서만 제거한다.
- 변형: 균일 스케일, 좌우 반전, 회전, 위치 이동만 허용한다.

## 배경

지역 데이터와 이미지 경로는 `data/act1-regions.json`에서 관리한다. 배경 이미지와 충돌 레이어는 독립되어 있으며 임시 발판만 코드로 표시한다. 현재 이미지는 비주얼 방향 검증용 생성 이미지이며 최종 픽셀 아트 에셋으로 확정하지 않는다.
