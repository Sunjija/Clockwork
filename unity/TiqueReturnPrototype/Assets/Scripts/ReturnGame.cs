using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed class ReturnGame : MonoBehaviour
    {
        public ReturnModel Model { get; private set; }
        readonly Dictionary<string, Sprite> art = new Dictionary<string, Sprite>();
        readonly Dictionary<string, Sprite[]> animation = new Dictionary<string, Sprite[]>();
        readonly Dictionary<string, int[]> durations = new Dictionary<string, int[]>();
        readonly Dictionary<string, SpriteRenderer> visible = new Dictionary<string, SpriteRenderer>();
        readonly Dictionary<string, AudioClip> sounds = new Dictionary<string, AudioClip>();
        Camera worldCamera;
        RenderTexture target;
        Sprite pixel;
        AudioSource speaker;
        Font korean;
        GUIStyle label, large, small, button;
        float accumulator;
        bool jumpPending, dashPending, attackPending, interactPending, focusPause;
        bool smoke;
        float smokeStart;
        readonly ReturnPilot pilot = new ReturnPilot();
        readonly Color cyan = new Color(.40f,.84f,.79f), gold = new Color(.86f,.73f,.47f);
        readonly Color ink = new Color(.93f,.95f,.91f), dim = new Color(.65f,.73f,.73f);
        readonly Color red = new Color(.91f,.38f,.32f), panel = new Color(.04f,.075f,.09f,.94f);

        void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            QualitySettings.antiAliasing = 0;
            Application.runInBackground = true;
            smoke = Array.IndexOf(Environment.GetCommandLineArgs(), "--return-smoke") >= 0;
            smokeStart = Time.realtimeSinceStartup + 1f;
            Model = new ReturnModel(); Model.Sound = PlaySound;
            ClipFile meta = JsonUtility.FromJson<ClipFile>(Resources.Load<TextAsset>("Return/clips").text);
            foreach (ClipSpec c in meta.clips)
            {
                durations[c.name] = c.durations;
                var frames = new Sprite[c.durations.Length];
                for (int n=0;n<frames.Length;n++) frames[n] = LoadSprite("Return/Tique/" + c.name + "/" + n.ToString("00"));
                animation[c.name] = frames;
            }
            foreach (string name in new[]{"limbus","inspection","console","magnet","weight","pressure","gate","rail-handle","guardian","fist","arm-link","practice","platform"})
                art[name] = LoadSprite("Return/Art/" + name);
            foreach (string name in new[]{"switch","jump","dash","hit","hurt","warning","land","success"})
                sounds[name] = Resources.Load<AudioClip>("Return/Audio/" + name);
            var p = new Texture2D(1,1); p.SetPixel(0,0,Color.white); p.Apply(); p.filterMode = FilterMode.Point;
            pixel = Sprite.Create(p,new Rect(0,0,1,1),Vector2.one*.5f,64);
            var cameraObject = new GameObject("Native 640x360 Camera");
            cameraObject.transform.SetParent(transform);
            worldCamera = cameraObject.AddComponent<Camera>(); cameraObject.AddComponent<AudioListener>();
            worldCamera.orthographic=true;worldCamera.orthographicSize=180f/64;worldCamera.transform.position=new Vector3(320f/64,180f/64,-10);
            worldCamera.backgroundColor=new Color(.04f,.06f,.07f);worldCamera.clearFlags=CameraClearFlags.SolidColor;
            target=new RenderTexture(640,360,16,RenderTextureFormat.ARGB32);target.filterMode=FilterMode.Point;target.Create();
            worldCamera.targetTexture=target;
            // Clear the actual display, including letterbox bars; the world camera renders only to the texture.
            var displayObject=new GameObject("Presentation Camera");displayObject.transform.SetParent(transform);
            var displayCamera=displayObject.AddComponent<Camera>();displayCamera.cullingMask=0;
            displayCamera.depth=1;displayCamera.clearFlags=CameraClearFlags.SolidColor;displayCamera.backgroundColor=Color.black;
            speaker=gameObject.AddComponent<AudioSource>();speaker.playOnAwake=false;speaker.volume=.35f;
            korean=Font.CreateDynamicFontFromOSFont(new[]{"Malgun Gothic","Apple SD Gothic Neo","Noto Sans CJK KR","Arial"},24);
            DrawWorld();
            if(smoke)StartCoroutine(SmokePlaythrough());
        }
        Sprite LoadSprite(string path)
        {
            Texture2D t=Resources.Load<Texture2D>(path);
            if(t==null)throw new InvalidOperationException("Missing asset: "+path);
            t.filterMode=FilterMode.Point;
            return Sprite.Create(t,new Rect(0,0,t.width,t.height),Vector2.one*.5f,64);
        }
        void PlaySound(string name)
        {
            if(!Model.muted && sounds.TryGetValue(name,out AudioClip sound) && sound!=null)speaker.PlayOneShot(sound,name=="land"?.28f:.8f);
        }
        void Update()
        {
            if(smoke && Time.realtimeSinceStartup < smokeStart){DrawWorld();return;}
            if(Input.GetKeyDown(KeyCode.Escape))TogglePause();
            if(Input.GetKeyDown(KeyCode.M))Model.muted=!Model.muted;
            if(Input.GetKeyDown(KeyCode.F11))Screen.fullScreen=!Screen.fullScreen;
            if(Model.paused) { ClearPending(); return; }
            if(!smoke)
            {
                if(Model.phase==Phase.Title && (Input.GetKeyDown(KeyCode.Return)||Input.GetKeyDown(KeyCode.Space))){Model.Start();ClearPending();DrawWorld();return;}
                else if(Model.phase==Phase.Dead && Input.GetKeyDown(KeyCode.Return))Model.Retry();
                else if(Model.phase==Phase.Ending && Input.GetKeyDown(KeyCode.Return))Restart();
                jumpPending |= Input.GetKeyDown(KeyCode.Space)||Input.GetKeyDown(KeyCode.UpArrow);
                dashPending |= Input.GetKeyDown(KeyCode.LeftShift)||Input.GetKeyDown(KeyCode.RightShift);
                attackPending |= Input.GetKeyDown(KeyCode.J);
                interactPending |= Input.GetKeyDown(KeyCode.E);
            }
            int horizontal=(Input.GetKey(KeyCode.RightArrow)||Input.GetKey(KeyCode.D)?1:0)-(Input.GetKey(KeyCode.LeftArrow)||Input.GetKey(KeyCode.A)?1:0);
            accumulator+=Mathf.Min(Time.unscaledDeltaTime,.1f);
            const float tick=1f/120;
            while(accumulator>=tick)
            {
                Model.Tick(tick,smoke?pilot.Next(Model):new Command{axis=horizontal,jump=jumpPending,dash=dashPending,attack=attackPending,interact=interactPending});
                ClearPending();accumulator-=tick;
            }
            DrawWorld();
        }
        void ClearPending(){jumpPending=dashPending=attackPending=interactPending=false;}
        void TogglePause(){if(Model.phase==Phase.Title||Model.phase==Phase.Ending)return;Model.paused=!Model.paused;ClearPending();accumulator=0;}
        void OnApplicationFocus(bool focused)
        {
            if(smoke||Model==null)return;
            if(!focused&&Model.CanMove){Model.paused=true;focusPause=true;ClearPending();}
        }
        void Restart(){Model=new ReturnModel();Model.Sound=PlaySound;ClearPending();accumulator=0;}
        void Draw(string id,Sprite sprite,float x,float y,float w,float h,int layer,Color? color=null,bool flip=false)
        {
            w=Mathf.Max(1,Mathf.Round(w));h=Mathf.Max(1,Mathf.Round(h));
            if(!visible.TryGetValue(id,out SpriteRenderer r))
            {
                var go=new GameObject(id);go.transform.SetParent(transform);r=go.AddComponent<SpriteRenderer>();visible[id]=r;
            }
            r.enabled=true;r.sprite=sprite;r.sortingOrder=layer;r.color=color??Color.white;r.flipX=flip;
            r.transform.position=new Vector3((Mathf.Round(x)+w*.5f)/64,(360-Mathf.Round(y)-h*.5f)/64,0);
            r.transform.localScale=new Vector3(w/sprite.rect.width,h/sprite.rect.height,1);
        }
        void Prop(string id,string sprite,float x,float y,int layer=4,Color? color=null)
        {var s=art[sprite];Draw(id,s,x,y,s.rect.width,s.rect.height,layer,color);}
        void Bar(string id,float x,float y,float w,float h,Color c,int layer=3){Draw(id,pixel,x,y,w,h,layer,c);}
        void DrawWorld()
        {
            foreach(var r in visible.Values)r.enabled=false;
            var m=Model;
            Draw("background",art[m.Inspection?"inspection":"limbus"],0,0,640,360,0);
            // The top of this strip is the actual floor collision line.
            Bar("floor-cap",0,252,640,2,new Color(.55f,.51f,.39f));
            if(!m.Inspection)
            {
                for(int n=0;n<m.platforms.Count;n++)
                {
                    Platform p=m.platforms[n];Draw("platform"+n,art["platform"],p.x,p.y,p.width,8,3);
                }
                Bar("supply-horizontal",150,186,444,3,m.magnetOn?new Color(.15f,.22f,.24f):cyan,1);
                Bar("supply-vertical",150,186,3,38,cyan,1);
                Bar("magnet-cable",308,95,3,94,m.magnetOn?cyan:new Color(.18f,.24f,.25f),1);
                Bar("rail",326,91,173,7,new Color(.4f,.44f,.41f),2);
                for(int n=0;n<12;n++)Bar("rail-notch"+n,328+n*14,94,6,2,gold,3);
                Bar("hanger",m.magnetX-3,97,6,17,gold);
                Prop("magnet","magnet",m.magnetX-20,111);
                if(m.magnetOn)
                    for(int n=0;n<3;n++)Bar("magnet-ray"+n,m.magnetX-12+n*12,145,1,Mathf.Max(3,m.crateBottom-145),new Color(.4f,.85f,.8f,.4f),2);
                Prop("weight","weight",m.crateX-16,m.crateBottom-30,4);
                Prop("plate","pressure",441,248,3,m.PlateDown?cyan:Color.white);
                Prop("power","console",134,208);
                Prop("handle","rail-handle",241,224);
                if(!m.practiceDone)Prop("practice","practice",508,220);
                else Bar("practice-solved",520,238,16,6,cyan);
                float gateY=m.gateOpen?75:140;
                Prop("gate","gate",578,gateY,4);
                Bar("gate-power",578,129,27,6,!m.magnetOn?cyan:dim);
                Bar("gate-weight",609,129,27,6,m.PlateDown?cyan:dim);
            }
            else
            {
                Prop("boss","guardian",496,92,3);
                bool healthy=m.phase==Phase.Exit||m.phase==Phase.Ending;
                if(healthy){Bar("eye-l",540,123,14,7,cyan,5);Bar("eye-r",569,123,14,7,cyan,5);}
                Bar("arm-rail",76,83,482,6,new Color(.25f,.31f,.32f),2);
                for(int n=0;n<Mathf.Max(1,Mathf.CeilToInt((m.fistBottom-125)/20));n++)
                    Prop("arm"+n,"arm-link",m.fistX-9,88+n*20,2);
                Prop("fist","fist",m.fistX-27,m.fistBottom-54,4,m.WeakOpen?Color.white:new Color(.77f,.79f,.77f));
                Prop("trap","pressure",208,248,3,m.arenaMagnet?cyan:Color.white);
                Prop("trap-console","console",88,208);
                Prop("rescan","console",462,208,4,m.phase==Phase.Rescan?cyan:Color.white);
                if(m.arenaMagnet)
                    for(int n=0;n<3;n++)Bar("trap-ray"+n,222+n*12,220,1,29,new Color(.4f,.85f,.8f,.45f),2);
                if(m.bossMove==BossMove.Aim||m.bossMove==BossMove.Slam)
                {
                    Bar("target",m.aimX-30,249,60,3,red,6);
                    Bar("aim-left",m.aimX-30,240,2,9,red,6);Bar("aim-right",m.aimX+28,240,2,9,red,6);
                }
                if(m.bossMove==BossMove.WaveCharge)Bar("wave-warning",20,250,475,2,new Color(.91f,.38f,.32f,.45f+.4f*Mathf.Sin(m.clock*14)),5);
                if(m.waveX>-30)
                {
                    Bar("wave-base",m.waveX-12,244,24,7,red,5);Bar("wave-core",m.waveX-6,240,12,9,gold,6);
                }
                if(m.WeakOpen)Bar("weak-terminal",m.fistX-7,m.fistBottom-31,14,9,m.flash>0?ink:red,6);
                if(m.phase==Phase.Exit||m.phase==Phase.Ending)Bar("exit-light",605,160,15,91,new Color(.75f,.96f,.89f,.35f),1);
            }
            string clip=m.Pose(durations,out int frame);
            Color color=m.invincible>0 && m.phase==Phase.Combat && Mathf.Sin(m.clock*24)>0?new Color(1,1,1,.35f):Color.white;
            Bar("shadow",m.x-10,m.y-1,20,2,new Color(0,0,0,.55f),4);
            Draw("Tique",animation[clip][frame],m.x-32,m.y-56,64,64,8,color,m.facing<0);
            if(m.flash>0&&m.WeakOpen)
            {
                Bar("spark-h",m.fistX-15,m.fistBottom-29,30,2,gold,10);Bar("spark-v",m.fistX,m.fistBottom-38,2,22,ink,10);
            }
        }
        void SetupStyles()
        {
            if(label!=null)return;
            label=new GUIStyle(GUI.skin.label){font=korean,fontSize=22,wordWrap=true};label.normal.textColor=ink;
            large=new GUIStyle(label){fontSize=54,fontStyle=FontStyle.Bold};
            small=new GUIStyle(label){fontSize=18};small.normal.textColor=dim;
            button=new GUIStyle(GUI.skin.button){font=korean,fontSize=22,padding=new RectOffset(16,16,10,10)};
            button.normal.textColor=ink;button.hover.textColor=cyan;button.focused.textColor=cyan;
        }
        void Panel(Rect rect,Color? color=null){GUI.color=color??panel;GUI.DrawTexture(rect,Texture2D.whiteTexture);GUI.color=Color.white;}
        void Text(Rect rect,string text,GUIStyle style=null,Color? color=null)
        {GUI.color=color??Color.white;GUI.Label(rect,text,style??label);GUI.color=Color.white;}
        bool Button(Rect rect,string text){return GUI.Button(rect,text,button);}
        void OnGUI()
        {
            if(Model==null||target==null)return;
            SetupStyles();
            float s=Mathf.Min(Screen.width/1280f,Screen.height/720f);
            GUI.matrix=Matrix4x4.TRS(new Vector3((Screen.width-1280*s)/2,(Screen.height-720*s)/2,0),Quaternion.identity,new Vector3(s,s,1));
            GUI.DrawTexture(new Rect(0,0,1280,720),target,ScaleMode.StretchToFill,false);
            var m=Model;
            if(m.phase==Phase.Title)
            {
                Panel(new Rect(0,0,1280,720),new Color(.025f,.055f,.065f,.80f));
                Text(new Rect(104,132,900,80),"티크: 귀환",large);
                Text(new Rect(108,229,760,80),"고철로 분류된 작은 로봇.\n문 너머, 돌아갈 곳을 찾아서.");
                Text(new Rect(108,340,850,55),"전자석 퍼즐을 풀고, 출구를 지키는 문지기를 통과하세요.",small);
                if(Button(new Rect(108,424,300,62),"귀환 경로 찾기  ·  Enter"))m.Start();
                Text(new Rect(108,518,1020,36),"← → 이동    Space 점프    E 조작    Shift 대시    J 공격",small);
                Text(new Rect(108,627,1000,30),"CLOCKWORK  /  졸업작품 프로토타입    ·    F11 전체화면    M 소리",small);
                return;
            }
            string title=m.Inspection?"02  출구 검사실":"01  폐기장 동력실";
            Panel(new Rect(22,18,1236,76));Text(new Rect(44,29,320,31),title);
            string objective=m.phase==Phase.Puzzle?(m.gateOpen?"열린 문을 지나 검사실로 이동":"문 동력과 추의 무게, 두 조건을 연결하세요"):
                m.phase==Phase.Rescan?"과부하 해제 · 오른쪽 단말에서 재검사":m.phase==Phase.Exit?"폐기 판정 취소 · 오른쪽 출구로":m.phase==Phase.Arrival?"문지기 기동 중…":"팔을 피하고, 내려온 붉은 단자를 공격하세요";
            Text(new Rect(44,62,960,24),objective,small);
            if(m.phase==Phase.Combat||m.phase==Phase.Dead||m.phase==Phase.Arrival)
            {
                for(int i=0;i<4;i++)Panel(new Rect(865+i*27,37,20,18),i<m.hp?cyan:new Color(.18f,.25f,.27f));
                Text(new Rect(998,28,140,26),"과부하",small);
                for(int i=0;i<6;i++)Panel(new Rect(1000+i*34,59,27,9),i<m.overload?red:new Color(.18f,.25f,.27f));
            }
            Panel(new Rect(0,651,1280,69));
            Text(new Rect(30,670,1060,30),"← → 이동    Space / ↑ 점프·더블점프    E 조작    Shift 대시    J 공격",small);
            if(Button(new Rect(1130,661,124,42),"일시정지"))TogglePause();
            if(m.messageLeft>0)
            {
                Panel(new Rect(100,559,1080,65));Text(new Rect(120,574,1040,42),m.message);
            }
            string prompt=m.Interaction();
            if(!string.IsNullOrEmpty(prompt)&&m.CanMove)
            {
                float px=Mathf.Clamp(m.x*2-150,24,940);
                Panel(new Rect(px,343,320,44));Text(new Rect(px+12,350,304,32),prompt,small);
            }
            if(m.phase==Phase.Puzzle)
            {
                Text(new Rect(260,517,145,26),"동력 분배기",small);
                Text(new Rect(450,517,130,26),"레일 핸들",small);
                Text(new Rect(842,517,160,26),"추 압력판",small);
                if(m.noProgress>25&&!m.gateOpen && m.messageLeft<=0)
                    Text(new Rect(120,576,1040,40),m.noProgress>45?"추를 옮긴 다음, 전원을 끊어 압력판에 내려놓아 보세요.":"문 옆의 두 표시를 확인하세요. 추는 자석이 옮길 수 있어요.",label,gold);
                if(Mathf.Abs(m.x-528)<48&&!m.practiceDone)Text(new Rect(940,393,210,55),"J  붉은 단자 타격",small,gold);
            }
            if(m.phase==Phase.Rescan)Text(new Rect(881,378,320,40),"E  재검사",label,cyan);
            if(m.phase==Phase.Dead)
            {
                Panel(new Rect(0,0,1280,720),new Color(.035f,.05f,.06f,.85f));
                Text(new Rect(374,184,740,80),"다시 움직일 수 있어.",new GUIStyle(large){fontSize=42});
                Text(new Rect(375,279,700,70),"퍼즐은 그대로 두고, 문지기 앞에서 다시 시작합니다.");
                if(Button(new Rect(376,378,520,62),"검사실에서 다시 시작  ·  Enter"))m.Retry();
                if(m.deaths>=2&&Button(new Rect(376,460,520,55),m.helpMode?"도움 적용됨 · 예고와 반격 시간 확대":"도움 받기 · 예고와 반격 시간 확대"))m.helpMode=true;
            }
            else if(m.phase==Phase.Ending)
            {
                Panel(new Rect(0,0,1280,720),new Color(.025f,.065f,.075f,.90f));
                Text(new Rect(222,140,900,90),"귀환을 시작합니다.",large);
                Text(new Rect(228,252,870,55),"식별명: 티크.   귀환처: 엘리아스 공방.",label,cyan);
                Text(new Rect(228,316,890,90),"폐기 판정 취소.\n통과를 허가합니다, 티크.");
                Text(new Rect(228,430,870,40),"플레이 시간  "+TimeSpan.FromSeconds(m.playTime).ToString(@"mm\:ss")+"   ·   문 너머의 여행은 계속됩니다.",small);
                if(Button(new Rect(228,504,350,62),"처음부터 다시  ·  Enter"))Restart();
                if(Button(new Rect(602,504,200,62),"종료"))Application.Quit();
            }
            if(m.paused)
            {
                Panel(new Rect(0,0,1280,720),new Color(.025f,.055f,.065f,.92f));
                Text(new Rect(420,153,800,76),"잠시 멈췄어요.",new GUIStyle(large){fontSize=44});
                if(focusPause)Text(new Rect(420,235,700,42),"창을 전환하면 자동으로 일시정지합니다.",small);
                if(Button(new Rect(420,312,440,60),"계속 플레이  ·  Esc")){m.paused=false;focusPause=false;}
                if(Button(new Rect(420,389,440,52),m.muted?"소리 켜기":"소리 끄기"))m.muted=!m.muted;
                if(Button(new Rect(420,458,440,52),"처음부터 다시"))Restart();
                if(Button(new Rect(420,527,440,52),"종료"))Application.Quit();
            }
        }
        void OnDestroy()
        {
            if(target!=null){target.Release();Destroy(target);}
        }

        // Packaged-player integration check. Uses ordinary command inputs, no invulnerability or teleport.
        IEnumerator SmokePlaythrough()
        {
            string[] args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"--qa-dir");
            string folder=n>=0&&n+1<args.Length?args[n+1]:Path.Combine(Application.persistentDataPath,"ReturnQA");
            Directory.CreateDirectory(folder);
            yield return Capture(folder,"01-title");
            float deadline=Time.realtimeSinceStartup+180;
            bool carry=false,gate=false,arrival=false,captured=false,hit=false;
            while(Model.phase!=Phase.Ending&&Model.phase!=Phase.Dead&&Time.realtimeSinceStartup<deadline)
            {
                if(!carry&&Model.attached&&Model.crateX>465){carry=true;yield return Capture(folder,"02-magnet-carry");}
                if(!gate&&Model.gateOpen){gate=true;yield return Capture(folder,"03-puzzle-open");}
                if(!arrival&&Model.phase==Phase.Arrival){arrival=true;yield return Capture(folder,"04-guardian");}
                if(!captured&&Model.captured){captured=true;yield return Capture(folder,"05-magnet-trap");}
                if(!hit&&Model.overload<6){hit=true;yield return Capture(folder,"06-hit");}
                yield return null;
            }
            if(Model.phase!=Phase.Ending){yield return Capture(folder,"failure");SmokeFail(folder,"Playthrough ended in "+Model.phase);yield break;}
            yield return Capture(folder,"07-ending");
            bool pass=Model.hp==4&&captured&&Model.practiceDone;
            File.WriteAllText(Path.Combine(folder,"runtime-result.json"),"{\"passed\":"+pass.ToString().ToLowerInvariant()+",\"phase\":\""+Model.phase+"\",\"health\":"+Model.hp+",\"magnetCaptured\":"+captured.ToString().ToLowerInvariant()+"}");
            File.WriteAllLines(Path.Combine(folder,"events.txt"),Model.events);Debug.Log("RETURN_SMOKE "+(pass?"PASS":"FAIL"));
            Application.Quit(pass?0:2);
        }
        IEnumerator Capture(string folder,string name)
        {
            yield return new WaitForEndOfFrame();
            var texture=ScreenCapture.CaptureScreenshotAsTexture();
            File.WriteAllBytes(Path.Combine(folder,name+".png"),texture.EncodeToPNG());Destroy(texture);
        }
        void SmokeFail(string folder,string error)
        {
            File.WriteAllText(Path.Combine(folder,"runtime-result.json"),"{\"passed\":false,\"reason\":\""+error+"\"}");
            File.WriteAllLines(Path.Combine(folder,"events.txt"),Model.events);Debug.LogError("RETURN_SMOKE "+error);Application.Quit(2);
        }
    }
}
