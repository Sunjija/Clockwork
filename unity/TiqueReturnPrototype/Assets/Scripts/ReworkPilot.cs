using System;

namespace TiqueReturn
{
    // QA input driver only. It uses the same public input commands as the player, never changes game state.
    public sealed class ReworkPilot
    {
        int room=-1,step;
        public ReworkCommand Next(ReworkModel m)
        {
            var c=ReworkCommand.Empty;var p=m.hero;
            if(m.phase==Journey.Title){c.interact=true;return c;}
            if(m.phase==Journey.RoomClear){c.interact=m.age>1;return c;}
            if(m.phase==Journey.Arrival){c.interact=m.age>1.5f;return c;}
            if(m.phase==Journey.Puzzle)
            {
                if(room!=m.roomIndex){room=m.roomIndex;step=0;}
                if(m.age>.55f&&m.stepLock<=0&&step<m.puzzle.room.solution.Length)c.grid=m.puzzle.room.solution[step++]-'0';
                return c;
            }
            if(m.phase==Journey.Restored){c.axis=p.x<602?1:0;c.interact=p.x>594;return c;}
            if(m.phase!=Journey.Combat)return c;
            float target;
            if(m.Vulnerable)
            {
                target=m.WeakX+m.bossFacing*32;
                c.axis=Math.Abs(p.x-target)>2?Math.Sign(target-p.x):0;
                if(Math.Abs(p.x-target)<8){if(p.facing!=-m.bossFacing)c.axis=-m.bossFacing;c.attack=true;}
                return c;
            }
            int goal=m.bossX<320?1:0;
            if(m.charged>=0&&Math.Abs(m.bossX-m.pylons[m.charged])>75)goal=m.charged;
            target=m.pylons[goal]+(goal==0?-42:42);
            if(m.charged!=goal&&Math.Abs(p.x-m.pylons[goal])>30)target=m.pylons[goal];
            if(Math.Abs(p.x-m.pylons[goal])<34&&m.charged!=goal)c.interact=true;
            if(m.bossMove==IronMove.SlamAim&&m.bossAge>.48f||m.bossMove==IronMove.Slam)
                target=m.aimX<320?Math.Min(618,m.aimX+100):Math.Max(22,m.aimX-100);
            c.axis=Math.Abs(p.x-target)>2?Math.Sign(target-p.x):0;
            foreach(var w in m.waves)
            {
                float closing=Math.Abs(w.direction*(m.assisted?118:150+m.Rage*15)-c.axis*ReworkModel.Speed);
                if((p.x-w.x)*w.direction>0&&Math.Abs(w.x-p.x)<closing*.26f+12&&p.grounded)c.jump=true;
            }
            if(m.bossMove==IronMove.Charge&&Math.Abs(m.bossX-p.x)<110)
            {
                bool safe=m.charged>=0&&(p.x-m.pylons[m.charged])*m.bossFacing>20;
                if(!safe){c.axis=-m.bossFacing;c.dash=p.dashReady;}
            }
            if(m.bossMove==IronMove.SlamAim&&m.bossAge>.55f&&Math.Abs(p.x-m.aimX)<74)c.dash=true;
            return c;
        }
    }
}
