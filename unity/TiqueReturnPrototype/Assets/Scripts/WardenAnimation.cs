using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    // Same exposure durations as Tique revision 10. Gameplay can hold an aim,
    // airborne apex or exposed pose; it never stretches the image itself.
    public static class WardenAnimation
    {
        public static int FrameAt(int[] durations,float seconds,int first=0,int last=-1,bool loop=false)
        {
            if(last<0)last=durations.Length-1;
            float time=Math.Max(0,seconds)*1000;int sum=0;
            for(int i=first;i<=last;i++)sum+=durations[i];
            if(loop)time%=sum;
            for(int i=first;i<=last;i++){if(time<durations[i])return i;time-=durations[i];}
            return last;
        }
        public static int Select(ReworkModel m,IDictionary<string,int[]> durations,out string clip)
        {
            string name="idle";int first=0,last=0;float age=m.bossAge;bool loop=false;
            float warning=m.assisted?1.4f:1.05f;
            switch(m.bossMove)
            {
                case IronMove.ChargeAim:name="charge";last=2;break;
                case IronMove.Charge:
                    name="charge";first=3;last=6;
                    // One launch, then alternate two foot contacts under the chassis.
                    if(age>=.03f){first=4;age-=.03f;loop=true;}
                    break;
                case IronMove.WaveAim:
                    name="attack";last=2;
                    if(age>=warning-.03f){first=last=3;}
                    break;
                case IronMove.Wave:
                    name="attack";first=4;last=11;
                    // A second phase-three pulse gets its own matching bite.
                    if(m.Rage>=2&&age>=1.1f)age-=1.1f;
                    break;
                case IronMove.SlamAim:name="slam";last=6;break;
                case IronMove.Slam:name="slam";first=7;last=9;break;
                case IronMove.Open:name="stagger";last=6;break;
                case IronMove.Down:name="stagger";first=last=6;break;
                case IronMove.Recover:
                    name=m.bossSequence;
                    if(name=="charge"){first=7;last=11;}
                    else if(name=="slam"){first=10;last=14;}
                    else if(name=="stagger"){first=7;last=11;}
                    else {first=last=11;} // Wave already played its recovery.
                    break;
            }
            clip="iron-"+name;return FrameAt(durations[clip],age,first,last,loop);
        }
    }
}
