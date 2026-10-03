using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    public static class ReworkChecks
    {
        static void Assert(bool ok,string text){if(!ok)throw new Exception("V2 CHECK: "+text);}
        public static List<string> Run(PuzzleBook book,Action<string> log=null)
        {
            var passed=new List<string>();Action<string> pass=s=>{passed.Add(s);log?.Invoke("V2 PASS "+s);};
            foreach(var room in book.levels)
            {
                var p=new CorePuzzle(room);Assert(!p.Solved,"unsolved initial board");
                foreach(char d in room.solution)Assert(p.Move(d-'0'),"solution contains legal steps");
                Assert(p.Solved&&p.pushes==room.pushes,"solver and production rules agree");
                Assert(p.moves==room.moves,"solution move count");
                while(p.Undo()){}
                Assert(p.player==room.start&&p.moves==0&&p.pushes==0,"undo all steps resets counters and player");
                for(int i=0;i<p.boxes.Length;i++)Assert(p.boxes[i]==room.boxes[i],"undo restores all boxes");
            }
            pass("3 independently solved boards replay and fully undo through production rules");
            var custom=new PuzzleRoom{rows=new[]{"#######","#.....#","#.....#","#.....#","#.....#","#.....#","#######"},start=22,boxes=new[]{23,26},types=new[]{1,0},goals=new[]{25,12}};
            var slide=new CorePuzzle(custom);Assert(slide.Move(1)&&slide.boxes[0]==25,"orb stops before another box");
            Assert(slide.player==23,"player moves only one tile while orb slides");
            Assert(!slide.Move(0)||slide.player==22,"ordinary walk");slide.Reset();Assert(slide.boxes[0]==23,"restart");
            pass("sliding orb is stopped by an object; restart restores original layout");
            var wrong=new CorePuzzle(new PuzzleRoom{rows=custom.rows,start=22,boxes=new[]{12,25},types=new[]{0,1},goals=new[]{25,12}});
            Assert(!wrong.Solved,"wrong-colored goals cannot finish board");pass("socket completion requires correct type");
            var m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;
            m.hero.invincible=0;m.hero.dashAge=0;m.Damage("test");Assert(m.health==5,"dash avoids damage");
            m.hero.dashAge=9;m.Damage("test");m.Damage("test");Assert(m.health==4,"damage grace avoids repeat hit");
            m.paused=true;float time=m.clock;m.Tick(.3f,ReworkCommand.Empty);Assert(m.clock==time,"pause freezes game");
            pass("dash invulnerability, damage grace and pause freeze");
            m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.bossMove=IronMove.Rest;
            m.hero.x=m.WeakX-25;m.hero.facing=1;
            for(int i=0;i<50;i++){var c=ReworkCommand.Empty;c.attack=true;m.Tick(1f/120,c);}
            Assert(m.bossHealth==9,"closed armor rejects punch");pass("armor cannot be bypassed with attacks");
            m.phase=Journey.Dead;m.health=0;m.Retry();Assert(m.health==5&&m.bossHealth==9&&m.phase==Journey.Arrival,"checkpoint retry");
            pass("boss checkpoint retries without replaying puzzles");
            foreach(Journey encounter in new[]{Journey.Arrival,Journey.Combat,Journey.Restored,Journey.Ending,Journey.Dead})
            {
                m=new ReworkModel(book);m.roomIndex=book.levels.Length-1;m.puzzle=new CorePuzzle(book.levels[m.roomIndex]);
                foreach(char d in m.puzzle.room.solution)Assert(m.puzzle.Move(d-'0'),"restart fixture solution");
                var checkpoint=m.puzzle;int moves=checkpoint.moves,pushes=checkpoint.pushes;
                m.phase=encounter;m.paused=m.muted=m.assisted=m.reducedEffects=true;
                m.health=1;m.bossHealth=2;m.breaks=2;m.openHits=2;m.pattern=7;
                m.clock=42;m.playTime=35;m.controlTime=26;m.guideTime=3;m.openingTime=6;
                m.totalMoves=70;m.totalPushes=20;m.deaths=4;m.hintLevel=2;
                m.hero.x=430;m.hero.y=180;m.hero.vy=-90;m.hero.jumps=2;m.hero.attackAge=m.hero.dashAge=0;
                m.bossX=200;m.bossY=150;m.bossFacing=1;m.bossSequence="stagger";
                m.charged=1;m.chargeLife=10;m.chargeCooldown=.2f;
                m.waves.Add(new RingWave{x=120,direction=1});m.feedback.Emit("hurt",80,100);
                m.pylonChargedAt[0]=m.pylonChargedAt[1]=40;m.lastDischargedPylon=1;
                m.dischargedAt=m.lastCoreHitAt=m.restoredAt=m.lastBossDamageAt=m.hurtAt=41;
                m.shake=m.flash=m.hitStop=.1f;m.actionConsumed=true;m.hitSerial=m.attackResolved=8;
                m.openingSource=CoreOpeningSource.SlamCounter;m.counterOpportunities=4;m.counterHits=3;m.lastSlamMissAt=41;
                int epoch=m.inputEpoch;
                Assert(m.RestartCombat(),"arena restart accepted from "+encounter);
                Assert(m.phase==Journey.Arrival&&m.age==2.4f&&!m.paused,"restart lands at ready combat guide");
                Assert(m.health==5&&m.bossHealth==9&&m.breaks==0&&m.openHits==0&&m.pattern==0,"full encounter reset");
                Assert(m.hero.x==80&&m.hero.y==ReworkModel.Floor&&m.hero.vy==0&&m.hero.grounded&&m.hero.jumps==0&&!m.hero.Attacking&&!m.hero.Dashing,"hero spawn and action reset");
                Assert(m.bossX==490&&m.bossY==ReworkModel.Floor&&m.bossFacing==-1&&m.bossMove==IronMove.Rest&&m.bossAge==0&&m.bossSequence=="charge","boss spawn reset");
                Assert(m.charged==-1&&m.chargeLife==0&&m.chargeCooldown==0&&m.waves.Count==0&&m.pylonChargedAt[0]==-100&&m.pylonChargedAt[1]==-100&&m.lastDischargedPylon==-1,"hazards and pylons reset");
                Assert(m.shake==0&&m.flash==0&&m.hitStop==0&&!m.actionConsumed&&m.hitSerial==-1&&m.attackResolved==-1&&m.hurtAt==-100&&m.lastBossDamageAt==-100&&m.lastCoreHitAt==-100&&m.restoredAt==-100,"stale encounter feedback reset");
                Assert(m.openingSource==CoreOpeningSource.None&&m.counterOpportunities==0&&m.counterHits==0&&m.lastSlamMissAt==-100&&!m.Vulnerable,"counter source, records and exposure reset");
                Assert(ReferenceEquals(checkpoint,m.puzzle)&&m.puzzle.Solved&&m.puzzle.moves==moves&&m.puzzle.pushes==pushes&&m.roomIndex==book.levels.Length-1,"solved puzzle checkpoint preserved");
                Assert(m.clock==42&&m.playTime==35&&m.controlTime==26&&m.guideTime==3&&m.openingTime==6&&m.totalMoves==70&&m.totalPushes==20&&m.deaths==4&&m.hintLevel==2,"journey totals preserved");
                Assert(m.muted&&m.assisted&&m.reducedEffects&&m.inputEpoch==epoch+1,"preferences kept and pending input invalidated");
                m.Tick(1f/120,ReworkCommand.Empty);Assert(m.phase==Journey.Arrival,"restart cannot auto-enter combat");
                var enter=ReworkCommand.Empty;enter.interact=true;m.Tick(1f/120,enter);Assert(m.phase==Journey.Combat,"guide Enter starts fresh combat");
                Assert(m.RestartCombat(),"repeated restart is safe");
            }
            pass("combat-only restart from all five arena states resets encounter and preserves puzzle checkpoint/preferences");
            m=new ReworkModel(book);Assert(m.RestartCombat()&&m.phase==Journey.Arrival&&!m.puzzle.Solved&&m.totalMoves==0,"title combat practice does not fake puzzle completion");
            foreach(Journey nonArena in new[]{Journey.Opening,Journey.Puzzle,Journey.RoomClear})
            {m=new ReworkModel(book);m.phase=nonArena;int epoch=m.inputEpoch;Assert(!m.RestartCombat()&&m.phase==nonArena&&m.inputEpoch==epoch,"non-arena restart is a no-op");}
            pass("title permits combat-only practice, puzzle/opening phases reject encounter restart");
            m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Restored;
            m.hero.x=90;m.hero.y=236;m.hero.grounded=true;m.hero.jumps=0;
            var walk=ReworkCommand.Empty;walk.axis=1;
            for(int i=0;i<18;i++)m.Tick(1f/120,walk);
            Assert(!m.hero.grounded&&m.hero.clock<=m.hero.graceUntil,"walked off service ledge into coyote window");
            var jump=ReworkCommand.Empty;jump.jump=true;m.Tick(1f/120,jump);
            Assert(m.hero.jumps==1&&!m.hero.doublePose,"coyote consumes first jump");
            m.Tick(1f/120,jump);Assert(m.hero.jumps==2&&m.hero.doublePose,"double jump remains available");
            float vy=m.hero.vy;m.Tick(1f/120,jump);Assert(m.hero.vy>vy,"third jump cannot reset vertical speed");
            pass("V2 service ledge coyote jump preserves exactly one double jump");
            m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.bossMove=IronMove.Charge;
            m.bossX=500;m.bossFacing=1;m.charged=1;m.chargeLife=10;
            m.Tick(1f/120,ReworkCommand.Empty);Assert(!m.Vulnerable,"standing over charged pylon is not a new collision");
            m.bossX=430;m.bossFacing=1;
            for(int i=0;i<20&&!m.Vulnerable;i++)m.Tick(1f/120,ReworkCommand.Empty);
            Assert(m.Vulnerable&&m.charged==-1&&m.breaks==1,"swept charge impact consumes pylon and opens armor");
            pass("armor break requires a new impact, not an overlapping pylon exploit");
            CheckCounters(book,pass);
            return passed;
        }

        const float Step=1f/120;
        static ReworkModel SlamFixture(PuzzleBook book,float x,float y=ReworkModel.Floor)
        {
            var m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;
            m.bossMove=IronMove.Slam;m.bossSequence="slam";m.bossX=m.aimX=320;m.bossY=ReworkModel.Floor-1;
            m.hero.x=x;m.hero.y=y;m.hero.vy=0;m.hero.grounded=y==ReworkModel.Floor;m.hero.invincible=0;
            return m;
        }
        static void Until(ReworkModel m,Func<bool> done,int maximum=1000)
        {for(int i=0;i<maximum&&!done();i++)m.Tick(Step,ReworkCommand.Empty);Assert(done(),"timed model condition reached");}
        static void Punch(ReworkModel m)
        {
            // Ordinary X commands at the production core coordinate; no direct HP mutation.
            m.hero.x=m.WeakX+m.bossFacing*22;m.hero.facing=-m.bossFacing;m.hero.y=ReworkModel.Floor;m.hero.vy=0;m.hero.grounded=true;
            var c=ReworkCommand.Empty;c.attack=true;int hp=m.bossHealth;
            for(int i=0;i<120&&m.bossHealth==hp&&m.phase==Journey.Combat;i++)m.Tick(Step,c);
            Assert(m.bossHealth==hp-1,"production X attack hits exactly once");
        }
        static void CheckCounters(PuzzleBook book,Action<string> pass)
        {
            var m=SlamFixture(book,388.1f);m.waves.Add(new RingWave{x=90,direction=1});m.bossHealth=3;
            m.Tick(Step,ReworkCommand.Empty);
            Assert(m.health==5&&m.bossMove==IronMove.CounterSettle&&m.openingSource==CoreOpeningSource.SlamCounter,"horizontal geometric miss enters landing settle");
            Assert(m.waves.Count==0&&m.counterOpportunities==1&&m.lastSlamMissAt==m.clock,"rage-two miss removes prior waves and does not release new ones");
            int face=m.bossFacing;Assert(face==1&&!m.Vulnerable,"counter points at the escape side but settle is armored");
            for(int i=0;i<20;i++)m.Tick(Step,ReworkCommand.Empty);
            Assert(m.bossMove==IronMove.CounterSettle&&!m.Vulnerable,"settle lasts at least .2 seconds");
            Until(m,()=>m.bossMove==IronMove.Open);
            Assert(m.openingSource==CoreOpeningSource.SlamCounter&&m.bossAge==0&&!m.Vulnerable&&m.OpenHitLimit==1,"counter enters open transition with one-hit limit");
            Assert(Math.Abs(m.OpeningDuration-1.8f)<.001f&&Math.Abs(m.OpeningRemaining-1.8f)<.001f,"counter has .2 transition plus 1.6 exposure");
            for(int i=0;i<20;i++)m.Tick(Step,ReworkCommand.Empty);
            Assert(!m.Vulnerable,"counter cannot be hit during held-pose transition");
            Until(m,()=>m.Vulnerable);
            Assert(m.bossFacing==face&&m.OpeningRemaining>1.58f&&m.OpeningRemaining<=1.6f,"core has full 1.6-second usable exposure and stable side");
            Punch(m);Assert(m.counterHits==1&&m.openHits==1&&m.bossMove==IronMove.Recover&&!m.Vulnerable&&m.openingSource==CoreOpeningSource.None,"first counter hit closes armor immediately");
            int hp=m.bossHealth;var held=ReworkCommand.Empty;held.attack=true;for(int i=0;i<55;i++)m.Tick(Step,held);
            Assert(m.bossHealth==hp,"holding attack cannot take a second counter hit");
            pass("missed slam: .2 landing, aligned .2 opening, 1.6 exposure, one hit, stable side and clean rage-two hazards");

            m=SlamFixture(book,387.9f);m.Tick(Step,ReworkCommand.Empty);
            Assert(m.health==4&&m.bossMove==IronMove.Recover&&m.counterOpportunities==0,"inside 68-pixel radius is a landed slam, not a counter");
            foreach(bool dash in new[]{false,true})
            {
                m=SlamFixture(book,320);if(dash)m.hero.dashAge=0;else m.hero.invincible=1;
                m.Tick(Step,ReworkCommand.Empty);
                Assert(m.health==5&&m.bossMove==IronMove.Recover&&m.counterOpportunities==0&&!m.Vulnerable,"damage immunity inside impact cannot count as an evade");
            }
            m=SlamFixture(book,320,ReworkModel.Floor-76);m.Tick(Step,ReworkCommand.Empty);
            Assert(m.counterOpportunities==1&&m.bossMove==IronMove.CounterSettle,"jump geometrically above slam rectangle earns counter");
            m=SlamFixture(book,320,ReworkModel.Floor-74);m.Tick(Step,ReworkCommand.Empty);
            Assert(m.health==4&&m.counterOpportunities==0,"insufficient jump height is still hit");
            m=SlamFixture(book,320);m.bossHealth=3;m.Tick(Step,ReworkCommand.Empty);
            Assert(m.health==4&&m.waves.Count==2&&m.counterOpportunities==0,"rage-two connected slam keeps original landing waves");
            m=SlamFixture(book,320);m.bossHealth=3;m.health=1;m.Tick(Step,ReworkCommand.Empty);
            Assert(m.phase==Journey.Dead&&m.waves.Count==0&&m.counterOpportunities==0,"fatal slam cannot resurrect hazards or enter counter");
            pass("counter eligibility is slam geometry, never dash/grace; high jump works, connected/fatal rage slam stays safe");

            foreach(bool assist in new[]{false,true})
            {
                m=SlamFixture(book,220);m.assisted=assist;m.Tick(Step,ReworkCommand.Empty);
                Until(m,()=>m.Vulnerable);float exposedAt=m.clock;
                Until(m,()=>m.bossMove!=IronMove.Open);
                Assert(m.bossMove==IronMove.Recover&&!m.Vulnerable&&m.counterHits==0&&m.openingSource==CoreOpeningSource.None,"unused counter times out without damage");
                Assert(m.clock-exposedAt>=1.59f&&m.clock-exposedAt<1.62f,"counter usable timeout is 1.6 seconds in both modes");
                m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.assisted=assist;
                m.bossMove=IronMove.Charge;m.bossX=430;m.bossFacing=1;m.charged=1;m.chargeLife=10;
                Until(m,()=>m.Vulnerable);
                Assert(m.openingSource==CoreOpeningSource.Pylon&&m.OpenHitLimit==3&&m.OpeningDuration==(assist?7:5.2f),"pylon source, three-hit quota and existing duration retained");
                for(int hit=0;hit<3;hit++)
                {Until(m,()=>!m.hero.Attacking&&m.hitStop<=0);Punch(m);Assert(m.bossHealth==8-hit&&m.openHits==hit+1,"each pylon X reduces HP once");if(hit<2)Assert(m.Vulnerable,"pylon remains open until third hit");}
                Assert(m.bossMove==IronMove.Recover&&m.counterHits==0&&m.breaks==1&&!m.Vulnerable,"third pylon hit closes armor, not first");
                m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.assisted=assist;
                m.bossMove=IronMove.Charge;m.bossX=430;m.bossFacing=1;m.charged=1;m.chargeLife=10;
                Until(m,()=>m.Vulnerable);float pylonOpenAt=m.clock;
                Until(m,()=>m.bossMove!=IronMove.Open);
                Assert(m.clock-pylonOpenAt>=(assist?7:5.2f)&&m.clock-pylonOpenAt<(assist?7.02f:5.22f),"pylon timeout stays exactly at existing duration");
            }
            pass("counter timeouts in both modes; pylon route preserves duration and all three production attack hits");

            m=SlamFixture(book,220);m.Tick(Step,ReworkCommand.Empty);Until(m,()=>m.Vulnerable);
            m.hero.x=80;var whiff=ReworkCommand.Empty;whiff.attack=true;
            for(int i=0;i<65;i++)m.Tick(Step,whiff);
            Assert(m.bossHealth==9&&m.openHits==0&&m.counterHits==0&&m.Vulnerable,"out-of-range X punches do not spend the counter quota");
            m.phase=Journey.Dead;m.health=0;m.Retry();
            Assert(m.phase==Journey.Arrival&&m.openingSource==CoreOpeningSource.None&&m.counterOpportunities==0&&m.counterHits==0&&m.lastSlamMissAt==-100,"death retry clears pending counter exposure");
            pass("counter air punches spend no quota; death retry resets pending exposure");

            // A controlled nine-opportunity encounter proves the small route has no
            // hidden pillar-count gate. Each exposure comes from an actual missed
            // production slam, and every HP loss comes from ordinary X Tick input.
            m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;
            for(int hit=0;hit<9;hit++)
            {
                m.bossMove=IronMove.Slam;m.bossSequence="slam";m.bossAge=0;m.bossX=m.aimX=320;m.bossY=ReworkModel.Floor-1;
                m.hero.x=420;m.hero.y=ReworkModel.Floor;m.hero.vy=0;m.hero.grounded=true;m.hero.attackAge=m.hero.dashAge=9;
                m.Tick(Step,ReworkCommand.Empty);Until(m,()=>m.Vulnerable);Punch(m);
                Assert(m.bossHealth==8-hit&&m.counterHits==hit+1,"counter-only encounter damages one HP per valid exposure");
                if(hit<8)Until(m,()=>m.hitStop<=0);
            }
            Assert(m.phase==Journey.Restored&&m.bossMove==IronMove.Down&&m.bossHealth==0&&m.counterHits==9&&m.counterOpportunities==9&&m.breaks==0&&m.charged==-1&&m.waves.Count==0,"nine counter hits alone restore the exit without a charged pillar");
            Assert(m.RestartCombat()&&m.openingSource==CoreOpeningSource.None&&m.counterHits==0&&m.counterOpportunities==0&&m.lastSlamMissAt==-100,"post-victory combat restart clears all counter state");
            pass("nine geometric counter opportunities + production X attacks defeat guardian with zero pillars; restart clears new state");

            foreach(bool assist in new[]{false,true})
            {
                m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;m.assisted=assist;
                for(int i=0;i<120*240&&m.phase==Journey.Combat;i++)m.Tick(Step,CounterOnlyCommand(m));
                Assert(m.phase==Journey.Restored&&m.health>0&&m.bossHealth==0&&m.breaks==0&&m.counterHits==9,"ordinary-input counter-only pilot wins full pattern loop: "+m.phase+" HP="+m.health+" boss="+m.bossHealth+" counters="+m.counterHits);
                Assert(m.events.Exists(e=>e.EndsWith(":boss-Charge"))&&m.events.Exists(e=>e.EndsWith(":wave-release"))&&m.events.Exists(e=>e.EndsWith(":boss-Slam")),"counter-only pilot survives every original boss pattern");
                pass("ordinary inputs alone defeat complete guardian pattern loop: nine counters, zero pylons, assisted="+assist+", HP="+m.health+", time="+m.playTime.ToString("F2",System.Globalization.CultureInfo.InvariantCulture)+"s");
            }
        }
        static ReworkCommand CounterOnlyCommand(ReworkModel m)
        {
            var c=ReworkCommand.Empty;var p=m.hero;float target=80;
            if(m.bossMove==IronMove.CounterSettle||m.bossMove==IronMove.Open&&m.openingSource==CoreOpeningSource.SlamCounter)
            {
                target=m.WeakX+m.bossFacing*22;
                c.axis=Math.Abs(target-p.x)>2?Math.Sign(target-p.x):0;
                if(Math.Abs(target-p.x)<5&&m.Vulnerable){if(p.facing!=-m.bossFacing)c.axis=-m.bossFacing;c.attack=true;}
                return c;
            }
            if(m.bossMove==IronMove.SlamAim&&m.bossAge>.48f||m.bossMove==IronMove.Slam)
            {
                target=m.aimX<320?Math.Min(618,m.aimX+100):Math.Max(22,m.aimX-100);
                c.axis=Math.Abs(target-p.x)>2?Math.Sign(target-p.x):0;
                if(m.bossMove==IronMove.SlamAim&&m.bossAge>.55f&&Math.Abs(p.x-m.aimX)<74)c.dash=p.dashReady;
                return c;
            }
            c.axis=Math.Abs(target-p.x)>2?Math.Sign(target-p.x):0;
            // The original service ledge is a legal refuge from floor waves. Reach it
            // with a double jump, then jump above any approaching charge's body.
            if(p.grounded&&p.y==ReworkModel.Floor)c.jump=true;
            else if(p.jumps==1&&p.y>236&&p.vy>-90)c.jump=true;
            if(m.bossMove==IronMove.ChargeAim&&m.bossAge>.75f&&Math.Abs(m.bossX-p.x)<140&&p.grounded)c.jump=true;
            if(m.bossMove==IronMove.Charge&&Math.Abs(m.bossX-p.x)<125&&p.grounded)c.jump=true;
            return c;
        }
    }
}
