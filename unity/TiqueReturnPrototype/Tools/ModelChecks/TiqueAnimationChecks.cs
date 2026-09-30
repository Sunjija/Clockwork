using TiqueReturn;

static class TiqueAnimationChecks
{
    public static object Run(PuzzleBook book, IDictionary<string, int[]> clips)
    {
        var checks = new List<string>();
        int selections = 0;
        void Check(bool ok, string name)
        {
            if (!ok) throw new Exception("TIQUE ANIMATION: " + name);
            checks.Add(name);
        }
        int Pick(ReturnModel hero, out string clip)
        {
            int frame = TiqueAnimation.Select(hero, clips, out clip);
            if (frame < 0 || frame >= clips[clip].Length) throw new Exception("Tique index outside " + clip + ": " + frame);
            selections++;
            return frame;
        }
        ReturnModel Hero() => new ReturnModel { phase = Phase.Combat, grounded = true, attackAge = 9, dashAge = 9, airAge = 9, landAge = 9 };
        ReworkModel Arena()
        {
            var model = new ReworkModel(book); model.BeginArena(); model.phase = Journey.Combat;
            return model;
        }

        var jump = Arena(); var command = ReworkCommand.Empty; command.jump = true;
        jump.Tick(1f / 120, command);
        Check(jump.hero.y < ReworkModel.Floor && jump.hero.vy < 0 && Pick(jump.hero, out var clip) == 3 && clip == "Jump", "first jump immediately rises in takeoff, never a grounded preload");
        jump.Tick(1f / 120, command);
        Check(jump.hero.jumps == 2 && jump.hero.vy < 0 && Pick(jump.hero, out clip) == 3 && clip == "DoubleJump", "double jump impulse immediately shows release, never grounded crouch");

        foreach (bool doubleJump in new[] { false, true })
        {
            var hero = Hero(); hero.grounded = false; hero.doublePose = doubleJump;
            var seen = new HashSet<int>();
            for (int i = 0; i < 12; i++) { hero.airAge = i / 120f; hero.vy = -245 + hero.airAge * 800; seen.Add(Pick(hero, out clip)); }
            Check(seen.SetEquals(new[] { 3, 4 }), (doubleJump ? "double" : "first") + " jump moves from release into rising without grounded preload drawings");
            hero.airAge = .2f;
            foreach (float velocity in new[] { -220f, -80f, -20f, 15f, 80f, 220f }) { hero.vy = velocity; Pick(hero, out _); }
            hero.vy = 220; int falling = Pick(hero, out clip); hero.airAge = 9;
            Check(Pick(hero, out _) == falling && falling == (doubleJump ? 8 : 9), (doubleJump ? "double" : "first") + " jump holds its falling pose instead of replaying takeoff");

            hero.grounded = true; hero.axis = 1; hero.dashAge = .2f; seen.Clear(); bool landingPrecedence = true;
            for (int i = 0; i < 15; i++)
            {
                hero.landAge = i / 120f;
                if (hero.landAge < .12f) { seen.Add(Pick(hero, out clip)); landingPrecedence &= clip == (doubleJump ? "DoubleJump" : "Jump"); }
            }
            Check(landingPrecedence, (doubleJump ? "double" : "first") + " landing keeps precedence over held direction and dash recovery");
            Check(seen.SetEquals(Enumerable.Range(doubleJump ? 9 : 10, doubleJump ? 4 : 5)), (doubleJump ? "double" : "first") + " jump landing exposes its entire suffix inside 120ms");
            hero.landAge = .12f;
            Check(Pick(hero, out clip) >= 0 && clip == "Walk", "held movement resumes immediately after the existing landing presentation");
            hero.grounded = false; hero.landAge = 0;
            Check(Pick(hero, out clip) == falling && clip == (doubleJump ? "DoubleJump" : "Jump"), "an airborne pose ignores stale landing time");
        }

