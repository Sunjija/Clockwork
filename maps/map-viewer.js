(() => {
  "use strict";

  const MAPS = [
    { id: "world-atlas", label: "전체 전도", href: "world-atlas.html" },
    { id: "act1", label: "ACT1 지하", href: "act1-underground.html" },
    { id: "act2", label: "ACT2 지상", href: "act2-surface.html" },
    { id: "act3", label: "ACT3 타워", href: "act3-tower.html" }
  ];

  const FILTERS = [
    { id: "boss", label: "보스" },
    { id: "memory", label: "기억" },
    { id: "save", label: "세이브" },
    { id: "treasure", label: "보상" },
    { id: "gate", label: "잠금" }
  ];

  const body = document.body;
  const root = document.documentElement;
  const wrap = document.querySelector(".wrap");
  const header = wrap?.querySelector(":scope > header");
  const scroller = wrap?.querySelector(".map-scroll");
  const canvas = scroller?.querySelector(".canvas");

  if (!wrap || !header || !scroller || !canvas) return;

  const currentMap = body.dataset.mapId || inferMapId();
  const rooms = [...canvas.querySelectorAll(".room")];
  const activeFilters = new Set();
  const initialUnit = numberFromCss("--u", 56);
  const canvasColumns = Math.max(1, canvas.getBoundingClientRect().width / initialUnit);
  let zoom = 1;
  let selectedRoom = null;
  let toastTimer = 0;

  body.classList.add("map-viewer-ready");
  enrichRooms();
  const tools = buildTools();
  const criticalFlow = buildCriticalFlow();
  const inspector = buildInspector();
  const dialog = buildNodeDialog();
  const toast = buildToast();
  header.insertAdjacentElement("afterend", tools);
  if (criticalFlow) tools.insertAdjacentElement("afterend", criticalFlow);
  wrap.append(inspector, dialog, toast);
  addSkipLink();
  bindRoomInteractions();
  updateFilterState();

  window.ClockworkMapViewer = Object.freeze({
    exportData,
    focusRoom,
    getRooms: () => exportData().rooms,
    resetView
  });

  function inferMapId() {
    const path = location.pathname.toLowerCase();
    return MAPS.find((map) => path.includes(map.id))?.id ||
      (path.includes("act1") ? "act1" : path.includes("act2") ? "act2" : path.includes("act3") ? "act3" : "map");
  }

  function numberFromCss(name, fallback) {
    const value = Number.parseFloat(getComputedStyle(root).getPropertyValue(name));
    return Number.isFinite(value) ? value : fallback;
  }

  function roomName(room) {
    return room.querySelector(".nm")?.textContent.replace(/\s+/g, " ").trim() || room.id;
  }

  function collectTags(room) {
    const tags = new Set();
    const classNames = [...room.classList];
    classNames.filter((name) => name !== "room").forEach((name) => tags.add(name));
    if (room.querySelector(".chip.boss")) tags.add("boss");
    if (room.querySelector(".chip.mem, .chip.echo")) tags.add("memory");
    if (room.querySelector(".chip.cp")) tags.add("save");
    if (room.dataset.reward || room.querySelector(".chip.trs, .chip.key, .chip.slot, .chip.abl, .chip.auth, .chip.restore")) tags.add("treasure");
    if (room.dataset.requires || room.querySelector(".chip.lock, .chip.lockG, .chip.lockD, .chip.unk")) tags.add("gate");
    return [...tags];
  }

  function enrichRooms() {
    rooms.forEach((room, index) => {
      if (!room.id) room.id = `${currentMap}-room-${String(index + 1).padStart(3, "0")}`;
      const name = roomName(room);
      const tags = collectTags(room);
      room.dataset.nodeName = name;
      room.dataset.tags = tags.join(" ");
      room.dataset.search = `${name} ${room.textContent} ${room.id} ${tags.join(" ")}`.toLocaleLowerCase("ko");
      room.tabIndex = 0;
      room.setAttribute("role", "button");
      room.setAttribute("aria-label", `${name} 상세 보기`);
    });
  }

  function buildTools() {
    const tools = document.createElement("section");
    tools.className = "map-viewer-tools";
    tools.setAttribute("aria-label", "맵 도구");
    tools.innerHTML = `
      <div class="map-viewer-tools__top">
        <nav class="map-viewer-nav" aria-label="맵 전환">
          ${MAPS.map((map) => `<a href="${map.href}"${map.id === currentMap ? ' aria-current="page"' : ""}>${map.label}</a>`).join("")}
        </nav>
        <div class="map-viewer-controls" aria-label="보기 제어">
          <button class="map-viewer-action" type="button" data-action="zoom-out" title="축소" aria-label="축소">−</button>
          <button class="map-viewer-action" type="button" data-action="zoom-in" title="확대" aria-label="확대">＋</button>
          <button class="map-viewer-action" type="button" data-action="fit" title="화면 너비에 맞추기" aria-label="화면 너비에 맞추기">↔</button>
          <button class="map-viewer-action" type="button" data-action="reset" title="보기 초기화" aria-label="보기 초기화">↺</button>
          <button class="map-viewer-action map-viewer-action--wide" type="button" data-action="list" title="노드 목록 열기">노드</button>
          <button class="map-viewer-action map-viewer-action--wide" type="button" data-action="export" title="맵 데이터를 JSON으로 내보내기">JSON</button>
          <button class="map-viewer-action" type="button" data-action="print" title="인쇄" aria-label="인쇄">⎙</button>
        </div>
      </div>
      <div class="map-viewer-tools__bottom">
        <label class="map-viewer-search">
          <span class="sr-only" hidden>방 검색</span>
          <input type="search" autocomplete="off" placeholder="방·지역·ID 검색" aria-label="방·지역·ID 검색">
          <button class="map-viewer-search__clear" type="button" title="검색 지우기" aria-label="검색 지우기">×</button>
        </label>
        <div class="map-viewer-filters" aria-label="노드 필터">
          ${FILTERS.map((filter) => `<button class="map-viewer-filter" type="button" data-filter="${filter.id}" aria-pressed="false">${filter.label}</button>`).join("")}
        </div>
        <output class="map-viewer-status" aria-live="polite"></output>
      </div>`;

    const input = tools.querySelector("input[type='search']");
    input.addEventListener("input", updateFilterState);
    tools.querySelector(".map-viewer-search__clear").addEventListener("click", () => {
      input.value = "";
      input.focus();
      updateFilterState();
    });

    tools.querySelectorAll("[data-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        const filter = button.dataset.filter;
        activeFilters.has(filter) ? activeFilters.delete(filter) : activeFilters.add(filter);
        button.setAttribute("aria-pressed", String(activeFilters.has(filter)));
        updateFilterState();
      });
    });

    tools.addEventListener("click", (event) => {
      const button = event.target.closest("[data-action]");
      if (!button) return;
      const actions = {
        "zoom-out": () => setZoom(zoom - 0.1),
        "zoom-in": () => setZoom(zoom + 0.1),
        fit: fitToWidth,
        reset: resetView,
        list: () => dialog.showModal(),
        export: downloadJson,
        print: () => window.print()
      };
      actions[button.dataset.action]?.();
    });

    return tools;
  }

  function buildInspector() {
    const panel = document.createElement("aside");
    panel.className = "map-node-inspector";
    panel.hidden = true;
    panel.setAttribute("aria-live", "polite");
    panel.innerHTML = `
      <div class="map-node-inspector__head">
        <div><h2></h2><div class="map-node-inspector__id"></div></div>
        <button class="map-node-inspector__close" type="button" title="닫기" aria-label="상세 닫기">×</button>
      </div>
      <div class="map-node-inspector__meta"></div>
      <div class="map-node-inspector__text"></div>`;
    panel.querySelector("button").addEventListener("click", closeInspector);
    return panel;
  }

  function buildCriticalFlow() {
    const flowRooms = rooms
      .filter((room) => room.dataset.flowOrder)
      .sort((a, b) => Number(a.dataset.flowOrder) - Number(b.dataset.flowOrder));
    if (!flowRooms.length) return null;

    const section = document.createElement("section");
    section.className = "map-critical-flow";
    section.setAttribute("aria-label", "플레이어 필수 진행 흐름");
    section.innerHTML = `
      <div class="map-critical-flow__head">
        <strong>필수 진행 흐름</strong>
        <span>노드를 누르면 맵에서 위치를 확인합니다</span>
      </div>
      <div class="map-critical-flow__rail">
        ${flowRooms.map((room) => `
          <button type="button" data-room-id="${escapeHtml(room.id)}" data-group="${escapeHtml(room.dataset.flowGroup || currentMap.toUpperCase())}" title="${escapeHtml(roomName(room))}로 이동">
            <span class="map-critical-flow__index">${escapeHtml(room.dataset.flowOrder)}</span>
            <span class="map-critical-flow__label">${escapeHtml(room.dataset.flowLabel || roomName(room))}</span>
            ${room.dataset.flowNote ? `<small>${escapeHtml(room.dataset.flowNote)}</small>` : ""}
          </button>`).join("")}
      </div>`;
    section.addEventListener("click", (event) => {
      const button = event.target.closest("[data-room-id]");
      if (button) focusRoom(button.dataset.roomId);
    });
    return section;
  }

  function buildNodeDialog() {
    const modal = document.createElement("dialog");
    modal.className = "map-node-dialog";
    modal.innerHTML = `
      <div class="map-node-dialog__head">
        <h2>노드 목록</h2>
        <button class="map-node-dialog__close" type="button" title="닫기" aria-label="노드 목록 닫기">×</button>
      </div>
      <div class="map-node-dialog__body">
        <table class="map-node-table">
          <thead><tr><th>방</th><th>ID</th><th>분류</th><th>좌표</th></tr></thead>
          <tbody>${rooms.map((room) => {
            const point = coordinates(room);
            return `<tr><td><button type="button" data-room-id="${room.id}">${escapeHtml(roomName(room))}</button></td><td><code>${room.id}</code></td><td>${escapeHtml(room.dataset.tags || "-")}</td><td>${point.x}, ${point.y}</td></tr>`;
          }).join("")}</tbody>
        </table>
      </div>`;
    modal.querySelector(".map-node-dialog__close").addEventListener("click", () => modal.close());
    modal.addEventListener("click", (event) => {
      if (event.target === modal) modal.close();
      const button = event.target.closest("[data-room-id]");
      if (!button) return;
      modal.close();
      focusRoom(button.dataset.roomId);
    });
    return modal;
  }

  function buildToast() {
    const element = document.createElement("div");
    element.className = "map-toast";
    element.setAttribute("role", "status");
    return element;
  }

  function addSkipLink() {
    if (!scroller.id) scroller.id = `${currentMap}-map`;
    const link = document.createElement("a");
    link.className = "map-skip-link";
    link.href = `#${scroller.id}`;
    link.textContent = "맵으로 이동";
    body.prepend(link);
  }

  function bindRoomInteractions() {
    rooms.forEach((room) => {
      room.addEventListener("click", () => selectRoom(room));
      room.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        selectRoom(room);
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !inspector.hidden) closeInspector();
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "f") {
        event.preventDefault();
        tools.querySelector("input[type='search']").focus();
      }
    });
  }

  function selectRoom(room) {
    selectedRoom?.classList.remove("is-selected");
    selectedRoom = room;
    room.classList.add("is-selected");
    const point = coordinates(room);
    inspector.querySelector("h2").textContent = roomName(room);
    inspector.querySelector(".map-node-inspector__id").textContent = room.id;
    inspector.querySelector(".map-node-inspector__meta").innerHTML = [
      ...room.dataset.tags.split(" ").filter(Boolean),
      room.dataset.requires ? `필요 ${room.dataset.requires}` : "",
      room.dataset.triggerRequires ? `발동 ${room.dataset.triggerRequires}` : "",
      room.dataset.reward ? `보상 ${room.dataset.reward}` : "",
      room.dataset.event ? `이벤트 ${room.dataset.event}` : "",
      `x ${point.x}`,
      `y ${point.y}`,
      `w ${point.w}`,
      `h ${point.h}`
    ].filter(Boolean).map((tag) => `<span>${escapeHtml(tag)}</span>`).join("");
    inspector.querySelector(".map-node-inspector__text").textContent = room.textContent.replace(/\s+/g, " ").trim();
    inspector.hidden = false;
  }

  function closeInspector() {
    inspector.hidden = true;
    selectedRoom?.classList.remove("is-selected");
    selectedRoom = null;
  }

  function coordinates(room) {
    const style = room.style;
    return {
      x: numberFromInline(style.getPropertyValue("--x")),
      y: numberFromInline(style.getPropertyValue("--y")),
      w: numberFromInline(style.getPropertyValue("--w")),
      h: numberFromInline(style.getPropertyValue("--h"))
    };
  }

  function numberFromInline(value) {
    const number = Number.parseFloat(value);
    return Number.isFinite(number) ? number : 0;
  }

  function updateFilterState() {
    const input = tools?.querySelector("input[type='search']");
    const query = (input?.value || "").trim().toLocaleLowerCase("ko");
    const filtering = Boolean(query || activeFilters.size);
    let matchCount = 0;

    rooms.forEach((room) => {
      const queryMatch = !query || room.dataset.search.includes(query);
      const tags = new Set(room.dataset.tags.split(" "));
      const filterMatch = !activeFilters.size || [...activeFilters].some((filter) => tags.has(filter));
      const match = queryMatch && filterMatch;
      room.classList.toggle("is-match", match);
      if (match) matchCount += 1;
    });

    body.classList.toggle("is-filtering", filtering);
    const output = tools?.querySelector(".map-viewer-status");
    if (output) output.textContent = filtering ? `${matchCount} / ${rooms.length}개 방` : `${rooms.length}개 방`;
  }

  function setZoom(nextZoom) {
    zoom = Math.min(1.6, Math.max(0.3, Number(nextZoom.toFixed(2))));
    root.style.setProperty("--u", `${initialUnit * zoom}px`);
    showToast(`확대 ${Math.round(zoom * 100)}%`);
  }

  function fitToWidth() {
    const available = Math.max(240, scroller.clientWidth - 24);
    setZoom(available / (canvasColumns * initialUnit));
    scroller.scrollTo({ left: 0, top: 0, behavior: "smooth" });
  }

  function resetView() {
    setZoom(1);
    scroller.scrollTo({ left: 0, top: 0, behavior: "smooth" });
    activeFilters.clear();
    tools.querySelectorAll("[data-filter]").forEach((button) => button.setAttribute("aria-pressed", "false"));
    tools.querySelector("input[type='search']").value = "";
    closeInspector();
    updateFilterState();
  }

  function focusRoom(roomId) {
    const room = document.getElementById(roomId);
    if (!room) return false;
    room.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    room.focus({ preventScroll: true });
    selectRoom(room);
    return true;
  }

  function exportData() {
    return {
      schemaVersion: 1,
      mapId: currentMap,
      title: document.title,
      exportedAt: new Date().toISOString(),
      rooms: rooms.map((room) => ({
        id: room.id,
        name: roomName(room),
        tags: room.dataset.tags.split(" ").filter(Boolean),
        coordinates: coordinates(room),
        requires: room.dataset.requires || null,
        triggerRequires: room.dataset.triggerRequires || null,
        reward: room.dataset.reward || null,
        event: room.dataset.event || null,
        text: room.textContent.replace(/\s+/g, " ").trim()
      })),
      connections: [...canvas.querySelectorAll(".d, .lk")].map((connection, index) => ({
        id: connection.id || `${currentMap}-connection-${String(index + 1).padStart(3, "0")}`,
        type: connection.classList.contains("d") ? "door" : "link",
        classes: [...connection.classList],
        x: numberFromInline(connection.style.getPropertyValue("--dx")),
        y: numberFromInline(connection.style.getPropertyValue("--dy")),
        length: numberFromInline(connection.style.getPropertyValue("--len")),
        from: connection.dataset.from || null,
        to: connection.dataset.to || null,
        direction: connection.dataset.direction || null,
        requires: connection.dataset.requires || null,
        unlocks: connection.dataset.unlocks || null,
        oneWay: connection.classList.contains("oneway"),
        label: connection.textContent.replace(/\s+/g, " ").trim() || null
      }))
    };
  }

  function downloadJson() {
    const data = JSON.stringify(exportData(), null, 2);
    const url = URL.createObjectURL(new Blob([data], { type: "application/json" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${currentMap}.json`;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
    showToast("JSON을 내보냈습니다");
  }

  function showToast(message) {
    toast.textContent = message;
    toast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 1400);
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }
})();
