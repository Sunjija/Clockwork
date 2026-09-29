using System;

namespace TiqueReturn
{
    // Test driver: supplies the same input commands as a player. Never changes game state.
    public sealed class ReturnPilot
    {
        int puzzleStep;
        static int Dir(ReturnModel m, float goal) => Math.Abs(m.x-goal)<1 ? 0 : m.x<goal ? 1 : -1;
        static Command Walk(ReturnModel m, float goal) => new Command { axis=Dir(m,goal) };
        public Command Next(ReturnModel m)
        {
            if(m.phase==Phase.Title) return new Command {interact=true};
            if(m.phase==Phase.Puzzle)
            {
                switch(puzzleStep)
                {
                    case 0:
                        if(Dir(m,150)!=0)return Walk(m,150);
                        if(!m.magnetOn)return new Command {interact=true};
                        puzzleStep++;break;
                    case 1: if(m.attached&&m.crateBottom<=167.1f)puzzleStep++;break;
                    case 2:
                        if(Dir(m,255)!=0)return Walk(m,255);
                        if(!m.railRight)return new Command {interact=true};
                        puzzleStep++;break;
                    case 3: if(m.railBusy<=0&&Math.Abs(m.crateX-468)<1)puzzleStep++;break;
                    case 4:
                        if(Dir(m,150)!=0)return Walk(m,150);
                        if(m.magnetOn)return new Command {interact=true};
                        puzzleStep++;break;
                    case 5: if(m.gateOpen)puzzleStep++;break;
                    case 6:
                        if(Dir(m,507)!=0&&!m.Attacking)return Walk(m,507);
                        if(!m.practiceDone)return new Command {axis=1,attack=!m.Attacking};
                        puzzleStep++;break;
                    default: return Walk(m,614);
                }
            }
            if(m.phase==Phase.Combat)
            {
                if(m.bossMove==BossMove.Aim||m.bossMove==BossMove.Slam)
                {
                    if(m.bossMove==BossMove.Aim&&m.bossAge<.41f)
                        return m.arenaMagnet?Walk(m,235):default;
                    var c=Walk(m,m.aimX-52);
                    c.dash=m.dashReady&&!m.Dashing&&Math.Abs(m.x-m.aimX)<35;
                    return c;
                }
                if(m.bossMove==BossMove.Open)
                {
                    if(Math.Abs(m.x-(m.fistX-27))>3&&!m.Attacking)return Walk(m,m.fistX-27);
                    return new Command {axis=1,attack=!m.Attacking};
                }
                Command travel;
                if(!m.arenaMagnet&&m.trapCooldown<=0)
                {
                    travel=Walk(m,104);
                    travel.interact=Math.Abs(m.x-104)<8&&Math.Abs(m.y-ReturnModel.Floor)<14;
                }
                else travel=Walk(m,235);
                if(m.bossMove==BossMove.Wave)
                    travel.jump=m.grounded&&m.waveX-m.x<50&&m.waveX>m.x-25;
                return travel;
            }
            if(m.phase==Phase.Rescan)
            {
                if(Dir(m,478)!=0)return Walk(m,478);
                return new Command {interact=true};
            }
            if(m.phase==Phase.Exit)return Walk(m,614);
            return default;
        }
    }
}