        var dash = Hero(); var dashSeen = new HashSet<int>(); bool activeDashSelected = true;
        for (int i = 0; i < 20; i++)
        {
            dash.dashAge = i / 120f;
            if (dash.Dashing) { dashSeen.Add(Pick(dash, out clip)); activeDashSelected &= clip == "Dash"; }
        }
        Check(activeDashSelected, "active dash remains selected throughout its existing movement window");
        Check(dashSeen.SetEquals(Enumerable.Range(0, 7)), "160ms dash exposes preparation and all four active silhouettes at 120Hz");
        dashSeen.Clear();
        for (int i = 0; i < 22; i++)
        {
            dash.dashAge = .16f + i / 120f;
            if (dash.dashAge < .34f) dashSeen.Add(Pick(dash, out _));
        }
        Check(dashSeen.SetEquals(Enumerable.Range(7, 5)), "stationary grounded recovery exposes all five recovery frames");
        dash.dashAge = .2f; dash.axis = 1;
        Check(Pick(dash, out clip) >= 0 && clip == "Walk", "resumed movement immediately overrides residual dash recovery");
        dash.axis = 0; dash.grounded = false; dash.vy = 80; dash.airAge = .3f;
        Check(Pick(dash, out clip) == 8 && clip == "Jump", "airborne dash ending returns to falling physics rather than ground recovery");
        dash.dashAge = .05f; dash.attackAge = .1f;
        Check(Pick(dash, out clip) >= 0 && clip == "Dash", "active dash precedes attack and airborne posture");
        dash.dashAge = 9;
        Check(Pick(dash, out clip) == 3 && clip == "Attack", "airborne attack stays valid and precedes the ordinary air pose");
        dash.grounded = true; dash.landAge = 0;
        Check(Pick(dash, out clip) == 3 && clip == "Attack", "ongoing attack keeps its pose when physics reaches the floor");

        var attack = Hero(); var attackSeen = new HashSet<int>();
        for (int i = 0; i < 56; i++)
        {
            attack.attackAge = i / 120f;
            if (attack.Attacking) attackSeen.Add(Pick(attack, out _));
        }
        Check(attackSeen.SetEquals(Enumerable.Range(0, 12)), "460ms attack exposes all twelve poses");
        attack.attackAge = .12f;
        Check(Pick(attack, out clip) == 4 && clip == "Attack", "existing 120ms contact begins on the punch impact pose");
        attack.attackAge = .46f;
        Check(Pick(attack, out clip) >= 0 && clip == "Idle", "attack ends at its unchanged 460ms boundary");

        // The player presents at 60Hz while production physics ticks at 120Hz.
        // Sample after two real ticks, not at synthetic age zero: a short first
        // exposure can otherwise pass a 120Hz test yet never reach the screen.
        foreach (bool doubleJump in new[] { false, true })
        {
            var presented = Arena();
            var jumpCommand = ReworkCommand.Empty; jumpCommand.jump = true;
            if (doubleJump) presented.Tick(1f / 120, jumpCommand);
            var preparationSeen = new HashSet<int>(); var landingSeen = new HashSet<int>();
            bool firstPresentationRises = false;
            for (int rendered = 0; rendered < 75; rendered++)
            {
                presented.Tick(1f / 120, rendered == 0 ? jumpCommand : ReworkCommand.Empty);
                presented.Tick(1f / 120, ReworkCommand.Empty);
                int frame = Pick(presented.hero, out clip);
                if (rendered == 0) firstPresentationRises = presented.hero.vy < 0 && presented.hero.y < ReworkModel.Floor;
                if (clip != (doubleJump ? "DoubleJump" : "Jump")) continue;
                if (!presented.hero.grounded && presented.hero.airAge < .1f) preparationSeen.Add(frame);
                if (presented.hero.grounded && presented.hero.landAge < .12f) landingSeen.Add(frame);
            }
            Check(firstPresentationRises && preparationSeen.SetEquals(new[] { 3, 4 }),
                (doubleJump ? "double" : "first") + " jump visibly starts in release and rising at 60Hz without an airborne crouch");
            Check(landingSeen.SetEquals(Enumerable.Range(doubleJump ? 9 : 10, doubleJump ? 4 : 5)),
                (doubleJump ? "double" : "first") + " jump landing visibly exposes every suffix pose at 60Hz");
        }
        var presentedDash = Arena(); var dashCommand = ReworkCommand.Empty; dashCommand.dash = true;
        var visibleDash = new HashSet<int>(); var visibleRecovery = new HashSet<int>(); bool dashMovedImmediately = false;
        for (int rendered = 0; rendered < 25; rendered++)
        {
            presentedDash.Tick(1f / 120, rendered == 0 ? dashCommand : ReworkCommand.Empty);
            presentedDash.Tick(1f / 120, ReworkCommand.Empty);
            int frame = Pick(presentedDash.hero, out clip);
            if (rendered == 0) dashMovedImmediately = presentedDash.hero.x > 80 && presentedDash.hero.Dashing;
            if (clip != "Dash") continue;
            if (presentedDash.hero.Dashing) visibleDash.Add(frame); else visibleRecovery.Add(frame);
        }
        Check(dashMovedImmediately && visibleDash.SetEquals(Enumerable.Range(0, 7)), "60Hz dash visibly exposes all preparation/active poses without delaying movement");
        Check(visibleRecovery.SetEquals(Enumerable.Range(7, 5)), "60Hz stationary dash visibly exposes every recovery pose");
        var presentedAttack = Arena(); var attackCommand = ReworkCommand.Empty; attackCommand.attack = true;
        var visibleAttack = new HashSet<int>();
        for (int rendered = 0; rendered < 30; rendered++)
        {
            presentedAttack.Tick(1f / 120, rendered == 0 ? attackCommand : ReworkCommand.Empty);
            presentedAttack.Tick(1f / 120, ReworkCommand.Empty);
            int frame = Pick(presentedAttack.hero, out clip);
            if (clip == "Attack") visibleAttack.Add(frame);
        }
        Check(visibleAttack.SetEquals(Enumerable.Range(0, 12)), "60Hz attack visibly exposes all twelve existing timed poses");

