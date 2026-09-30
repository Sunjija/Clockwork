using TiqueReturn;
using System.Text.Json;
static class WorkOrderChecks
{
    public static object Run(PuzzleBook book)
    {
        var checks=new List<string>();void Check(bool ok,string name){if(!ok)throw new Exception("WORK ORDER: "+name);checks.Add(name);}
        void Step(ReworkModel m,float seconds){for(int i=0;i<(int)(seconds*120+.5f);i++)m.Tick(1f/120,ReworkCommand.Empty);}
        foreach(float skip in new[]{.01f,1.2f,2.1f,4f,7f,10f,12f,14.1f})
        {
            var m=new ReworkModel(book);m.Start();Step(m,skip);var c=ReworkCommand.Empty;c.interact=true;m.Tick(1f/120,c);
            Check(m.phase==Journey.Puzzle&&m.puzzle.player==book.levels[0].start&&m.puzzle.moves==0&&m.puzzle.pushes==0&&m.health==5,"opening skip "+skip+" preserves board/HP/counters");
            Check(m.feedback.cues.Count==0&&m.stepLock==0,"opening skip "+skip+" clears reservations");
        }
        var a=new ReworkModel(book);a.Start();Step(a,14.1f);
        Check(a.events.Count(e=>e.EndsWith(":opening-land"))==1,"natural opening lands once");
        Check(a.openingTime>=14&&a.phase==Journey.Puzzle,"14s opening hands off at same tile");
        Check(OpeningSequence.DropOffset(2,OpeningSequence.FootY(a.puzzle.player/7))==0,"opening uses puzzle feet, no combat-floor teleport");
        a=new ReworkModel(book);a.Start();Step(a,1.5f);a.paused=true;float t=a.age;Step(a,2);Check(a.age==t&&a.openingTime==t,"opening pause freezes reserved landing");
        a=new ReworkModel(book);a.BeginArena();Step(a,8);Check(a.phase==Journey.Arrival&&a.waves.Count==0,"guide never auto-starts combat");
        a.age=1;var enter=ReworkCommand.Empty;enter.interact=true;a.Tick(.01f,enter);Check(a.phase==Journey.Arrival,"early guide Enter is ignored");a.age=2.4f;a.Tick(.01f,enter);Check(a.phase==Journey.Combat,"new Enter after boot enables combat");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;var all=ReworkCommand.Empty;all.dash=all.jump=all.attack=all.interact=true;a.Tick(1f/120,all);
        Check(a.hero.Dashing&&!a.hero.Attacking&&a.hero.jumps==0,"same tick dash beats jump/attack/interact");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;all.dash=false;a.Tick(1f/120,all);Check(a.hero.jumps==1&&!a.hero.Attacking,"same tick jump beats attack");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.hero.x=300;var attack=ReworkCommand.Empty;attack.attack=true;a.Tick(1f/120,attack);Step(a,.23f);
        Check(a.feedback.cues.Count(c=>c.kind=="air")==1&&a.bossHealth==9,"air punch emits once without damage");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.bossX=490;a.hero.x=420;a.hero.facing=1;a.Tick(1f/120,attack);Step(a,.14f);
        Check(a.feedback.cues.Count(c=>c.kind=="armor")==1&&a.bossHealth==9,"actual armored-body intersection emits chips");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.bossMove=IronMove.Open;a.bossAge=1;a.hero.x=a.WeakX-25;a.hero.facing=1;a.Tick(1f/120,attack);Step(a,.12f);
        Check(a.bossHealth==8&&a.openHits==1&&a.hitStop>0,"successful contact emits one damage + hitstop");
        var cue=a.feedback.cues.Single(c=>c.kind=="hit");float cueTime=cue.age,clock=a.clock,x=cue.x;a.Tick(.02f,ReworkCommand.Empty);
        Check(a.clock==clock&&cue.age==cueTime&&cue.x==x,"hitstop freezes contact effect and captured position");
        a.paused=true;Step(a,1);Check(a.feedback.cues.Single(c=>c.kind=="hit").age==cueTime,"pause freezes FX");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.Tick(1f/120,attack);var jump=ReworkCommand.Empty;jump.jump=true;a.Tick(1f/120,jump);Step(a,.25f);Check(a.feedback.cues.All(c=>c.kind!="hit"&&c.kind!="armor"&&c.kind!="air"),"jump cancellation removes lingering damage and miss cues");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.bossMove=IronMove.Open;a.bossHealth=1;a.hero.x=a.WeakX-25;a.hero.facing=1;a.waves.Add(new RingWave{x=300,direction=1});a.Tick(1f/120,attack);Step(a,.13f);
        Check(a.phase==Journey.Restored&&a.waves.Count==0&&!a.hero.Attacking&&!a.hero.Dashing,"last hit clears threats and active actions");
        a=new ReworkModel(book);a.BeginArena();a.phase=Journey.Combat;a.hero.invincible=0;a.Damage("check");a.Damage("check");Check(a.health==4&&a.feedback.cues.Count(c=>c.kind=="hurt")==1,"hurt protection prevents duplicate HP and cues");
        a.phase=Journey.Dead;a.Retry();Check(a.phase==Journey.Arrival&&a.age>=2.4f&&a.feedback.cues.Count==0,"retry skips boot and clears old cues");
        a=new ReworkModel(book);a.phase=Journey.Puzzle;a.feedback.Emit("hit",10,10);var reset=ReworkCommand.Empty;reset.restart=true;a.Tick(.01f,reset);Check(a.feedback.cues.All(c=>c.kind!="hit"),"puzzle reset clears stale combat FX");
        var fx=new ReturnFeedback();fx.Emit("dust",1,2);fx.Emit("boost",3,4);Check(fx.cues[0].lifetime==.2f&&fx.cues[1].lifetime==.17f,"shared dust and boost end at authored exposure duration");
        fx.Bridge(20,30,40,50);var bridge=fx.cues.Last();Check(bridge.x==20&&bridge.y==30&&bridge.endX==40&&bridge.endY==50,"bridge captures both contact endpoints");
        return new{passed=true,count=checks.Count,scope="Production C# model, not physical keyboard or human animation judgement",checks};
    }
}
