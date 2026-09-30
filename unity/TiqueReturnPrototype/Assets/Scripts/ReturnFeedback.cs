using System;
using System.Collections.Generic;
namespace TiqueReturn
{
    public sealed class FeedbackCue
    {
        public int serial,direction; public string kind; public float x,y,age;
        public float lifetime,endX,endY;
    }
    // World-clock events. Positions are captured at contact, never followed during recovery.
    public sealed class ReturnFeedback
    {
        public readonly List<FeedbackCue> cues=new List<FeedbackCue>();int serial;
        public void Emit(string kind,float x,float y,int direction=1,float lifetime=-1)
        {
            if(lifetime<0)lifetime=kind=="dust"?.2f:kind=="boost"?.17f:kind=="wall-brake"?.16f:.22f;
            if(kind=="hit") {int count=0;for(int i=cues.Count-1;i>=0;i--)if(cues[i].kind=="hit"&&++count>=2)cues.RemoveAt(i);}
            cues.Add(new FeedbackCue{serial=++serial,kind=kind,x=x,y=y,direction=direction,lifetime=lifetime});
        }
        public void Advance(float dt){for(int i=cues.Count-1;i>=0;i--){cues[i].age+=dt;if(cues[i].age>=cues[i].lifetime)cues.RemoveAt(i);}}
        public void Clear(){cues.Clear();}
        public void Bridge(float x,float y,float endX,float endY)
        {Emit("bridge",x,y,1,.1f);var cue=cues[cues.Count-1];cue.endX=endX;cue.endY=endY;}
    }
    public static class OpeningSequence
    {
        public const float Landing=2,Duration=14;
        public static float FootX(float tileX)=>194+tileX*36+18;
        public static float FootY(float tileY)=>64+tileY*36+32;
        public static int DirectionX(int direction)=>direction==0?-1:direction==1?1:0;
        public static int DirectionY(int direction)=>direction==2?-1:direction==3?1:0;
        public static float DropOffset(float age,float footY)
        {
            if(age<1)return -footY-64;
            float t=Math.Min(1,Math.Max(0,age-1));return (-footY-64)*(1-t*t);
        }
        public static int LandingFrame(float age)
        {
            if(age<2)return age<1.65f?8:9;
            if(age>=2.16f)return -1;
            return 10+Math.Min(4,(int)((age-2)/.032f));
        }
        public static string Record(float age)
        {
            if(age<3)return "";
            if(age<6)return "귀환처: 엘리아스 공방.";
            if(age<9)return "귀환 회로: 연결 0 / 3.";
            if(age<11)return "…돌아갈 수 있겠네.";
            return "방향키로 이동. 추를 소켓으로 밀어주세요.";
        }
    }
}
