using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed class ReworkGame : MonoBehaviour
    {
        public ReworkModel Model {get;private set;}
        PuzzleBook book;
        readonly Dictionary<string,Sprite> art=new Dictionary<string,Sprite>();
        readonly Dictionary<string,Sprite[]> animations=new Dictionary<string,Sprite[]>();
        readonly Dictionary<string,int[]> durations=new Dictionary<string,int[]>();
        readonly Dictionary<string,SpriteRenderer> pool=new Dictionary<string,SpriteRenderer>();
        readonly Dictionary<string,AudioClip> audio=new Dictionary<string,AudioClip>();
        Camera cameraWorld;RenderTexture target;Sprite pixel;AudioSource speaker;Font font;
        GUIStyle normal,small,title,button;float accumulator,keyRepeat;int heldDirection=-1;
        ReworkCommand pending=ReworkCommand.Empty;
        bool smoke;float smokeStart;readonly ReworkPilot pilot=new ReworkPilot();
        readonly HashSet<string> screenshots=new HashSet<string>();
        readonly Color cyan=new Color(.39f,.89f,.87f),gold=new Color(.95f,.73f,.36f),red=new Color(1,.36f,.28f);
        readonly Color ink=new Color(.91f,.95f,.95f),dim=new Color(.60f,.70f,.75f),panel=new Color(.026f,.05f,.075f,.95f);
        void Awake()
        {
            Application.targetFrameRate=60;QualitySettings.vSyncCount=0;QualitySettings.antiAliasing=0;Application.runInBackground=true;
            smoke=Array.IndexOf(Environment.GetCommandLineArgs(),"--return-v2-smoke")>=0;smokeStart=Time.realtimeSinceStartup+1.2f;
            book=JsonUtility.FromJson<PuzzleBook>(Resources.Load<TextAsset>("ReturnV2/puzzles").text);Restart();
            var clips=JsonUtility.FromJson<ClipFile>(Resources.Load<TextAsset>("Return/clips").text);
            foreach(var c in clips.clips)
            {
                durations[c.name]=c.durations;Sprite[] frames=new Sprite[c.durations.Length];
                for(int i=0;i<frames.Length;i++)frames[i]=Load("Return/Tique/"+c.name+"/"+i.ToString("00"));animations[c.name]=frames;
            }
            foreach(string name in new[]{"workshop","arena","floor","wall","battery","orb","amber-socket","cyan-socket","pylon","gear"})art[name]=Load("ReturnV2/Art/"+name);
            foreach(string clip in new[]{"idle","attack","stagger"})
            {
                int count=clip=="attack"?6:4;var frames=new Sprite[count];
                for(int i=0;i<count;i++)frames[i]=Load("ReturnV2/Art/Warden/"+clip+"/"+i.ToString("00"));animations["iron-"+clip]=frames;
            }
            foreach(string name in new[]{"jump","dash","land","hit","hurt","success","switch","warning"})audio[name]=Resources.Load<AudioClip>("Return/Audio/"+name);
            var tex=new Texture2D(1,1);tex.SetPixel(0,0,Color.white);tex.Apply();pixel=Sprite.Create(tex,new Rect(0,0,1,1),Vector2.one*.5f,64);
            var cam=new GameObject("640 x 360 Pixel Camera");cam.transform.SetParent(transform);cameraWorld=cam.AddComponent<Camera>();cam.AddComponent<AudioListener>();
            cameraWorld.orthographic=true;cameraWorld.orthographicSize=180f/64;cameraWorld.transform.position=new Vector3(5,180f/64,-10);
            cameraWorld.backgroundColor=Color.black;cameraWorld.clearFlags=CameraClearFlags.SolidColor;
            target=new RenderTexture(640,360,16,RenderTextureFormat.ARGB32){filterMode=FilterMode.Point};target.Create();cameraWorld.targetTexture=target;
            var presentation=new GameObject("Display");presentation.transform.SetParent(transform);var display=presentation.AddComponent<Camera>();
            display.cullingMask=0;display.depth=1;display.clearFlags=CameraClearFlags.SolidColor;display.backgroundColor=Color.black;
            speaker=gameObject.AddComponent<AudioSource>();speaker.playOnAwake=false;speaker.volume=.3f;
            font=Font.CreateDynamicFontFromOSFont(new[]{"Malgun Gothic","Noto Sans CJK KR","Arial"},24);
            DrawWorld();if(smoke)StartCoroutine(Smoke());
        }
        Sprite Load(string path)
        {
            var t=Resources.Load<Texture2D>(path);if(t==null)throw new InvalidOperationException("Missing V2 art: "+path);
            t.filterMode=FilterMode.Point;return Sprite.Create(t,new Rect(0,0,t.width,t.height),Vector2.one*.5f,64);
        }
        void Restart(){Model=new ReworkModel(book);Model.Sound=Sound;pending=ReworkCommand.Empty;accumulator=0;}
        void Sound(string name){if(!Model.muted&&speaker!=null&&audio.TryGetValue(name,out var clip))speaker.PlayOneShot(clip,name=="land"?.2f:.8f);}
        bool Down(KeyCode a,KeyCode b)=>Input.GetKeyDown(a)||Input.GetKeyDown(b);
        void Update()
        {
            if(smoke&&Time.realtimeSinceStartup<smokeStart){DrawWorld();return;}
            if(Input.GetKeyDown(KeyCode.F11))Screen.fullScreen=!Screen.fullScreen;
            if(Input.GetKeyDown(KeyCode.M))Model.muted=!Model.muted;
            if(Input.GetKeyDown(KeyCode.Escape)){Model.paused=!Model.paused;pending=ReworkCommand.Empty;accumulator=0;}
            if(Model.paused)return;
            if(!smoke)
            {
                if(Model.phase==Journey.Ending&&Input.GetKeyDown(KeyCode.Return)){Restart();return;}
                pending.interact|=Down(KeyCode.E,KeyCode.Return);
                pending.undo|=Down(KeyCode.Z,KeyCode.Backspace);pending.restart|=Input.GetKeyDown(KeyCode.R);pending.hint|=Input.GetKeyDown(KeyCode.H);
                pending.jump|=Down(KeyCode.Space,KeyCode.UpArrow);pending.dash|=Down(KeyCode.LeftShift,KeyCode.RightShift);pending.attack|=Input.GetKeyDown(KeyCode.J);
                pending.axis=(Input.GetKey(KeyCode.RightArrow)||Input.GetKey(KeyCode.D)?1:0)-(Input.GetKey(KeyCode.LeftArrow)||Input.GetKey(KeyCode.A)?1:0);
                int dir=-1;
                if(Input.GetKey(KeyCode.LeftArrow)||Input.GetKey(KeyCode.A))dir=0;
                if(Input.GetKey(KeyCode.RightArrow)||Input.GetKey(KeyCode.D))dir=1;
                if(Input.GetKey(KeyCode.UpArrow)||Input.GetKey(KeyCode.W))dir=2;
                if(Input.GetKey(KeyCode.DownArrow)||Input.GetKey(KeyCode.S))dir=3;
                keyRepeat-=Time.unscaledDeltaTime;
                if(dir>=0&&(dir!=heldDirection||keyRepeat<=0)){pending.grid=dir;keyRepeat=dir!=heldDirection?.23f:.16f;}
                heldDirection=dir;
            }
            accumulator+=Mathf.Min(.1f,Time.unscaledDeltaTime);
            while(accumulator>=1f/120)
            {
                int axis=pending.axis;Model.Tick(1f/120,smoke?pilot.Next(Model):pending);
                pending=ReworkCommand.Empty;pending.axis=axis;accumulator-=1f/120;
            }
            DrawWorld();
        }
        void OnApplicationFocus(bool focus){if(!focus&&!smoke&&Model!=null&&Model.phase!=Journey.Title){Model.paused=true;pending=ReworkCommand.Empty;accumulator=0;}}
        void Draw(string id,Sprite sprite,float x,float y,int layer,Color? tint=null,bool flip=false,float width=0,float height=0)
        {
            if(!pool.TryGetValue(id,out var r)){var go=new GameObject(id);go.transform.SetParent(transform);r=go.AddComponent<SpriteRenderer>();pool[id]=r;}
            float w=width>0?width:sprite.rect.width,h=height>0?height:sprite.rect.height;
            r.enabled=true;r.sprite=sprite;r.sortingOrder=layer;r.color=tint??Color.white;r.flipX=flip;
            r.transform.position=new Vector3((Mathf.Round(x)+w*.5f)/64,(360-Mathf.Round(y)-h*.5f)/64,0);
            r.transform.localScale=new Vector3(w/sprite.rect.width,h/sprite.rect.height,1);
        }
        void Prop(string id,string sprite,float x,float y,int layer=4,Color? tint=null){Draw(id,art[sprite],x,y,layer,tint);}
        void Bar(string id,float x,float y,float w,float h,Color color,int layer=3){Draw(id,pixel,x,y,layer,color,false,Mathf.Max(1,w),Mathf.Max(1,h));}
        void Tique(float x,float y,string clip,int frame,int layer=1000,bool flip=false)
        {
            Color color=Model.InArena&&Model.hero.invincible>0&&Model.phase==Journey.Combat&&Mathf.Sin(Model.clock*22)>0?new Color(1,1,1,.45f):Color.white;
            Draw("tique",animations[clip][frame],x-32,y-56,layer,color,flip);
        }
        void DrawWorld()
        {
            foreach(var r in pool.Values)r.enabled=false;var m=Model;
            Prop("bg",m.InArena?"arena":"workshop",0,0,0);
            cameraWorld.transform.position=new Vector3((320+(m.shake>0?Mathf.Round(Mathf.Sin(m.clock*90)*2):0))/64,180f/64,-10);
            if(!m.InArena)
            {
                const float bx=194,by=64,cell=36;
                var p=m.puzzle;float duration=.15f;
                for(int i=0;i<p.boxes.Length;i++)if(Mathf.Abs(p.boxes[i]%7-p.previousBoxes[i]%7)+Mathf.Abs(p.boxes[i]/7-p.previousBoxes[i]/7)>1)duration=.27f;
                float t=1-Mathf.Clamp01(p.motion/duration);t=t*t*(3-2*t);
                for(int pos=0;pos<49;pos++)
                {
                    float x=bx+pos%7*cell,y=by+pos/7*cell;
                    Prop("tile"+pos,p.Wall(pos)?"wall":"floor",x,y,p.Wall(pos)?10+pos/7*20:1,p.Wall(pos)?new Color(.5f,.62f,.72f):new Color(.62f,.69f,.76f));
                }
                for(int i=0;i<p.room.goals.Length;i++)
                {
                    int pos=p.room.goals[i];Prop("goal"+i,p.room.types[i]==0?"amber-socket":"cyan-socket",bx+pos%7*cell,by+pos/7*cell,2,p.GoalFilled(i)?Color.white:new Color(.8f,.9f,.95f));
                }
                for(int i=0;i<p.boxes.Length;i++)
                {
                    float x=Mathf.Lerp(p.previousBoxes[i]%7,p.boxes[i]%7,t),y=Mathf.Lerp(p.previousBoxes[i]/7,p.boxes[i]/7,t);
                    bool orb=p.room.types[i]==1;Prop("box"+i,orb?"orb":"battery",bx+x*cell+(orb?5:3),by+y*cell+(orb?6:2),15+Mathf.RoundToInt(y*20));
                }
                float px=Mathf.Lerp(p.previousPlayer%7,p.player%7,t),py=Mathf.Lerp(p.previousPlayer/7,p.player/7,t);
                string clip=p.motion>0?"Walk":"Idle";int frame=p.motion>0?(int)(m.clock*14)%animations["Walk"].Length:0;
                Tique(bx+px*cell+18,by+py*cell+32,clip,frame,18+Mathf.RoundToInt(py*20),p.lastDirection==0);
            }
            else
            {
                Bar("floor",0,282,640,1,new Color(.4f,.47f,.52f),3);
                Draw("ledge-l",art["floor"],44,236,3,Color.white,false,48,6);Draw("ledge-r",art["floor"],548,236,3,Color.white,false,48,6);
                for(int i=0;i<2;i++)
                {
                    Prop("pylon"+i,"pylon",m.pylons[i]-17,230,5,m.charged==i?Color.white:new Color(.36f,.49f,.54f));
                    if(m.charged==i){Bar("power"+i,m.pylons[i]-19,285,38*m.chargeLife/16,2,cyan,6);Bar("charge-beam"+i,m.pylons[i]-1,207,2,20,cyan,4);}
                }
                string bossClip="idle";float idle=m.clock%1.44f;int bossFrame=idle<.4f?0:idle<.54f?1:idle<.84f?2:3;
                if(m.bossMove==IronMove.ChargeAim||m.bossMove==IronMove.WaveAim||m.bossMove==IronMove.SlamAim){bossClip="attack";bossFrame=m.bossAge<.55f?0:1;}
                if(m.bossMove==IronMove.Charge||m.bossMove==IronMove.Slam){bossClip="attack";bossFrame=m.bossAge<.1f?2:3;}
                if(m.bossMove==IronMove.Recover){bossClip="attack";bossFrame=m.bossAge<.3f?4:5;}
                if(m.bossMove==IronMove.Open||m.bossMove==IronMove.Down){bossClip="stagger";bossFrame=m.bossMove==IronMove.Down?3:Mathf.Min(3,(int)(m.bossAge*6));}
                Draw("iron-maw",animations["iron-"+bossClip][bossFrame],m.bossX-96,m.bossY-132,10,m.bossMove==IronMove.Down?new Color(.4f,.47f,.53f):Color.white,m.bossFacing>0);
                if(m.Vulnerable)
                {
                    Prop("exposed-core","gear",m.WeakX-12,250,11,m.flash>0?new Color(1,.9f,.7f):Color.white);
                    Bar("open-time",m.bossX-42,m.bossY-112,84*(1-Mathf.Clamp01(m.bossAge/(m.assisted?7:5.2f))),2,gold,12);
                }
                if(m.bossMove==IronMove.ChargeAim)
                {
                    float start=m.bossFacing<0?24:m.bossX,end=m.bossFacing<0?m.bossX:616;
                    Bar("charge-track",start,280,end-start,2,red,12);
                    for(int i=0;i<5;i++)Bar("charge-tick"+i,start+(end-start)*(i+1)/6,274,3,7,red,12);
                }
                if(m.bossMove==IronMove.SlamAim||m.bossMove==IronMove.Slam)
                {
                    Bar("slam-area",m.aimX-68,280,136,3,red,12);Bar("slam-l",m.aimX-68,261,2,20,red,12);Bar("slam-r",m.aimX+66,261,2,20,red,12);
                }
                if(m.bossMove==IronMove.WaveAim)for(int i=0;i<15;i++)Bar("wave-warn"+i,20+i*41,279,18,3,gold,12);
                for(int i=0;i<m.waves.Count;i++)Prop("wave"+i,"gear",m.waves[i].x-12,260,12);
                string pose=m.hero.Pose(durations,out int f);Tique(m.hero.x,m.hero.y,pose,f,20,m.hero.facing<0);
                if(m.phase==Journey.Restored||m.phase==Journey.Ending)Bar("exit",608,188,9,94,new Color(.45f,.9f,.9f,.65f),4);
            }
        }
        void Styles()
        {
            if(normal!=null)return;
            normal=new GUIStyle(GUI.skin.label){font=font,fontSize=22,wordWrap=true};normal.normal.textColor=ink;
            small=new GUIStyle(normal){fontSize=19};small.normal.textColor=dim;
            title=new GUIStyle(normal){fontSize=46,fontStyle=FontStyle.Bold};
            button=new GUIStyle(GUI.skin.button){font=font,fontSize=21,padding=new RectOffset(12,12,8,8)};button.normal.textColor=ink;button.hover.textColor=cyan;
        }
        void Panel(float x,float y,float w,float h,Color? color=null){GUI.color=color??panel;GUI.DrawTexture(new Rect(x,y,w,h),Texture2D.whiteTexture);GUI.color=Color.white;}
        void Text(float x,float y,float w,float h,string text,GUIStyle style=null,Color? color=null){GUI.color=color??Color.white;GUI.Label(new Rect(x,y,w,h),text,style??normal);GUI.color=Color.white;}
        bool Button(float x,float y,float w,float h,string text)=>GUI.Button(new Rect(x,y,w,h),text,button);
        void Overlay(){Panel(0,0,1280,720,new Color(.02f,.035f,.06f,.87f));}
        void OnGUI()
        {
            if(Model==null||target==null)return;Styles();float s=Mathf.Min(Screen.width/1280f,Screen.height/720f);
            GUI.matrix=Matrix4x4.TRS(new Vector3((Screen.width-1280*s)/2,(Screen.height-720*s)/2,0),Quaternion.identity,new Vector3(s,s,1));
            GUI.DrawTexture(new Rect(0,0,1280,720),target,ScaleMode.StretchToFill,false);var m=Model;
            if(m.phase==Journey.Title)
            {
                Overlay();Text(100,93,1000,40,"CLOCKWORK   /   RETURN PROTOCOL",small,cyan);
                Text(96,157,1000,80,"티크 : 귀환 회로",title);
                Text(100,267,920,94,"모두가 멈춘 공장. 아직 뛰는 작은 하트 하나.\n세 개의 회로를 잇고, 폐기 명령을 끝내세요.");
                Text(100,376,960,50,"공간 퍼즐 3개  →  철갑 문지기  →  귀환 기록",small);
                if(Button(100,460,338,62,"회로에 접속  ·  Enter"))m.Start();
                Text(100,558,1030,72,"퍼즐  방향키 / WASD · Z 되돌리기 · R 방 초기화 · H 힌트\n전투  ← → 이동 · Space 점프 · Shift 대시 · J 공격 · E 충전",small);
                Text(100,662,1000,34,"F11 전체화면   ·   M 소리   ·   Esc 일시정지",small);return;
            }
            Panel(20,16,1240,78);
            Text(40,25,760,36,m.InArena?"02  /  폐기 집행실":"01  /  귀환 동력실",normal,cyan);
            Text(40,60,1170,32,m.InArena?"충전 기둥으로 돌진을 유도하고, 열린 노심을 공격하세요.":"같은 색·모양의 소켓에 모든 전원을 놓으세요. 당길 수는 없어요.",small);
            if(!m.InArena)
            {
                string[] names={"무게의 자리","멈추는 곳","서로의 벽"};
                Panel(24,128,326,382);Text(44,148,282,35,"회로 "+(m.roomIndex+1)+" / 3",small,cyan);
                Text(42,195,294,62,names[m.roomIndex],new GUIStyle(title){fontSize=32});
                Text(44,280,282,82,"노란 추  ◆\n한 칸씩 밀립니다.",normal,gold);
                if(m.roomIndex>0)Text(44,377,282,102,"시안 구슬  ●\n막힐 때까지\n미끄러집니다.",normal,cyan);
                else Text(44,387,282,88,"소켓에 넣는 순서와\n뒤로 돌아갈 길을 생각해 보세요.",small);
                Panel(928,128,328,382);Text(950,148,284,38,"움직임  "+m.puzzle.moves+"  /  밀기  "+m.puzzle.pushes,small);
                if(Button(948,205,286,50,"한 수 되돌리기  ·  Z"))pending.undo=true;
                if(Button(948,267,286,50,"이 방 다시 시작  ·  R"))pending.restart=true;
                if(Button(948,329,286,50,"힌트 보기  ·  H"))pending.hint=true;
                Text(950,401,282,101,m.Hint(),small,m.hintLevel>0?gold:dim);
                Panel(24,532,326,99);Text(43,548,290,80,m.roomIndex==0?"“내가 돌아갈 곳은…\n엘리아스 공방.”":m.roomIndex==1?"기록 조각 02\n“기다릴게. 서두르지 마.”":"기록 조각 03\n“네 하트는 고장이 아니야.”",small);
                Text(934,539,310,89,m.puzzle.feedback,small,cyan);
            }
            else
            {
                Text(843,26,220,31,"티크",small);for(int i=0;i<5;i++)Panel(911+i*26,35,18,14,i<m.health?cyan:new Color(.16f,.23f,.29f));
                Panel(398,114,484,52);Text(415,119,216,35,"철갑 문지기",small);
                for(int i=0;i<9;i++)Panel(624+i*26,131,20,10,i<m.bossHealth?red:new Color(.18f,.23f,.28f));
                string state=m.Vulnerable?"노심 노출  ·  J 공격":m.bossMove==IronMove.ChargeAim?"돌진 준비  ·  기둥 뒤로 유도":m.bossMove==IronMove.WaveAim?"충격파 준비  ·  점프":m.bossMove==IronMove.SlamAim?"낙하 조준  ·  붉은 구역에서 대시":"충전  →  유도  →  반격";
                Text(400,177,600,44,state,normal,m.Vulnerable?cyan:gold);
                for(int i=0;i<2;i++)Text(m.pylons[i]*2-64,583,170,33,m.charged==i?"충전  "+Mathf.CeilToInt(m.chargeLife)+"초":"E  충전",small,m.charged==i?cyan:dim);
                if(m.noticeLeft>0){Panel(98,606,1084,48);Text(116,614,1050,38,m.notice,small);}
            }
            Panel(0,660,1280,60);Text(25,676,1078,34,m.InArena?"← → 이동    Space / ↑ 점프·더블점프    Shift 대시    J 공격    E 충전":"방향키 / WASD 이동    Z 되돌리기    R 방 초기화    H 단계별 힌트",small);
            if(Button(1137,669,120,42,"Esc  정지"))m.paused=true;
            if(m.phase==Journey.RoomClear)
            {
                Overlay();Text(210,170,1000,80,"회로 "+(m.roomIndex+1)+" 연결 완료",title);
                Text(215,287,860,94,m.roomIndex==2?"귀환 전력을 복구했어요.\n출구를 막은 폐기 집행 장치가 깨어납니다.":"멈췄던 공장에 작은 불빛이 돌아옵니다.\n다음 방에서는 움직임의 규칙이 달라져요.");
                if(Button(215,433,540,63,m.roomIndex==2?"문지기에게  ·  Enter":"다음 회로로  ·  Enter"))pending.interact=true;
            }
            if(m.phase==Journey.Arrival)
            {
                Panel(135,207,1010,240);Text(168,226,930,60,"폐기 집행 장치 : IRON MAW",new GUIStyle(title){fontSize=34});
                Text(170,299,928,96,"기둥 옆 E로 충전한 뒤, 기둥 뒤에서 돌진을 유도하세요.\n장갑이 열리면 붉은 노심을 J로 공격할 수 있어요.\n충격파는 점프, 낙하는 대시로 피하세요.");
                Text(170,410,850,36,"Enter로 시작  ·  잠시 후 자동 시작",small,cyan);
            }
            if(m.phase==Journey.Dead)
            {
                Overlay();Text(230,160,900,90,"다시, 하트를 켜고.",title);
                Text(236,281,900,70,"회로는 복구되어 있어요. 문지기 앞에서 다시 시작합니다.");
                if(Button(236,388,515,60,"다시 도전  ·  Enter"))pending.interact=true;
                if(Button(236,470,515,55,m.assisted?"도움 켜짐 · 예고와 반격 시간 확대":"도움 모드 켜기"))m.assisted=!m.assisted;
            }
            if(m.phase==Journey.Restored)Text(986,375,260,73,"귀환 기록\n오른쪽 문에서 E",normal,cyan);
            if(m.phase==Journey.Ending)
            {
                Overlay();Text(180,135,1000,86,"돌아갈 곳이 있어.",title);
                Text(184,257,1000,70,"식별명: 티크.   귀환처: 엘리아스 공방.",normal,cyan);
                Text(184,332,970,100,"“고장이 아니야. 네가 살아 있다는 뜻이지.”\n작은 하트가 한 번 더 뛰었습니다.\n폐기 판정 취소. 귀환을 허가합니다.");
                Text(184,463,900,42,"플레이  "+TimeSpan.FromSeconds(m.playTime).ToString(@"mm\:ss")+"   ·   회로 밀기 "+m.totalPushes+"회   ·   장갑 파괴 "+m.breaks+"회",small);
                if(Button(184,536,340,61,"처음부터  ·  Enter"))Restart();if(Button(546,536,220,61,"종료"))Application.Quit();
            }
            if(m.paused)
            {
                Overlay();Text(365,161,750,80,"잠시 멈췄어요.",title);
                if(Button(365,285,550,60,"계속하기  ·  Esc")){m.paused=false;pending=ReworkCommand.Empty;}
                if(Button(365,365,550,54,m.muted?"소리 켜기":"소리 끄기"))m.muted=!m.muted;
                if(Button(365,438,550,54,"처음부터 다시"))Restart();if(Button(365,511,550,54,"종료"))Application.Quit();
            }
        }
        IEnumerator Capture(string folder,string name)
        {
            if(!screenshots.Add(name))yield break;yield return new WaitForEndOfFrame();
            var texture=ScreenCapture.CaptureScreenshotAsTexture();if(texture==null)throw new InvalidOperationException("Visible player capture failed");
            File.WriteAllBytes(Path.Combine(folder,name+".png"),texture.EncodeToPNG());Destroy(texture);
        }
        IEnumerator Smoke()
        {
            string[] args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"--qa-dir");string folder=n>=0?args[n+1]:Path.Combine(Application.persistentDataPath,"ReturnV2QA");Directory.CreateDirectory(folder);
            yield return Capture(folder,"01-title");float deadline=Time.realtimeSinceStartup+210;
            while(Model.phase!=Journey.Ending&&Model.phase!=Journey.Dead&&Time.realtimeSinceStartup<deadline)
            {
                if(Model.phase==Journey.Puzzle)yield return Capture(folder,"02-puzzle-"+(Model.roomIndex+1));
                if(Model.phase==Journey.Arrival)yield return Capture(folder,"03-guardian");
                if(Model.bossMove==IronMove.ChargeAim)yield return Capture(folder,"04-charge-warning");
                if(Model.bossMove==IronMove.Open)yield return Capture(folder,"05-armor-open");
                if(Model.bossMove==IronMove.Wave)yield return Capture(folder,"06-wave");
                if(Model.bossMove==IronMove.SlamAim)yield return Capture(folder,"07-slam");
                yield return null;
            }
            bool pass=Model.phase==Journey.Ending&&Model.breaks>=3;yield return Capture(folder,pass?"08-ending":"failure");
            File.WriteAllText(Path.Combine(folder,"result.json"),"{\"passed\":"+pass.ToString().ToLowerInvariant()+",\"phase\":\""+Model.phase+"\",\"health\":"+Model.health+",\"breaks\":"+Model.breaks+",\"playSeconds\":"+Model.playTime.ToString("F2",System.Globalization.CultureInfo.InvariantCulture)+"}");
            File.WriteAllLines(Path.Combine(folder,"events.txt"),Model.events);Debug.Log("RETURN_V2_SMOKE "+(pass?"PASS":"FAIL"));Application.Quit(pass?0:2);
        }
        void OnDestroy(){if(target!=null){target.Release();Destroy(target);}}
    }
}
