(() => {
  "use strict";

  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d");
  const regionName = document.getElementById("regionName");
  const regionStep = document.getElementById("regionStep");
  const regionNote = document.getElementById("regionNote");
  const routeChip = document.getElementById("routeChip");
  const gateNote = document.getElementById("gateNote");
  const loading = document.getElementById("loading");
  const mainTabs = document.getElementById("mainTabs");
  const optionalTabs = document.getElementById("optionalTabs");

  const W = 1280;
  const H = 720;
  const PLAYER_W = 36;
  const PLAYER_H = 64;
  const RENDER_HEIGHT = 104;
  const WORLD_GROUND_Y = 560;
  const ASCENT_GRAVITY = 1840;
  const FALL_GRAVITY = ASCENT_GRAVITY * 2;
  const JUMP_CUT_GRAVITY = 1120;
  const MAX_FALL_SPEED = 860;
  const NORMAL_MOVE_SPEED = 250;
  const DAMAGED_MOVE_SPEED = 215;
  const GROUND_MOVE_RESPONSE = 21;
  const AIR_MOVE_RESPONSE = 9;
  const WEAPON_PROFILES = {
    fist: {
      duration: 0.36,
      activeWindow: [0.3, 0.56],
      hitbox: { x: 12, y: -72, w: 54, h: 56 }
    },
    greatsword: {
      duration: 0.68,
      activeWindow: [0.38, 0.62],
      hitbox: { x: 10, y: -96, w: 130, h: 100 }
    },
    hammer: {
      duration: 0.86,
      activeWindow: [0.38, 0.58],
      hitbox: { x: 8, y: -100, w: 136, h: 102 }
    }
  };
  const previewMotion = new URLSearchParams(location.search).get("previewMotion");
  const keys = new Set();
  const pressed = new Set();

  const imageCache = new Map();
  const art = {
    master: null,
    actions: {},
    animation: null,
    ready: false
  };

  const state = {
    data: null,
    region: null,
    regionImage: null,
    platforms: [],
    imageToken: 0,
    lastTime: performance.now(),
    hitboxes: false,
    weapon: "fist",
    player: null
  };

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  const down = (...codes) => codes.some((code) => keys.has(code));
  const consume = (...codes) => codes.some((code) => pressed.has(code));
  function weaponProfile(name = state.weapon) {
    return WEAPON_PROFILES[name] || WEAPON_PROFILES.fist;
  }

  function isDamagedMovementRegion(region) {
    if (!region || !state.data) return false;
    const mainIndex = state.data.mainRoute.indexOf(region.id);
    if (mainIndex >= 0) return mainIndex <= 1;
    const branch = state.data.optionalBranches.find((entry) => entry.id === region.id);
    return branch?.anchor === "limbus";
  }

  function loadImage(src) {
    if (imageCache.has(src)) return imageCache.get(src);
    const promise = new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error(`이미지를 불러오지 못했습니다: ${src}`));
      image.src = src;
    });
    imageCache.set(src, promise);
    return promise;
  }

  function regionImageSrc(region) {
    const revision = state.data?.assetRevision || 1;
    return `${region.image}?v=${revision}`;
  }

  function chromaCrop(image, trim = true) {
    const out = document.createElement("canvas");
    out.width = image.width;
    out.height = image.height;
    const g = out.getContext("2d", { willReadFrequently: true });
    g.drawImage(image, 0, 0);
    const pixels = g.getImageData(0, 0, out.width, out.height);
    const data = pixels.data;
    const total = out.width * out.height;
    const seen = new Uint8Array(total);
    const queue = new Int32Array(total);
    let head = 0;
    let tail = 0;

    const isBackdrop = (index) => {
      const offset = index * 4;
      const red = data[offset];
      const green = data[offset + 1];
      const blue = data[offset + 2];
      const neutral = red > 178 && green > 178 && blue > 178 && Math.max(red, green, blue) - Math.min(red, green, blue) < 38;
      const chromaGreen = green > 170 && red < 90 && blue < 110 && green > red * 2.2 && green > blue * 1.8;
      return neutral || chromaGreen;
    };

    const enqueue = (index) => {
      if (seen[index] || !isBackdrop(index)) return;
      seen[index] = 1;
      queue[tail++] = index;
    };

    for (let x = 0; x < out.width; x += 1) {
      enqueue(x);
      enqueue((out.height - 1) * out.width + x);
    }
    for (let y = 0; y < out.height; y += 1) {
      enqueue(y * out.width);
      enqueue(y * out.width + out.width - 1);
    }

    while (head < tail) {
      const index = queue[head++];
      const x = index % out.width;
      const y = Math.floor(index / out.width);
      if (x > 0) enqueue(index - 1);
      if (x + 1 < out.width) enqueue(index + 1);
      if (y > 0) enqueue(index - out.width);
      if (y + 1 < out.height) enqueue(index + out.width);
    }

    for (let index = 0; index < total; index += 1) {
      if (seen[index]) data[index * 4 + 3] = 0;
    }
    g.putImageData(pixels, 0, 0);
    return trim ? trimTransparent(out, 12) : out;
  }

  function opaqueBounds(source) {
    const g = source.getContext("2d", { willReadFrequently: true });
    const { data } = g.getImageData(0, 0, source.width, source.height);
    let minX = source.width;
    let minY = source.height;
    let maxX = -1;
    let maxY = -1;

    for (let y = 0; y < source.height; y += 1) {
      for (let x = 0; x < source.width; x += 1) {
        if (data[(y * source.width + x) * 4 + 3] === 0) continue;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }

    return maxX < 0 ? { minX: 0, minY: 0, maxX: source.width - 1, maxY: source.height - 1 } : { minX, minY, maxX, maxY };
  }

  function trimTransparent(source, padding) {
    const g = source.getContext("2d", { willReadFrequently: true });
    const { data } = g.getImageData(0, 0, source.width, source.height);
    let minX = source.width;
    let minY = source.height;
    let maxX = -1;
    let maxY = -1;

    for (let y = 0; y < source.height; y += 1) {
      for (let x = 0; x < source.width; x += 1) {
        if (data[(y * source.width + x) * 4 + 3] === 0) continue;
        minX = Math.min(minX, x);
        minY = Math.min(minY, y);
        maxX = Math.max(maxX, x);
        maxY = Math.max(maxY, y);
      }
    }

    if (maxX < 0) return source;
    minX = Math.max(0, minX - padding);
    minY = Math.max(0, minY - padding);
    maxX = Math.min(source.width - 1, maxX + padding);
    maxY = Math.min(source.height - 1, maxY + padding);

    const out = document.createElement("canvas");
    out.width = maxX - minX + 1;
    out.height = maxY - minY + 1;
    out.getContext("2d").drawImage(source, minX, minY, out.width, out.height, 0, 0, out.width, out.height);
    return out;
  }

  function makeAnchoredFrame(image, sourceFacing, opaqueHeight) {
    const sprite = chromaCrop(image, false);
    const bounds = opaqueBounds(sprite);
    const height = Math.max(1, bounds.maxY - bounds.minY + 1);
    return {
      sprite,
      sourceFacing,
      anchorX: (bounds.minX + bounds.maxX) / 2,
      anchorY: bounds.maxY,
      scale: opaqueHeight / height
    };
  }

  function makeSequenceFrame(image, sourceFacing, scale, anchorOverride = null) {
    const sourceAnchor = anchorOverride || art.animation?.canonical?.sourceAnchor || { x: 320, y: 480 };
    return {
      sprite: chromaCrop(image, false),
      sourceFacing,
      anchorX: sourceAnchor.x,
      anchorY: sourceAnchor.y,
      scale
    };
  }

  function clip(name) {
    return art.animation?.clips?.[name] || {};
  }

  function actionProgress(timeRemaining, duration) {
    return clamp(1 - timeRemaining / duration, 0, 1);
  }

  function phaseAt(name, progress) {
    const phases = clip(name).phases || [];
    return phases.find((phase) => progress >= phase.from && progress < phase.to) || phases.at(-1) || null;
  }

  function timelineAt(name, progress, timelineName = "timeline") {
    const timeline = clip(name)[timelineName] || [];
    return timeline.find((pose) => progress < pose.to) || timeline.at(-1) || null;
  }

  function sequenceAt(name, progress) {
    const frames = art.actions[name] || [];
    if (!frames.length) return art.master;
    const timedPose = timelineAt(name, clamp(progress, 0, 0.9999));
    const frameIndex = timedPose?.frame ?? Math.floor(clamp(progress, 0, 0.9999) * frames.length);
    return frames[Math.min(frames.length - 1, frameIndex)];
  }

  async function loadCharacterArt(config) {
    const characterImageSrc = (src) => `${src}?v=${config.revision || 1}`;
    const loadFrameSet = (frames) => Promise.all(frames.map((frame) => loadImage(characterImageSrc(frame.src))));
    const attackEntries = Object.entries(config.attackSets?.sets || {});
    const [animation, master, idle, walk, jump, doubleJump, dash, attackImages] = await Promise.all([
      fetch(config.animationSpec).then((response) => {
        if (!response.ok) throw new Error(`Animation spec could not be loaded: ${config.animationSpec}`);
        return response.json();
      }),
      loadImage(characterImageSrc(config.master)),
      loadFrameSet(config.idle),
      loadFrameSet(config.walk),
      loadFrameSet(config.jump),
      loadFrameSet(config.doubleJump),
      loadFrameSet(config.dash),
      Promise.all(attackEntries.map(([, attack]) => loadFrameSet(attack.frames)))
    ]);
    art.animation = animation;
    const opaqueHeight = config.canonicalOpaqueHeight || animation.canonical?.opaqueHeight || RENDER_HEIGHT;
    const sequenceScale = config.sequenceScale || 0.34;
    const sequenceScales = config.sequenceScales || {};
    const prepareSequence = (images, frames, scale = sequenceScale, sourceAnchor = null) => images.map(
      (image, index) => makeSequenceFrame(image, frames[index].sourceFacing, scale, sourceAnchor)
    );
    art.master = makeAnchoredFrame(master, config.masterFacing || 1, opaqueHeight);
    art.actions.idle = prepareSequence(idle, config.idle, sequenceScales.idle || sequenceScale);
    art.actions.walk = prepareSequence(walk, config.walk, sequenceScales.walk || sequenceScale);
    art.actions.jump = prepareSequence(jump, config.jump, sequenceScales.jump || sequenceScale);
    art.actions.doubleJump = prepareSequence(doubleJump, config.doubleJump, sequenceScales.doubleJump || sequenceScale);
    art.actions.dash = prepareSequence(dash, config.dash, sequenceScales.dash || sequenceScale);
    attackEntries.forEach(([name, attack], index) => {
      art.actions[`${name}-attack`] = prepareSequence(
        attackImages[index],
        attack.frames,
        attack.sequenceScale || sequenceScale,
        attack.sourceAnchor || null
      );
    });
    state.weapon = config.attackSets?.default || attackEntries[0]?.[0] || "fist";
    art.ready = true;
  }

  function backgroundTransform(region, image) {
    const view = state.data?.backgroundViews?.[region?.id] || {};
    const zoom = Number.isFinite(view.zoom) ? view.zoom : 1;
    const sourceGroundY = Number.isFinite(view.sourceGroundY) ? view.sourceGroundY : image.height * 0.75;
    const width = W * zoom;
    const height = H * zoom;
    const scale = height / image.height;
    return {
      x: (W - width) / 2 + (view.offsetX || 0),
      y: WORLD_GROUND_Y - sourceGroundY * scale,
      width,
      height
    };
  }

  function platformsForRegion(region) {
    const layout = region.layout;
    const list = [{ x: 0, y: WORLD_GROUND_Y, w: W, h: H - WORLD_GROUND_Y, kind: "ground" }];
    const additions = {
      vertical: [
        { x: 120, y: 500, w: 220, h: 18, kind: "temporary" },
        { x: 390, y: 440, w: 220, h: 18, kind: "temporary" },
        { x: 670, y: 380, w: 220, h: 18, kind: "temporary" },
        { x: 950, y: 320, w: 210, h: 18, kind: "temporary" }
      ],
      treatment: [
        { x: 210, y: 500, w: 220, h: 18, kind: "temporary" },
        { x: 500, y: 440, w: 220, h: 18, kind: "temporary" },
        { x: 790, y: 380, w: 220, h: 18, kind: "temporary" }
      ],
      drainage: [
        { x: 150, y: 502, w: 220, h: 18, kind: "temporary" },
        { x: 430, y: 444, w: 220, h: 18, kind: "temporary" },
        { x: 710, y: 386, w: 220, h: 18, kind: "temporary" },
        { x: 980, y: 328, w: 180, h: 18, kind: "temporary" }
      ],
      sorter: [
        { x: 150, y: 500, w: 230, h: 18, kind: "temporary" },
        { x: 430, y: 440, w: 230, h: 18, kind: "temporary" },
        { x: 730, y: 380, w: 230, h: 18, kind: "temporary" }
      ],
      aqueduct: [
        { x: 110, y: 500, w: 220, h: 18, kind: "temporary" },
        { x: 380, y: 440, w: 220, h: 18, kind: "temporary" },
        { x: 650, y: 380, w: 220, h: 18, kind: "temporary" },
        { x: 920, y: 440, w: 220, h: 18, kind: "temporary" }
      ],
      dig: [
        { x: 100, y: 502, w: 210, h: 18, kind: "temporary" },
        { x: 350, y: 444, w: 210, h: 18, kind: "temporary" },
        { x: 600, y: 386, w: 210, h: 18, kind: "temporary" },
        { x: 850, y: 328, w: 210, h: 18, kind: "temporary" }
      ]
    };
    return list.concat(additions[layout] || []);
  }

  function makePlayer(spawnSide = "left") {
    return {
      x: spawnSide === "right" ? W - 122 : 86,
      y: WORLD_GROUND_Y - PLAYER_H,
      w: PLAYER_W,
      h: PLAYER_H,
      vx: 0,
      vy: 0,
      face: spawnSide === "right" ? -1 : 1,
      lastMoveDirection: spawnSide === "right" ? -1 : 1,
      grounded: true,
      coyote: 0.1,
      attackTime: 0,
      attackWeapon: null,
      dashTime: 0,
      dashCooldown: 0,
      jumpTakeoffTime: 0,
      landingTime: 0,
      doubleJumpTime: 0,
      airJumps: 1,
      motionTime: 0,
      walkDistance: 0,
      wasWalking: false
    };
  }

  function selectWeapon(name) {
    if (!WEAPON_PROFILES[name] || !art.actions[`${name}-attack`]?.length) return;
    state.weapon = name;
    document.querySelectorAll("#weaponSwitch button[data-weapon]").forEach((button) => {
      button.setAttribute("aria-pressed", button.dataset.weapon === name ? "true" : "false");
    });
    canvas.dataset.weapon = name;
  }

  function createTabs() {
    mainTabs.replaceChildren();
    optionalTabs.replaceChildren();
    for (const region of state.data.regions) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "region-tab";
      button.dataset.region = region.id;
      button.textContent = region.name;
      button.title = region.requires ? `${region.name} · 필요: ${region.requires}` : region.name;
      button.addEventListener("click", () => switchRegion(region.id));
      (region.route === "main" ? mainTabs : optionalTabs).append(button);
    }
  }

  async function switchRegion(id, spawnSide = "left") {
    const region = state.data.regions.find((entry) => entry.id === id);
    if (!region) return;
    const token = ++state.imageToken;
    state.region = region;
    state.regionImage = null;
    state.platforms = platformsForRegion(region);
    state.player = makePlayer(spawnSide);
    loading.hidden = false;
    updateInterface();
    history.replaceState(null, "", `?region=${encodeURIComponent(id)}`);

    try {
      const image = await loadImage(regionImageSrc(region));
      if (token !== state.imageToken) return;
      state.regionImage = image;
      loading.hidden = true;
      prefetchNeighbors(region);
    } catch (error) {
      if (token !== state.imageToken) return;
      loading.textContent = error.message;
    }
    canvas.focus();
  }

  function prefetchNeighbors(region) {
    const index = state.data.mainRoute.indexOf(region.id);
    if (index >= 0) {
      for (const nextId of [state.data.mainRoute[index - 1], state.data.mainRoute[index + 1]]) {
        const next = state.data.regions.find((entry) => entry.id === nextId);
        if (next) loadImage(regionImageSrc(next)).catch(() => {});
      }
    }
    for (const branch of state.data.optionalBranches.filter((entry) => entry.anchor === region.id)) {
      const optional = state.data.regions.find((entry) => entry.id === branch.id);
      if (optional) loadImage(regionImageSrc(optional)).catch(() => {});
    }
  }

  function updateInterface() {
    const region = state.region;
    const mainIndex = state.data.mainRoute.indexOf(region.id);
    regionName.textContent = region.name;
    regionNote.textContent = region.description;
    routeChip.textContent = region.route === "main" ? "메인 진행" : "선택 탐사";
    regionStep.textContent = region.route === "main"
      ? `${String(mainIndex + 1).padStart(2, "0")} / ${String(state.data.mainRoute.length).padStart(2, "0")}`
      : "OPTIONAL";
    gateNote.hidden = !region.requires;
    gateNote.textContent = region.requires ? `진입 능력: ${region.requires}` : "";
    document.querySelectorAll(".region-tab").forEach((button) => {
      button.setAttribute("aria-current", button.dataset.region === region.id ? "true" : "false");
    });
  }

  function update(dt) {
    const p = state.player;
    const groundedAtStart = p.grounded;
    const dashDuration = clip("dash").duration || 0.32;
    const doubleJumpDuration = clip("doubleJump").duration || 0.34;
    p.attackTime = Math.max(0, p.attackTime - dt);
    p.dashTime = Math.max(0, p.dashTime - dt);
    p.dashCooldown = Math.max(0, p.dashCooldown - dt);
    p.jumpTakeoffTime = Math.max(0, p.jumpTakeoffTime - dt);
    p.landingTime = Math.max(0, p.landingTime - dt);
    p.doubleJumpTime = Math.max(0, p.doubleJumpTime - dt);
    if (p.grounded) p.airJumps = 1;
    p.coyote = p.grounded ? 0.11 : Math.max(0, p.coyote - dt);
    p.motionTime += dt;

    if (consume("Digit1")) selectWeapon("fist");
    if (consume("Digit2")) selectWeapon("greatsword");
    if (consume("Digit3")) selectWeapon("hammer");

    let move = (down("ArrowLeft", "KeyA") ? -1 : 0) + (down("ArrowRight", "KeyD") ? 1 : 0);
    if (previewMotion === "walk-left") move = -1;
    if (previewMotion === "walk-right") move = 1;
    if (move) {
      p.face = move;
      p.lastMoveDirection = move;
    } else {
      p.face = p.lastMoveDirection;
    }

    if (consume("KeyC") && p.dashCooldown === 0) {
      p.dashTime = dashDuration;
      p.dashCooldown = 0.54;
      p.vy = 0;
      p.motionTime = 0;
    }
    if (consume("KeyX") && p.attackTime === 0 && p.dashTime === 0) {
      p.attackWeapon = state.weapon;
      p.attackTime = weaponProfile(p.attackWeapon).duration;
      p.motionTime = 0;
    }
    if (consume("KeyZ") && p.dashTime === 0) {
      if (p.coyote > 0) {
        p.vy = -575;
        p.grounded = false;
        p.coyote = 0;
        p.jumpTakeoffTime = clip("jump").takeoffDuration || 0.12;
        p.landingTime = 0;
        p.motionTime = 0;
      } else if (!p.grounded && p.airJumps > 0) {
        p.vy = -550;
        p.airJumps -= 1;
        p.doubleJumpTime = doubleJumpDuration;
        p.jumpTakeoffTime = 0;
        p.motionTime = 0;
      }
    }

    if (p.dashTime > 0) {
      p.vx = p.face * 530;
      p.vy = 0;
    } else {
      const damagedMovement = isDamagedMovementRegion(state.region);
      const moveSpeed = damagedMovement ? DAMAGED_MOVE_SPEED : NORMAL_MOVE_SPEED;
      canvas.dataset.moveSpeed = String(moveSpeed);
      canvas.dataset.movementState = damagedMovement ? "damaged" : "normal";
      const target = move * moveSpeed;
      p.vx += (target - p.vx) * Math.min(1, dt * (p.grounded ? GROUND_MOVE_RESPONSE : AIR_MOVE_RESPONSE));
      const gravity = p.vy < 0 ? ASCENT_GRAVITY : FALL_GRAVITY;
      p.vy = Math.min(MAX_FALL_SPEED, p.vy + gravity * dt);
    }
    if (!down("KeyZ") && p.vy < -180) p.vy += JUMP_CUT_GRAVITY * dt;

    const horizontalStart = p.x;
    moveAxis(p, p.vx * dt, 0);
    const horizontalTravel = Math.abs(p.x - horizontalStart);
    if (groundedAtStart && p.dashTime === 0 && Math.abs(p.vx) > 24) {
      p.walkDistance += horizontalTravel;
    }
    p.grounded = false;
    const verticalStep = p.dashTime > 0 && p.vy === 0 ? 0.01 : p.vy * dt;
    moveAxis(p, 0, verticalStep);
    if (!groundedAtStart && p.grounded) {
      p.landingTime = clip("jump").landingDuration || 0.12;
      p.jumpTakeoffTime = 0;
    }

    const walkingNow = p.grounded && Math.abs(p.vx) > 24 && p.dashTime === 0;
    if (!walkingNow && p.wasWalking && p.grounded && clip("walk").snapToContactOnStop) {
      const cycleDistance = clip("walk").cycleDistance || 155;
      const progress = (p.walkDistance % cycleDistance) / cycleDistance;
      const contactProgress = progress < 0.25 ? 0 : progress < 0.75 ? 0.5 : 1;
      p.walkDistance += (contactProgress - progress) * cycleDistance;
    }
    p.wasWalking = walkingNow;

    if (p.y > H + 100) {
      state.player = makePlayer("left");
      return;
    }
    handleRegionEdges();
  }

  function moveAxis(entity, dx, dy) {
    entity.x += dx;
    entity.y += dy;
    for (const platform of state.platforms) {
      if (!overlaps(entity, platform)) continue;
      if (dx > 0) { entity.x = platform.x - entity.w; entity.vx = 0; }
      if (dx < 0) { entity.x = platform.x + platform.w; entity.vx = 0; }
      if (dy > 0) {
        entity.y = platform.y - entity.h;
        entity.vy = 0;
        entity.grounded = true;
        entity.airJumps = 1;
        entity.doubleJumpTime = 0;
      }
      if (dy < 0) { entity.y = platform.y + platform.h; entity.vy = 0; }
    }
  }

  function handleRegionEdges() {
    const p = state.player;
    const mainIndex = state.data.mainRoute.indexOf(state.region.id);

    if (p.x > W + 24) {
      if (mainIndex >= 0 && mainIndex < state.data.mainRoute.length - 1) {
        switchRegion(state.data.mainRoute[mainIndex + 1], "left");
      } else {
        p.x = W - p.w;
        p.vx = 0;
      }
    }

    if (p.x + p.w < -24) {
      if (state.region.route === "optional") {
        switchRegion(state.region.returnTo, "right");
      } else if (mainIndex > 0) {
        switchRegion(state.data.mainRoute[mainIndex - 1], "right");
      } else {
        p.x = 0;
        p.vx = 0;
      }
    }
  }

  function drawBackground() {
    if (!state.regionImage) {
      ctx.fillStyle = "#070b0f";
      ctx.fillRect(0, 0, W, H);
      return;
    }
    ctx.imageSmoothingEnabled = true;
    const transform = backgroundTransform(state.region, state.regionImage);
    ctx.drawImage(state.regionImage, transform.x, transform.y, transform.width, transform.height);
    const shade = ctx.createLinearGradient(0, 0, 0, H);
    shade.addColorStop(0, "rgba(2, 5, 8, .08)");
    shade.addColorStop(0.65, "rgba(2, 5, 8, 0)");
    shade.addColorStop(1, "rgba(2, 5, 8, .28)");
    ctx.fillStyle = shade;
    ctx.fillRect(0, 0, W, H);
  }

  function drawTemporaryPlatforms() {
    for (const platform of state.platforms.filter((entry) => entry.kind === "temporary")) {
      ctx.fillStyle = "rgba(17, 22, 25, .91)";
      ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
      ctx.fillStyle = "#6f7471";
      ctx.fillRect(platform.x, platform.y, platform.w, 4);
      ctx.fillStyle = "#895d37";
      for (let x = platform.x + 14; x < platform.x + platform.w; x += 32) ctx.fillRect(x, platform.y + 8, 3, 3);
    }
  }

  function drawPose(sprite, sourceFacing, x, bottom, height, facing, alpha = 1, angle = 0, offsetX = 0, offsetY = 0) {
    if (!sprite) return;
    const width = height * sprite.width / sprite.height;
    ctx.save();
    ctx.translate(Math.round(x + offsetX), Math.round(bottom + offsetY));
    ctx.scale(facing === sourceFacing ? 1 : -1, 1);
    ctx.rotate(angle);
    ctx.globalAlpha = alpha;
    ctx.imageSmoothingEnabled = art.animation?.canonical?.pixelSmoothing !== false;
    ctx.drawImage(sprite, -width / 2, -height, width, height);
    ctx.restore();
  }

  function drawAnchoredPose(frame, x, bottom, facing, alpha = 1, angle = 0, offsetX = 0, offsetY = 0) {
    if (!frame?.sprite) return;
    const direction = facing === frame.sourceFacing ? 1 : -1;
    ctx.save();
    ctx.translate(Math.round(x + offsetX), Math.round(bottom + offsetY));
    ctx.scale(direction, 1);
    ctx.rotate(angle);
    ctx.globalAlpha = alpha;
    ctx.imageSmoothingEnabled = art.animation?.canonical?.pixelSmoothing !== false;
    ctx.drawImage(
      frame.sprite,
      -frame.anchorX * frame.scale,
      -frame.anchorY * frame.scale,
      frame.sprite.width * frame.scale,
      frame.sprite.height * frame.scale
    );
    ctx.restore();
  }

  function drawHammerSwingTrail(x, bottom, facing, progress) {
    const start = 0.34;
    const end = 0.62;
    if (progress < start || progress > end) return;

    const t = clamp((progress - start) / (end - start), 0, 1);
    const eased = 1 - Math.pow(1 - t, 3);
    const tail = -2.52;
    const head = tail + eased * 3.08;
    const alpha = Math.sin(Math.PI * t);

    ctx.save();
    ctx.translate(Math.round(x), Math.round(bottom - 54));
    ctx.scale(facing, 1);
    ctx.rotate(-0.04);
    ctx.lineCap = "round";
    ctx.globalCompositeOperation = "screen";
    ctx.shadowColor = `rgba(255, 190, 67, ${alpha * 0.6})`;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(0, 0, 88, tail, head);
    ctx.strokeStyle = `rgba(232, 147, 38, ${0.26 + alpha * 0.5})`;
    ctx.lineWidth = 24;
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, 88, tail + 0.07, head);
    ctx.strokeStyle = `rgba(255, 244, 190, ${0.28 + alpha * 0.7})`;
    ctx.lineWidth = 9;
    ctx.stroke();
    ctx.restore();
  }

  function drawGreatswordSlashTrail(x, bottom, facing, progress) {
    const start = 0.34;
    const end = 0.62;
    if (progress < start || progress > end) return;

    const t = clamp((progress - start) / (end - start), 0, 1);
    const alpha = Math.sin(Math.PI * t);

    ctx.save();
    ctx.translate(Math.round(x), Math.round(bottom - 42));
    ctx.scale(facing, 1);
    ctx.lineCap = "round";
    ctx.globalCompositeOperation = "screen";
    ctx.beginPath();
    ctx.moveTo(-50, -67);
    ctx.quadraticCurveTo(16, -46, 88, 18);
    ctx.strokeStyle = `rgba(95, 218, 245, ${0.08 + alpha * 0.3})`;
    ctx.lineWidth = 8;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(-46, -65);
    ctx.quadraticCurveTo(18, -43, 88, 18);
    ctx.strokeStyle = `rgba(244, 252, 255, ${0.16 + alpha * 0.54})`;
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();
  }

  function drawPlayer() {
    if (!art.ready || !state.player) return;
    const p = state.player;
    const x = p.x + p.w / 2;
    const bottom = p.y + p.h + 3;
    let anchoredFrame = art.actions.idle[0] || art.master;
    let angle = 0;
    let offsetX = 0;
    let offsetY = 0;
    let animationName = "idle";
    let animationPhase = "settle";
    let attackProgress = 0;
    let attackWeapon = null;

    if (p.attackTime > 0) {
      attackWeapon = p.attackWeapon || state.weapon;
      const duration = weaponProfile(attackWeapon).duration;
      attackProgress = actionProgress(p.attackTime, duration);
      const activeWindow = weaponProfile(attackWeapon).activeWindow;
      animationName = `${attackWeapon}-attack`;
      animationPhase = attackProgress < activeWindow[0]
        ? "anticipation"
        : attackProgress <= activeWindow[1] ? "active" : "recovery";
      anchoredFrame = sequenceAt(animationName, attackProgress);
      if (attackWeapon === "hammer") {
        if (attackProgress < 0.38) {
          angle = -0.035 * p.face;
          offsetX = -2 * p.face;
        } else if (attackProgress < 0.62) {
          const swing = (attackProgress - 0.38) / 0.24;
          angle = (-0.035 + swing * 0.12) * p.face;
          offsetX = Math.round(swing * 7) * p.face;
        } else {
          const recovery = clamp((attackProgress - 0.62) / 0.38, 0, 1);
          angle = (0.085 * (1 - recovery)) * p.face;
          offsetX = Math.round(7 * (1 - recovery)) * p.face;
        }
      } else if (attackWeapon === "greatsword") {
        if (attackProgress < 0.38) {
          angle = -0.025 * p.face;
          offsetX = -1 * p.face;
        } else if (attackProgress < 0.62) {
          const slash = (attackProgress - 0.38) / 0.24;
          angle = (-0.025 + slash * 0.105) * p.face;
          offsetX = Math.round(slash * 6) * p.face;
        } else {
          const recovery = clamp((attackProgress - 0.62) / 0.38, 0, 1);
          angle = (0.065 * (1 - recovery)) * p.face;
          offsetX = Math.round(5 * (1 - recovery)) * p.face;
        }
      }
    } else if (p.dashTime > 0) {
      const duration = clip("dash").duration || 0.32;
      const progress = actionProgress(p.dashTime, duration);
      const phase = phaseAt("dash", progress);
      animationName = "dash";
      animationPhase = phase?.name || "active";
      anchoredFrame = sequenceAt("dash", progress);
      if (animationPhase === "anticipation") {
        angle = -0.055 * p.face;
      } else if (animationPhase === "active") {
        angle = 0.13 * p.face;
        offsetX = 5 * p.face;
      } else {
        angle = 0.035 * p.face;
        offsetX = 2 * p.face;
      }
      if (animationPhase === "active") {
        ctx.save();
        ctx.strokeStyle = "rgba(86, 221, 242, .28)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x - p.face * 54, bottom - 54);
        ctx.lineTo(x - p.face * 18, bottom - 54);
        ctx.moveTo(x - p.face * 44, bottom - 38);
        ctx.lineTo(x - p.face * 12, bottom - 38);
        ctx.stroke();
        ctx.restore();
      }
    } else if (p.doubleJumpTime > 0) {
      const duration = clip("doubleJump").duration || 0.34;
      const progress = actionProgress(p.doubleJumpTime, duration);
      const phase = phaseAt("doubleJump", progress);
      animationName = "doubleJump";
      animationPhase = phase?.name || "impulse";
      anchoredFrame = sequenceAt("doubleJump", progress);
    } else if (p.landingTime > 0 && p.grounded) {
      const duration = clip("jump").landingDuration || 0.12;
      const progress = actionProgress(p.landingTime, duration);
      animationName = "jump";
      animationPhase = "land";
      anchoredFrame = progress < 0.72 ? art.actions.jump[5] : art.actions.idle[0];
    } else if (!p.grounded) {
      const apexVelocity = clip("jump").apexVelocity || 90;
      animationName = "jump";
      if (p.jumpTakeoffTime > 0) {
        const duration = clip("jump").takeoffDuration || 0.12;
        const progress = actionProgress(p.jumpTakeoffTime, duration);
        const pose = timelineAt("jump", progress, "takeoffTimeline");
        animationPhase = "takeoff";
        anchoredFrame = art.actions.jump[pose?.frame ?? (progress < 0.42 ? 0 : 1)];
      } else if (p.vy < -apexVelocity) {
        animationPhase = "rise";
        anchoredFrame = art.actions.jump[2];
      } else if (Math.abs(p.vy) <= apexVelocity) {
        animationPhase = "apex";
        anchoredFrame = art.actions.jump[3];
      } else {
        animationPhase = "fall";
        anchoredFrame = art.actions.jump[4];
      }
    } else if (Math.abs(p.vx) > 24) {
      const cycleDistance = clip("walk").cycleDistance || 155;
      const progress = clip("walk").sync === "ground-distance"
        ? (p.walkDistance % cycleDistance) / cycleDistance
        : (p.motionTime % (clip("walk").duration || 0.72)) / (clip("walk").duration || 0.72);
      const pose = timelineAt("walk", progress) || { name: "contact-a", frame: 0, offsetY: 0 };
      animationName = "walk";
      animationPhase = pose.name;
      anchoredFrame = sequenceAt("walk", progress);
      offsetY = pose.offsetY || 0;
    } else {
      const duration = clip("idle").duration || 1.25;
      const progress = (p.motionTime % duration) / duration;
      animationPhase = phaseAt("idle", progress)?.name || "settle";
      anchoredFrame = sequenceAt("idle", progress);
      offsetY = animationPhase === "compress" ? 1 : animationPhase === "rise" ? -1 : 0;
    }

    state.animationDebug = { name: animationName, phase: animationPhase };
    canvas.dataset.animation = animationName;
    canvas.dataset.animationPhase = animationPhase;
    canvas.dataset.animationFrame = String(Math.max(0, (art.actions[animationName] || []).indexOf(anchoredFrame)));
    if (attackWeapon === "hammer") drawHammerSwingTrail(x + offsetX, bottom + offsetY, p.face, attackProgress);
    if (attackWeapon === "greatsword") drawGreatswordSlashTrail(x + offsetX, bottom + offsetY, p.face, attackProgress);
    drawAnchoredPose(anchoredFrame, x, bottom, p.face, 1, angle, offsetX, offsetY);

    if (animationName === "idle") {
      const pulse = 0.5 + Math.sin(p.motionTime * Math.PI * 1.25) * 0.5;
      ctx.save();
      ctx.globalCompositeOperation = "screen";
      ctx.fillStyle = `rgba(58, 224, 255, ${0.04 + pulse * 0.05})`;
      ctx.beginPath();
      ctx.ellipse(Math.round(x), Math.round(bottom - 34 + offsetY), 7 + pulse, 6 + pulse * 0.7, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    if (p.doubleJumpTime > 0) {
      const duration = clip("doubleJump").duration || 0.34;
      const progress = actionProgress(p.doubleJumpTime, duration);
      drawDoubleJumpCorePulse(x, bottom - 34 + offsetY, progress);
    }

  }

  function drawDoubleJumpCorePulse(x, y, progress) {
    const eased = 1 - Math.pow(1 - progress, 3);
    const radius = 12 + eased * 34;
    const alpha = Math.max(0, 1 - progress) * 0.78;

    ctx.save();
    ctx.translate(Math.round(x), Math.round(y));
    ctx.globalCompositeOperation = "screen";
    ctx.strokeStyle = `rgba(109, 238, 255, ${alpha})`;
    ctx.fillStyle = `rgba(140, 245, 255, ${alpha * 0.32})`;
    ctx.lineWidth = 3;

    ctx.beginPath();
    for (let i = 0; i <= 64; i += 1) {
      const angle = (Math.PI * 2 * i) / 64;
      const tooth = Math.max(0, Math.cos(angle * 8 + eased * 0.8)) * 3;
      const pointRadius = radius + tooth;
      const px = Math.cos(angle) * pointRadius;
      const py = Math.sin(angle) * pointRadius;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.stroke();

    ctx.globalAlpha = 0.72;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(0, 0, 7 + eased * 22, 0, Math.PI * 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(0, 0, 6 + eased * 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }

  function drawExitSignals() {
    const mainIndex = state.data.mainRoute.indexOf(state.region.id);
    const canLeft = state.region.route === "optional" || mainIndex > 0;
    const canRight = state.region.route === "main" && mainIndex < state.data.mainRoute.length - 1;
    ctx.fillStyle = "rgba(224, 190, 107, .7)";
    if (canLeft) {
      ctx.beginPath();
      ctx.moveTo(14, 350);
      ctx.lineTo(27, 339);
      ctx.lineTo(27, 361);
      ctx.fill();
    }
    if (canRight) {
      ctx.beginPath();
      ctx.moveTo(W - 14, 350);
      ctx.lineTo(W - 27, 339);
      ctx.lineTo(W - 27, 361);
      ctx.fill();
    }
  }

  function drawHitboxes() {
    if (!state.hitboxes) return;
    for (const platform of state.platforms) {
      ctx.fillStyle = platform.kind === "temporary" ? "rgba(255, 186, 70, .2)" : "rgba(83, 219, 240, .12)";
      ctx.strokeStyle = platform.kind === "temporary" ? "#ffba46" : "#53dbf0";
      ctx.fillRect(platform.x, platform.y, platform.w, platform.h);
      ctx.strokeRect(platform.x + 0.5, platform.y + 0.5, platform.w - 1, platform.h - 1);
    }
    const p = state.player;
    ctx.strokeStyle = "#ff6879";
    ctx.strokeRect(p.x + 0.5, p.y + 0.5, p.w - 1, p.h - 1);
    if (p.attackTime > 0) {
      const name = p.attackWeapon || state.weapon;
      const profile = weaponProfile(name);
      const progress = actionProgress(p.attackTime, profile.duration);
      if (progress >= profile.activeWindow[0] && progress <= profile.activeWindow[1]) {
        const hitbox = profile.hitbox;
        const originX = p.x + p.w / 2;
        const hitboxX = p.face > 0 ? originX + hitbox.x : originX - hitbox.x - hitbox.w;
        ctx.strokeStyle = name === "hammer" ? "#f0bd58" : name === "greatsword" ? "#6deeff" : "#ff9878";
        ctx.strokeRect(hitboxX + 0.5, p.y + p.h + hitbox.y + 0.5, hitbox.w, hitbox.h);
      }
    }
  }

  function render() {
    ctx.clearRect(0, 0, W, H);
    drawBackground();
    if (!state.regionImage) return;
    drawTemporaryPlatforms();
    drawExitSignals();
    drawPlayer();
    drawHitboxes();
  }

  function frame(now) {
    const dt = Math.min(0.033, (now - state.lastTime) / 1000);
    state.lastTime = now;
    if (state.regionImage && art.ready && state.player) update(dt);
    render();
    pressed.clear();
    requestAnimationFrame(frame);
  }

  async function initialize() {
    const response = await fetch("data/act1-regions.json?v=27");
    if (!response.ok) throw new Error("ACT1 지역 데이터를 불러오지 못했습니다.");
    state.data = await response.json();
    createTabs();
    await loadCharacterArt(state.data.characterAsset);
    selectWeapon(state.weapon);
    const requested = new URLSearchParams(location.search).get("region");
    const startId = state.data.regions.some((entry) => entry.id === requested) ? requested : state.data.mainRoute[0];
    await switchRegion(startId, previewMotion === "walk-left" ? "right" : "left");
  }

  addEventListener("keydown", (event) => {
    const gameKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "KeyA", "KeyD", "KeyZ", "KeyX", "KeyC", "KeyH", "Digit1", "Digit2", "Digit3"];
    if (gameKeys.includes(event.code)) event.preventDefault();
    if (!keys.has(event.code)) pressed.add(event.code);
    keys.add(event.code);
    if (event.code === "KeyH") state.hitboxes = !state.hitboxes;
  });

  addEventListener("keyup", (event) => keys.delete(event.code));
  canvas.addEventListener("pointerdown", () => canvas.focus());
  document.querySelectorAll("#weaponSwitch button[data-weapon]").forEach((button) => {
    button.addEventListener("click", () => {
      selectWeapon(button.dataset.weapon);
      canvas.focus();
    });
  });
  document.getElementById("resetButton").addEventListener("click", () => {
    if (!state.region) return;
    state.player = makePlayer("left");
    canvas.focus();
  });
  document.getElementById("fullscreenButton").addEventListener("click", () => {
    document.fullscreenElement ? document.exitFullscreen() : document.querySelector(".game-shell").requestFullscreen();
  });

  initialize().catch((error) => {
    loading.textContent = error.message;
  });
  canvas.focus();
  requestAnimationFrame(frame);
})();
