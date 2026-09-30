"""Repository audit before first-work-order implementation; no asset mutations."""
import hashlib, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'unity/TiqueReturnPrototype'
DOC = PROJECT / 'Docs/WorkOrderV01'
QA = PROJECT / 'QA/WorkOrderV01'
DOC.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)
bundle = ROOT / 'docs/graduation/tique-return-first-work-order-bundle-v0.1.md'
text = bundle.read_text(encoding='utf-8')

def policy(id):
    group = re.sub(r'\d+$', '', id); n = int(re.search(r'\d+$', id)[0])
    if group == 'TC':
        return ('정적 Idle/좌우 반전/Walk 원본', '신규 눈 픽셀만' if n in (2,3,4) else '재사용·재생 연결', '눈 ROI 밖 기본형 고정; 80/100/80ms; 이동 거리로 Walk 선택', 'TiqueMotion / 기본형 ROI·프레임·입력 전환 검사')
    if group == 'TP':
        new = n in (3,4,5,6,7,8,9,10,11,12,13,21)
        return ('CorePuzzle 규칙; 현재 본체는 Idle/Walk만 선택', '신규 접촉/밀기 키 포즈 + 기존 상태' if new else '재사용·사건 연결', '150/270ms 유지; 실패 이력 없음; 구슬 손 놓기/플레이어 도착 분리', 'CorePuzzle / PuzzleMotion / 네 방향 접점·undo·reset')
    if group == 'TB':
        new = n in (27,28,29,31,34)
        return ('ReworkModel.MoveHero + ReturnModel.Pose, 67 PNG; 피격은 깜빡임만', '신규 접촉·움찔·전원 저하' if new else '원본 부분 재생·전환 수정', '기존 속도/HP/시간 유지; 대시→점프→공격→상호작용; 즉시 취소', 'TiqueMotion / 이벤트·사거리·점프·취소·재도전 검사')
    if group == 'GB':
        new = n in (1,2,3,38)
        return ('WardenAnimation + 52 PNG + powered-down; 기동 없음', '신규 전력 단계 + 원본 포즈' if new else '원본 부분 재생·사건 연결', '벽/기둥 결과 분리; 노출 본체/노심 채널 분리; 확정 방향/좌표 고정', 'WardenAnimation / 예고·착지·노출·강화·차단 검사')
    if group == 'H':
        return ('IMGUI 단색 HP 사각형 5/9칸', '신규 픽셀 HUD 타일·상태', '실제 HP 즉시; 빈 칸 위 소실 윤곽만 200ms; 3칸 구획; 보호 표시', 'PixelUi / HP 5→0,9→0·강화·pause·retry 검사')
    if group == 'F':
        if n in (6,7,10):
            return ('피해 불가/취소 규칙 일부 있음; 접점 효과 없음', '사건 처리·신규 이미지 생략', '허공/취소/무적은 새 성공 스파크 없음; 주먹 호만 종료', 'FeedbackEvents / 이벤트 중복·거짓 명중 검사')
        if n in (20,24,30):
            return ('StateArt 기둥/노심/문/배경', '기존 도트 재사용 + 상태 연결', '37클립 중복 제작 생략; 게이지/차단 전환만 보완', 'WorldArtState / 장치 상태·시간 검사')
        return ('기존 경고/노심 내부 반응; 독립 접점·먼지·잔상 없음', '신규 네이티브 VFX 또는 원본 잔상', '사건 접점/방향 저장; hit-stop 접촉 핵 유지; pause 동결; 위험 위 가림 제한', 'FeedbackEvents / PNG·시간·접점·입력 전환 검사')
    if group == 'P':
        if n in (7,8,9):
            return ('socket-connect/filled/wrong/empty 도트', '재사용; 중복 성공/분리 효과 생략', '도착 후 연결; 떠나면 즉시 empty; 색+모양 이미 구별', 'WorldArtState / 도착·undo·wrong 검사')
        return ('물체 moving/배경 power 상태; 전용 접점 효과 없음', '공용 먼지·접촉·복구 표식 제작', '같은 사건 공유; 실패 수 증가 없음; reset/undo 오래된 효과 제거', 'PuzzleMotion / FeedbackEvents / 복구·도착 검사')
    if group == 'U':
        return ('OS Malgun Gothic/GUI.skin.button/1280 좌표 GUI', '신규 픽셀 UI 키트·배포 가능한 글꼴', '640×360 native 합성; 정수 viewport; 타일 패널; 키보드 선택/눌림/비활성', 'PixelUi / 실제 문자열 글리프·한글·720/1080/비정수 창')
    if group == 'O':
        return ('Title→Puzzle 즉시; Arrival 자동 6초; 귀환문 800ms', '신규 Opening·기동/안내 하위 상태', '14초 표시 오프셋; 같은 첫 칸; 새 Enter; HP/퍼즐 불변; 인계 입력 제거', 'OpeningSequence / 자연·각 구간 skip·pause·retry')
    if group == 'D':
        return ('Jump 08–14 후보와 첫 퍼즐 발 좌표', '기존 포즈 재사용 + 오프셋·공용 먼지', '하강/접지 구간만; (32,56) 기준; 착지 사건 1회; 논리 상태 불변', 'OpeningSequence / 발 접점·landing 이벤트·skip')
    if group == 'DO-A':
        if n in (1,2):
            return ('직접 본 Jump 08–14 PNG', '기존 하강·착지 재사용', '추가 전신 포즈 생략: 하강과 접지 복귀 구간이 이미 존재; 실제 화면 비교', 'baseline-poses.png / 발 접점·비율 검사')
        if n == 7:
            return ('없음', '별도 접촉선 생략', '작은 먼지로 접지 설명; 공격/위험처럼 보이는 선 추가하지 않음', '착지 실제 크기 검수')
        if n in (3,4,5,6):
            return ('독립 먼지/그림자/상단 통로 없음', '공용 먼지·그림자·통로 제작', '발 높이/운반 원인 보강; 새 지형/물리 없음', 'Feedback native / Opening 실제 화면')
        return ('기존 land/switch·StateArt 문/복구 배경', '기존 사건·UI 공유', '영상/보스/새 장소 중복 제작 생략', 'OpeningSequence / 사건·입력·귀환 검사')
    return ('부록 B의 신규 자산 후보; 현재 독립 묶음 없음', '공용 native 제작; A16은 글꼴 제목/귀환 아이콘 공유', '상태 수를 클립 수로 합산하지 않음; PNG/JSON/Piskel/APNG/변경 좌표', 'Feedback manifest / 원본 보존·픽셀·시간 검사')