        var idle = Hero(); var idleSeen = new HashSet<int>();
        int idlePeriod = clips["Idle"].Sum();
        for (int i = 0; i < idlePeriod; i += 4) { idle.clock = i / 1000f; idleSeen.Add(Pick(idle, out clip)); }
        Check(idleSeen.SetEquals(Enumerable.Range(0, clips["Idle"].Length)), "calm idle exposes every authored subtle frame");
        idle.clock = 0; int idleFirst = Pick(idle, out _); idle.clock = idlePeriod / 1000f;
        Check(Pick(idle, out _) == idleFirst, "idle loops with the manifest period");

        var hurt = Arena(); hurt.clock = 1.1f; hurt.hurtAt = hurt.clock; hurt.hero.invincible = 1;
        Check(TiqueAnimation.InitialHurtVisible(hurt) && !TiqueAnimation.ShouldBlinkBody(hurt), "stationary initial hurt remains visible during an otherwise hidden blink phase");
        hurt.hero.grounded = false; hurt.hero.axis = 1;
        Check(TiqueAnimation.InitialHurtVisible(hurt) && !TiqueAnimation.ShouldBlinkBody(hurt), "airborne moving initial hurt remains visible");
        hurt.hurtAt = hurt.clock - .16f;
        Check(!TiqueAnimation.InitialHurtVisible(hurt) && TiqueAnimation.ShouldBlinkBody(hurt), "body blinking resumes after hurt without extending protection");
        hurt.reducedEffects = true;
        Check(!TiqueAnimation.ShouldBlinkBody(hurt), "reduced effects retain a continuously visible body");
        hurt.reducedEffects = false; hurt.hurtAt = hurt.clock; hurt.hero.dashAge = .05f;
        Check(!TiqueAnimation.InitialHurtVisible(hurt), "a newly requested dash can replace hurt visually");
        hurt.hero.dashAge = 9; hurt.phase = Journey.Dead;
        Check(!TiqueAnimation.InitialHurtVisible(hurt) && !TiqueAnimation.ShouldBlinkBody(hurt), "death is never hidden by a stale protection or hurt timer");

        var puzzle = new CorePuzzle(book.levels[0]); puzzle.visualAge = 0; puzzle.motion = .15f;
        float startPhase = puzzle.walkAge;
        puzzle.AdvanceVisual(.0375f);
        Check(Math.Abs((puzzle.walkAge - startPhase) * 45 - 5.625f) < .001f, "puzzle feet advance with eased visible distance during acceleration");
        puzzle.AdvanceVisual(.075f);
        Check(Math.Abs((puzzle.walkAge - startPhase) * 45 - 30.375f) < .001f, "puzzle feet advance with eased visible distance during settling");
        puzzle.AdvanceVisual(.1f);
        Check(Math.Abs((puzzle.walkAge - startPhase) * 45 - 36) < .001f && puzzle.motion == 0, "a completed puzzle step keeps its original 36px distance and lock duration");
        float stopped = puzzle.walkAge; puzzle.AdvanceVisual(1);
        Check(puzzle.walkAge == stopped, "settled puzzle feet stop advancing");

        // Exercise the selector on actual production states without authoring a
        // second movement implementation or asserting subjective visual quality.
        var stress = Arena();
        for (int i = 0; i < 3600 && stress.phase == Journey.Combat; i++)
        {
            var c = ReworkCommand.Empty;
            c.axis = i % 240 < 120 ? 1 : -1; c.jump = i % 79 == 0; c.dash = i % 137 == 0; c.attack = i % 63 == 0;
            stress.Tick(1f / 120, c); Pick(stress.hero, out _);
        }
        Check(ReturnModel.DashTime == .16f && ReturnModel.Coyote == .12f && ReturnModel.JumpBuffer == .10f && ReworkModel.Speed == 88,
            "movement, dash, coyote and buffer constants remain unchanged");
        return new { passed = true, count = checks.Count, selections, idleFrames = clips["Idle"].Length, scope = "Production C# Tique selector and model; rendered art, physical inputs and subjective motion quality excluded", checks };
    }
}
