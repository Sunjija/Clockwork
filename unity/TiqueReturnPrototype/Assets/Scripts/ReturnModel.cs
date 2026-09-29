using System;
using System.Collections.Generic;
using Mathf = TiqueReturn.GridMath;

namespace TiqueReturn
{
    // Plain C# so the exact game rules can be checked without starting an editor.
    public static class GridMath
    {
        public static float Abs(float x) => Math.Abs(x);
        public static float Min(float a, float b) => Math.Min(a, b);
        public static int Min(int a, int b) => Math.Min(a, b);
        public static float Max(float a, float b) => Math.Max(a, b);
        public static float Clamp(float value, float low, float high) => Math.Min(high, Math.Max(low, value));
        public static float MoveTowards(float value, float target, float delta)
            => Math.Abs(target - value) <= delta ? target : value + Math.Sign(target - value) * delta;
    }
    public struct Platform
    {
        public float x, y, width, height;
        public Platform(float x, float y, float width, float height)
        { this.x = x; this.y = y; this.width = width; this.height = height; }
        public float xMin => x;
        public float xMax => x + width;
        public float yMin => y;
    }
    public enum Phase { Title, Puzzle, Arrival, Combat, Rescan, Exit, Ending, Dead }
    public enum BossMove { Rest, Aim, Slam, Open, Retract, WaveCharge, Wave, Disabled }
    public struct Command
    {
        public int axis;
        public bool jump, dash, attack, interact;
    }
    [Serializable] public class ClipSpec { public string name; public int[] durations; }
    [Serializable] public class ClipFile { public ClipSpec[] clips; }

    // All coordinates use a 640 x 360 reference grid, y down. No renderer controls collision.
    public sealed class ReturnModel
    {
        public const float Floor = 252f, Speed = 42f, Gravity = 800f;
        public const float Coyote = .12f, JumpBuffer = .10f, DashTime = .16f;
        public Phase phase = Phase.Title;
        public BossMove bossMove = BossMove.Rest;
        public float x = 62, y = Floor, vy, clock, playTime, phaseAge, walkAge, airAge = 9;
        public float attackAge = 9, dashAge = 9, landAge = 9, invincible, flash, hitStop;
        public int facing = 1, jumps, hp = 4, overload = 6, deaths, hits, axis;
        public bool grounded = true, dashReady = true, doublePose, paused, helpMode, muted;
        public float graceUntil = -100, jumpUntil = -100, dashCooldown;
        public bool magnetOn, railRight, attached, gateOpen, practiceDone;
        public float magnetX = 355, crateX = 355, crateBottom = Floor, railBusy;
        public bool poweredSeen, carriedSeen, placedSeen;
        public bool arenaMagnet, captured;
        public float trapCooldown, bossAge, aimX = 235, fistX = 532, fistBottom = 156, waveX = -100;
        public int cycles, attackSerial, lastHitSerial = -1;
        public string message = "", lastEvent = "ready";
        public float messageLeft, noProgress;
        public readonly List<string> events = new List<string>();
        public readonly List<Platform> platforms = new List<Platform>();
        public Action<string> Sound;
        public bool Inspection => phase != Phase.Title && phase != Phase.Puzzle;
        public bool Dashing => dashAge < DashTime;
        public bool Attacking => attackAge < .46f;
        public bool PlateDown => !attached && Mathf.Abs(crateX - 468) < 4 && crateBottom >= Floor - .5f;
        public bool CanMove => phase == Phase.Puzzle || phase == Phase.Combat || phase == Phase.Rescan || phase == Phase.Exit;
        public bool WeakOpen => phase == Phase.Combat && bossMove == BossMove.Open;
        public float TotalTime => playTime;

