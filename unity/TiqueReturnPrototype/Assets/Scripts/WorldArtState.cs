using System;

namespace TiqueReturn
{
    // Derives art from production state. Undo/reset use the restored board;
    // no independent visual latch can claim a disconnected socket is powered.
    public static class WorldArtState
    {
        // Connected wall tiles: N=1, E=2, S=4, W=8; outside the board
        // is not a neighboring tile, even though it blocks puzzle movement.
        public static int WallMask(CorePuzzle p,int pos)
        {
            int mask=0,x=pos%7,y=pos/7;
            if(y>0&&p.Wall(pos-7))mask|=1;
            if(x<6&&p.Wall(pos+1))mask|=2;
            if(y<6&&p.Wall(pos+7))mask|=4;
            if(x>0&&p.Wall(pos-1))mask|=8;
            return mask;
        }
        public static string Socket(CorePuzzle p,int goal,out float age)
        {
            age=0;string prefix=p.room.types[goal]==0?"amber-slot-":"cyan-slot-";
            int b=Array.IndexOf(p.boxes,p.room.goals[goal]);
            if(b<0||p.motion>0&&p.boxes[b]!=p.previousBoxes[b])return prefix+"empty";
            if(p.room.types[b]!=p.room.types[goal])return prefix+"wrong";
            age=Math.Max(0,p.visualAge-p.motionDuration);
            if(p.boxes[b]!=p.previousBoxes[b]&&age<.46f)return prefix+"connect";
            return prefix+"filled";
        }
        public static string Box(CorePuzzle p,int b,out float age)
        {
            age=p.visualAge;string prefix=p.room.types[b]==0?"battery-":"orb-";
            if(p.motion>0&&p.boxes[b]!=p.previousBoxes[b])return prefix+"moving";
            for(int g=0;g<p.room.goals.Length;g++)
                if(p.boxes[b]==p.room.goals[g]&&p.room.types[b]==p.room.types[g])return prefix+"docked";
            return prefix+"idle";
        }
        public static string Pylon(ReworkModel m,int index,out float age)
        {
            age=0;
            if(m.charged==index&&m.chargeLife>0)
            {
                age=m.clock-m.pylonChargedAt[index];
                if(age<.46f)return "pylon-charging";
                if(m.chargeLife<3){age=3-m.chargeLife;return "pylon-expiring";}
                return "pylon-armed";
            }
            if(index==m.lastDischargedPylon)
            {
                age=m.clock-m.dischargedAt;
                if(age<.46f)return "pylon-discharge";
                if(age<2)return "pylon-cooldown";
            }
            return "pylon-idle";
        }
        public static string Core(ReworkModel m,out float age)
        {
            age=m.clock-m.lastCoreHitAt;
            if(m.bossMove==IronMove.Down)return "core-off";
            return age<.46f?"core-hit":"core-exposed";
        }
        public static string Exit(ReworkModel m,out float age)
        {
            age=m.clock-m.restoredAt;
            if(m.phase!=Journey.Restored&&m.phase!=Journey.Ending)return "exit-locked";
            return age<.8f?"exit-opening":"exit-open";
        }
        public static int WorkshopPower(ReworkModel m)=>Math.Min(3,m.roomIndex+(m.puzzle.Solved&&m.puzzle.motion<=0?1:0));
    }
}
