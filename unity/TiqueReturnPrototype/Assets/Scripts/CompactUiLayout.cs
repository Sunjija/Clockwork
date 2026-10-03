using System;
using System.Collections.Generic;
using System.Text;

namespace TiqueReturn
{
    [Serializable] public sealed class UiPreferences
    {
        public bool autoHelp=true,largeText=false;
    }

    // The runtime and offline reviewer consume this same declarative draw list.
    // Image keys reuse unchanged approved sprites; panels/buttons resolve to the
    // image-first UiV2 skins, never to an independently painted approximation.
    [Serializable] public sealed class UiElement
    {
        public string kind="",id="",asset="",text="",color="ink",action="";
        public int x,y,width,height,size=16,index=-1;
        public bool enabled=true;
    }

    [Serializable] public sealed class UiPlan
    {
        public List<UiElement> elements=new List<UiElement>();
        public string phase="";
    }

    public static class CompactUiLayout
    {
        public const int CanvasWidth=640,CanvasHeight=360;
        public static int Advance(char c,int size)=>c<128?size/2:size;
        public static int LineHeight(int size)=>size+2;
        // NeoDunggeunmo's approved glyph masks are drawn on a 16px grid.
        // Shrinking that grid removed Korean strokes. All reading text stays
        // native; the legacy preference now enlarges titles by an integer 2x.
        public static int BodySize(UiPreferences p)=>16;
        public static int SecondarySize(UiPreferences p)=>16;
        public static int TitleSize(UiPreferences p)=>p!=null&&p.largeText?32:16;

        public static string Wrap(string value,int width,int size)
        {
            if(string.IsNullOrEmpty(value))return "";
            if(width<size||size<2)throw new ArgumentOutOfRangeException(nameof(width));
            value=value.Replace("\r","");var result=new StringBuilder();int line=0;
            for(int k=0;k<value.Length;k++)
            {
                char c=value[k];
                if(c=='\n'){result.Append('\n');line=0;continue;}
                if(line>0&&(k==0||value[k-1]==' '||value[k-1]=='\n')&&c!=' ')
                {
                    int word=0;
                    for(int j=k;j<value.Length&&value[j]!=' '&&value[j]!='\n';j++)word+=Advance(value[j],size);
                    if(line+word>width&&word<=width){result.Append('\n');line=0;}
                }
                int next=Advance(c,size);
                if(line+next>width){result.Append('\n');line=0;}
                if(line==0&&c==' ')continue;
                result.Append(c);line+=next;
            }
            return result.ToString();
        }

        public static int MeasureWidth(string text,int size)
        {
            int width=0,line=0;
            foreach(char c in text??"")
            {if(c=='\n'){width=Math.Max(width,line);line=0;}else line+=Advance(c,size);}
            return Math.Max(width,line);
        }
        public static int TextHeight(string text,int size)
        {
            if(string.IsNullOrEmpty(text))return 0;
            int lines=1;foreach(char c in text)if(c=='\n')lines++;
            return lines*LineHeight(size);
        }

        public static int MenuCount(ReworkModel m)
        {
            if(m==null)return 0;
            if(m.paused)return m.InArena?8:7;
            if(m.phase==Journey.Title||m.phase==Journey.Dead)return 2;
            if(m.phase==Journey.Ending)return 3;
            if(m.phase==Journey.Puzzle)return 2;
            if(m.phase==Journey.RoomClear)return m.age>.8f?1:0;
            if(m.phase==Journey.Arrival)return m.age>=2.4f?1:0;
            return 0;
        }

        public static UiPlan Build(ReworkModel m,UiPreferences prefs,string helpMessage="",bool helpVisible=false)
        {
            var plan=new UiPlan();if(m==null)return plan;
            prefs=prefs??new UiPreferences();var b=new Builder(plan,prefs);
            plan.phase=m.paused?"Paused":m.phase.ToString();
            bool showHelp=prefs.autoHelp&&helpVisible&&!string.IsNullOrWhiteSpace(helpMessage);
            if(m.paused){b.Pause(m);return plan;}
            if(m.phase==Journey.Title){b.Title();return plan;}
            if(m.phase==Journey.Ending){b.Ending(m);return plan;}
            if(m.phase==Journey.Opening){b.Opening(m);return plan;}
            if(!m.InArena)
            {
                b.Puzzle(m);
                if(m.phase==Journey.Puzzle&&showHelp)b.PuzzleHelp(helpMessage);
                if(m.phase==Journey.RoomClear&&m.age>.8f)b.RoomClear(m);
            }
            else
            {
                b.Combat(m,showHelp&&m.phase==Journey.Combat);
                if(m.phase==Journey.Arrival)b.Arrival(m);
                if(m.phase==Journey.Dead)b.Dead(m,showHelp?helpMessage:"");
                else if(m.phase==Journey.Combat&&showHelp)b.CombatHelp(helpMessage);
            }
            return plan;
        }