        public ReturnModel() { SetPlatforms(); }
        void SetPlatforms()
        {
            platforms.Clear();
            if (!Inspection) { platforms.Add(new Platform(20, 222, 48, 8)); platforms.Add(new Platform(77, 201, 45, 8)); }
        }
        public void Event(string name)
        {
            lastEvent = name; events.Add(clock.ToString("F2", System.Globalization.CultureInfo.InvariantCulture) + ":" + name);
            if (events.Count > 500) events.RemoveAt(0);
        }
        public void Say(string text, float seconds = 3.2f) { message = text; messageLeft = seconds; }
        public void Start()
        {
            phase = Phase.Puzzle; phaseAge = 0; Say("분류: 폐기 대상.   ……귀환 경로를 찾습니다.", 6);
            Event("start");
        }
        public void ResetPlayer(float px)
        {
            x = px; y = Floor; vy = 0; facing = 1; grounded = true; jumps = 0; dashReady = true;
            attackAge = dashAge = landAge = airAge = 9; invincible = 1; dashCooldown = 0;
            jumpUntil = graceUntil = -100; walkAge = 0; axis = 0; doublePose = false;
        }
        public void BeginArena()
        {
            phase = Phase.Arrival; phaseAge = 0; ResetPlayer(65); SetPlatforms();
            Say("식별 오류. 폐기 절차를 유지합니다.", 3); Event("arena-arrival");
        }
        public void Retry()
        {
            if (phase != Phase.Dead) return;
            phase = Phase.Combat; phaseAge = 0; hp = 4; overload = 6; cycles = 0;
            bossMove = BossMove.Rest; bossAge = 0; waveX = -100; fistX = 532; fistBottom = 156;
            arenaMagnet = captured = false; trapCooldown = 0; hitStop = 0; ResetPlayer(65);
            Say("내려오는 팔을 피한 뒤, 붉은 손목 단자를 공격하세요.", 4); Event("checkpoint-retry");
        }
        public string Interaction()
        {
            if (phase == Phase.Puzzle)
            {
                if (Near(150)) return railBusy > 0 ? "레일 이동 중…" : magnetOn ? "E  전력을 문으로" : "E  전력을 자석으로";
                if (Near(255)) return railBusy > 0 ? "레일 이동 중…" : railRight ? "E  자석을 보관점으로" : "E  자석을 압력판으로";
            }
            if (phase == Phase.Combat && Near(104)) return trapCooldown > 0 ? "자석 재충전 중…" : arenaMagnet ? "E  정비 자석 끄기" : "E  정비 자석 켜기";
            if (phase == Phase.Rescan && Near(478)) return "E  식별 검사 다시 시작";
            return "";
        }
        bool Near(float px) => Mathf.Abs(x - px) < 33 && Mathf.Abs(y - Floor) < 14;
        public void Interact()
        {
            if (phase == Phase.Title) { Start(); return; }
            if (phase == Phase.Dead) { Retry(); return; }
            if (phase == Phase.Puzzle)
            {
                if (Near(150) && railBusy <= 0)
                {
                    magnetOn = !magnetOn; noProgress = 0; poweredSeen |= magnetOn;
                    if (!magnetOn) attached = false;
                    Say(magnetOn ? "동력 → 전자석. 같은 표식의 금속이 반응합니다." : "동력 → 문. 자석이 놓은 추는 아래로 내려옵니다.");
                    Event(magnetOn ? "magnet-on" : "magnet-off"); Sound?.Invoke("switch");
                }
                else if (Near(255) && railBusy <= 0)
                {
                    railRight = !railRight; railBusy = 1.1f; noProgress = 0;
                    Event("rail-toggle"); Sound?.Invoke("switch");
                    if (!magnetOn) Say("자석만 움직였습니다. 추를 붙잡으려면 동력이 필요합니다.");
                }
            }
            else if (phase == Phase.Combat && Near(104) && trapCooldown <= 0)
            {
                arenaMagnet = !arenaMagnet; Sound?.Invoke("switch"); Event("arena-magnet-toggle");
                Say(arenaMagnet ? "자석 준비. 같은 표식 위로 수거 팔을 유도하세요." : "정비 자석 해제.");
            }
            else if (phase == Phase.Rescan && Near(478))
            {
                phase = Phase.Exit; phaseAge = 0; Sound?.Invoke("success"); Event("identity-restored");
                Say("식별명: 티크.   귀환처: 엘리아스 공방.", 6);
            }
        }
        public bool Jump()
        {
            jumpUntil = clock + JumpBuffer;
            return ConsumeJump();
        }
        bool ConsumeJump()
        {
            if (jumpUntil < clock || Dashing || !CanMove) return false;
            bool first = grounded || (jumps == 0 && clock <= graceUntil);
            if (!first && jumps >= 2) return false;
            bool coyote = first && !grounded;
            jumps = first ? 1 : 2; vy = first ? -220 : -205; grounded = false; doublePose = !first;
            jumpUntil = graceUntil = -100; airAge = 0; attackAge = 9;
            Event(coyote ? "coyote-jump" : first ? "jump" : "double-jump"); Sound?.Invoke("jump"); return true;
        }
        public bool Dash()
        {
            if (!CanMove || !dashReady || Dashing || dashCooldown > 0) return false;
            dashReady = false; dashAge = 0; dashCooldown = .30f; vy = 0; attackAge = 9;
            Sound?.Invoke("dash"); Event("dash"); return true;
        }
        public bool Attack()
        {
            if (!CanMove || Dashing || Attacking) return false;
            attackAge = 0; attackSerial++; Event("attack"); return true;
        }
        public void Tick(float dt, Command command)
        {
            if (paused) return;
            if (hitStop > 0) { hitStop = Mathf.Max(0, hitStop - dt); return; }
            clock += dt; phaseAge += dt; messageLeft -= dt; flash = Mathf.Max(0, flash - dt);
            invincible = Mathf.Max(0, invincible - dt); dashCooldown -= dt; trapCooldown -= dt;
            if (phase != Phase.Title && phase != Phase.Ending && phase != Phase.Dead) playTime += dt;
            if (command.interact) Interact();
            if (phase == Phase.Arrival && phaseAge > 3)
            {
                phase = Phase.Combat; phaseAge = 0; bossMove = BossMove.Rest; bossAge = 0;
                Say("팔을 피하고 붉은 단자를 J로 공격하세요.", 5); Event("combat-start");
            }
            if (!CanMove) return;
            axis = Math.Sign(command.axis);
            if (axis != 0 && !Dashing && !Attacking) facing = axis;
            if (command.jump) Jump();
            if (command.dash) Dash();
            if (command.attack) Attack();
            ConsumeJump();
            Move(dt);
            if (phase == Phase.Puzzle)
            {
                PuzzleTick(dt);
                if (x > 608 && gateOpen) BeginArena();
            }
            else if (phase == Phase.Combat) BossTick(dt);
            else if (phase == Phase.Exit && phaseAge > 4 && x > 607)
            {
                phase = Phase.Ending; phaseAge = 0; Event("ending"); Sound?.Invoke("success");
            }
            if (Attacking && attackAge >= .12f && attackAge <= .22f) ResolveAttack();
            attackAge += dt; dashAge += dt; airAge += dt; landAge += dt;
            if (grounded && !Dashing && dashCooldown <= 0) dashReady = true;
        }
        void Move(float dt)
        {
            bool onGround = grounded; float oldY = y, oldX = x;
            float vx = Dashing ? facing * 260 : Attacking && grounded ? 0 : axis * Speed;
            float limit = phase == Phase.Puzzle ? (gateOpen ? 624 : 575) : phase == Phase.Exit ? (phaseAge > 4 ? 624 : 570) : 486;
            x = Mathf.Clamp(x + vx * dt, 16, limit);
            if (!Dashing || grounded) { y += vy * dt + Gravity * dt * dt * .5f; vy += Gravity * dt; }
            grounded = false; float landingY = Floor;
            foreach (Platform p in platforms)
                if (x + 7 > p.xMin && x - 7 < p.xMax && oldY <= p.yMin + .01f && y >= p.yMin) landingY = Mathf.Min(landingY, p.yMin);
            if (vy >= 0 && oldY <= landingY + .01f && y >= landingY)
            {
                y = landingY; vy = 0; grounded = true; jumps = 0; graceUntil = -100;
                if (!onGround) { landAge = 0; Event("land"); Sound?.Invoke("land"); }
            }
            if (onGround && !grounded && jumps == 0 && vy >= 0) { graceUntil = clock + Coyote; airAge = 9; doublePose = false; Event("walk-off"); }
            if (grounded && !Dashing && !Attacking && x != oldX) walkAge += Mathf.Abs(x - oldX) / 25f;
            else if (grounded && axis == 0) walkAge = 0;
            ConsumeJump();
        }
        void PuzzleTick(float dt)
        {
            noProgress += dt;
            if (railBusy > 0) { railBusy = Mathf.Max(0, railBusy - dt); magnetX = Mathf.MoveTowards(magnetX, railRight ? 468 : 355, 113 / 1.1f * dt); }
            else magnetX = railRight ? 468 : 355;
            if (magnetOn && !attached && Mathf.Abs(crateX - magnetX) < 4 && railBusy <= 0) { attached = true; Event("weight-caught"); }
            if (attached) { crateX = magnetX; crateBottom = Mathf.MoveTowards(crateBottom, 167, 120 * dt); carriedSeen |= railRight; }
            else crateBottom = Mathf.MoveTowards(crateBottom, Floor, 150 * dt);
            if (PlateDown) placedSeen = true;
            if (PlateDown && !magnetOn && !gateOpen)
            {
                gateOpen = true; Say("두 조건 충족. 검사실로 가는 문이 열렸습니다.", 6); Event("puzzle-complete"); Sound?.Invoke("success");
            }
        }
        public void Damage(string reason)
        {
            if (phase != Phase.Combat || invincible > 0) return;
            hp--; hits++; invincible = 1f; flash = .2f; attackAge = 9; Sound?.Invoke("hurt"); Event("hurt-" + reason);
            if (hp <= 0)
            {
                deaths++; phase = Phase.Dead; phaseAge = 0; waveX = -100; Event("death");
            }
        }
        void NextBoss(BossMove move) { bossMove = move; bossAge = 0; }
        void BossTick(float dt)
        {
            bossAge += dt;
            float warning = (cycles == 0 ? 1.3f : overload <= 3 ? .85f : 1.0f) * (helpMode ? 1.4f : 1);
            switch (bossMove)
            {
                case BossMove.Rest:
                    fistX = Mathf.MoveTowards(fistX, 532, dt * 150); fistBottom = Mathf.MoveTowards(fistBottom, 156, dt * 150);
                    if (bossAge > .8f) { aimX = Mathf.Clamp(x, 92, 425); NextBoss(BossMove.Aim); Sound?.Invoke("warning"); }
                    break;
                case BossMove.Aim:
                    if (bossAge < .4f) aimX = Mathf.Clamp(x, 92, 425);
                    fistX = Mathf.MoveTowards(fistX, aimX, dt * 360); fistBottom = Mathf.MoveTowards(fistBottom, 118, dt * 260);
                    if (bossAge >= warning) NextBoss(BossMove.Slam);
                    break;
                case BossMove.Slam:
                    fistX = aimX; fistBottom = Mathf.MoveTowards(fistBottom, Floor, dt * 900);
                    if (fistBottom >= Floor)
                    {
                        if (Mathf.Abs(x - aimX) < 30 && y > Floor - 85) Damage("slam");
                        captured = arenaMagnet && trapCooldown <= 0 && Mathf.Abs(aimX - 235) <= 30;
                        if (captured) { arenaMagnet = false; trapCooldown = 7; Event("magnet-capture"); Say("팔이 붙잡혔습니다. 붉은 단자를 공격하세요!", 2.8f); }
                        Sound?.Invoke("land"); NextBoss(BossMove.Open);
                    }
                    break;
                case BossMove.Open:
                    if (bossAge >= (captured ? 2.8f : 1.8f) * (helpMode ? 1.35f : 1)) NextBoss(BossMove.Retract);
                    break;
                case BossMove.Retract:
                    fistBottom = Mathf.MoveTowards(fistBottom, 156, dt * 230); fistX = Mathf.MoveTowards(fistX, 532, dt * 300);
                    if (bossAge > .65f) { NextBoss(BossMove.WaveCharge); Sound?.Invoke("warning"); }
                    break;
                case BossMove.WaveCharge:
                    if (bossAge > (helpMode ? 1.3f : .95f)) { waveX = 500; NextBoss(BossMove.Wave); }
                    break;
                case BossMove.Wave:
                    waveX -= dt * (helpMode ? 110 : 140);
                    if (Mathf.Abs(x - waveX) < 17 && y > Floor - 16) Damage("wave");
                    if (waveX < -20) { waveX = -100; cycles++; NextBoss(BossMove.Rest); }
                    break;
            }
        }
        void ResolveAttack()
        {
            if (lastHitSerial == attackSerial) return;
            float handX = x + facing * 22;
            if (phase == Phase.Puzzle && !practiceDone && Mathf.Abs(handX - 528) < 21 && y > Floor - 18)
            {
                practiceDone = true; lastHitSerial = attackSerial; Sound?.Invoke("hit"); hitStop = .045f;
                Say("타격 확인. 내려온 붉은 단자를 이 주먹으로 칠 수 있습니다."); Event("practice-hit");
            }
            if (WeakOpen && Mathf.Abs(handX - fistX) <= 20 && y > Floor - 15)
            {
                lastHitSerial = attackSerial; overload--; hitStop = .05f; flash = .12f; Sound?.Invoke("hit"); Event("boss-hit");
                if (overload <= 0)
                {
                    phase = Phase.Rescan; phaseAge = 0; bossMove = BossMove.Disabled; waveX = -100;
                    Say("과부하 해제. 오른쪽 검사 단말에서 E를 누르세요.", 6); Event("guardian-stopped");
                }
            }
        }
        static int Frame(float ms, int[] durations, int start = 0)
        {
            for (int n = start; n < durations.Length; n++) { if (ms < durations[n]) return n; ms -= durations[n]; }
            return durations.Length - 1;
        }
        public string Pose(Dictionary<string, int[]> clips, out int frame)
        {
            frame = 0;
            if (Dashing) { frame = Mathf.Min(6, Frame(dashAge * 1000, clips["Dash"], 3)); return "Dash"; }
            if (Attacking) { frame = Frame(attackAge * 1000, clips["Attack"]); return "Attack"; }
            if (!grounded)
            {
                if (doublePose) { frame = airAge < .045f ? 2 : airAge < .09f ? 3 : vy < -35 ? 4 : vy < 0 ? 5 : vy < 35 ? 6 : vy < 140 ? 7 : 8; return "DoubleJump"; }
                frame = airAge < .04f ? 3 : vy < -40 ? (airAge < .145f ? 4 : 5) : vy < 0 ? 6 : vy < 40 ? 7 : vy < 140 ? 8 : 9; return "Jump";
            }
            if (axis != 0 && CanMove) { int length = 0; foreach (int d in clips["Walk"]) length += d; frame = Frame(walkAge * 1000 % length, clips["Walk"]); return "Walk"; }
            if (landAge < .12f) { string c = doublePose ? "DoubleJump" : "Jump"; frame = Frame(landAge * 1000, clips[c], doublePose ? 9 : 10); return c; }
            return "Idle";
        }
    }
}
