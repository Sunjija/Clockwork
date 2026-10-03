using System;
using System.Collections.Generic;
using System.Linq;
using TiqueReturn;

public static class AdaptiveGuidanceChecks
{
    const float Step=1f/120;
    static void Assert(bool result,string message)
    {if(!result)throw new Exception("ADAPTIVE GUIDANCE CHECK: "+message);}
    static PuzzleRoom Room(int start=22,int box=34,int goal=11,int type=0)=>new PuzzleRoom
    {rows=new[]{"#######","#.....#","#.....#","#.....#","#.....#","#.....#","#######"},start=start,boxes=new[]{box},goals=new[]{goal},types=new[]{type},solution=""};
    static ReworkModel Puzzle(PuzzleBook book,PuzzleRoom room)
    {var m=new ReworkModel(book);m.puzzle=new CorePuzzle(room);m.phase=Journey.Puzzle;return m;}
    static AdaptiveGuidance Watch(ReworkModel m)
    {var g=new AdaptiveGuidance();g.Observe(m,ReworkCommand.Empty);return g;}
    static void Tick(ReworkModel m,AdaptiveGuidance g,ReworkCommand c,int held=-1,float dt=Step)
    {m.Tick(dt,c);g.Observe(m,c,held);}
    static void Wait(ReworkModel m,AdaptiveGuidance g,float seconds)
    {for(int n=0;n<(int)Math.Ceiling(seconds/Step);n++)Tick(m,g,ReworkCommand.Empty);}
    static void Press(ReworkModel m,AdaptiveGuidance g,int direction)
    {var c=ReworkCommand.Empty;c.grid=direction;Tick(m,g,c,direction);Tick(m,g,ReworkCommand.Empty);}
    static void Walk(ReworkModel m,AdaptiveGuidance g,params int[] directions)
    {foreach(int direction in directions){Press(m,g,direction);Wait(m,g,.3f);}}
    static ReworkModel Combat(PuzzleBook book)
    {var m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;return m;}
    static void Damage(ReworkModel m,AdaptiveGuidance g,string cause)
    {m.clock+=.1f;m.hero.invincible=0;m.hero.dashAge=9;m.Damage(cause);g.Observe(m,ReworkCommand.Empty);}