        sealed class Builder
        {
            readonly UiPlan plan;readonly UiPreferences prefs;
            int Body=>BodySize(prefs);int Small=>SecondarySize(prefs);int TitleFont=>TitleSize(prefs);
            int ButtonHeight=>28;
            public Builder(UiPlan plan,UiPreferences prefs){this.plan=plan;this.prefs=prefs;}
            void Panel(string id,int x,int y,int width,int height)
            {plan.elements.Add(new UiElement{kind="panel",id=id,x=x,y=y,width=width,height=height,asset="panel"});}
            void Image(string id,int x,int y,int width,int height,string asset,string color="")
            {plan.elements.Add(new UiElement{kind="image",id=id,x=x,y=y,width=width,height=height,asset=asset,color=color});}
            void Fill(string id,int x,int y,int width,int height,string color)
            {if(width>0)plan.elements.Add(new UiElement{kind="fill",id=id,x=x,y=y,width=width,height=height,color=color});}
            void Text(string id,int x,int y,int width,string text,string color="ink",int size=0)
            {
                if(size==0)size=Body;text=Wrap(text,width,size);
                if(text.Length>0)plan.elements.Add(new UiElement{kind="text",id=id,x=x,y=y,width=width,height=TextHeight(text,size),text=text,color=color,size=size});
            }
            void Button(string id,int x,int y,int width,string text,int index,string action,bool enabled=true)
            {
                // Native skin corners require 8px horizontal and 5px vertical
                // padding. Labels stay on one line at either text preference.
                string wrapped=Wrap(text,width-24,Body);
                if(wrapped.IndexOf('\n')>=0)throw new InvalidOperationException("Button label wraps: "+id);
                plan.elements.Add(new UiElement{kind="button",id=id,x=x,y=y,width=width,height=ButtonHeight,asset="button",text=wrapped,color=enabled?"ink":"dim",size=Body,index=index,action=action,enabled=enabled});
            }

            void RoomBadge(ReworkModel m)
            {
                string[] names={"무게의 자리","멈추는 곳","서로의 벽"};int room=Math.Max(0,Math.Min(names.Length-1,m.roomIndex));
                Panel("room-badge",12,12,208,34);
                Text("room-progress",24,22,80,"회로 "+(room+1)+"/3","cyan");
                Text("room-name",112,22,94,names[room],"dim",Small);
            }
            public void Puzzle(ReworkModel m)
            {
                RoomBadge(m);int weights=0,orbs=0,weightDone=0,orbDone=0;
                for(int i=0;i<m.puzzle.room.goals.Length;i++)
                {
                    if(m.puzzle.room.types[i]==1){orbs++;if(m.puzzle.GoalFilled(i))orbDone++;}
                    else {weights++;if(m.puzzle.GoalFilled(i))weightDone++;}
                }
                Panel("socket-progress",468,12,160,34);
                Image("weight-goal",479,20,18,18,"state-amber-slot-empty");
                Text("weight-count",502,22,40,weightDone+"/"+weights,"gold");
                if(orbs>0)
                {Image("orb-goal",552,20,18,18,"state-cyan-slot-empty");Text("orb-count",576,22,40,orbDone+"/"+orbs,"cyan");}
                if(m.phase==Journey.Puzzle)
                {
                    if(m.roomIndex==0)Text("puzzle-objective",12,56,168,"소켓을 모두 채우세요.","dim",Small);
                    Button("undo",12,328,106,"Z 되돌리기",0,"undo",m.puzzle.UndoCount>0);
                    Button("reset-room",126,328,94,"R 초기화",1,"restart-room");
                    Text("puzzle-controls",234,342,268,"방향키 이동","dim",Small);
                    Text("pause-shortcut",550,342,78,"Esc 메뉴","dim",Small);
                }
            }
            public void PuzzleHelp(string value)
            {
                const int x=12,y=82,width=166;string wrapped=Wrap(value,width-24,Body);
                int bodyHeight=TextHeight(wrapped,Body),height=bodyHeight+20;
                // Failure guidance is concise by contract. Overflow is rejected,
                // never silently omitted or drawn over the puzzle board.
                if(height>110)throw new InvalidOperationException("Puzzle guidance is too long for the contextual card");
                Panel("auto-help",x,y,width,height);
                Text("auto-help-message",x+12,y+10,width-24,value,"ink");
            }
            public void CombatHelp(string value)
            {
                if(MeasureWidth(value,Body)>592||value.IndexOf('\n')>=0)
                    throw new InvalidOperationException("Combat guidance must fit one readable line");
                Panel("auto-help",12,310,616,32);
                Text("auto-help-message",24,317,592,value,"ink");
            }

