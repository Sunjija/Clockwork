using System;
using System.Collections.Generic;

namespace TiqueReturn
{
public static class ReturnChecks
{
    static void Assert(bool result,string text){if(!result)throw new Exception("RETURN_CHECK FAILED: "+text);}
    static void Advance(ReturnModel m,float seconds,int axis=0)
    {int count=(int)Math.Round(seconds*120);for(int i=0;i<count;i++)m.Tick(1f/120,new Command{axis=axis});}
    static ReturnModel Puzzle(){var m=new ReturnModel();m.Start();return m;}
    static void Use(ReturnModel m,float x){m.x=x;m.y=ReturnModel.Floor;m.grounded=true;m.Interact();}
    public static List<string> Run(Action<string> log = null)
    {
        var results=new List<string>();
        Action<string,Action> check=(name,test)=>{test();results.Add(name);log?.Invoke("RETURN_CHECK PASS "+name);};
        check("puzzle sequence and mechanical gate latch",()=>{
            var m=Puzzle();Use(m,150);Advance(m,1);Assert(m.attached,"magnet catch");Use(m,255);Advance(m,1.3f);
            Assert(m.attached&&Math.Abs(m.crateX-468)<1,"carried to plate");Use(m,150);Advance(m,1);
            Assert(m.gateOpen&&m.PlateDown,"both conditions");Use(m,150);Advance(m,1);Assert(m.gateOpen,"gate remains latched");
        });
        check("wrong-order puzzle is recoverable, no mid-rail drops",()=>{
            var m=Puzzle();Use(m,255);Use(m,150);Assert(!m.magnetOn,"input blocked during rail travel");Advance(m,1.3f);
            Assert(!m.gateOpen&&!m.attached,"empty crane");Use(m,150);Use(m,255);Advance(m,1.3f);Advance(m,1);
            Assert(m.attached,"retrieved from storage");Use(m,255);Advance(m,1.3f);Use(m,150);Advance(m,1);Assert(m.gateOpen,"recovered");
        });
        check("coyote first jump retains double jump",()=>{
            var m=Puzzle();m.x=125;m.y=201;m.grounded=true;m.platforms.Clear();m.platforms.Add(new Platform(0,201,120,8));
            Advance(m,.06f,1);Assert(!m.grounded,"left edge");Assert(m.Jump()&&m.jumps==1,"grace first jump");
            Advance(m,.1f);Assert(m.Jump()&&m.jumps==2,"double remains");Assert(!m.Jump(),"third blocked");
        });
        check("expired coyote uses only airborne jump",()=>{
            var m=Puzzle();m.x=125;m.y=201;m.grounded=true;m.platforms.Clear();m.platforms.Add(new Platform(0,201,120,8));
            Advance(m,.2f,1);Assert(m.clock>m.graceUntil,"expired");m.Jump();Assert(m.jumps==2&&!m.Jump(),"no free extra jump");
        });
        check("100ms landing buffer consumes once",()=>{
            var m=Puzzle();m.y=246;m.vy=120;m.grounded=false;m.jumps=2;Assert(!m.Jump(),"buffer waits");Advance(m,.1f);
            Assert(!m.grounded&&m.jumps==1&&m.vy<0,"buffered jump");
        });
        check("dash leaves ledge and cannot repeat in air",()=>{
            var m=Puzzle();m.x=125;m.y=201;m.grounded=true;m.platforms.Clear();m.platforms.Add(new Platform(0,201,120,8));
            m.Dash();Advance(m,.25f);Assert(!m.grounded&&m.y>201&&!m.Dash(),"air dash constraint");
        });
        check("attack hit occurs once and only during authored impact",()=>{
            var m=Puzzle();m.BeginArena();m.phase=Phase.Combat;m.bossMove=BossMove.Open;m.bossAge=0;m.fistX=240;m.fistBottom=252;m.x=213;
            m.Attack();Advance(m,.1f);Assert(m.overload==6,"windup no damage");Advance(m,.15f);Assert(m.overload==5,"single damage");Advance(m,.1f);Assert(m.overload==5,"no multihit");
        });
        check("invulnerability and boss checkpoint preserve puzzle",()=>{
            var m=Puzzle();m.gateOpen=true;m.BeginArena();m.phase=Phase.Combat;m.invincible=0;m.Damage("test");m.Damage("test");Assert(m.hp==3,"invulnerability");
            for(int i=0;i<3;i++){m.invincible=0;m.Damage("test");}Assert(m.phase==Phase.Dead,"death");m.Retry();
            Assert(m.phase==Phase.Combat&&m.hp==4&&m.overload==6&&m.gateOpen,"checkpoint");
        });
        check("magnet captures only a marked landing in its zone",()=>{
            var m=Puzzle();m.BeginArena();m.phase=Phase.Combat;m.bossMove=BossMove.Slam;m.aimX=235;m.fistBottom=251;m.x=180;m.arenaMagnet=true;
            Advance(m,.02f);Assert(m.captured&&!m.arenaMagnet&&m.trapCooldown>0,"captured and cooling");
        });
        check("jump clears wave, standing takes damage",()=>{
            var m=Puzzle();m.BeginArena();m.phase=Phase.Combat;m.bossMove=BossMove.Wave;m.x=220;m.waveX=236;m.invincible=0;m.y=220;m.grounded=false;
            Advance(m,.1f);Assert(m.hp==4,"above wave");m.y=252;m.grounded=true;m.waveX=232;Advance(m,.03f);Assert(m.hp==3,"floor wave damages");
        });
        check("rescan and exit are required for ending",()=>{
            var m=Puzzle();m.BeginArena();m.phase=Phase.Rescan;m.x=478;m.Interact();Assert(m.phase==Phase.Exit,"identity");Advance(m,4.2f);m.x=614;Advance(m,.02f);Assert(m.phase==Phase.Ending,"ending");
        });
        check("pause freezes physics and timers",()=>{
            var m=Puzzle();m.Jump();m.paused=true;float t=m.clock,y=m.y;Advance(m,1,1);Assert(m.clock==t&&m.y==y,"paused");
        });
        return results;
    }
}
}
