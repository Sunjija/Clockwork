# 문지기 동작 이미지

각 폴더에는 순서대로 재생하는 투명 배경 PNG `frame-0.png`–`frame-7.png`와 반복 확인용 `preview.gif`가 있습니다. PNG는 192×192px입니다.

| 폴더 | 동작 |
|---|---|
| idle | 대기 |
| walk | 걷기 |
| rolling_charge | 입을 닫은 수평축 회전 돌진 |
| jaw_shockwave | 턱 공격 · 충격파 |
| drop_slam | 도약 · 내려찍기 |
| stagger_recover | 비틀거림 · 회복 |
| hit_reaction | 피격 반응 |
| defeat | 쓰러짐 |

`sprite-sheet-alpha.png`는 위 순서로 8행×8열 배치한 전체 스프라이트 시트입니다. 셀 크기는 192×192px입니다.

GIF는 자세 검토를 위한 미리보기입니다. 전투 이동, 판정, 모션블러/VFX는 포함하지 않으며 게임 코드에는 적용하지 않았습니다. 이 폴더는 검토용으로 정리한 에셋 묶음이며, 기존 생성 원본은 로컬 작업 폴더에 별도로 보존되어 있습니다.
