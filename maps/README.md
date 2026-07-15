# CLOCKWORK map viewer

네 개의 맵은 원래의 절대 좌표 레이아웃과 문서 내용을 유지하면서 `map-viewer.css`와 `map-viewer.js`를 공유한다. 별도 빌드나 서버 없이 HTML 파일을 직접 열어 사용할 수 있다.

## 공통 기능

- 전체 전도/ACT1/ACT2/ACT3 탭 이동
- 방 이름, 본문, 안정 ID 검색
- 보스/기억/세이브/보상/잠금 필터
- 확대, 축소, 너비 맞춤, 보기 초기화
- 키보드 포커스와 방 상세 패널
- 노드 목록과 좌표 확인
- 현재 맵의 방/연결 JSON 내보내기
- A3 인쇄 스타일
- 모바일 가로 스크롤과 접근성 레이블

## 새 맵 추가 규약

1. `<body data-map-id="unique-map-id" data-map-version="2">`를 지정한다.
2. 맵 뷰포트는 `.map-scroll > .canvas` 구조를 사용한다.
3. 방은 `.room`, 이름은 `.room .nm`, 부가 정보는 `.room .ic`으로 작성한다.
4. 방 좌표는 `style="--x:0;--y:0;--w:2;--h:1"` 형식을 사용한다.
5. 문은 `.d`, 비인접 연결은 `.lk`를 사용하고 각각 안정적인 `id`를 부여한다.
6. 문서의 마지막에 `map-viewer.js`, 인라인 스타일 뒤에 `map-viewer.css`를 불러온다.

방에는 필요에 따라 `data-requires`, `data-reward`, `data-event`를 지정한다. 연결에는 `data-from`, `data-to`, `data-direction`, `data-requires`, `data-unlocks`를 사용할 수 있다. 일방통행은 `.oneway` 클래스로 표시하며, 이 값들은 JSON 내보내기에 그대로 포함된다.

최소 구조:

```html
<link rel="stylesheet" href="./map-viewer.css">
<body data-map-id="sample" data-map-version="2">
  <div class="wrap">
    <header>...</header>
    <div class="map-scroll">
      <div class="canvas">
        <div id="sample-room-001" class="room" data-reward="sample_key" style="--x:0;--y:0;--w:2;--h:1">
          <div class="nm">방 이름</div>
          <div class="ic"><span class="chip cp">CP</span></div>
        </div>
        <i id="sample-door-001" class="d h gate oneway"
           data-from="sample-room-001" data-to="sample-room-002"
           data-direction="east" data-requires="sample_key"
           data-unlocks="sample_shortcut" style="--dx:2;--dy:.5"></i>
      </div>
    </div>
  </div>
  <script src="./map-viewer.js"></script>
</body>
```

## 데이터 API

브라우저에서 `window.ClockworkMapViewer.exportData()`를 호출하면 화면과 같은 방/연결 데이터를 객체로 얻는다. `focusRoom(id)`는 ID로 방을 선택하고, `resetView()`는 검색·필터·확대를 초기화한다.

기존 연결의 출발/도착 방은 좌표만으로 자동 추론하지 않는다. 구현에 사용할 연결부터 `data-from`과 `data-to`를 명시하고, 미입력 연결은 JSON에서 `null`로 내보낸다.