    public static List<string> Run(PuzzleBook book,Action<string> log=null)
    {
        var passed=new List<string>();void Pass(string s){passed.Add(s);log?.Invoke("GUIDANCE PASS "+s);}
        var blocked=Room(box:23);blocked.rows[3]="#..#..#";
        var m=Puzzle(book,blocked);var g=Watch(m);
        Press(m,g,1);Press(m,g,1);Assert(!g.Visible,"first two distinct blocked pushes stay quiet");
        Press(m,g,1);Assert(g.Visible&&g.Key=="puzzle-blocked"&&g.Level==1,"third real blocked push gives one short contextual tip");
        Assert(g.Remaining<=AdaptiveGuidance.TipDuration&&g.Remaining>4.7f,"tip is a timed toast, not an overlay");
        Pass("three distinct blocked pushes trigger; first failures remain quiet");

        m=Puzzle(book,blocked);g=Watch(m);var hold=ReworkCommand.Empty;hold.grid=1;
        for(int i=0;i<120*60;i++)Tick(m,g,hold,1);
        Assert(g.DisplayCount==0&&g.ActiveStagnation<2,"60 seconds held blocked auto-repeat is one attempt, not active stagnation");
        Tick(m,g,ReworkCommand.Empty);Press(m,g,1);Press(m,g,1);
        Assert(g.DisplayCount==1,"release and re-press separates attempts after a held arrow");
        Pass("held blocked auto-repeat never manufactures repeated-failure or stagnation evidence");

        m=Puzzle(book,Room());g=Watch(m);
        for(int i=0;i<10;i++)Press(m,g,0);
        Assert(g.DisplayCount==0,"ordinary wall collisions are not failed pushes");
        var undo=ReworkCommand.Empty;undo.undo=true;
        for(int i=0;i<10;i++)Tick(m,g,undo);
        Assert(g.DisplayCount==0,"undo on empty history is not a failed attempt");
        var reset=ReworkCommand.Empty;reset.restart=true;
        for(int i=0;i<10;i++)Tick(m,g,reset);
        Assert(g.DisplayCount==0,"reset of unchanged initial board does not count");
        Wait(m,g,120);Assert(g.DisplayCount==0&&g.ActiveStagnation<2,"AFK never produces a tip");
        Pass("ordinary walls, empty undo/reset and AFK stay silent");

        m=Puzzle(book,Room());g=Watch(m);
        for(int i=0;i<3;i++){Press(m,g,1);Tick(m,g,undo);}
        Assert(g.Visible&&g.Key=="puzzle-undo","three real move/undo cycles trigger room strategy");
        Assert(!g.Message.Contains("아래쪽")&&!g.Message.Contains("위쪽"),"tip does not reveal authored solution sequence");
        Pass("successful undo cycles produce non-spoiling room-specific strategy");

        m=Puzzle(book,Room());g=Watch(m);
        Press(m,g,1);Tick(m,g,reset);Assert(!g.Visible,"one meaningful reset stays quiet");
        Press(m,g,1);Tick(m,g,reset);
        Assert(g.Visible&&g.Key=="puzzle-reset","second meaningful reset retains retry support");
        Pass("two meaningful room resets count across attempts without treating empty reset as failure");

        m=Puzzle(book,Room(box:23,goal:24,type:1));g=Watch(m);
        Press(m,g,1);Assert(m.puzzle.boxes[0]==26&&!g.Visible,"first socket passover stays quiet");
        Tick(m,g,reset);Press(m,g,1);
        Assert(g.Visible&&g.Key=="puzzle-orb"&&g.Message.Contains("소켓"),"two real orb overshoots teach stopping rule");
        m=Puzzle(book,Room(box:23,goal:26,type:1));g=Watch(m);Press(m,g,1);
        Assert(m.phase==Journey.RoomClear&&!g.Visible,"orb correctly stopping on socket never creates a failure tip");
        Pass("orb passovers are distinguished from correct socket arrival and teach obstacle stopping");

        m=Puzzle(book,blocked);g=Watch(m);for(int i=0;i<3;i++)Press(m,g,1);
        Assert(g.DisplayCount==1,"cooldown fixture starts with one tip");
        for(int i=0;i<3;i++)Press(m,g,1);
        Wait(m,g,5);Assert(g.DisplayCount==1&&!g.Visible,"repeated evidence cannot replace or immediately repeat a tip");
        Wait(m,g,20);Assert(g.DisplayCount==2&&g.Level==2,"after 24-second cooldown repeated failure escalates strategy");
        float remaining=g.Remaining,stagnation=g.ActiveStagnation,clock=m.clock;
        m.paused=true;for(int i=0;i<300;i++)Tick(m,g,hold,1,.1f);
        Assert(m.clock==clock&&!g.Visible&&g.Remaining==remaining&&g.ActiveStagnation==stagnation,"pause hides toast and freezes all guidance clocks/evidence");
        m.paused=false;Tick(m,g,ReworkCommand.Empty);
        Assert(g.Visible&&g.Remaining<remaining,"resume restores unexpired toast without consuming paused time");
        Pass("4.8-second toast, 24-second cooldown, gradual escalation and pause freeze");

        m=Puzzle(book,blocked);g=Watch(m);for(int i=0;i<3;i++)Press(m,g,1);
        Wait(m,g,5);for(int i=0;i<3;i++)Press(m,g,1);
        Walk(m,g,3,1,2);Assert(m.puzzle.pushes==1,"recovery push succeeds in a different direction");
        Wait(m,g,25);Assert(g.DisplayCount==1&&!g.Visible,"successful recovery cancels stale blocked-push tip queued during cooldown");
        Pass("successful recovery push cancels obsolete queued support before cooldown delivery");

        m=Puzzle(book,Room(box:24));g=Watch(m);Walk(m,g,1,1);
        for(int i=0;i<8;i++)Walk(m,g,2,3);
        Assert(g.DisplayCount==0,"walking repeatedly behind a previously pushed part is not a board revisit failure");
        Walk(m,g,2,1,1,3,0,0,2,0,0,3,1,1);
        Assert(g.Visible&&g.Key=="puzzle-revisit","three real pushes revisiting earlier part layouts trigger strategy");
        Pass("board revisit requires genuine repeated part layouts, never ordinary walking loops");

        m=Puzzle(book,Room());g=Watch(m);
        for(int i=0;i<120*52;i++)
        {
            var c=ReworkCommand.Empty;if(i%36==0)c.grid=(i/36)%2==0?1:0;
            Tick(m,g,c,c.grid);
        }
        Assert(g.DisplayCount==1&&g.Key=="puzzle-stagnation","48 seconds of actual active walking without goal progress triggers strategy");
        m.phase=Journey.RoomClear;Tick(m,g,ReworkCommand.Empty);
        Assert(!g.Visible&&g.ActiveStagnation==0,"room success clears stale guidance");
        m.roomIndex=1;m.puzzle=new CorePuzzle(Room(box:23,goal:24,type:1));m.phase=Journey.Puzzle;
        Tick(m,g,ReworkCommand.Empty);Assert(!g.Visible&&g.ActiveStagnation<.1f,"new room resets room evidence and old pending tips");
        Pass("active-only stagnation works; room completion/new room clear context");

        m=Combat(book);g=Watch(m);Damage(m,g,"wave");Damage(m,g,"charge");
        Assert(!g.Visible,"different one-off hazards do not combine into a false repeated hazard");
        Damage(m,g,"wave");Assert(!g.Visible,"fresh damage defers the tip while the user recovers");
        Wait(m,g,.71f);Assert(g.Visible&&g.Key=="combat-wave"&&g.Message.Contains("점프"),"same actual hazard repeated gives its own dodge strategy at a safe beat");
        int processed=g.ProcessedEvents;for(int i=0;i<500;i++)g.Observe(m,ReworkCommand.Empty);
        Assert(g.ProcessedEvents==processed&&g.DisplayCount==1,"events are consumed once via cursor, not replayed each frame");
        Pass("same-hazard actual damage triggers; mixed first hits and repeated event observation do not");

        m=Combat(book);g=Watch(m);
        for(int i=0;i<3;i++){m.clock+=.1f;m.Event("armor-contact");g.Observe(m,ReworkCommand.Empty);}
        Assert(g.Visible&&g.Key=="combat-armor","third armor rejection explains opening mechanics");
        m.Event("boss-hit");g.Observe(m,ReworkCommand.Empty);Assert(!g.Visible,"successful core hit dismisses obsolete failure support");
        Pass("three armor rejections explain opening, successful core hit clears support");

        m=Combat(book);m.bossMove=IronMove.WaveAim;g=Watch(m);
        for(int i=0;i<3;i++){m.Event("armor-contact");g.Observe(m,ReworkCommand.Empty);}
        Assert(!g.Visible,"queued support never covers a boss telegraph");
        for(int i=0;i<120*8&&!g.Visible;i++)Tick(m,g,ReworkCommand.Empty);
        Assert(g.Visible&&g.Key=="combat-armor"&&m.bossMove==IronMove.Recover&&m.bossAge>=.2f,"queued evidence delivers at next safe recovery, never indefinitely re-delayed");
        int count=g.DisplayCount;Wait(m,g,5);
        Assert(g.DisplayCount==count,"pending consumed once; ongoing patterns cannot requeue the displayed evidence");
        m=Combat(book);g=Watch(m);m.hero.grounded=false;m.hero.attackAge=0;m.hero.dashAge=0;
        for(int i=0;i<3;i++){m.Event("armor-contact");g.Observe(m,ReworkCommand.Empty);}
        Assert(!g.Visible,"airborne, attack and dash presentation remains quiet");
        m.hero.grounded=true;m.hero.attackAge=m.hero.dashAge=9;g.Observe(m,ReworkCommand.Empty);
        Assert(g.Visible,"grounded Rest immediately releases pending support without restarting a timer");
        Pass("combat guidance waits for safe grounded Rest/Recover and then delivers once, never indefinitely postponed");

        m=Combat(book);g=Watch(m);
        MissWindow(m,g);Assert(!g.Visible,"first missed counter window stays quiet");
        MissWindow(m,g);Wait(m,g,.21f);Assert(g.Visible&&g.Key=="combat-core"&&g.Message.Contains("한 번"),"second real missed counter explains one-hit timing at recovery");
        m=Combat(book);g=Watch(m);MissWindow(m,g);
        m.bossMove=IronMove.Open;m.openingSource=CoreOpeningSource.Pylon;m.openHits=0;
        Tick(m,g,ReworkCommand.Empty);m.openHits=1;m.Event("boss-hit");g.Observe(m,ReworkCommand.Empty);
        m.bossMove=IronMove.Recover;Tick(m,g,ReworkCommand.Empty);
        Assert(!g.Visible,"successful open window does not count as a miss and clears prior misses");
        Pass("missed core windows require two actual empty windows; hit windows never count");

        m=Combat(book);g=Watch(m);Damage(m,g,"wave");m.health=1;Damage(m,g,"wave");
        Assert(m.phase==Journey.Dead&&!g.Visible,"fatal second hit never overlays death screen");
        m.Retry();g.Observe(m,ReworkCommand.Empty);Assert(!g.Visible,"checkpoint arrival hides old tip");
        var enter=ReworkCommand.Empty;enter.interact=true;Tick(m,g,enter);
        Assert(m.phase==Journey.Combat&&!g.Visible,"retry does not spam guidance on the first frame");
        Wait(m,g,3.05f);Assert(!g.Visible,"post-retry grace does not release support in the middle of a charge");
        Wait(m,g,1.7f);Assert(g.Visible&&g.Key=="combat-wave","meaningful hazard knowledge survives retry and reaches next safe recovery");
        m.phase=Journey.Restored;g.Observe(m,ReworkCommand.Empty);Assert(!g.Visible,"victory clears tip");
        m.phase=Journey.Ending;g.Observe(m,ReworkCommand.Empty);Assert(!g.Visible,"ending stays silent");
        var replacement=new ReworkModel(book);g.Observe(replacement,ReworkCommand.Empty);
        Assert(g.DisplayCount==0&&!g.Visible&&g.ProcessedEvents==0,"new game resets all support knowledge");
        Pass("death/arrival/retry/victory/ending/new-game transitions preserve only useful retry knowledge");

        var messages=AdaptiveGuidance.MessagesForAudit();int maximum=messages.Max(AdaptiveGuidance.MeasureAt16);
        Assert(messages.All(s=>s.Length<=35)&&maximum<=592,"every strategy fits one 16px accessibility line without truncation");
        Pass("all "+messages.Distinct().Count()+" short strategy strings ≤35 chars, maxMeasuredWidth16="+maximum+"px / 592px");

        var observed=new ReworkModel(book);var control=new ReworkModel(book);g=Watch(observed);
        var pilot=new ReworkPilot();
        for(int i=0;i<120*210&&control.phase!=Journey.Ending&&control.phase!=Journey.Dead;i++)
        {
            var c=pilot.Next(control);control.Tick(Step,c);Tick(observed,g,c,c.grid);
            Assert(observed.phase==control.phase&&observed.clock==control.clock&&observed.hero.x==control.hero.x&&observed.hero.y==control.hero.y&&observed.health==control.health&&observed.bossHealth==control.bossHealth&&observed.bossMove==control.bossMove,"observer never modifies production state/timing");
        }
        Assert(control.phase==Journey.Ending&&observed.phase==Journey.Ending,"unchanged ordinary-input production route completes");
        Assert(observed.events.SequenceEqual(control.events)&&observed.puzzle.boxes.SequenceEqual(control.puzzle.boxes),"support never writes gameplay events or puzzle state");
        Pass("full input-only paired production playthrough proves guidance is read-only and gameplay/timings unchanged");
        return passed;
    }
    static void MissWindow(ReworkModel m,AdaptiveGuidance g)
    {
        m.bossMove=IronMove.Slam;m.bossSequence="slam";m.bossAge=0;m.openHits=0;
        m.bossX=m.aimX=320;m.bossY=ReworkModel.Floor-1;m.hero.x=420;m.hero.y=ReworkModel.Floor;
        m.hero.dashAge=m.hero.attackAge=9;m.hero.vy=0;m.hero.grounded=true;
        Tick(m,g,ReworkCommand.Empty);
        bool opened=false;
        for(int i=0;i<500;i++)
        {
            Tick(m,g,ReworkCommand.Empty);if(m.bossMove==IronMove.Open)opened=true;
            if(opened&&m.bossMove!=IronMove.Open)return;
        }
        throw new Exception("Counter window fixture did not close");
    }
}
