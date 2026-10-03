using TiqueReturn;

static class WorldArtChecks
{
    public static List<string> Run(PuzzleBook book,ClipFile clips)
    {
        var pass=new List<string>();var names=clips.clips.ToDictionary(c=>c.name,c=>c.durations);
        void Check(bool condition,string message){if(!condition)throw new Exception(message);}
        void Known(string name){Check(names.ContainsKey(name),"Missing state asset: "+name);}
        string[] rows={"#######","#.....#","#.....#","#.....#","#.....#","#.....#","#######"};
        var p=new CorePuzzle(new PuzzleRoom{rows=rows,start=22,boxes=new[]{23},types=new[]{0},goals=new[]{24}});
        Check(WorldArtState.WallMask(p,0)==6&&WorldArtState.WallMask(p,6)==12&&WorldArtState.WallMask(p,42)==3&&WorldArtState.WallMask(p,48)==9,"Connected wall corner masks do not wrap rows or include outside tiles");
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-empty","Empty socket initially");
        Check(p.Move(1),"Legal push");
        Check(WorldArtState.Box(p,0,out _) =="battery-moving","Moving weight frame during interpolation");
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-empty","No false connection before physical arrival");
        p.AdvanceVisual(.16f);
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-connect","Contact plays connection frames");
        Check(WorldArtState.Box(p,0,out _) =="battery-docked","Contact powers weight");
        p.AdvanceVisual(.5f);Check(WorldArtState.Socket(p,0,out _) =="amber-slot-filled","Connected state persists");
        p.Undo();Check(WorldArtState.Socket(p,0,out _) =="amber-slot-empty"&&WorldArtState.Box(p,0,out _) =="battery-idle","Undo restores art, no stale latches");
        p.Move(1);p.Reset();Check(WorldArtState.Socket(p,0,out _) =="amber-slot-empty","Reset clears state art");
        pass.Add("move/contact/connect/filled sequence, undo and reset match the board");
        p=new CorePuzzle(new PuzzleRoom{rows=rows,start=22,boxes=new[]{23,10},types=new[]{0,0},goals=new[]{24,12}});
        Check(p.Move(1),"Place weight on one socket before complete board");p.AdvanceVisual(.7f);
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-filled","Partial socket connected");
        foreach(int direction in new[]{2,1,1,3,0})Check(p.Move(direction),"Connected weight remains movable");
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-empty","Moving connected weight away clears connection");
        p=new CorePuzzle(new PuzzleRoom{rows=rows,start=22,boxes=new[]{23,10},types=new[]{1,0},goals=new[]{24,12}});
        Check(p.Move(1)&&p.boxes[0]==26,"Empty goal does not stop orb");p.AdvanceVisual(.3f);
        Check(WorldArtState.Socket(p,0,out _) =="cyan-slot-empty","Passed socket does not latch a false connection");
        pass.Add("connected props are not locked; orb passes goals; wall adjacency stays in bounds");
        p=new CorePuzzle(new PuzzleRoom{rows=rows,start=22,boxes=new[]{24,25},types=new[]{0,1},goals=new[]{25,24}});
        Check(WorldArtState.Socket(p,0,out _) =="amber-slot-wrong"&&WorldArtState.Socket(p,1,out _) =="cyan-slot-wrong","Wrong type is distinct from empty and filled");
        Check(!p.Solved,"Wrong art agrees with unsolved rules");pass.Add("mismatched sockets use error-state sprites");
        var orbRows=(string[])rows.Clone();orbRows[3]="#...#.#";
        p=new CorePuzzle(new PuzzleRoom{rows=orbRows,start=22,boxes=new[]{23},types=new[]{1},goals=new[]{24}});
        p.Move(1);p.AdvanceVisual(.15f);
        Check(p.motionDuration==.27f&&p.motion>0&&WorldArtState.Box(p,0,out _) =="orb-moving","One-cell orb still uses its actual 270ms slide");
        p.AdvanceVisual(.13f);Check(WorldArtState.Box(p,0,out _) =="orb-docked","Orb settles at socket");pass.Add("orb travel timing and docked state agree");
        var m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.hero.x=m.pylons[0];
        var e=ReworkCommand.Empty;e.interact=true;m.Tick(1f/120,e);
        Check(WorldArtState.Pylon(m,0,out _) =="pylon-charging","E starts capacitor fill");
        m.Tick(.47f,ReworkCommand.Empty);Check(WorldArtState.Pylon(m,0,out _) =="pylon-armed","Charge finishes with armed prop");
        m.chargeLife=2;Check(WorldArtState.Pylon(m,0,out _) =="pylon-expiring","Expiry warning uses separate art");
        m.chargeLife=.001f;m.Tick(.01f,ReworkCommand.Empty);Check(WorldArtState.Pylon(m,0,out _) =="pylon-idle","Expired charge returns to idle");
        m.charged=1;m.chargeLife=10;m.bossMove=IronMove.Charge;m.bossX=430;m.bossFacing=1;
        for(int i=0;i<20&&!m.Vulnerable;i++)m.Tick(1f/120,ReworkCommand.Empty);
        Check(m.Vulnerable&&WorldArtState.Pylon(m,1,out _) =="pylon-discharge","Real pylon impact stamps a discharge");
        m.clock+=.5f;Check(WorldArtState.Pylon(m,1,out _) =="pylon-cooldown","Spent shutter during cooldown");
        m.clock+=2;Check(WorldArtState.Pylon(m,1,out _) =="pylon-idle","Cooldown ends visually");
        m.Retry(); // No-op while alive.
        m.phase=Journey.Dead;m.Retry();Check(m.lastDischargedPylon==-1&&WorldArtState.Pylon(m,1,out _) =="pylon-idle","Checkpoint clears old state events");
        pass.Add("pylon charge, arm, expiry, impact discharge, cooldown and retry");
        m.phase=Journey.Combat;m.bossMove=IronMove.Open;m.lastCoreHitAt=m.clock;
        Check(WorldArtState.Core(m,out _) =="core-hit","Core hit has its own frame sequence");
        m.clock+=.5f;Check(WorldArtState.Core(m,out _) =="core-exposed","Core returns to exposed state");
        m.bossMove=IronMove.Down;Check(WorldArtState.Core(m,out _) =="core-off","Defeated core goes dark");
        Check(WorldArtState.Exit(m,out _) =="exit-locked","Combat keeps exit closed");
        m.phase=Journey.Restored;m.restoredAt=m.clock;m.hero.x=602;
        m.chargeCooldown=.6f;
        Check(WorldArtState.Exit(m,out _) =="exit-opening","Restoration starts actual door frames");
        m.Tick(.1f,e);Check(m.phase==Journey.Restored,"Interaction cannot skip opening");
        m.Tick(.71f,ReworkCommand.Empty);Check(WorldArtState.Exit(m,out _) =="exit-open","Open door after 800ms");
        Check(m.chargeCooldown<=0,"Cooling continues after the boss is stopped");
        m.Tick(.01f,e);Check(m.phase==Journey.Ending&&WorldArtState.Exit(m,out _) =="exit-open","Ending keeps door open across age reset");
        pass.Add("core hit/off and locked/opening/open exit with interaction guard");
        int selections=0;
        foreach(var c in clips.clips)
        {
            Known(c.name);
            for(int i=0;i<1200;i++)
            {int f=WardenAnimation.FrameAt(c.durations,i/120f,loop:true);Check(f>=0&&f<c.durations.Length,"Invalid state frame");selections++;}
        }
        Check(names.Count==37,"Full state inventory");
        pass.Add($"all 37 state clip timelines sampled {selections} times within bounds");
        return pass;
    }
}