            public void Combat(ReworkModel m,bool helpShown)
            {
                if(m.phase==Journey.Arrival)return;
                Panel("player-health",12,12,122,32);
                Image("player-heart",23,20,16,16,m.health>0?"fx-heart-full":"fx-heart-empty");
                for(int i=0;i<5;i++)
                {
                    string state=i<m.health?"full":i==m.health&&m.clock-m.hurtAt<.2f?"ghost":"empty";
                    Image("player-cell-"+i,44+i*14,22,10,12,"fx-tique-cell-"+state);
                }
                if(m.hero.invincible>0&&m.phase==Journey.Combat)Image("player-protected",142,16,24,24,"fx-protect");
                if(m.health==1)Text("player-danger",12,51,118,"하트 1","red",Small);
                Text("guardian-name",258,10,124,"철갑 문지기","dim",Small);
                Panel("guardian-health",248,28,144,28);
                for(int i=0;i<9;i++)
                {
                    string state=i<m.bossHealth?"full":i==m.bossHealth&&m.clock-m.lastBossDamageAt<.2f?"ghost":"empty";
                    Image("guardian-cell-"+i,260+i*12+i/3*3,36,10,12,"fx-iron-"+state);
                }
                if(m.phase==Journey.Combat)
                {
                    string tell=m.bossMove==IronMove.ChargeAim?"돌진":m.bossMove==IronMove.WaveAim?"충격파":m.bossMove==IronMove.SlamAim?"낙하":"";
                    if(tell.Length>0){Panel("pattern-chip",536,12,92,28);Text("pattern-name",548,20,68,tell,"gold");}
                    if(m.Vulnerable)
                    {
                        Panel("core-window",426,12,202,44);
                        Text("core-action",438,20,178,"X 노심 "+m.openHits+"/"+m.OpenHitLimit,"cyan");
                        Fill("core-window-track",438,43,178,3,"shade");
                        float remaining=Math.Max(0,Math.Min(1,m.OpeningRemaining/(m.openingSource==CoreOpeningSource.SlamCounter?ReworkModel.CounterExposureDuration:m.OpeningDuration)));
                        Fill("core-window-fill",438,43,(int)(178*remaining),3,"cyan");
                    }
                    if(m.hero.grounded&&m.chargeCooldown<=0)
                    {
                        for(int i=0;i<m.pylons.Length;i++)if(Math.Abs(m.hero.x-m.pylons[i])<36)
                        {
                            Panel("interact-context",508,58,120,28);
                            Text("interact-action",520,65,96,"E 충전","cyan");break;
                        }
                    }
                }
                if(m.phase==Journey.Restored)
                {
                    Panel("return-objective",432,12,196,28);
                    Text("return-goal",444,20,172,"오른쪽 문으로","cyan");
                    if(m.hero.x>594){Panel("return-interact",508,58,120,28);Text("return-action",520,65,96,"E 귀환","cyan");}
                }
                if(m.phase==Journey.Combat||m.phase==Journey.Restored)
                {
                    Text("combat-controls",12,342,500,helpShown?"Z 점프 · X 공격 · C 대시":"← → 이동 · Z 점프 · X 공격 · C 대시","dim",Small);
                    Text("pause-shortcut",550,342,78,"Esc 메뉴","dim",Small);
                }
            }

