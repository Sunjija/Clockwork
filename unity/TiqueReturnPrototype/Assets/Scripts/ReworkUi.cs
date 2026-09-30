using System;
using System.Collections.Generic;
using UnityEngine;
namespace TiqueReturn
{
    public sealed partial class ReworkGame
    {
        [Serializable] sealed class FontAtlas {public string characters="";public int columns=32,cell=16;}
        FontAtlas glyphs;Texture2D fontAtlas;readonly Dictionary<char,int> glyphIndex=new Dictionary<char,int>();
        int menuSelection;Journey menuPhase;bool menuWasPaused;
        int pressedButton=-1;float pressedAt=-10;
        void LoadPixelUi()
        {
            glyphs=JsonUtility.FromJson<FontAtlas>(Resources.Load<TextAsset>("ReturnV2/Feedback/font").text);
            fontAtlas=Resources.Load<Texture2D>("ReturnV2/Feedback/font");fontAtlas.filterMode=FilterMode.Point;
            for(int i=0;i<glyphs.characters.Length;i++)glyphIndex[glyphs.characters[i]]=i;
        }
        static int Advance(char c)=>c<128?8:16;
        void Text(int x,int y,int width,string value,Color? tint=null,int scale=1)
        {
            int px=x,py=y;GUI.color=tint??ink;
            for(int k=0;k<value.Length;k++)
            {
                char c=value[k];
                if(c=='\n'){px=x;py+=16*scale;continue;}
                // Wrap before a word that would overflow (words end at spaces), so
                // punctuation stays attached to its word; over-long words still break.
                if(px>x&&(k==0||value[k-1]==' '||value[k-1]=='\n')&&c!=' ')
                {
                    int word=0;for(int j=k;j<value.Length&&value[j]!=' '&&value[j]!='\n';j++)word+=Advance(value[j])*scale;
                    if(px+word>x+width&&word<=width){px=x;py+=16*scale;}
                }
                if(px+Advance(c)*scale>x+width){px=x;py+=16*scale;}
                if(px==x&&c==' ')continue;
                if(glyphIndex.TryGetValue(c,out int i))GUI.DrawTextureWithTexCoords(new Rect(px,py,16*scale,16*scale),fontAtlas,
                    new Rect(i%glyphs.columns*16f/fontAtlas.width,1-(i/glyphs.columns+1)*16f/fontAtlas.height,16f/fontAtlas.width,16f/fontAtlas.height),true);
                px+=Advance(c)*scale;
            }
            GUI.color=Color.white;
        }
        void UiSprite(string name,Rect rect,Color? color=null)
        {GUI.color=color??Color.white;GUI.DrawTexture(rect,animations["fx-"+name][0].texture,ScaleMode.StretchToFill,true);GUI.color=Color.white;}
        void KeyCap(int x,int y,string key){int w=key.Length*8+10;Panel(x,y,w,20);Text(x+5,y+2,w-8,key,cyan);}
        void CombatKeys()
        {
            KeyCap(12,331,"< >");Text(55,333,42,"이동",dim);
            KeyCap(103,331,"Z");KeyCap(127,331,"Space");Text(180,333,42,"점프",dim);
            UiSprite("icon-jump",new Rect(218,334,12,12));KeyCap(243,331,"X");Text(269,333,42,"공격",dim);
            UiSprite("icon-attack",new Rect(309,334,12,12));KeyCap(337,331,"C");Text(363,333,42,"대시",dim);
            UiSprite("icon-dash",new Rect(403,334,12,12));KeyCap(434,331,"E");Text(460,333,74,"상호작용",dim);UiSprite("icon-interact",new Rect(528,334,12,12));KeyCap(573,331,"Esc");
        }
        void Panel(int x,int y,int w,int h,string tile="panel")
        {
            var tex=animations["fx-"+tile][0].texture;
            GUI.color=new Color(.04f,.075f,.10f);GUI.DrawTexture(new Rect(x+2,y+2,w-4,h-4),Texture2D.whiteTexture);GUI.color=Color.white;
            // Four intact corners. Last edge pieces crop UVs by exactly the
            // remaining native pixels; stretching 3 texels into 1 caused seams.
            void Tile(int dx,int dy,int tw,int th,int sx,int sy)
            {GUI.DrawTextureWithTexCoords(new Rect(x+dx,y+dy,tw,th),tex,new Rect(sx/9f,1-(sy+th)/9f,tw/9f,th/9f));}
            Tile(0,0,3,3,0,0);Tile(w-3,0,3,3,6,0);Tile(0,h-3,3,3,0,6);Tile(w-3,h-3,3,3,6,6);
            for(int col=3;col<w-3;col+=3){int cw=Math.Min(3,w-3-col);Tile(col,0,cw,3,3,0);Tile(col,h-3,cw,3,3,6);}
            for(int row=3;row<h-3;row+=3){int ch=Math.Min(3,h-3-row);Tile(0,row,3,ch,0,3);Tile(w-3,row,3,ch,6,3);}
        }
        bool Button(int x,int y,int w,string label,int index=0,bool enabled=true)
        {
            var rect=new Rect(x,y,w,27);var e=Event.current;bool over=rect.Contains(e.mousePosition);
            if(enabled&&over&&e.type==EventType.MouseDown){pressedButton=index;pressedAt=Time.unscaledTime;}
            bool pressed=pressedButton==index&&Time.unscaledTime-pressedAt<.1f;
            string tile=!enabled?"button-disabled":pressed?"button-pressed":over||menuSelection==index?"button-selected":"button";
            Panel(x,y,w,27,tile);Text(x+8,y+(pressed?6:5),w-16,label,enabled?ink:dim);
            if(enabled&&over&&e.type==EventType.MouseUp&&e.button==0){e.Use();menuSelection=index;return true;}return false;
        }
        void FlushInput(bool release=true){pending=ReworkCommand.Empty;accumulator=0;heldDirection=-1;keyRepeat=0;releaseGate=release;}
        void MenuAction(int selected)
        {
            var m=Model;
            if(m.paused)
            {
                if(selected==0){m.paused=false;FlushInput();}
                if(selected==1)m.muted=!m.muted;
                if(selected==2)m.reducedEffects=!m.reducedEffects;
                if(selected==3)Restart();if(selected==4)Application.Quit();
            }
            else if(m.phase==Journey.Title)m.Start();
            else if(m.phase==Journey.Dead){if(selected==0)m.Retry();else m.assisted=!m.assisted;}
            else if(m.phase==Journey.Ending){if(selected==0)Restart();else Application.Quit();}
        }
        bool HandleMenuKeys()
        {
            var m=Model;if(menuPhase!=m.phase||menuWasPaused!=m.paused){menuSelection=0;menuPhase=m.phase;menuWasPaused=m.paused;}
            bool menu=m.paused||m.phase==Journey.Title||m.phase==Journey.Dead||m.phase==Journey.Ending;
            if(!menu)
            {
                if(m.phase==Journey.Puzzle)
                {if(Input.GetKeyDown(KeyCode.Tab))menuSelection=(menuSelection+1)%3;
                    if(Input.GetKeyDown(KeyCode.Return)){if(menuSelection==0)pending.undo=true;if(menuSelection==1)pending.restart=true;if(menuSelection==2)pending.hint=true;}}
                return false;
            }
            int count=m.paused?5:m.phase==Journey.Title?1:2;
            if(Input.GetKeyDown(KeyCode.DownArrow)||Input.GetKeyDown(KeyCode.Tab))menuSelection=(menuSelection+1)%count;
            if(Input.GetKeyDown(KeyCode.UpArrow))menuSelection=(menuSelection+count-1)%count;
            if(Input.GetKeyDown(KeyCode.Return))MenuAction(menuSelection);
            return true;
        }
        // 10x12 cells fill their slots; the boss meter groups 3+3+3 with a brass notch.
        static int CellsWidth(int count,bool boss)=>boss?6+count*12+6+3:24+count*13+3;
        void Cells(int x,int y,int count,int hp,bool boss,float lostAge)
        {
            Panel(x,y,CellsWidth(count,boss),20);
            if(!boss)UiSprite(hp>0?"heart-full":"heart-empty",new Rect(x+4,y+2,16,16));
            for(int i=0;i<count;i++)
            {
                string kind=boss?"iron-":"tique-cell-";kind+=i<hp?"full":i==hp&&lostAge<.2f?"ghost":"empty";
                int cx=boss?x+6+i*12+i/3*3:x+24+i*13;
                UiSprite(kind,new Rect(cx,y+4,10,12));
                // The lost cell's core flashes white for one beat, then shows the pale afterimage.
                if(i==hp&&lostAge<.05f){GUI.color=ink;GUI.DrawTexture(new Rect(cx+2,y+6,6,8),Texture2D.whiteTexture);GUI.color=Color.white;}
                if(boss&&(i==2||i==5)){GUI.color=gold;GUI.DrawTexture(new Rect(cx+11,y+5,1,10),Texture2D.whiteTexture);GUI.color=Color.white;}
            }
        }
        void Gauge(int x,int y,int width,float value,Color color)
        {Panel(x,y,width+4,9);GUI.color=color;GUI.DrawTexture(new Rect(x+2,y+3,Mathf.Clamp(Mathf.Floor(value*width),0,width),3),Texture2D.whiteTexture);GUI.color=Color.white;}
        void Circuit(int x,int y,int connected)
        {for(int i=0;i<3;i++){Panel(x+i*23,y,18,12);if(i<connected){GUI.color=cyan;GUI.DrawTexture(new Rect(x+i*23+3,y+3,12,6),Texture2D.whiteTexture);GUI.color=Color.white;}}}
        void OnGUI()
        {
            if(Model==null||target==null||glyphs==null)return;
            int s=Math.Max(1,Math.Min(Screen.width/640,Screen.height/360));int ox=(Screen.width-640*s)/2,oy=(Screen.height-360*s)/2;
            GUI.matrix=Matrix4x4.TRS(new Vector3(ox,oy,0),Quaternion.identity,new Vector3(s,s,1));GUI.color=Color.white;
            GUI.DrawTexture(new Rect(0,0,640,360),target,ScaleMode.StretchToFill,false);var m=Model;
            if(m.phase==Journey.Title)
            {
                Panel(42,45,556,267);Text(64,64,520,"CLOCKWORK / RETURN CIRCUIT",cyan);
                Text(64,94,520,"티크: 귀환 회로",ink,2);
                Text(64,153,504,"멈춘 공장. 아직 뛰는 작은 하트 하나.\n세 회로를 잇고 폐기 명령을 끝내세요.");
                if(Button(64,208,234,"시작   Enter"))MenuAction(0);
                Text(64,244,504,"퍼즐: 방향키 / Z 되돌리기 / R 초기화 / H 힌트",dim);
                Text(64,268,504,"전투: ← → 이동 / Z Space ↑ 점프 / X 공격 / C 대시\nE 상호작용   Esc 정지   F11 전체화면",dim);return;
            }
            if(m.phase==Journey.Opening)
            {
                if(m.age<1){GUI.color=Color.black;float covered=(1-Mathf.Floor(m.age*8)/8)*360;GUI.DrawTexture(new Rect(0,0,640,covered),Texture2D.whiteTexture);GUI.color=Color.white;}
                string record=OpeningSequence.Record(m.age);
                if(record.Length>0){Panel(98,18,444,30);Text(110,25,420,record,cyan);}
                if(m.age>=6&&m.age<9)Circuit(286,52,0);
                if(m.age>=11){Panel(12,63,171,66);Text(24,75,146,"회로 1 / 3",cyan);Circuit(24,104,0);KeyCap(12,332,"< >");Text(58,334,142,"방향키 이동",dim);}
                Text(458,338,170,"Enter 건너뛰기",dim);
            }
            else if(!m.InArena)
            {
                Panel(12,12,616,36);Text(24,23,390,"귀환 동력실  회로 "+(m.roomIndex+1)+" / 3",cyan);
                Panel(12,63,174,168);string[] names={"무게의 자리","멈추는 곳","서로의 벽"};Text(24,75,154,names[m.roomIndex],gold);
                Text(24,110,150,"노란 추\n한 칸씩 밀기",gold);
                Text(24,168,150,m.roomIndex==0?"뒤로 돌아갈\n길을 남기세요.":"시안 구슬\n벽까지 미끄러짐",cyan);
                Panel(456,63,174,258);Text(467,74,150,"이동 "+m.puzzle.moves+"  밀기 "+m.puzzle.pushes);
                if(Button(465,102,156,"Z 되돌리기",0,m.puzzle.UndoCount>0))pending.undo=true;UiSprite("icon-undo",new Rect(596,110,12,12));
                if(Button(465,138,156,"R 초기화",1))pending.restart=true;UiSprite("icon-reset",new Rect(596,146,12,12));
                if(Button(465,174,156,"H 힌트",2))pending.hint=true;UiSprite("icon-hint",new Rect(596,182,12,12));
                Text(465,211,156,m.Hint(),m.hintLevel>0?gold:dim);
                Panel(12,243,174,78);Text(24,255,150,m.roomIndex==0?"귀환처:\n엘리아스 공방.":m.roomIndex==1?"기다릴게.\n서두르지 마.":"네 하트는\n고장이 아니야.",cyan);
                Text(16,336,580,m.initialTutorial?"방향키 이동 · 추를 소켓으로 밀어주세요.":"방향키 이동   Z 되돌리기   R 초기화   H 힌트",dim);
                if(m.phase==Journey.RoomClear&&m.age>.8f)
                {Panel(150,116,342,126);Text(169,132,302,"회로 "+(m.roomIndex+1)+" 연결 완료",cyan);Text(169,163,302,m.roomIndex==2?"전력 복구. 문지기가 깨어납니다.":"멈춘 공장에 불빛이 돌아옵니다.");if(Button(169,202,300,"Enter 다음으로"))pending.interact=true;}
            }
            else if(m.phase!=Journey.Ending)
            {
                if(m.phase==Journey.Combat||m.phase==Journey.Restored||m.phase==Journey.Dead)
                {
                    int hp=m.health;if(m.clock-m.hudRefillAt<.2f)hp=Math.Min(m.health,(int)((m.clock-m.hudRefillAt)/.04f)+1);
                    Cells(12,12,5,hp,false,m.clock-m.hurtAt);Cells(252,12,9,m.bossHealth,true,m.clock-m.lastBossDamageAt);
                    Text(252+CellsWidth(9,true)+6,15,200,"철갑 문지기",dim);
                    if((m.bossHealth==6||m.bossHealth==3)&&m.clock-m.lastBossDamageAt<.22f){UiSprite("icon-locked",new Rect(238,16,12,12),gold);}
                    int after=12+CellsWidth(5,false)+4;
                    if(m.hero.invincible>0&&m.phase==Journey.Combat)UiSprite("protect",new Rect(after,10,24,24));
                    if(m.health==1)Text(after+28,16,120,"위험",red);
                }
                string state=m.phase==Journey.Restored?"폐기 명령 해제. 오른쪽 문에서 E":m.Vulnerable?"노심 노출 / X 공격":m.bossMove==IronMove.ChargeAim?"돌진: 기둥 뒤로 유도":m.bossMove==IronMove.WaveAim?"충격파: 점프":m.bossMove==IronMove.SlamAim?"낙하: 표시 밖으로 대시":"E 충전 → 유도 → X 반격";
                if(m.phase!=Journey.Arrival){Panel(188,41,264,27);Text(198,47,244,state,m.Vulnerable?cyan:gold);}
                if(m.Vulnerable){Gauge(276,74,88,1-m.bossAge/(m.assisted?7:5.2f),gold);for(int i=0;i<3;i++){GUI.color=i<m.openHits?cyan:dim;GUI.DrawTexture(new Rect(376+i*6,75,3,6),Texture2D.whiteTexture);GUI.color=Color.white;}}
                for(int i=0;i<2;i++)if(m.charged==i){Gauge((int)m.pylons[i]-22,289,40,m.chargeLife/16,cyan);if(m.chargeLife<3)UiSprite("icon-locked",new Rect(m.pylons[i]+25,286,12,12));}
                CombatKeys();
                if(m.phase==Journey.Arrival)
                {
                    Panel(136,80,369,156);Text(150,94,340,m.age<2.4f?"문지기 전원 재가동…":"폐기 집행 장치",gold);
                    Text(150,128,337,"E로 기둥 충전. 기둥 뒤로 돌진 유도.\n열린 노심에 X. 한 번에 세 번까지.\n충격파는 점프, 낙하는 대시.");
                    if(m.age>=2.4f){if(Button(150,199,339,"Enter 전투 시작"))pending.interact=true;}else Text(150,202,336,"안전하게 준비하세요.",dim);
                }
            }
            if(m.phase==Journey.Dead&&m.age>.3f)
            {Panel(118,78,408,200);Text(140,96,360,"다시, 하트를 켜고.",cyan);Text(140,136,360,"회로는 복구되어 있어요.");if(Button(140,182,363,"Enter 다시 도전",0))MenuAction(0);if(Button(140,221,363,m.assisted?"도움 켜짐":"도움 모드 켜기",1))MenuAction(1);}
            if(m.phase==Journey.Ending)
            {
                Panel(74,45,492,270);Text(96,62,448,"돌아갈 곳이 있어.",cyan,2);Text(96,112,440,"식별명: 티크.\n귀환처: 엘리아스 공방.\n네 하트는 고장이 아니야.\n폐기 판정 취소. 귀환을 허가합니다.");
                Text(96,202,440,"조작 "+TimeSpan.FromSeconds(m.controlTime).ToString(@"mm\:ss")+" / 밀기 "+m.totalPushes+" / 장갑 파괴 "+m.breaks,dim);
                if(Button(96,251,236,"Enter 처음부터",0))MenuAction(0);if(Button(344,251,192,"종료",1))MenuAction(1);
            }
            if(m.paused)
            {
                Panel(154,38,333,282);Text(177,52,288,"잠시 멈췄어요.",cyan);
                string[] labels={"계속하기",m.muted?"소리 켜기":"소리 끄기",m.reducedEffects?"효과 줄임: 켜짐":"효과 줄임: 꺼짐","처음부터 다시","종료"};
                for(int i=0;i<labels.Length;i++)if(Button(177,86+i*39,288,labels[i],i))MenuAction(i);
                Text(177,290,288,"↑ ↓ 선택 / Enter / Esc 계속",dim);
            }
        }
    }
}
