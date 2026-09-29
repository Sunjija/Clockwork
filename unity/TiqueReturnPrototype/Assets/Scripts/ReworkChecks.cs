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
            return passed;
        }
    }
}