rows={}
for line in text.splitlines():
    m=re.match(r'\|\s*((?:TC|TP|TB|GB|H|F|P|U|O|D|DO-A|A)\d{2})\b[^|]*\|',line)
    if m and m[1] not in rows:
        cells=[x.strip() for x in line.strip('|').split('|')]
        rows[m[1]]=cells
assert len(rows)==230,(len(rows),list(rows))
out=['# 첫 작업 지시 v0.1 — 구현 전 ID 작업표','',
     '기준: origin/main 7d83949. 통합 번들 1,208줄·통합 지시·부록 A/B/C 전체를 직접 읽고 소스를 조사했다. 아래는 **구현 전** 판단이며 완료 보고가 아니다. 기존 사용자 실험 디렉터리는 보존한다.', '',
     '티크 67 PNG·문지기 52 PNG·StateArt 187 PNG는 별도 SHA-256로 보존한다. 게임 규칙과 캐릭터 비율은 유지한다. 표의 규범 조건·시간은 원문 ID의 내용이며 접점은 티크 (32,56), 문지기 발 132px, 퍼즐 공통 발 변환을 사용한다.', '',
     '| ID | 단위 | 현재 구현/그림 | 제작 판단·근거 | 발생·시간·접점 계약 | 구현/검증 연결 |',
     '|---|---|---|---|---|---|']
for id,cells in rows.items():
    current,strategy,reason,check=policy(id)
    contract=' / '.join(cells[2:]).replace('|','/')
    out.append(f'| {id} | {cells[1]} | {current} | {strategy}: {reason} | {contract} | {check} |')
(DOC/'id-work-table.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
(QA/'id-work-table.json').write_text(json.dumps({id:dict(name=cells[1],sourceContract=cells[2:],policy=policy(id)) for id,cells in rows.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for rel in ('Return/Tique','ReturnV2/WardenAuthored','ReturnV2/StateArt'):
    files += list((PROJECT/'Assets/Resources'/rel).rglob('*.png'))
files += [PROJECT/'Assets/Resources/Return/clips.json',PROJECT/'Assets/Resources/ReturnV2/WardenAuthored/clips.json',PROJECT/'Assets/Resources/ReturnV2/StateArt/clips.json']
baseline={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(QA/'original-sha256.json').write_text(json.dumps(baseline,indent=2)+'\n',encoding='utf-8')
print(f'Created pre-implementation table for {len(rows)} IDs; recorded {len(files)} source hashes.')
