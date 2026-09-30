using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    // Picks IRON MAW v7 frames (Resources/ReturnV2/WardenV7) from production state.
    // Each clip is assembled by tools/art/dotify_guardian_motion.py so that a state
    // only ever plays forward through one clip; a long exposure at the end of a clip
    // is the pose held while gameplay waits (curled ball, rearing, apex, core bared).
    public static class WardenAnimation
    {
        public const int CanvasWidth=192, CanvasHeight=176, Baseline=164; // drawn at (bossX-96, bossY-164)
        public static int FrameAt(int[] durations,float seconds,int first=0,int last=-1,bool loop=false)
        {
            if(last<0)last=durations.Length-1;
            float time=Math.Max(0,seconds)*1000;int sum=0;
            for(int i=first;i<=last;i++)sum+=durations[i];
            if(loop)time%=sum;
            for(int i=first;i<=last;i++){if(time<durations[i])return i;time-=durations[i];}
            return last;
        }
        public static string ClipFor(ReworkModel m)
        {
            switch(m.bossMove)
            {
                case IronMove.ChargeAim:return "charge-aim";
                case IronMove.Charge:return "charge-roll";
                case IronMove.WaveAim:return "wave-aim";
                case IronMove.Wave:return "wave-strike";
                case IronMove.SlamAim:return "slam-rise";
                case IronMove.Slam:return "slam-fall";
                case IronMove.Open:return "stagger-open";
                case IronMove.Down:return "defeat";
                case IronMove.Recover:
                    // Wall crash recoils; a pylon crash already went through Open.
                    return m.bossSequence=="charge"?"charge-crash":m.bossSequence=="slam"?"slam-land":m.bossSequence=="stagger"?"stagger-close":"idle";
                default:return "idle";
            }
        }
        public static int Select(ReworkModel m,IDictionary<string,int[]> durations,out string clip)
        {
            string name=ClipFor(m);float age=m.bossAge;int first=0,last=-1;bool loop=false;
            float warning=m.assisted?1.4f:1.05f;
            switch(name)
            {
                case "idle":loop=true;age=m.clock;break; // breathing keeps its phase across states
                case "charge-roll":loop=true;break;
                case "wave-aim":
                    // Rear up and hold; the swing down fills the last 30ms before the waves.
                    last=2;if(age>=warning-.03f)first=last=3;
                    break;
                case "wave-strike":
                    // Phase three sends a second pair: the jaw hits the floor again.
                    if(m.Rage>=2&&age>=1.1f)age-=1.1f;
                    break;
                case "defeat":age=m.age;break; // bossAge stops once the phase is Restored
            }
            clip="iron-"+name;return FrameAt(durations[clip],age,first,last,loop);
        }
    }
}
