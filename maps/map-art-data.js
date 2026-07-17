window.CLOCKWORK_MAP_ART = Object.freeze({
  act1: [
    {
      id: "limbus",
      title: "림부스",
      image: "../art/concepts/act1/01-limbus-background-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=limbus",
      status: "1차 승인",
      description: "도심 자동 수거관의 종점이 된 거대한 폐기 구역. 차가운 고철 평원과 압축 잔해가 중심이다.",
      roomIds: ["act1-room-002", "act1-room-003", "act1-room-052"]
    },
    {
      id: "limbus-caligo-bridge",
      title: "림부스-칼리고 교량",
      image: "../art/concepts/act1/02-limbus-caligo-bridge-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=limbus-caligo-bridge",
      status: "1차 승인",
      description: "폐기 구역과 생활권 사이의 오래된 통근로. 교량 아래에는 유해한 초록색 렌티움 오염수가 흐른다.",
      roomIds: ["act1-room-006"]
    },
    {
      id: "caligo",
      title: "칼리고",
      image: "../art/concepts/act1/03-caligo-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=caligo",
      status: "콘셉트 후보",
      description: "궁핍하지만 정돈된 지하 생활권. 재사용 구리판, 생활 배관, 호박색 정비등이 마을의 온기를 만든다.",
      roomIds: ["act1-room-004", "act1-room-008", "act1-room-009", "act1-room-010", "act1-room-011"]
    },
    {
      id: "caligo-maintenance-shaft",
      title: "칼리고 하강 정비축",
      image: "../art/concepts/act1/04-caligo-maintenance-shaft-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=caligo-maintenance-shaft",
      status: "콘셉트 후보",
      description: "칼리고의 생활 배관이 교차로 대공동으로 내려가는 수직 전이 구간. 하강은 가능하지만 갈고리 전에는 역행할 수 없다.",
      roomIds: ["act1-room-012"]
    },
    {
      id: "crossroads-cavern",
      title: "교차로 대공동",
      image: "../art/concepts/act1/05-crossroads-cavern-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=crossroads-cavern",
      status: "콘셉트 후보",
      description: "오수 낙하 계통과 여러 지하 시설이 만나는 자연 공동. ACT1 탐색의 중심 허브다.",
      roomIds: ["act1-room-001", "act1-room-013", "act1-room-014", "act1-room-015"]
    },
    {
      id: "water-treatment",
      title: "정수장치",
      image: "../art/concepts/act1/06-water-treatment-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=water-treatment",
      status: "콘셉트 후보",
      description: "칼리고의 생존을 떠받치던 정수 설비. 가동 전 오염수는 초록색이고, 렌토 격파 후 정화수는 맑은 청록색으로 바뀐다.",
      roomIds: ["act1-room-016", "act1-room-018", "act1-room-019", "act1-room-020", "act1-room-021", "act1-room-022"]
    },
    {
      id: "b24-drainage",
      title: "B24 배수 구간",
      image: "../art/concepts/act1/07-b24-drainage-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=b24-drainage",
      status: "콘셉트 후보",
      description: "정수장치 재가동으로 수위가 내려간 뒤 드러나는 하강 통로. 물때, 진흙, 배수 철판이 심층 진입을 예고한다.",
      roomIds: ["act1-room-023", "act1-room-024", "act1-room-033", "act1-room-051"]
    },
    {
      id: "deep-hunter-domain",
      title: "지하심층·사냥꾼 영역",
      image: "../art/concepts/act1/08-deep-hunter-domain-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=deep-hunter-domain",
      status: "콘셉트 후보",
      description: "넓고 낮은 진흙 습지와 매복 흔적이 이어지는 사냥꾼의 영역. 탁한 금색 결정 흔적은 기억 회수를 예고한다.",
      roomIds: ["act1-room-025", "act1-room-026", "act1-room-027", "act1-room-028"]
    },
    {
      id: "terminus",
      title: "터미너스",
      image: "../art/concepts/act1/09-terminus-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=terminus",
      status: "콘셉트 후보",
      description: "B23까지만 굴착된 서부 수직 화물 시설. 황동 레일과 적재 발판을 따라 지상 화물 승강장으로 올라간다.",
      roomIds: ["act1-room-005", "act1-room-029", "act1-room-030", "act1-room-031", "act1-room-032"]
    },
    {
      id: "optional-waste-sorter",
      title: "구 폐기물 선별장",
      image: "../art/concepts/act1/10-waste-sorter-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=optional-waste-sorter",
      status: "콘셉트 후보 · 선택 탐사",
      description: "림부스에서 갈고리 획득 후 재방문하는 폐쇄 선별 시설. 컨베이어, 자력 분류기, 압축 장치가 중심이다.",
      roomIds: ["act1-room-036", "act1-room-037", "act1-room-038", "act1-room-039"]
    },
    {
      id: "optional-aqueduct",
      title: "폐쇄 송수로",
      image: "../art/concepts/act1/11-closed-aqueduct-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=optional-aqueduct",
      status: "콘셉트 후보 · 선택 탐사",
      description: "갈고리로 진입하는 긴 수평 송수 계통. 원형 관, 밸브, 수압 전환 퍼즐이 정수장치와 차별화된다.",
      roomIds: ["act1-room-034", "act1-room-040", "act1-room-041", "act1-room-042", "act1-room-043", "act1-room-044"]
    },
    {
      id: "optional-dig-site",
      title: "심층 굴착지",
      image: "../art/concepts/act1/12-deep-dig-site-v1.png",
      prototype: "../prototypes/act1-world-slice/index.html?region=optional-dig-site",
      status: "콘셉트 후보 · 선택 탐사",
      description: "더블점프로 진입하는 건조한 폐굴착 구역. 천공기 프레임과 광차 레일이 심층 습지와 다른 이동 리듬을 만든다.",
      roomIds: ["act1-room-045", "act1-room-046", "act1-room-047", "act1-room-048", "act1-room-049", "act1-room-050"]
    }
  ]
});