            public void Opening(ReworkModel m)
            {
                string record=m.age<11?OpeningSequence.Record(m.age):"";
                if(record.Length>0){Panel("opening-record",136,12,368,34);Text("opening-record-text",148,22,344,record,"cyan");}
                if(m.age>=11){RoomBadge(m);Text("opening-objective",12,56,168,"귀환 회로를 이으세요.","dim",Small);}
                Text("opening-skip",508,342,120,"Enter 건너뛰기","dim",Small);
            }
            public void Title()
            {
                Panel("title-card",134,66,372,prefs.largeText?234:220);
                Text("title-kicker",156,83,328,"CLOCKWORK / RETURN","cyan",Small);
                Text("title",156,105,328,"티크: 귀환 회로","ink",TitleFont);
                Text("title-logline",156,prefs.largeText?147:139,328,"세 회로를 잇고, 공방으로 돌아가세요.","dim");
                int start=prefs.largeText?193:184;
                Button("start",156,start,328,"Enter 시작",0,"start");
                Button("combat-only",156,start+ButtonHeight+8,328,"전투만 시작",1,"restart-combat");
                Text("title-control-note",156,start+ButtonHeight*2+24,328,"방향키 선택 · Enter 확인","dim",Small);
            }
            public void Arrival(ReworkModel m)
            {
                Panel("arrival-ready",150,44,340,42);
                Text("arrival-title",162,57,176,m.age<2.4f?"전원 재가동…":"문지기가 길을 막는다.","gold");
                Button("begin-combat",352,53,126,m.age<2.4f?"준비 중":"Enter 시작",0,"next",m.age>=2.4f);
            }
            public void RoomClear(ReworkModel m)
            {
                int height=prefs.largeText?126:112,y=(360-height)/2;
                Panel("room-clear-card",158,y,324,height);
                Text("room-clear-title",174,y+12,292,"회로 "+(m.roomIndex+1)+" 연결 완료","cyan",TitleFont);
                Text("room-clear-note",174,y+(prefs.largeText?54:40),292,m.roomIndex==2?"문지기가 깨어납니다.":"공장에 불빛이 돌아옵니다.","dim");
                Button("next-room",174,y+height-ButtonHeight-12,292,"Enter 다음으로",0,"next");
            }
            public void Dead(ReworkModel m,string help)
            {
                string wrapped=Wrap(help,292,Body);int helpHeight=TextHeight(wrapped,Body);
                if(helpHeight>LineHeight(Body)*2)throw new InvalidOperationException("Retry guidance exceeds two lines");
                int height=(prefs.largeText?180:162)+(helpHeight>0?helpHeight+8:0),y=(360-height)/2;
                Panel("retry-card",156,y,328,height);
                Text("retry-title",174,y+13,292,"다시 도전할까요?","cyan",TitleFont);
                int note=prefs.largeText?58:44;
                Text("retry-checkpoint",174,y+note,292,"회로는 복구되어 있어요.","dim");
                if(helpHeight>0)Text("retry-help",174,y+note+28,292,help,"ink");
                int row=y+height-ButtonHeight*2-24;
                Button("retry",174,row,292,"Enter 다시 도전",0,"retry");
                Button("assist-mode",174,row+ButtonHeight+7,292,m.assisted?"도움 모드: 켜짐":"도움 모드: 꺼짐",1,"toggle-assisted");
            }
            public void Ending(ReworkModel m)
            {
                int height=prefs.largeText?268:248,y=(360-height)/2;
                Panel("ending-card",146,y,348,height);
                Text("ending-title",164,y+14,312,"돌아갈 곳이 있어.","cyan",TitleFont);
                string story="폐기 판정 취소.\n엘리아스 공방으로 귀환합니다.";
                int storyY=prefs.largeText?60:52;
                Text("ending-story",164,y+storyY,312,story,"ink");
                int storyHeight=TextHeight(Wrap(story,312,Body),Body);
                Text("ending-time",164,y+storyY+storyHeight+12,312,"조작 시간 "+TimeSpan.FromSeconds(m.controlTime).ToString(@"mm\:ss"),"dim",Small);
                int row=y+height-3*ButtonHeight-38;
                Button("ending-restart",164,row,312,"처음부터",0,"restart-all");
                Button("ending-combat",164,row+ButtonHeight+7,312,"전투 다시 시작",1,"restart-combat");
                Button("ending-quit",164,row+2*(ButtonHeight+7),312,"종료",2,"quit");
            }
            public void Pause(ReworkModel m)
            {
                int count=m.InArena?8:7,rowHeight=ButtonHeight+3,header=prefs.largeText?56:48,height=header+count*rowHeight+26,y=(360-height)/2;
                Panel("pause-card",162,y,316,height);
                Text("pause-title",180,y+12,280,"잠시 멈췄어요.","cyan",TitleFont);
                var labels=new List<string>{"계속하기",m.muted?"소리: 꺼짐":"소리: 켜짐",m.reducedEffects?"효과 줄임: 켜짐":"효과 줄임: 꺼짐",prefs.autoHelp?"자동 안내: 켜짐":"자동 안내: 꺼짐",prefs.largeText?"제목 확대: 켜짐":"제목 확대: 꺼짐"};
                var actions=new List<string>{"continue","toggle-mute","toggle-effects","toggle-auto-help","toggle-large-text"};
                if(m.InArena){labels.Add("전투 다시 시작");actions.Add("restart-combat");}
                labels.Add("처음부터 다시");actions.Add("restart-all");labels.Add("종료");actions.Add("quit");
                for(int i=0;i<labels.Count;i++)Button("pause-"+actions[i],180,y+header+i*rowHeight,280,labels[i],i,actions[i]);
                Text("pause-controls",180,y+header+count*rowHeight+4,280,"↑↓ 선택  Enter 확인  Esc 닫기","dim",Small);
            }
        }
    }
}
