using System;
using System.Collections.Generic;
using M = TiqueReturn.GridMath;

namespace TiqueReturn
{
    public enum Journey { Title, Puzzle, RoomClear, Arrival, Combat, Restored, Ending, Dead }
    public enum IronMove { Rest, ChargeAim, Charge, WaveAim, Wave, SlamAim, Slam, Recover, Open, Down }
    public struct ReworkCommand
    {
        public int axis, grid; // Grid direction is -1 when no discrete move was requested.
        public bool jump,dash,attack,interact,undo,restart,hint;
        public static ReworkCommand Empty => new ReworkCommand{grid=-1};
    }
    public struct RingWave {public float x;public int direction;}
    public sealed class ReworkModel
    {
        public const float Floor=282, Speed=88;
        public readonly PuzzleBook book;
        public readonly ReturnModel hero=new ReturnModel();
        public readonly List<string> events=new List<string>();
        public readonly List<RingWave> waves=new List<RingWave>();
        public readonly float[] pylons={140,500};
        public Journey phase=Journey.Title;
        public IronMove bossMove=IronMove.Rest;
        public CorePuzzle puzzle;
        public int roomIndex,hintLevel,health=5,bossHealth=9,breaks,openHits,pattern,deaths,charged=-1;
        public int bossFacing=-1,hitSerial=-1,totalMoves,totalPushes;
        public float age,clock,playTime,bossAge,bossX=490,bossY=Floor,aimX,chargeLife,shake,flash;
        public float stepLock,hitStop,chargeCooldown;
        public bool paused,muted,assisted;
        public string notice="";
        public float noticeLeft;
        public Action<string> Sound;
        public bool InArena => phase==Journey.Arrival||phase==Journey.Combat||phase==Journey.Restored||phase==Journey.Ending||phase==Journey.Dead;
        public bool Vulnerable => phase==Journey.Combat&&bossMove==IronMove.Open;
        public int Rage => Math.Min(2,(9-bossHealth)/3);
        public float WeakX => bossX+bossFacing*48;
        public bool CanControl => phase==Journey.Combat||phase==Journey.Restored;
        public ReworkModel(PuzzleBook book) {this.book=book;hero.phase=Phase.Combat;ResetHero();LoadRoom(0);}
        void ResetHero()
        {
            hero.ResetPlayer(80);hero.y=Floor;hero.phase=Phase.Combat;
            hero.Sound=name=>Sound?.Invoke(name);hero.platforms.Clear();
        }
        public void Event(string s){events.Add(clock.ToString("F2",System.Globalization.CultureInfo.InvariantCulture)+":"+s);}
        public void Say(string s,float seconds=3){notice=s;noticeLeft=seconds;}
        void LoadRoom(int index){roomIndex=index;puzzle=new CorePuzzle(book.levels[index]);hintLevel=0;stepLock=0;}
        public void Start(){phase=Journey.Puzzle;age=0;Say("기록: 엘리아스 공방. 귀환 회로의 세 단절을 복구해야 해요.",5);Event("start");}
        public void BeginArena()
        {
            phase=Journey.Arrival;age=0;ResetHero();health=5;bossHealth=9;breaks=openHits=pattern=0;
            bossX=490;bossY=Floor;bossFacing=-1;charged=-1;chargeLife=chargeCooldown=0;waves.Clear();Next(IronMove.Rest);
            Say("귀환 전력 복구. 그러나 폐기 집행 장치가 길을 막습니다.",4);Event("arena-arrival");
        }
        public void Retry(){if(phase!=Journey.Dead)return;BeginArena();Event("checkpoint-retry");}
        void Next(IronMove move){bossMove=move;bossAge=0;Event("boss-"+move);}
        public void Tick(float dt,ReworkCommand c)
        {
            if(paused)return;
            if(hitStop>0){hitStop=M.Max(0,hitStop-dt);return;}
            clock+=dt;age+=dt;noticeLeft-=dt;shake=M.Max(0,shake-dt);flash=M.Max(0,flash-dt);
            if(phase!=Journey.Title&&phase!=Journey.Ending&&phase!=Journey.Dead)playTime+=dt;
            if(phase==Journey.Title){if(c.interact)Start();return;}
            if(phase==Journey.Dead){if(c.interact)Retry();return;}
            if(phase==Journey.Ending)return;
            if(phase==Journey.Puzzle)
            {
                stepLock=M.Max(0,stepLock-dt);puzzle.motion=M.Max(0,puzzle.motion-dt);
                if(c.undo){puzzle.Undo();stepLock=0;Event("undo");}
                else if(c.restart){puzzle.Reset();stepLock=0;Event("room-reset");}
                else if(c.hint){hintLevel=Math.Min(3,hintLevel+1);Event("hint");}
                else if(c.grid>=0&&stepLock<=0)
                {
                    int pushes=puzzle.pushes;
                    if(puzzle.Move(c.grid)){stepLock=puzzle.motion;Sound?.Invoke(puzzle.pushes>pushes?"switch":"land");}
                }
                if(puzzle.Solved){phase=Journey.RoomClear;age=0;totalMoves+=puzzle.moves;totalPushes+=puzzle.pushes;Sound?.Invoke("success");Event("room-clear-"+(roomIndex+1));}
                return;
            }
            if(phase==Journey.RoomClear)
            {
                puzzle.motion=M.Max(0,puzzle.motion-dt);
                if(c.interact&&age>.5f)
                {if(roomIndex==book.levels.Length-1)BeginArena();else{LoadRoom(roomIndex+1);phase=Journey.Puzzle;age=0;noticeLeft=0;}}
                return;
            }
            if(phase==Journey.Arrival)
            {
                if(c.interact||age>6){phase=Journey.Combat;age=0;Next(IronMove.Rest);Say("기둥 옆에서 E로 충전 → 기둥 뒤로 돌진 유도 → 열린 붉은 틈을 J로 공격",7);}
                return;
            }
            MoveHero(dt,c);
            if(phase==Journey.Restored)
            {
                if(hero.x>594&&c.interact){phase=Journey.Ending;age=0;Event("ending");Sound?.Invoke("success");}
                return;
            }
            chargeLife-=dt;chargeCooldown-=dt;
            if(chargeLife<=0)charged=-1;
            if(c.interact&&hero.grounded&&chargeCooldown<=0)
            {
                for(int i=0;i<pylons.Length;i++)if(M.Abs(hero.x-pylons[i])<36)
                {charged=i;chargeLife=16;chargeCooldown=.25f;Event("pylon-charge-"+i);Sound?.Invoke("switch");Say("충전 완료. 문지기와 이 기둥 사이에 서지 말고, 기둥 뒤로 유도하세요.",3);break;}
            }
            BossTick(dt);
            if(phase!=Journey.Combat)return;
            for(int i=waves.Count-1;i>=0;i--)
            {
                RingWave w=waves[i];w.x+=w.direction*dt*(assisted?118:150+Rage*15);waves[i]=w;
                if(M.Abs(w.x-hero.x)<15&&hero.y>Floor-22)Damage("wave");
                if(w.x<-25||w.x>665)waves.RemoveAt(i);
            }
            if(hero.Attacking&&hero.attackAge>=.12f&&hero.attackAge<=.22f&&hitSerial!=hero.attackSerial)
            {
                float hand=hero.x+hero.facing*22;
                if(Vulnerable&&M.Abs(hand-WeakX)<31&&hero.y>Floor-25)
                {
                    hitSerial=hero.attackSerial;bossHealth--;openHits++;flash=.12f;shake=.1f;hitStop=.045f;
                    Event("boss-hit");Sound?.Invoke("hit");
                    if(bossHealth<=0){phase=Journey.Restored;age=0;Next(IronMove.Down);waves.Clear();Event("guardian-stopped");Say("폐기 명령을 해제했습니다. 오른쪽 문에서 E로 귀환 기록을 확인하세요.",8);}
                    else if(openHits>=3){Next(IronMove.Recover);Say("장갑 재결합. 다음 충전 기둥으로 이동하세요.",3);}
                }
            }
        }
        void MoveHero(float dt,ReworkCommand c)
        {
            var p=hero;p.clock=clock;p.axis=Math.Sign(c.axis);p.invincible=M.Max(0,p.invincible-dt);p.dashCooldown-=dt;
            if(p.axis!=0&&!p.Dashing&&!p.Attacking)p.facing=p.axis;
            if(c.jump)p.jumpUntil=clock+ReturnModel.JumpBuffer;
            if(p.jumpUntil>=clock&&!p.Dashing&&(p.grounded||p.jumps<2))
            {
                bool first=p.grounded||(p.jumps==0&&clock<=p.graceUntil);
                p.vy=first?-245:-220;p.jumps=first?1:2;p.grounded=false;p.doublePose=!first;
                p.jumpUntil=p.graceUntil=-100;p.airAge=0;p.attackAge=9;Sound?.Invoke("jump");Event(first?"jump":"double-jump");
            }
            if(c.dash&&p.dashReady&&p.dashCooldown<=0&&!p.Dashing)
            {p.dashAge=0;p.dashReady=false;p.dashCooldown=.45f;p.vy=0;p.attackAge=9;Sound?.Invoke("dash");Event("dash");}
            if(c.attack&&!p.Dashing&&!p.Attacking){p.attackAge=0;p.attackSerial++;}
            float oldY=p.y,oldX=p.x;bool grounded=p.grounded;
            float vx=p.Dashing?p.facing*325:p.Attacking&&p.grounded?p.axis*25:p.axis*Speed;
            p.x=M.Clamp(p.x+vx*dt,22,618);
            if(!p.Dashing||p.grounded){p.y+=p.vy*dt+400*dt*dt;p.vy+=800*dt;}
            float landing=Floor;
            // Two service ledges make positioning and coyote jumps meaningful in the arena.
            foreach(var ledge in new[]{new Platform(44,236,48,6),new Platform(548,236,48,6)})
                if(p.x+6>ledge.x&&p.x-6<ledge.xMax&&oldY<=ledge.y+.01f&&p.y>=ledge.y)landing=M.Min(landing,ledge.y);
            p.grounded=false;
            if(p.vy>=0&&oldY<=landing+.01f&&p.y>=landing)
            {p.y=landing;p.vy=0;p.grounded=true;p.jumps=0;p.graceUntil=-100;if(!grounded){p.landAge=0;Sound?.Invoke("land");}}
            if(grounded&&!p.grounded&&p.jumps==0){p.graceUntil=clock+.12f;p.airAge=9;Event("walk-off");}
            if(p.grounded&&!p.Dashing&&!p.Attacking)p.walkAge+=M.Abs(p.x-oldX)/45;
            p.attackAge+=dt;p.dashAge+=dt;p.airAge+=dt;p.landAge+=dt;
            if(p.grounded&&!p.Dashing&&p.dashCooldown<=0)p.dashReady=true;
        }
        public void Damage(string cause)
        {
            if(phase!=Journey.Combat||hero.invincible>0||hero.Dashing)return;
            health--;hero.invincible=assisted?1.5f:1.1f;hero.attackAge=9;shake=.18f;Event("hurt-"+cause);Sound?.Invoke("hurt");
            if(health<=0){phase=Journey.Dead;age=0;deaths++;waves.Clear();Event("death");}
        }
        void BossTick(float dt)
        {
            bossAge+=dt;float warn=assisted?1.4f:1.05f;
            switch(bossMove)
            {
                case IronMove.Rest:
                    if(bossAge>.8f)
                    {
                        bossFacing=hero.x<bossX?-1:1;
                        if(pattern%3==0){Next(IronMove.ChargeAim);Sound?.Invoke("warning");}
                        else if(pattern%3==1){Next(IronMove.WaveAim);Sound?.Invoke("warning");}
                        else{aimX=M.Clamp(hero.x,85,555);Next(IronMove.SlamAim);Sound?.Invoke("warning");}
                    }
                    break;
                case IronMove.ChargeAim:
                    if(bossAge<.35f)bossFacing=hero.x<bossX?-1:1;
                    if(bossAge>warn+.2f){Next(IronMove.Charge);Event("charge-release");}break;
                case IronMove.Charge:
                    float old=bossX;bossX+=bossFacing*dt*(assisted?230:280+Rage*18);
                    if(charged>=0&&(old+bossFacing*49-pylons[charged])*bossFacing<0&&(bossX+bossFacing*49-pylons[charged])*bossFacing>=0)
                    {
                        bossX=pylons[charged]-bossFacing*49;charged=-1;chargeLife=0;chargeCooldown=2;
                        breaks++;openHits=0;waves.Clear();Next(IronMove.Open);shake=.3f;Sound?.Invoke("hit");Event("armor-break");Say("장갑이 열렸어요! 기둥 쪽 붉은 틈을 J로 세 번 공격하세요.",4);break;
                    }
                    if(M.Abs(hero.x-bossX)<61&&hero.y>Floor-58)Damage("charge");
                    if(bossX<82||bossX>558){bossX=M.Clamp(bossX,82,558);Next(IronMove.Recover);shake=.2f;}break;
                case IronMove.WaveAim:
                    if(bossAge>warn){Next(IronMove.Wave);SpawnWaves();}break;
                case IronMove.Wave:
                    if(Rage>=2&&bossAge>1.1f&&bossAge-dt<=1.1f)SpawnWaves();
                    if(bossAge>(Rage>=2?2:1.1f))Next(IronMove.Recover);break;
                case IronMove.SlamAim:
                    if(bossAge<.45f)aimX=M.Clamp(hero.x,85,555);
                    bossY=Floor-M.Min(70,bossAge*120);
                    if(bossAge>warn+.2f)Next(IronMove.Slam);break;
                case IronMove.Slam:
                    bossX=M.MoveTowards(bossX,aimX,dt*900);bossY=M.MoveTowards(bossY,Floor,dt*230);
                    if(bossY>=Floor)
                    {
                        bossX=aimX;if(M.Abs(hero.x-bossX)<68&&hero.y>Floor-75)Damage("slam");
                        shake=.23f;Sound?.Invoke("land");if(Rage>=2)SpawnWaves();Next(IronMove.Recover);
                    }break;
                case IronMove.Open:
                    if(bossAge>(assisted?7:5.2f))Next(IronMove.Recover);break;
                case IronMove.Recover:
                    bossY=Floor;
                    if(bossAge>.85f){pattern++;Next(IronMove.Rest);}break;
            }
        }
        void SpawnWaves(){waves.Add(new RingWave{x=bossX-54,direction=-1});waves.Add(new RingWave{x=bossX+54,direction=1});Sound?.Invoke("land");Event("wave-release");}
        public string Hint()
        {
            if(hintLevel==0)return "H를 누르면 이 방의 힌트를 볼 수 있어요.";
            string[][] hints={
                new[]{"추를 가장 가까운 소켓으로 보내기 전에, 그 뒤에 설 공간이 있는지 보세요.","아래쪽 추를 먼저 오른쪽으로 보낼 길을 확보하세요.","위쪽 추를 왼쪽으로 옮긴 뒤, 아래 추의 왼쪽으로 돌아가 보세요."},
                new[]{"구슬은 소켓에서 멈추지 않아요. 바로 다음 칸에 장애물이 필요해요.","노란 추를 구슬의 임시 벽으로 쓸 수 있어요.","추를 먼저 완성하지 말고, 구슬을 옮길 때 필요한 멈춤점을 찾아보세요."},
                new[]{"두 구슬도 서로를 멈추는 벽이 될 수 있어요.","완성된 소켓 위의 구슬도 다시 움직여야 할 수 있어요.","통로와 멈춤점을 동시에 남기세요. 노란 추의 뒤로 돌아갈 공간도 필요해요."}
            };
            return hints[roomIndex][Math.Min(2,hintLevel-1)];
        }
    }
}
