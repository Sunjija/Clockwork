(() => {
  "use strict";

  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d");
  const areaLabel = document.getElementById("areaLabel");
  const cameraReadout = document.getElementById("cameraReadout");
  const loading = document.getElementById("loading");
  const message = document.getElementById("message");

  const W = 1280;
  const H = 720;
  const WORLD_W = W * 3;
  const PLAYER_SPRITE_SIZE = 106;
  const keys = new Set();
  const pressed = new Set();

  const backgroundFiles = [
    "assets/backgrounds/01-bridge-exit.png",
    "assets/backgrounds/02-scrap-plain.png",
    "assets/backgrounds/03-fall-site.png"
  ];

  const animationDefs = {
    idle: { frames: 4, fps: 6, loop: true },
    run: { frames: 8, fps: 12, loop: true },
    jump: { frames: 7, fps: 12, loop: false },
    attack: { frames: 6, fps: 24, loop: false },
    dash: { frames: 6, fps: 18, loop: false },
    hit: { frames: 6, fps: 13, loop: false }
  };

  const animationRoot = "../lento-vertical-slice/assets/tique/animations";
  const art = { backgrounds: [], animations: {}, ready: false };

  const platforms = [
    { x: 0, y: 540, w: 1280, h: 180, type: "ground" },
    { x: 1280, y: 462, w: 430, h: 258, type: "ground" },
    { x: 1710, y: 500, w: 420, h: 220, type: "ground" },
    { x: 2130, y: 532, w: 430, h: 188, type: "ground" },
    { x: 2560, y: 540, w: 1280, h: 180, type: "ground" },
    { x: 1450, y: 352, w: 220, h: 22, type: "temporary" },
    { x: 2190, y: 390, w: 190, h: 22, type: "temporary" }
  ];

  const areas = [
    { min: 0, max: 1279, name: "교량 출구", room: "ROOM 1/3" },
    { min: 1280, max: 2559, name: "고철 평원", room: "ROOM 2/3" },
    { min: 2560, max: 3839, name: "추락 지점", room: "ROOM 3/3" }
  ];

  const interactables = [
    {
      x: 3540,
      y: 430,
      w: 120,
      h: 110,
      text: "청소 로봇이 티크를 폐기한 투입구다. 현재는 지상 쪽에서 봉인되어 있다."
    },
    {
      x: 42,
      y: 410,
      w: 150,
      h: 130,
      text: "림부스-칼리고 교량으로 이어지는 정비 출구다."
    }
  ];

  const state = {
    cameraX: 2560,
    targetCameraX: 2560,
    lastTime: performance.now(),
    hitboxes: false,
    messageTime: 0,
    player: makePlayer()
  };

  function makePlayer() {
    return {
      x: 3610,
      y: 430,
      w: 34,
      h: 62,
      vx: 0,
      vy: 0,
      face: -1,
      grounded: false,
      coyote: 0,
      dashTime: 0,
      dashCooldown: 0,
      attackTime: 0,
      animation: "idle",
      animationTime: 0
    };
  }

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  const down = (...codes) => codes.some((code) => keys.has(code));
  const consume = (...codes) => codes.some((code) => pressed.has(code));

  function loadImage(src) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error(`이미지를 불러오지 못했습니다: ${src}`));
      image.src = src;
    });
  }

  async function loadArt() {
    art.backgrounds = await Promise.all(backgroundFiles.map(loadImage));
    await Promise.all(Object.entries(animationDefs).map(async ([name, def]) => {
      art.animations[name] = await Promise.all(
        Array.from({ length: def.frames }, (_, index) => loadImage(`${animationRoot}/${name}/frame-${index}.png`))
      );
    }));
    art.ready = true;
    loading.hidden = true;
  }

  function setAnimation(name) {
    if (state.player.animation === name) return;
    state.player.animation = name;
    state.player.animationTime = 0;
  }

  function update(dt) {
    const p = state.player;
    state.messageTime = Math.max(0, state.messageTime - dt);
    p.coyote = p.grounded ? 0.11 : Math.max(0, p.coyote - dt);
    p.dashCooldown = Math.max(0, p.dashCooldown - dt);
    p.dashTime = Math.max(0, p.dashTime - dt);
    p.attackTime = Math.max(0, p.attackTime - dt);
    p.animationTime += dt;

    if (state.messageTime === 0) message.hidden = true;

    const move = (down("ArrowLeft", "KeyA") ? -1 : 0) + (down("ArrowRight", "KeyD") ? 1 : 0);
    if (move) p.face = move;

    if (consume("KeyC") && p.dashCooldown === 0) {
      p.dashTime = animationDefs.dash.frames / animationDefs.dash.fps;
      p.dashCooldown = 0.52;
      p.vy = 0;
    }

    if (consume("KeyX") && p.attackTime === 0 && p.dashTime === 0) {
      p.attackTime = animationDefs.attack.frames / animationDefs.attack.fps;
    }

    if (p.dashTime > 0) {
      p.vx = p.face * 520;
      p.vy = 0;
    } else {
      const targetVelocity = move * 205;
      const acceleration = p.grounded ? 18 : 9;
      p.vx += (targetVelocity - p.vx) * Math.min(1, dt * acceleration);
      p.vy = Math.min(840, p.vy + 1820 * dt);
    }

    if (consume("KeyZ") && p.coyote > 0 && p.dashTime === 0) {
      p.vy = -570;
      p.grounded = false;
      p.coyote = 0;
    }
    if (!down("KeyZ") && p.vy < -180) p.vy += 1100 * dt;
    if (consume("ArrowUp")) inspectNearby();

    moveAxis(p, p.vx * dt, 0);
    p.grounded = false;
    moveAxis(p, 0, p.vy * dt);
    p.x = clamp(p.x, 0, WORLD_W - p.w);

    if (p.y > H + 100) reset();

    const nextAnimation = p.attackTime > 0
      ? "attack"
      : p.dashTime > 0
        ? "dash"
        : !p.grounded
          ? "jump"
          : Math.abs(p.vx) > 24
            ? "run"
            : "idle";
    setAnimation(nextAnimation);

    state.targetCameraX = clamp(p.x + p.w / 2 - W / 2, 0, WORLD_W - W);
    state.cameraX += (state.targetCameraX - state.cameraX) * Math.min(1, dt * 7.5);
    updateAreaReadout();
  }

  function moveAxis(entity, dx, dy) {
    entity.x += dx;
    entity.y += dy;
    for (const platform of platforms) {
      if (!overlaps(entity, platform)) continue;
      if (dx > 0) { entity.x = platform.x - entity.w; entity.vx = 0; }
      if (dx < 0) { entity.x = platform.x + platform.w; entity.vx = 0; }
      if (dy > 0) { entity.y = platform.y - entity.h; entity.vy = 0; entity.grounded = true; }
      if (dy < 0) { entity.y = platform.y + platform.h; entity.vy = 0; }
    }
  }

  function inspectNearby() {
    const p = state.player;
    const range = { x: p.x - 45, y: p.y - 30, w: p.w + 90, h: p.h + 60 };
    const target = interactables.find((item) => overlaps(range, item));
    if (!target) return;
    message.textContent = target.text;
    message.hidden = false;
    state.messageTime = 3.5;
  }

  function updateAreaReadout() {
    const center = state.player.x + state.player.w / 2;
    const area = areas.find((entry) => center >= entry.min && center <= entry.max) || areas[0];
    areaLabel.textContent = area.name;
    cameraReadout.textContent = area.room;
  }

  function drawBackgrounds() {
    ctx.imageSmoothingEnabled = true;
    for (let index = 0; index < art.backgrounds.length; index += 1) {
      const x = index * W - state.cameraX;
      if (x <= -W || x >= W) continue;
      ctx.drawImage(art.backgrounds[index], Math.round(x), 0, W, H);
    }

    const gradient = ctx.createLinearGradient(0, 0, 0, H);
    gradient.addColorStop(0, "rgba(1, 5, 8, .08)");
    gradient.addColorStop(0.72, "rgba(1, 5, 8, 0)");
    gradient.addColorStop(1, "rgba(1, 5, 8, .2)");
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, W, H);
  }

  function drawTemporaryPlatforms() {
    ctx.save();
    ctx.translate(-Math.round(state.cameraX), 0);
    for (const platform of platforms.filter((entry) => entry.type === "temporary")) {
      ctx.fillStyle = "rgba(20, 25, 27, .94)";
      ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
      ctx.fillStyle = "#6d716e";
      ctx.fillRect(platform.x, platform.y, platform.w, 4);
      ctx.fillStyle = "#8f6038";
      for (let x = platform.x + 14; x < platform.x + platform.w; x += 30) ctx.fillRect(x, platform.y + 7, 3, 3);
    }
    ctx.restore();
  }

  function animationFrame(name, time) {
    const def = animationDefs[name];
    const frames = art.animations[name];
    if (!def || !frames?.length) return null;
    const rawIndex = Math.floor(time * def.fps);
    const index = def.loop ? rawIndex % frames.length : Math.min(rawIndex, frames.length - 1);
    return frames[index];
  }

  function drawPlayer() {
    const p = state.player;
    const frame = animationFrame(p.animation, p.animationTime);
    if (!frame) return;

    const centerX = Math.round(p.x + p.w / 2 - state.cameraX);
    const bottom = Math.round(p.y + p.h + 5);
    ctx.save();
    ctx.translate(centerX, bottom);
    ctx.scale(p.face, 1);
    ctx.imageSmoothingEnabled = true;

    if (p.dashTime > 0) {
      ctx.globalAlpha = 0.16;
      ctx.drawImage(frame, -p.face * 28 - PLAYER_SPRITE_SIZE / 2, -PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE);
      ctx.globalAlpha = 0.3;
      ctx.drawImage(frame, -p.face * 14 - PLAYER_SPRITE_SIZE / 2, -PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE);
      ctx.globalAlpha = 1;
    }

    ctx.drawImage(frame, -PLAYER_SPRITE_SIZE / 2, -PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE, PLAYER_SPRITE_SIZE);
    ctx.restore();
  }

  function drawHitboxes() {
    if (!state.hitboxes) return;
    ctx.save();
    ctx.translate(-Math.round(state.cameraX), 0);
    for (const platform of platforms) {
      ctx.fillStyle = platform.type === "temporary" ? "rgba(255, 184, 74, .2)" : "rgba(92, 225, 255, .12)";
      ctx.strokeStyle = platform.type === "temporary" ? "#ffb84a" : "#5ce1ff";
      ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
      ctx.strokeRect(platform.x + 0.5, platform.y + 0.5, platform.w - 1, platform.h - 1);
    }
    ctx.restore();

    const p = state.player;
    ctx.strokeStyle = "#ff6477";
    ctx.strokeRect(Math.round(p.x - state.cameraX) + 0.5, Math.round(p.y) + 0.5, p.w - 1, p.h - 1);
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    if (!art.ready) {
      ctx.fillStyle = "#06090d";
      ctx.fillRect(0, 0, W, H);
      return;
    }
    drawBackgrounds();
    drawTemporaryPlatforms();
    drawPlayer();
    drawHitboxes();
  }

  function frame(now) {
    const dt = Math.min(0.033, (now - state.lastTime) / 1000);
    state.lastTime = now;
    if (art.ready) update(dt);
    render();
    pressed.clear();
    requestAnimationFrame(frame);
  }

  function reset() {
    state.player = makePlayer();
    state.cameraX = 2560;
    state.targetCameraX = 2560;
    state.messageTime = 0;
    message.hidden = true;
    updateAreaReadout();
    canvas.focus();
  }

  addEventListener("keydown", (event) => {
    const gameKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "KeyA", "KeyD", "KeyZ", "KeyX", "KeyC", "KeyH"];
    if (gameKeys.includes(event.code)) event.preventDefault();
    if (!keys.has(event.code)) pressed.add(event.code);
    keys.add(event.code);
    if (event.code === "KeyH") state.hitboxes = !state.hitboxes;
  });

  addEventListener("keyup", (event) => keys.delete(event.code));
  canvas.addEventListener("pointerdown", () => canvas.focus());
  document.getElementById("resetButton").addEventListener("click", reset);
  document.getElementById("fullscreenButton").addEventListener("click", () => {
    document.fullscreenElement ? document.exitFullscreen() : document.querySelector(".game-frame").requestFullscreen();
  });

  loadArt().catch((error) => {
    loading.textContent = error.message;
    loading.classList.add("error");
  });
  updateAreaReadout();
  canvas.focus();
  requestAnimationFrame(frame);
})();
