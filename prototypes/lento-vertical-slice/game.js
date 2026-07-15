(() => {
  "use strict";

  const canvas = document.getElementById("game");
  const ctx = canvas.getContext("2d");
  ctx.imageSmoothingEnabled = false;

  const W = 640;
  const H = 360;
  const OUTPUT_SCALE = 2;
  const WORLD_W = 960;
  const FLOOR = 302;
  const PIPE_X = [150, 480, 810];
  const PIPE_CY = 243;
  const keys = new Set();
  const pressed = new Set();
  const tuning = { telegraph: 1, time: 1, hitboxes: false, invincible: false, parry: false };
  const colors = {
    ink: "#101416", metal: "#303a3d", edge: "#59666a", brass: "#d88c3f",
    brassLight: "#f5bd5b", copper: "#925032", cyan: "#20d7ef", cyanDark: "#07546d",
    fur: "#4c5144", furDark: "#242a27", gold: "#d7b64d", warning: "#e35b45",
    poison: "#91c851", water: "#285b68", bone: "#d7d1b9"
  };

  const art = {
    ready: false,
    sprites: {},
    actionSprites: {},
    animations: {},
    tique: Object.assign(new Image(), { src: "reference/tique-character-sheet.png" }),
    lento: Object.assign(new Image(), { src: "reference/lento-concept-board.png" })
  };

  const animationFiles = {
    tiqueIdle: Array.from({ length: 4 }, (_, index) => `assets/tique/animations/idle/frame-${index}.png`),
    tiqueRun: Array.from({ length: 8 }, (_, index) => `assets/tique/animations/run/frame-${index}.png`),
    tiqueJump: Array.from({ length: 7 }, (_, index) => `assets/tique/animations/jump/frame-${index}.png`),
    tiqueAttackHorizontal: Array.from({ length: 6 }, (_, index) => `assets/tique/animations/attack/frame-${index}.png`),
    tiqueDash: Array.from({ length: 6 }, (_, index) => `assets/tique/animations/dash/frame-${index}.png`),
    tiqueHit: Array.from({ length: 6 }, (_, index) => `assets/tique/animations/hit/frame-${index}.png`)
  };

  const animationFps = {
    tiqueIdle: 6,
    tiqueRun: 12,
    tiqueJump: 12,
    tiqueAttackHorizontal: 24,
    tiqueDash: 18,
    tiqueHit: 13
  };

  const actionSpriteFiles = {
    tiqueIdle: "assets/tique/idle.png",
    tiqueRun: "assets/tique/run.png",
    tiqueJump: "assets/tique/jump-start.png",
    tiqueLand: "assets/tique/land.png",
    tiqueAttackHorizontal: "assets/tique/attack-horizontal.png",
    tiqueAttackUp: "assets/tique/attack-up.png",
    tiqueAttackDown: "assets/tique/attack-down.png",
    tiqueDash: "assets/tique/dash.png",
    tiqueHit: "assets/tique/hit.png",
    tiqueStunned: "assets/tique/stunned.png",
    tiqueDown: "assets/tique/down.png",
    lentoSide: "assets/lento/bite-recover.png",
    lentoPipe: "assets/lento/pipe-silhouette.png",
    lentoBite: "assets/lento/bite.png",
    lentoRecover: "assets/lento/bite-recover.png",
    lentoHowl: "assets/lento/howl.png",
    lentoCoil: "assets/lento/tail-sweep.png",
    lentoSweep: "assets/lento/tail-sweep.png",
    lentoPoisonTell: "assets/lento/poison-spit.png",
    lentoPoison: "assets/lento/poison-spit.png",
    lentoJumpTell: "assets/lento/jump-slam.png",
    lentoJump: "assets/lento/jump-slam.png",
    lentoLand: "assets/lento/jump-slam.png",
    lentoSonic: "assets/lento/sonic-tail-slam.png",
    lentoChargeTell: "assets/lento/charge.png",
    lentoCharge: "assets/lento/charge.png",
    lentoCrash: "assets/lento/wall-crash.png"
  };

  const cropTable = {
    tiqueIdle: [70, 1120, 340, 450],
    tiqueWalk: [430, 1120, 420, 450],
    tiqueRun: [835, 1120, 420, 450],
    tiqueJump: [1240, 1120, 380, 450],
    tiqueLand: [1620, 1120, 410, 450],
    tiqueHit: [1610, 1650, 420, 450],
    tiqueDown: [2000, 1650, 430, 450],
    lentoSide: [410, 20, 490, 270],
    lentoPipe: [1265, 20, 390, 280],
    lentoBite: [235, 325, 220, 160],
    lentoRecover: [465, 325, 190, 160],
    lentoHowl: [680, 320, 300, 175],
    lentoCoil: [1010, 320, 175, 170],
    lentoSweep: [1190, 320, 455, 175],
    lentoPoisonTell: [25, 520, 235, 170],
    lentoPoison: [275, 520, 250, 170],
    lentoJumpTell: [550, 520, 160, 170],
    lentoJump: [700, 510, 130, 190],
    lentoLand: [810, 520, 185, 170],
    lentoSonic: [1015, 515, 620, 180],
    lentoChargeTell: [35, 725, 245, 160],
    lentoCharge: [270, 720, 310, 170],
    lentoCrash: [800, 715, 220, 175]
  };

  function chromaCrop(image, crop) {
    const [sx, sy, sw, sh] = crop;
    const out = document.createElement("canvas");
    out.width = sw;
    out.height = sh;
    const g = out.getContext("2d", { willReadFrequently: true });
    g.imageSmoothingEnabled = false;
    g.drawImage(image, sx, sy, sw, sh, 0, 0, sw, sh);
    const pixels = g.getImageData(0, 0, sw, sh);
    const d = pixels.data;
    const total = sw * sh;
    const seen = new Uint8Array(total);
    const queue = new Int32Array(total);
    let head = 0;
    let tail = 0;
    const isBackdrop = index => {
      const i = index * 4;
      const r = d[i], green = d[i + 1], b = d[i + 2];
      return r > 178 && green > 178 && b > 178 && Math.max(r, green, b) - Math.min(r, green, b) < 38;
    };
    const enqueue = index => {
      if (seen[index] || !isBackdrop(index)) return;
      seen[index] = 1;
      queue[tail++] = index;
    };
    for (let x = 0; x < sw; x++) { enqueue(x); enqueue((sh - 1) * sw + x); }
    for (let y = 0; y < sh; y++) { enqueue(y * sw); enqueue(y * sw + sw - 1); }
    while (head < tail) {
      const index = queue[head++];
      const x = index % sw;
      const y = Math.floor(index / sw);
      if (x > 0) enqueue(index - 1);
      if (x + 1 < sw) enqueue(index + 1);
      if (y > 0) enqueue(index - sw);
      if (y + 1 < sh) enqueue(index + sw);
    }
    for (let index = 0; index < total; index++) {
      if (seen[index]) d[index * 4 + 3] = 0;
    }
    g.putImageData(pixels, 0, 0);
    return out;
  }

  const actionSpriteLoads = Object.entries(actionSpriteFiles).map(([name, src]) => {
    const image = Object.assign(new Image(), { src });
    return image.decode().then(() => { art.actionSprites[name] = image; });
  });

  const animationLoads = Object.entries(animationFiles).flatMap(([name, paths]) => {
    art.animations[name] = [];
    return paths.map((src, index) => {
      const image = Object.assign(new Image(), { src });
      return image.decode().then(() => { art.animations[name][index] = image; });
    });
  });

  Promise.all([art.tique.decode(), art.lento.decode(), ...actionSpriteLoads, ...animationLoads]).then(() => {
    for (const [name, crop] of Object.entries(cropTable)) {
      art.sprites[name] = chromaCrop(name.startsWith("tique") ? art.tique : art.lento, crop);
    }
    art.ready = true;
  }).catch(() => { art.ready = false; });

  let audioCtx = null;
  let soundOn = false;
  let last = performance.now();
  let cameraX = 0;
  let shake = 0;
  let flash = 0;
  let game;

  const clamp = (n, a, b) => Math.max(a, Math.min(b, n));
  const lerp = (a, b, t) => a + (b - a) * t;
  const hit = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  const consume = (...names) => names.some(name => pressed.has(name));
  const down = (...names) => names.some(name => keys.has(name));

  function beep(freq = 180, duration = 0.08, type = "square", gain = 0.035) {
    if (!soundOn) return;
    audioCtx ||= new AudioContext();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = type;
    o.frequency.value = freq;
    g.gain.setValueAtTime(gain, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
    o.connect(g).connect(audioCtx.destination);
    o.start();
    o.stop(audioCtx.currentTime + duration);
  }

  function makePlayer() {
    return {
      x: 62, y: FLOOR - 48, w: 32, h: 48, vx: 0, vy: 0, face: 1,
      hp: 5, maxHp: 5, grounded: true, attacking: 0, attackUsed: false,
      dodge: 0, invuln: 0, slow: 0, stun: 0, captured: 0, hidden: 0,
      state: "idle", damageTaken: 0
    };
  }

  function makeBoss() {
    return {
      x: 735, y: FLOOR - 74, w: 105, h: 74, hp: 100, maxHp: 100,
      face: -1, visible: false, vulnerable: false, armor: false,
      hurt: 0, groggy: 0, phaseDamage: 0, targetX: 0
    };
  }

  function reset(phase = 1) {
    game = {
      phase, state: "intro", stateTime: 0, pattern: "silhouette", patternTime: 0,
      nextPattern: 1.8, sequence: 0, complete: false, drained: false,
      player: makePlayer(), boss: makeBoss(), rats: [], projectiles: [], waves: [],
      puddles: [], particles: [], message: "", messageTime: 0, totalDamage: 0,
      activePipe: 1, panelReady: false
    };
    if (phase === 2) {
      game.boss.hp = 70;
      beginPhase2();
    } else if (phase === 3) {
      game.boss.hp = 20;
      beginPhase3();
    } else {
      setPattern("silhouette", 0);
      showMessage("배관 너머에서 무언가 움직인다", 2.3);
    }
    syncUI();
    canvas.focus();
  }

  function setPattern(name, duration = 0) {
    game.pattern = name;
    game.patternTime = 0;
    game.nextPattern = duration;
    game.boss.vulnerable = false;
  }

  function showMessage(text, duration = 1.5) {
    game.message = text;
    game.messageTime = duration;
  }

  function damagePlayer(amount, sourceX) {
    const p = game.player;
    if (p.invuln > 0 || p.hidden > 0 || tuning.invincible || game.complete) return false;
    p.hp -= amount;
    p.damageTaken += amount;
    p.invuln = 1.05;
    p.vx = sourceX < p.x ? 150 : -150;
    p.vy = -150;
    shake = 0.28;
    flash = 0.08;
    beep(90, 0.16, "sawtooth", 0.05);
    if (p.hp <= 0) {
      p.hp = 0;
      p.state = "down";
      showMessage("코어 정지 · 우측 검증 패널에서 재시작", 99);
    }
    return true;
  }

  function damageBoss(amount) {
    const b = game.boss;
    if (!b.visible || (!b.vulnerable && game.phase === 1) || b.hurt > 0 || b.armor || game.complete) return false;
    const dealt = b.vulnerable ? amount : Math.max(1, Math.floor(amount * 0.5));
    b.hp = Math.max(0, b.hp - dealt);
    b.hurt = 0.14;
    b.phaseDamage += dealt;
    game.totalDamage += dealt;
    burst(b.x + b.w * 0.5, b.y + 30, colors.gold, 6);
    beep(125, 0.06);
    if (game.phase === 1 && b.phaseDamage >= 12 && game.pattern === "p1_recover") {
      b.phaseDamage = 0;
      b.groggy = 2.15;
      b.vulnerable = true;
      setPattern("p1_groggy", 2.15);
      showMessage("렌토가 배관에 끼었다", 1.5);
    }
    if (b.hp <= 70 && game.phase === 1) beginPhase2();
    if (b.hp <= 20 && game.phase === 2) beginPhase3();
    if (b.hp <= 0) defeatBoss();
    return true;
  }

  function beginPhase2() {
    game.phase = 2;
    game.boss.hp = Math.min(game.boss.hp, 70);
    game.boss.x = 450;
    game.boss.y = FLOOR - game.boss.h;
    game.boss.visible = true;
    game.boss.armor = true;
    game.boss.vulnerable = false;
    setPattern("p2_entry", 1.8 / tuning.telegraph);
    showMessage("렌토가 배관을 찢고 나온다", 1.8);
    shake = 0.8;
    syncUI();
  }

  function beginPhase3() {
    game.phase = 3;
    game.boss.hp = Math.min(game.boss.hp, 20);
    game.boss.visible = true;
    game.boss.x = 450;
    game.boss.y = FLOOR - game.boss.h;
    game.boss.armor = false;
    game.rats.length = 0;
    setPattern("p3_scream", 1.55 / tuning.telegraph);
    showMessage("궁지에 몰린 렌토가 비명을 지른다", 1.8);
    shake = 0.9;
    syncUI();
  }

  function defeatBoss() {
    game.complete = true;
    game.boss.visible = false;
    game.projectiles.length = 0;
    game.waves.length = 0;
    game.rats.length = 0;
    game.panelReady = true;
    setPattern("defeated", 0);
    showMessage("제어반을 재가동하라", 4);
    beep(70, 0.4, "triangle", 0.06);
    syncUI();
  }

  function burst(x, y, color, count) {
    for (let i = 0; i < count; i++) {
      game.particles.push({ x, y, vx: (Math.random() - 0.5) * 120, vy: -30 - Math.random() * 90, life: 0.5 + Math.random() * 0.35, color });
    }
  }

  function spawnRats(count = 4) {
    for (let i = 0; i < count; i++) {
      game.rats.push({ x: game.boss.x - 10 - i * 24, y: FLOOR - 18, w: 24, h: 18, hp: 2, vx: 0, attack: Math.random() * 0.8, hurt: 0 });
    }
    game.boss.armor = true;
  }

  function attackRect() {
    const p = game.player;
    return { x: p.face > 0 ? p.x + p.w - 4 : p.x - 24, y: p.y + 11, w: 28, h: 26 };
  }

  function startAttack() {
    const p = game.player;
    if (p.attacking > 0 || p.dodge > 0 || p.hidden > 0 || p.stun > 0 || p.captured > 0 || p.hp <= 0) return;
    p.attacking = 0.24;
    p.attackUsed = false;
    beep(280, 0.04, "square", 0.025);
  }

  function startDodge() {
    const p = game.player;
    if (p.dodge > 0 || !p.grounded || p.stun > 0 || p.captured > 0 || p.hidden > 0 || p.hp <= 0) return;
    p.dodge = 0.34;
    p.invuln = Math.max(p.invuln, 0.32);
    p.vx = p.face * 255;
    beep(420, 0.05, "triangle", 0.02);
  }

  function tryInteract() {
    const p = game.player;
    if (game.panelReady && Math.abs(p.x - 890) < 62) {
      game.drained = true;
      game.panelReady = false;
      showMessage("정화시설 재가동 · 배수가 시작된다", 99);
      beep(220, 0.2, "sine", 0.05);
      return;
    }
    if (game.phase === 3 && (game.pattern === "p3_charge_tell" || game.pattern === "p3_charge")) {
      const pipe = PIPE_X.find(x => Math.abs((p.x + p.w / 2) - x) < 55);
      if (pipe !== undefined) {
        p.hidden = 1.7;
        p.vx = 0;
        showMessage("배관 안으로 숨었다", 1);
        beep(340, 0.08, "triangle", 0.025);
      }
    }
  }

  function updatePlayer(dt) {
    const p = game.player;
    p.invuln = Math.max(0, p.invuln - dt);
    p.attacking = Math.max(0, p.attacking - dt);
    p.dodge = Math.max(0, p.dodge - dt);
    p.slow = Math.max(0, p.slow - dt);
    p.stun = Math.max(0, p.stun - dt);
    p.captured = Math.max(0, p.captured - dt);
    p.hidden = Math.max(0, p.hidden - dt);
    if (p.hp <= 0) {
      return;
    }

    if (consume("KeyX")) startAttack();
    if (consume("KeyC")) startDodge();
    if (consume("ArrowUp")) tryInteract();

    const locked = p.stun > 0 || p.captured > 0 || p.hidden > 0;
    const move = locked ? 0 : (down("ArrowLeft") ? -1 : 0) + (down("ArrowRight") ? 1 : 0);
    if (move && p.dodge <= 0) {
      p.face = move;
      const speed = p.slow > 0 ? 74 : 142;
      p.vx = move * speed;
    } else if (p.dodge <= 0) {
      p.vx *= p.grounded ? 0.72 : 0.94;
    }
    if (!locked && consume("KeyZ") && p.grounded) {
      p.vy = -315;
      p.grounded = false;
      beep(360, 0.05, "square", 0.02);
    }

    p.vy += 900 * dt;
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    if (p.y + p.h >= FLOOR) {
      p.y = FLOOR - p.h;
      p.vy = 0;
      p.grounded = true;
    }
    p.x = clamp(p.x, 18, WORLD_W - p.w - 18);

    if (p.attacking > 0.08 && p.attacking < 0.19 && !p.attackUsed) {
      const ar = attackRect();
      let connected = false;
      for (const rat of game.rats) {
        if (rat.hp > 0 && hit(ar, rat)) {
          rat.hp -= 1;
          rat.hurt = 0.12;
          rat.vx = p.face * 120;
          burst(rat.x, rat.y, colors.bone, 4);
          connected = true;
        }
      }
      if (hit(ar, game.boss)) connected = damageBoss(4) || connected;

      if (game.phase === 1 && game.pattern === "silhouette") {
        const pipe = PIPE_X.findIndex(x => Math.abs((p.x + p.w / 2) - x) < 64);
        if (pipe >= 0) {
          game.activePipe = pipe;
          game.boss.x = PIPE_X[pipe] - 50;
          game.boss.y = FLOOR - game.boss.h;
          setPattern("p1_tell", 0.9 / tuning.telegraph);
          showMessage("금속음이 배관 안으로 번진다", 1.1);
          burst(PIPE_X[pipe], 122, colors.edge, 7);
          beep(105, 0.18, "square", 0.05);
          connected = true;
        }
      }

      if (tuning.parry && game.phase === 3 && game.pattern === "p3_charge" && Math.abs(game.boss.x - p.x) < 90) {
        chargeCrash(true);
        connected = true;
      }
      p.attackUsed = connected;
    }

    for (const puddle of game.puddles) {
      if (puddle.life > 0 && p.grounded && p.x + p.w > puddle.x && p.x < puddle.x + puddle.w) p.slow = Math.max(p.slow, 0.25);
    }

    p.state = locked ? (p.hidden > 0 ? "hidden" : p.captured > 0 ? "captured" : "stunned") :
      p.attacking > 0 ? "attack" : p.dodge > 0 ? "dodge" : !p.grounded ? "jump" : Math.abs(p.vx) > 12 ? "run" : "idle";
  }

  function updateBoss(dt) {
    const b = game.boss;
    b.hurt = Math.max(0, b.hurt - dt);
    b.groggy = Math.max(0, b.groggy - dt);
    game.patternTime += dt;

    if (game.complete) return;
    if (game.phase === 1) updatePhase1(dt);
    if (game.phase === 2) updatePhase2(dt);
    if (game.phase === 3) updatePhase3(dt);
  }

  function updatePhase1(dt) {
    const b = game.boss;
    if (game.pattern === "silhouette") {
      b.visible = false;
      game.activePipe = Math.floor((performance.now() / 1100) % 3);
      return;
    }
    if (game.pattern === "p1_tell" && game.patternTime >= game.nextPattern) {
      b.visible = true;
      b.face = game.player.x < b.x ? -1 : 1;
      setPattern("p1_bite", 0.38);
      shake = 0.18;
      beep(72, 0.18, "sawtooth", 0.04);
      return;
    }
    if (game.pattern === "p1_bite") {
      const bite = { x: b.face < 0 ? b.x - 62 : b.x + b.w - 6, y: b.y + 14, w: 68, h: 48 };
      if (game.patternTime > 0.11 && game.patternTime < 0.29 && hit(bite, game.player)) damagePlayer(1, b.x);
      if (game.patternTime >= game.nextPattern) {
        setPattern("p1_recover", 1.45);
        b.vulnerable = true;
        showMessage("물기가 빗나갔다 · 지금이 빈틈이다", 1.1);
      }
      return;
    }
    if (game.pattern === "p1_recover") {
      b.vulnerable = true;
      if (game.patternTime >= game.nextPattern) {
        b.visible = false;
        setPattern("silhouette", 0);
      }
      return;
    }
    if (game.pattern === "p1_groggy") {
      b.visible = true;
      b.vulnerable = true;
      if (game.patternTime >= game.nextPattern) {
        b.visible = false;
        setPattern("silhouette", 0);
      }
    }
  }

  function updatePhase2(dt) {
    const b = game.boss;
    const p = game.player;
    if (game.pattern === "p2_entry" && game.patternTime >= game.nextPattern) {
      spawnRats(4);
      setPattern("p2_command", 1.4);
      showMessage("하울링이 새끼쥐를 몰아붙인다", 1.4);
      return;
    }

    game.rats = game.rats.filter(r => r.hp > 0);
    b.armor = game.rats.length > 0;
    b.vulnerable = !b.armor;

    if (game.pattern === "p2_command") {
      if (game.patternTime >= game.nextPattern) setPattern("p2_neutral", 1.1);
    } else if (game.pattern === "p2_tail_tell" && game.patternTime >= game.nextPattern) {
      setPattern("p2_tail", 0.62);
      beep(85, 0.13, "sawtooth", 0.04);
    } else if (game.pattern === "p2_tail") {
      const sweep = { x: b.x - 92, y: FLOOR - 34, w: 225, h: 32 };
      if (game.patternTime > 0.12 && game.patternTime < 0.48 && hit(sweep, p) && damagePlayer(1, b.x)) {
        p.captured = 1.1;
        p.x = b.x + (b.face < 0 ? -12 : 72);
        showMessage("렌토가 티크를 물고 갉아먹는다", 1.1);
      }
      if (game.patternTime >= game.nextPattern) setPattern("p2_neutral", 1.1);
    } else if (game.pattern === "p2_spit_tell" && game.patternTime >= game.nextPattern) {
      game.projectiles.push({ type: "poison", x: b.x + 20, y: b.y + 22, vx: (p.x < b.x ? -1 : 1) * 185, vy: -155, life: 3 });
      setPattern("p2_neutral", 1.4);
      beep(150, 0.12, "square", 0.03);
    } else if (game.pattern === "p2_neutral" && game.patternTime >= game.nextPattern) {
      if (game.rats.length > 0) {
        setPattern("p2_command", 1.1 / tuning.telegraph);
      } else {
        const pick = game.sequence++ % 3;
        if (pick === 0) {
          spawnRats(3);
          setPattern("p2_command", 1.15 / tuning.telegraph);
          showMessage("하울링 · 새끼쥐 공격 명령", 1);
        } else if (pick === 1) {
          setPattern("p2_tail_tell", 0.72 / tuning.telegraph);
          showMessage("꼬리를 크게 휘감는다", 0.75);
        } else {
          setPattern("p2_spit_tell", 0.7 / tuning.telegraph);
          showMessage("목구멍에 독이 차오른다", 0.75);
        }
      }
    }
  }

  function updatePhase3(dt) {
    const b = game.boss;
    const p = game.player;
    b.armor = false;
    b.vulnerable = game.pattern === "p3_groggy";

    if (game.pattern === "p3_scream" && game.patternTime >= game.nextPattern) {
      setPattern("p3_neutral", 0.8);
      return;
    }
    if (game.pattern === "p3_neutral" && game.patternTime >= game.nextPattern) {
      const pick = game.sequence++ % 3;
      if (pick === 0) startJumpSlam();
      if (pick === 1) startSonic();
      if (pick === 2) startCharge();
      return;
    }
    if (game.pattern === "p3_jump_tell" && game.patternTime >= game.nextPattern) {
      b.visible = true;
      b.x = b.targetX - b.w / 2;
      b.y = -100;
      setPattern("p3_jump_fall", 0.43);
    } else if (game.pattern === "p3_jump_fall") {
      b.y = lerp(-100, FLOOR - b.h, clamp(game.patternTime / game.nextPattern, 0, 1));
      if (game.patternTime >= game.nextPattern) {
        b.y = FLOOR - b.h;
        shake = 0.55;
        burst(b.x + b.w / 2, FLOOR - 4, colors.warning, 14);
        const slam = { x: b.x - 50, y: FLOOR - 32, w: b.w + 100, h: 32 };
        if (hit(slam, p)) damagePlayer(2, b.x);
        setPattern("p3_neutral", 1.05);
      }
    } else if (game.pattern === "p3_sonic_tell" && game.patternTime >= game.nextPattern) {
      setPattern("p3_sonic", 1.65);
      [0, 0.42, 0.84].forEach(delay => game.waves.push({ x: b.x + b.w / 2, y: FLOOR - 20, dir: p.x < b.x ? -1 : 1, delay, life: 2, hit: false }));
      beep(64, 0.32, "sine", 0.045);
    } else if (game.pattern === "p3_sonic" && game.patternTime >= game.nextPattern) {
      setPattern("p3_neutral", 0.85);
    } else if (game.pattern === "p3_charge_tell" && game.patternTime >= game.nextPattern) {
      b.face = p.x < b.x ? -1 : 1;
      setPattern("p3_charge", 1.35);
      beep(92, 0.2, "sawtooth", 0.045);
    } else if (game.pattern === "p3_charge") {
      b.x += b.face * 390 * dt;
      if (hit(b, p) && p.hidden <= 0 && !tuning.parry) damagePlayer(2, b.x);
      if (b.x <= 14 || b.x + b.w >= WORLD_W - 14 || game.patternTime >= game.nextPattern) chargeCrash(false);
    } else if (game.pattern === "p3_groggy" && game.patternTime >= game.nextPattern) {
      setPattern("p3_neutral", 0.75);
    }
  }

  function startJumpSlam() {
    game.boss.targetX = clamp(game.player.x + game.player.w / 2 + (Math.random() - 0.5) * 70, 90, WORLD_W - 90);
    game.boss.visible = false;
    setPattern("p3_jump_tell", 0.85 / tuning.telegraph);
    showMessage("천장에서 낙하 지점이 울린다", 0.9);
  }

  function startSonic() {
    setPattern("p3_sonic_tell", 0.82 / tuning.telegraph);
    showMessage("렌토가 꼬리로 바닥을 겨눈다", 0.9);
  }

  function startCharge() {
    setPattern("p3_charge_tell", 1.05 / tuning.telegraph);
    showMessage("배관에 숨으면 돌진을 흘릴 수 있다", 1.2);
  }

  function chargeCrash(parried) {
    const b = game.boss;
    b.x = clamp(b.x, 16, WORLD_W - b.w - 16);
    shake = 0.7;
    setPattern("p3_groggy", parried ? 1.6 : 2.25);
    b.vulnerable = true;
    showMessage(parried ? "실험 패링 성공 · 렌토 그로기" : "벽 충돌 · 렌토 그로기", 1.4);
    burst(b.x + (b.face > 0 ? b.w : 0), b.y + 28, colors.edge, 12);
    beep(58, 0.24, "square", 0.055);
  }

  function updateRats(dt) {
    const p = game.player;
    for (const r of game.rats) {
      r.hurt = Math.max(0, r.hurt - dt);
      r.attack -= dt;
      const dir = p.x < r.x ? -1 : 1;
      if (r.hurt <= 0) r.vx = lerp(r.vx, dir * 75, 0.08);
      r.x += r.vx * dt;
      if (r.attack <= 0 && Math.abs(r.x - p.x) < 32) {
        damagePlayer(1, r.x);
        r.attack = 1.1;
      }
    }
  }

  function updateHazards(dt) {
    const p = game.player;
    for (const q of game.projectiles) {
      q.life -= dt;
      q.vy += 420 * dt;
      q.x += q.vx * dt;
      q.y += q.vy * dt;
      if (q.y > FLOOR - 8) {
        game.puddles.push({ x: q.x - 24, y: FLOOR - 7, w: 58, life: 5 });
        q.life = 0;
      } else if (hit({ x: q.x - 6, y: q.y - 6, w: 12, h: 12 }, p)) {
        if (damagePlayer(1, q.x)) p.slow = 3.2;
        q.life = 0;
      }
    }
    game.projectiles = game.projectiles.filter(q => q.life > 0);
    for (const q of game.puddles) q.life -= dt;
    game.puddles = game.puddles.filter(q => q.life > 0);

    for (const w of game.waves) {
      w.delay -= dt;
      if (w.delay > 0) continue;
      w.life -= dt;
      w.x += w.dir * 245 * dt;
      const wr = { x: w.x - 16, y: FLOOR - 26, w: 32, h: 26 };
      if (!w.hit && hit(wr, p)) {
        if (damagePlayer(1, w.x)) p.stun = 1.15;
        w.hit = true;
      }
    }
    game.waves = game.waves.filter(w => w.life > 0 && w.x > -50 && w.x < WORLD_W + 50);

    for (const q of game.particles) {
      q.life -= dt;
      q.vy += 260 * dt;
      q.x += q.vx * dt;
      q.y += q.vy * dt;
    }
    game.particles = game.particles.filter(q => q.life > 0);
  }

  function update(dt) {
    dt = Math.min(dt, 0.034) * tuning.time;
    if (!art.ready) {
      pressed.clear();
      return;
    }
    game.messageTime = Math.max(0, game.messageTime - dt);
    shake = Math.max(0, shake - dt);
    flash = Math.max(0, flash - dt);
    updatePlayer(dt);
    updateBoss(dt);
    updateRats(dt);
    updateHazards(dt);
    const targetCamera = clamp(game.player.x - W * 0.42, 0, WORLD_W - W);
    cameraX = lerp(cameraX, targetCamera, 0.07);
    syncUI();
    pressed.clear();
  }

  function rect(x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
  }

  function drawBackground() {
    rect(0, 0, W, H, "#080d0f");
    rect(0, 38, W, 226, "#121b1d");

    for (let y = 54; y < 260; y += 24) {
      const offset = (Math.floor(y / 24) % 2) * 28;
      for (let x = -cameraX * 0.14 % 56 - 56 + offset; x < W + 56; x += 56) {
        rect(x, y, 53, 21, "#172225");
        rect(x + 2, y + 2, 49, 2, "#243034");
        rect(x + 2, y + 19, 49, 2, "#0a1012");
      }
    }

    rect(0, 38, W, 8, "#4b5758");
    rect(0, 46, W, 4, "#090d0f");
    rect(0, 62, W, 9, "#293739");
    for (let x = -cameraX * 0.32 % 96 - 96; x < W + 96; x += 96) {
      rect(x, 63, 70, 6, "#536063");
      rect(x + 16, 71, 8, 154, "#263235");
      rect(x + 19, 73, 2, 150, "#647073");
      rect(x + 56, 71, 8, 154, "#1d282a");
    }

    for (let x = -cameraX % 128 - 128; x < W + 128; x += 128) {
      rect(x + 10, 96, 84, 116, "#0d1517aa");
      rect(x + 15, 101, 74, 106, "#182326");
      rect(x + 20, 106, 64, 2, "#334043");
      rect(x + 20, 198, 64, 3, "#090d0f");
      rect(x + 28, 123, 20, 5, "#293638");
      rect(x + 57, 123, 18, 5, "#293638");
    }

    for (let x = -cameraX * 0.62 % 190 - 80; x < W + 190; x += 190) drawValve(x + 86, 116);

    rect(0, 252, W, 9, "#273437");
    rect(0, 261, W, 7, "#070b0c");
    rect(0, FLOOR, W, H - FLOOR, "#1c292c");
    rect(0, FLOOR, W, 5, "#778285");
    rect(0, FLOOR + 5, W, 4, "#080d0f");
    for (let x = -cameraX % 48 - 48; x < W + 48; x += 48) {
      rect(x, FLOOR + 10, 45, 31, "#263235");
      rect(x + 3, FLOOR + 13, 39, 2, "#3c494b");
      rect(x + 40, FLOOR + 16, 2, 20, "#101719");
      rect(x + 8, FLOOR + 27, 7, 3, "#6a4432");
    }

    for (const px of PIPE_X) drawPipe(px - cameraX);

    if (game.drained) {
      rect(0, H - 13, W, 13, "#18333a");
      for (let x = -((performance.now() * 0.05) % 60); x < W; x += 60) rect(x, H - 12, 28, 2, "#61c0cd");
    } else {
      rect(0, H - 18, W, 18, "#1e464f");
      rect(0, H - 18, W, 2, "#4a9098");
      for (let x = -((performance.now() * 0.025) % 45); x < W; x += 45) {
        rect(x, H - 16, 22, 2, "#347581");
        rect(x + 12, H - 8, 18, 2, "#16343a");
      }
    }

    drawPixelGlow(game.player.x - cameraX + 16, game.player.y + 27, colors.cyan, 34);
    if (game.boss.visible) drawPixelGlow(game.boss.x - cameraX + game.boss.w / 2, game.boss.y + 39, "#e8a52c", 44);

    rect(0, 0, 7, H, "#05080999");
    rect(W - 7, 0, 7, H, "#05080999");

    if (game.panelReady || game.drained) drawPanel(890 - cameraX);
  }

  function drawValve(x, y) {
    ctx.strokeStyle = "#4e5c5e";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(x, y, 14, 0, Math.PI * 2);
    ctx.stroke();
    rect(x - 2, y - 18, 4, 36, "#364345");
    rect(x - 18, y - 2, 36, 4, "#364345");
    rect(x - 4, y - 4, 8, 8, "#88523a");
  }

  function drawPixelGlow(x, y, color, size) {
    ctx.save();
    ctx.globalAlpha = 0.05;
    rect(x - size, y - size, size * 2, size * 2, color);
    ctx.globalAlpha = 0.08;
    rect(x - size * 0.65, y - size * 0.65, size * 1.3, size * 1.3, color);
    ctx.globalAlpha = 0.12;
    rect(x - size * 0.3, y - size * 0.3, size * 0.6, size * 0.6, color);
    ctx.restore();
  }

  function drawPipe(x) {
    const cy = PIPE_CY;
    ctx.fillStyle = "#090e0f";
    ctx.beginPath();
    ctx.arc(x, cy, 61, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#172124";
    ctx.lineWidth = 18;
    ctx.stroke();
    ctx.strokeStyle = "#687477";
    ctx.lineWidth = 11;
    ctx.stroke();
    ctx.strokeStyle = "#303c3f";
    ctx.lineWidth = 5;
    ctx.stroke();

    for (let i = 0; i < 8; i++) {
      const a = i * Math.PI / 4;
      const bx = x + Math.cos(a) * 53;
      const by = cy + Math.sin(a) * 53;
      rect(bx - 3, by - 3, 6, 6, i % 3 === 0 ? "#9a5d3b" : "#1b2426");
      rect(bx - 1, by - 1, 2, 2, "#90999a");
    }

    rect(x - 34, cy + 38, 11, 4, "#71422f");
    rect(x + 12, cy - 48, 16, 4, "#8a5034");
    rect(x + 36, cy + 20, 5, 15, "#334b3b");
    if (game.phase === 3 && (game.pattern === "p3_charge_tell" || game.pattern === "p3_charge")) {
      ctx.save();
      ctx.globalAlpha = 0.6 + Math.sin(performance.now() / 90) * 0.22;
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(x, cy, 63, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
    if (game.phase === 1 && game.pattern === "silhouette" && game.activePipe === PIPE_X.indexOf(Math.round(x + cameraX))) {
      const bob = Math.sin(performance.now() / 180) * 3;
      if (art.ready) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(x, cy, 43, 0, Math.PI * 2);
        ctx.clip();
        ctx.globalAlpha = 0.62;
        ctx.drawImage(art.sprites.lentoPipe, x - 55, cy - 44 + bob, 110, 86);
        ctx.restore();
      } else {
        rect(x - 24, cy - 25 + bob, 48, 54, "#111514");
      }
      rect(x - 13, cy - 10 + bob, 5, 4, "#d1a32d");
      rect(x + 8, cy - 10 + bob, 5, 4, "#d1a32d");
    }
  }

  function drawPanel(x) {
    rect(x - 22, 222, 44, 80, "#263033");
    rect(x - 17, 228, 34, 44, "#596468");
    rect(x - 11, 235, 22, 24, game.drained ? colors.cyan : "#5a382a");
    rect(x - 5, 279, 10, 10, colors.brassLight);
    if (game.panelReady) {
      ctx.fillStyle = colors.bone;
      ctx.font = "10px sans-serif";
      ctx.textAlign = "center";
      ctx.fillText("↑", x, 213);
    }
  }

  function drawArtSprite(name, x, bottom, width, height, facing = 1, alpha = 1, angle = 0, frameIndex = null) {
    const frames = art.animations[name];
    const loopIndex = frames?.length ? Math.floor(performance.now() * (animationFps[name] || 10) / 1000) % frames.length : 0;
    const sprite = frames?.[frameIndex === null ? loopIndex : clamp(frameIndex, 0, frames.length - 1)] || art.actionSprites[name] || art.sprites[name];
    if (!sprite) return false;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(Math.round(x), Math.round(bottom));
    ctx.scale(facing, 1);
    ctx.rotate(angle * facing);
    ctx.drawImage(sprite, -width / 2, -height, width, height);
    ctx.restore();
    return true;
  }

  function drawTique(p) {
    if (p.hidden > 0) {
      const pipe = PIPE_X.reduce((a, b) => Math.abs(b - p.x) < Math.abs(a - p.x) ? b : a);
      const x = pipe - cameraX;
      ctx.save();
      ctx.beginPath();
      ctx.arc(x, PIPE_CY, 40, 0, Math.PI * 2);
      ctx.clip();
      if (art.ready) drawArtSprite("tiqueIdle", x, FLOOR - 2, 72, 94, 1, 0.82);
      ctx.restore();
      drawPixelGlow(x, PIPE_CY, colors.cyan, 31);
      rect(x - 13, PIPE_CY - 8, 7, 6, colors.cyan);
      rect(x + 6, PIPE_CY - 8, 7, 6, colors.cyan);
      return;
    }

    const x = p.x - cameraX + p.w / 2;
    const bottom = (p.grounded ? FLOOR : p.y + p.h) + 5;
    const flicker = p.invuln > 0 && Math.floor(performance.now() / 65) % 2 === 0;
    const alpha = flicker ? 0.42 : 1;
    let sprite = "tiqueIdle";
    let width = 96;
    let height = 96;
    let angle = 0;
    let frameIndex = null;
    if (p.state === "run") sprite = "tiqueRun";
    if (p.state === "jump") {
      sprite = "tiqueJump";
      frameIndex = Math.round(clamp((p.vy + 315) / 630, 0, 1) * 6);
    }
    if (p.attacking > 0) {
      sprite = down("ArrowUp") ? "tiqueAttackUp" : down("ArrowDown") ? "tiqueAttackDown" : "tiqueAttackHorizontal";
      if (sprite === "tiqueAttackHorizontal") frameIndex = Math.floor(clamp(1 - p.attacking / 0.24, 0, 0.999) * 6);
    }
    if (p.state === "stunned") sprite = "tiqueStunned";
    if (p.invuln > 0.58 && p.state !== "dodge") {
      sprite = "tiqueHit";
      frameIndex = Math.floor(clamp((1.05 - p.invuln) / 0.47, 0, 0.999) * 6);
    }
    if (p.state === "down") { sprite = "tiqueDown"; width = 112; height = 112; }
    if (p.state === "dodge") {
      sprite = "tiqueDash";
      frameIndex = Math.floor(clamp(1 - p.dodge / 0.34, 0, 0.999) * 6);
    }

    ctx.save();
    ctx.globalAlpha = 0.35;
    ctx.fillStyle = "#020405";
    ctx.beginPath();
    ctx.ellipse(x, FLOOR + 1, p.state === "down" ? 28 : 18, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    drawArtSprite(sprite, x, bottom, width, height, p.face, alpha, angle, frameIndex);

    if (p.attacking > 0) {
      const reach = p.face > 0 ? x + 21 : x - 21;
      ctx.save();
      ctx.globalAlpha = 0.78;
      ctx.strokeStyle = colors.cyan;
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(reach, bottom - 37, 26, p.face > 0 ? -1.1 : 2.1, p.face > 0 ? 1.15 : 4.25);
      ctx.stroke();
      ctx.restore();
      rect(reach + p.face * 17 - 3, bottom - 41, 7, 7, colors.brassLight);
    }
    if (p.slow > 0) {
      rect(x - 22, FLOOR - 3, 44, 5, "#506e31");
      rect(x - 12, FLOOR - 6, 24, 3, colors.poison);
    }
  }

  function drawLento(b) {
    if (!b.visible) return;
    const x = b.x - cameraX + b.w / 2;
    const bottom = (b.y + b.h) + 6;
    let sprite = "lentoSide";
    let width = 242;
    let height = 142;
    if (game.pattern === "p1_bite") { sprite = "lentoBite"; width = 212; height = 154; }
    if (game.pattern === "p1_recover") { sprite = "lentoRecover"; width = 202; height = 144; }
    if (game.pattern.includes("groggy")) { sprite = "lentoCrash"; width = 214; height = 146; }
    if (["p2_entry", "p2_command", "p3_scream"].includes(game.pattern)) { sprite = "lentoHowl"; width = 232; height = 158; }
    if (game.pattern === "p2_tail_tell") { sprite = "lentoCoil"; width = 174; height = 152; }
    if (game.pattern === "p2_tail") { sprite = "lentoSweep"; width = 306; height = 136; }
    if (game.pattern === "p2_spit_tell") { sprite = "lentoPoisonTell"; width = 190; height = 142; }
    if (game.projectiles.some(q => q.type === "poison") && game.phase === 2) { sprite = "lentoPoison"; width = 204; height = 142; }
    if (game.pattern === "p3_jump_tell") { sprite = "lentoJumpTell"; width = 178; height = 142; }
    if (game.pattern === "p3_jump_fall") { sprite = "lentoJump"; width = 154; height = 174; }
    if (game.pattern === "p3_sonic_tell" || game.pattern === "p3_sonic") { sprite = "lentoSonic"; width = 286; height = 136; }
    if (game.pattern === "p3_charge_tell") { sprite = "lentoChargeTell"; width = 212; height = 136; }
    if (game.pattern === "p3_charge") { sprite = "lentoCharge"; width = 270; height = 128; }

    ctx.save();
    ctx.globalAlpha = 0.5;
    ctx.fillStyle = "#020405";
    ctx.beginPath();
    ctx.ellipse(x, FLOOR + 2, width * 0.35, 7, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    const hurtAlpha = b.hurt > 0 ? 0.52 : 1;
    drawArtSprite(sprite, x, bottom, width, height, b.face, hurtAlpha);

    if (b.armor) {
      ctx.save();
      ctx.globalAlpha = 0.72 + Math.sin(performance.now() / 110) * 0.12;
      ctx.strokeStyle = "#d7b64d";
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 5]);
      ctx.beginPath();
      ctx.ellipse(x, bottom - 55, width * 0.42, 55, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  }

  function drawHazards() {
    for (const q of game.puddles) {
      rect(q.x - cameraX, q.y, q.w, 7, colors.poison);
      rect(q.x - cameraX + 7, q.y - 3, q.w - 15, 3, "#c2e773");
    }
    for (const q of game.projectiles) {
      rect(q.x - cameraX - 6, q.y - 6, 12, 12, colors.poison);
      rect(q.x - cameraX - 2, q.y - 9, 5, 5, "#c2e773");
    }
    for (const w of game.waves) {
      if (w.delay > 0) continue;
      rect(w.x - cameraX - 3, FLOOR - 28, 6, 28, "#e7cb6b");
      rect(w.x - cameraX - 13, FLOOR - 19, 26, 4, "#917c38");
    }
    if (game.pattern === "p3_jump_tell") {
      const x = game.boss.targetX - cameraX;
      rect(x - 50, FLOOR - 8, 100, 8, "#762d28");
      rect(x - 25, FLOOR - 12, 50, 4, colors.warning);
    }
    if (game.pattern === "p1_bite" && tuning.hitboxes) {
      const b = game.boss;
      const r = { x: b.face < 0 ? b.x - 62 : b.x + b.w - 6, y: b.y + 14, w: 68, h: 48 };
      ctx.strokeStyle = colors.warning;
      ctx.strokeRect(r.x - cameraX, r.y, r.w, r.h);
    }
  }

  function drawRats() {
    for (const r of game.rats) {
      const x = r.x - cameraX;
      rect(x, r.y + 5, 22, 12, r.hurt > 0 ? colors.bone : colors.furDark);
      rect(x + 14, r.y, 10, 11, colors.fur);
      rect(x + 19, r.y + 3, 3, 3, colors.gold);
      rect(x - 7, r.y + 13, 9, 3, colors.fur);
    }
  }

  function drawParticles() {
    for (const q of game.particles) rect(q.x - cameraX, q.y, 3, 3, q.color);
  }

  function drawHUD() {
    rect(14, 14, 180, 10, "#0a0e0f");
    rect(17, 17, 174 * (game.boss.hp / game.boss.maxHp), 4, colors.warning);
    ctx.fillStyle = "#dfe4df";
    ctx.font = "bold 9px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText("RENTO", 15, 34);
    ctx.fillStyle = colors.brassLight;
    ctx.fillText(`PHASE ${game.phase}`, 154, 34);

    for (let i = 0; i < game.player.maxHp; i++) {
      const x = 15 + i * 18;
      rect(x, 328, 13, 13, i < game.player.hp ? colors.cyanDark : "#273034");
      if (i < game.player.hp) rect(x + 3, 331, 7, 7, colors.cyan);
    }
    if (game.player.slow > 0) {
      ctx.fillStyle = colors.poison;
      ctx.fillText("STICKY", 111, 338);
    }

    if (game.messageTime > 0) {
      ctx.font = "bold 11px sans-serif";
      const width = Math.min(430, ctx.measureText(game.message).width + 28);
      rect((W - width) / 2, 270, width, 24, "#0c1112dd");
      ctx.fillStyle = "#f0e7d0";
      ctx.textAlign = "center";
      ctx.fillText(game.message, W / 2, 286);
    }
    if (game.drained) {
      rect(198, 104, 244, 87, "#101719e8");
      ctx.textAlign = "center";
      ctx.fillStyle = colors.cyan;
      ctx.font = "bold 15px sans-serif";
      ctx.fillText("정화시설 재가동", 320, 132);
      ctx.fillStyle = colors.bone;
      ctx.font = "11px sans-serif";
      ctx.fillText("배수 완료 · 갈고리 획득 경로 개방", 320, 156);
      ctx.fillStyle = colors.brassLight;
      ctx.fillText("RENTO CLEAR", 320, 177);
    }

    if (tuning.hitboxes) {
      ctx.strokeStyle = colors.cyan;
      ctx.strokeRect(game.player.x - cameraX, game.player.y, game.player.w, game.player.h);
      if (game.boss.visible) {
        ctx.strokeStyle = colors.warning;
        ctx.strokeRect(game.boss.x - cameraX, game.boss.y, game.boss.w, game.boss.h);
      }
      if (game.player.attacking > 0) {
        const ar = attackRect();
        ctx.strokeStyle = colors.brassLight;
        ctx.strokeRect(ar.x - cameraX, ar.y, ar.w, ar.h);
      }
    }
  }

  function render() {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.setTransform(OUTPUT_SCALE, 0, 0, OUTPUT_SCALE, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.save();
    if (shake > 0) ctx.translate((Math.random() - 0.5) * 7, (Math.random() - 0.5) * 5);
    drawBackground();
    drawHazards();
    drawRats();
    drawLento(game.boss);
    drawTique(game.player);
    drawParticles();
    drawHUD();
    if (flash > 0) rect(0, 0, W, H, "#d9f5ef33");
    ctx.restore();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
  }

  const phasePatterns = {
    1: [
      ["배관 유인", () => { game.activePipe = 1; game.boss.x = PIPE_X[1] - 50; setPattern("p1_tell", 0.9 / tuning.telegraph); }],
      ["물기 빈틈", () => { game.boss.visible = true; setPattern("p1_recover", 1.45); game.boss.vulnerable = true; }],
      ["그로기", () => { game.boss.visible = true; setPattern("p1_groggy", 2.15); game.boss.vulnerable = true; }]
    ],
    2: [
      ["새끼쥐", () => { spawnRats(4); setPattern("p2_command", 1.2); }],
      ["꼬리 휩쓸기", () => setPattern("p2_tail_tell", 0.72 / tuning.telegraph)],
      ["독 뱉기", () => setPattern("p2_spit_tell", 0.7 / tuning.telegraph)]
    ],
    3: [
      ["점프 찍기", startJumpSlam],
      ["3연속 음파", startSonic],
      ["돌진", startCharge],
      ["벽 충돌", () => chargeCrash(false)]
    ]
  };

  function syncUI() {
    document.getElementById("buildState").textContent = `P${game.phase} · ${phaseTitle()}`;
    document.getElementById("stateReadout").textContent = game.player.state;
    document.getElementById("patternReadout").textContent = game.pattern;
    document.getElementById("damageReadout").textContent = String(game.totalDamage);
    document.getElementById("objective").textContent = objectiveText();
    document.querySelectorAll("[data-phase]").forEach(btn => btn.classList.toggle("active", Number(btn.dataset.phase) === game.phase));
    const grid = document.getElementById("patternGrid");
    const key = String(game.phase);
    if (grid.dataset.phase !== key) {
      grid.dataset.phase = key;
      grid.replaceChildren();
      for (const [label, action] of phasePatterns[game.phase]) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = label;
        button.addEventListener("click", () => { action(); canvas.focus(); });
        grid.appendChild(button);
      }
    }
  }

  function phaseTitle() {
    if (game.drained) return "배수 완료";
    if (game.complete) return "제어반 재가동";
    return game.phase === 1 ? "배관 속 포식자" : game.phase === 2 ? "무리의 우두머리" : "궁지의 폭주";
  }

  function objectiveText() {
    if (game.drained) return "정화시설이 다시 흐르기 시작했다";
    if (game.panelReady) return "오른쪽 제어반에서 ↑로 배수를 재가동하라";
    if (game.phase === 1) return game.pattern === "silhouette" ? "배관 가까이에서 공격해 소리를 내라" : "물기 뒤 드러난 머리와 코어를 공격하라";
    if (game.phase === 2) return game.rats.length ? "새끼쥐를 먼저 제거해 렌토의 방어를 무너뜨려라" : "렌토의 전조를 읽고 빈틈을 공격하라";
    if (game.pattern.includes("charge")) return "가까운 배관에서 ↑로 숨어 돌진을 벽에 유도하라";
    return "점프와 회피로 폭주 패턴을 넘겨라";
  }

  function frame(now) {
    update((now - last) / 1000);
    render();
    last = now;
    requestAnimationFrame(frame);
  }

  addEventListener("keydown", e => {
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "KeyZ", "KeyX", "KeyC"].includes(e.code)) e.preventDefault();
    if (!keys.has(e.code)) pressed.add(e.code);
    keys.add(e.code);
  });
  addEventListener("keyup", e => keys.delete(e.code));
  canvas.addEventListener("pointerdown", () => canvas.focus());

  document.querySelectorAll("[data-phase]").forEach(btn => btn.addEventListener("click", () => reset(Number(btn.dataset.phase))));
  document.getElementById("resetBtn").addEventListener("click", () => reset(game.phase));
  document.getElementById("invincibleToggle").addEventListener("change", e => tuning.invincible = e.target.checked);
  document.getElementById("hitboxToggle").addEventListener("change", e => tuning.hitboxes = e.target.checked);
  document.getElementById("parryToggle").addEventListener("change", e => tuning.parry = e.target.checked);
  document.getElementById("telegraphRange").addEventListener("input", e => {
    tuning.telegraph = Number(e.target.value);
    document.getElementById("telegraphOut").value = `${tuning.telegraph.toFixed(2)}×`;
  });
  document.getElementById("timeRange").addEventListener("input", e => {
    tuning.time = Number(e.target.value);
    document.getElementById("timeOut").value = `${tuning.time.toFixed(2)}×`;
  });
  document.getElementById("soundToggle").addEventListener("click", e => {
    soundOn = !soundOn;
    e.currentTarget.classList.toggle("active", soundOn);
    if (soundOn) beep(440, 0.08, "sine", 0.03);
    canvas.focus();
  });

  reset(1);
  requestAnimationFrame(frame);
})();
