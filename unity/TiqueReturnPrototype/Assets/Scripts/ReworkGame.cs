using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed partial class ReworkGame : MonoBehaviour
    {
        public ReworkModel Model {get;private set;}
        PuzzleBook book;
        string tiqueResourceRoot,readabilityResourceRoot,wardenResourceRoot;
        readonly Dictionary<string,Sprite> art=new Dictionary<string,Sprite>();
        readonly Dictionary<string,Sprite[]> animations=new Dictionary<string,Sprite[]>();
        readonly Dictionary<string,int[]> durations=new Dictionary<string,int[]>();
        readonly Dictionary<string,SpriteRenderer> pool=new Dictionary<string,SpriteRenderer>();
        readonly Dictionary<string,AudioClip> audio=new Dictionary<string,AudioClip>();
        Camera cameraWorld;RenderTexture target;Sprite pixel;AudioSource speaker;
        float accumulator,keyRepeat;int heldDirection=-1;
        ReworkCommand pending=ReworkCommand.Empty;
        bool smoke,tiqueReview,readabilityReview,offscreenCapture,releaseGate,readabilityArt;int inputEpoch,manualShot;float smokeStart;readonly ReworkPilot pilot=new ReworkPilot();
        readonly HashSet<string> screenshots=new HashSet<string>();
        readonly HashSet<string> seenArtStates=new HashSet<string>();
        readonly Color cyan=new Color(.39f,.89f,.87f),gold=new Color(.95f,.73f,.36f),red=new Color(1,.36f,.28f);
        readonly Color ink=new Color(.91f,.95f,.95f),dim=new Color(.60f,.70f,.75f),panel=new Color(.026f,.05f,.075f,.95f);
        void Awake()
        {
            Application.targetFrameRate=60;QualitySettings.vSyncCount=0;QualitySettings.antiAliasing=0;Application.runInBackground=true;
            smoke=Array.IndexOf(Environment.GetCommandLineArgs(),"--return-v2-smoke")>=0;smokeStart=Time.realtimeSinceStartup+1.2f;
            tiqueReview=Array.IndexOf(Environment.GetCommandLineArgs(),"--return-tique-review")>=0;
            readabilityReview=Array.IndexOf(Environment.GetCommandLineArgs(),"--return-readability-review")>=0;
            uiReview=Array.IndexOf(Environment.GetCommandLineArgs(),"--return-ui-review")>=0;
            offscreenCapture=(smoke||tiqueReview||readabilityReview)&&Array.IndexOf(Environment.GetCommandLineArgs(),"--return-offscreen-capture")>=0;
            book=JsonUtility.FromJson<PuzzleBook>(Resources.Load<TextAsset>("ReturnV2/puzzles").text);Restart();
            // Explicit QA fixture, never used by Play.cmd or the normal title.
            // Physical key probes can reach the existing safe guide without
            // confusing them with the input-only full-flow smoke pilot.
            if(Array.IndexOf(Environment.GetCommandLineArgs(),"--return-input-check")>=0){Model.BeginArena();Model.age=2.4f;}
            var tiqueAsset=Resources.Load<TextAsset>("ReturnV2/TiqueV10/clips");
            string tiqueRoot="ReturnV2/TiqueV10/";
            if(tiqueAsset==null){tiqueAsset=Resources.Load<TextAsset>("ReturnV2/TiqueV9/clips");tiqueRoot="ReturnV2/TiqueV9/";}
            if(tiqueAsset==null){tiqueAsset=Resources.Load<TextAsset>("ReturnV2/TiqueV8/clips");tiqueRoot=tiqueAsset!=null?"ReturnV2/TiqueV8/":"Return/Tique/";}
            tiqueResourceRoot=tiqueRoot;
            var clips=JsonUtility.FromJson<ClipFile>((tiqueAsset??Resources.Load<TextAsset>("Return/clips")).text);
            Debug.Log("TIQUE_ART_ROOT "+tiqueResourceRoot+" clips="+clips.clips.Length);
            foreach(var c in clips.clips)
            {
                string key=char.IsUpper(c.name[0])?c.name:"fx-"+c.name;
                durations[key]=c.durations;Sprite[] frames=new Sprite[c.durations.Length];
                for(int i=0;i<frames.Length;i++)frames[i]=Load(tiqueRoot+c.name+"/"+i.ToString("00"));animations[key]=frames;
            }
            foreach(string name in new[]{"floor","wall"})art[name]=Load("ReturnV2/Art/"+name);
            // v8 corrects selected poses; earlier guardian art stays preserved.
            wardenResourceRoot="ReturnV2/WardenV8/";
            var wardenAsset=Resources.Load<TextAsset>(wardenResourceRoot+"clips");
            if(wardenAsset==null){wardenResourceRoot="ReturnV2/WardenV7/";wardenAsset=Resources.Load<TextAsset>(wardenResourceRoot+"clips");}
            var warden=JsonUtility.FromJson<ClipFile>(wardenAsset.text);
            Debug.Log("WARDEN_ART_ROOT "+wardenResourceRoot+" clips="+warden.clips.Length);
            foreach(var clip in warden.clips)
            {
                var frames=new Sprite[clip.durations.Length];durations["iron-"+clip.name]=clip.durations;
                for(int i=0;i<frames.Length;i++)frames[i]=Load(wardenResourceRoot+clip.name+"/"+i.ToString("00"));
                animations["iron-"+clip.name]=frames;
            }
            var states=JsonUtility.FromJson<ClipFile>(Resources.Load<TextAsset>("ReturnV2/StateArt/clips").text);
            foreach(var clip in states.clips)
            {
                var frames=new Sprite[clip.durations.Length];durations["state-"+clip.name]=clip.durations;
                for(int i=0;i<frames.Length;i++)frames[i]=Load("ReturnV2/StateArt/"+clip.name+"/"+i.ToString("00"));
                animations["state-"+clip.name]=frames;
            }
            // Image-first v2 overrides matching puzzle props only. The older
            // readability prototype remains a fallback and a preserved comparison.
            readabilityResourceRoot="ReturnV2/ReadabilityArtV2/";
            var readable=Resources.Load<TextAsset>(readabilityResourceRoot+"clips");
            if(readable==null)
            {
                readabilityResourceRoot="ReturnV2/ReadabilityArt/";
                readable=Resources.Load<TextAsset>(readabilityResourceRoot+"clips");
            }
            if(readable!=null)
            {
                foreach(var clip in JsonUtility.FromJson<ClipFile>(readable.text).clips)
                {
                    string key="state-"+clip.name;var frames=new Sprite[clip.durations.Length];durations[key]=clip.durations;
                    for(int i=0;i<frames.Length;i++)frames[i]=Load(readabilityResourceRoot+clip.name+"/"+i.ToString("00"));
                    animations[key]=frames;
                }
                readabilityArt=true;Debug.Log("PUZZLE_ART_ROOT "+readabilityResourceRoot);
            }
            var feedbackClips=JsonUtility.FromJson<ClipFile>(Resources.Load<TextAsset>("ReturnV2/Feedback/clips").text);
            foreach(var c in feedbackClips.clips){string key="fx-"+c.name;if(animations.ContainsKey(key))continue;durations[key]=c.durations;var f=new Sprite[c.durations.Length];for(int i=0;i<f.Length;i++)f[i]=Load("ReturnV2/Feedback/"+c.name+"/"+i.ToString("00"));animations[key]=f;}
            foreach(string name in new[]{"jump","dash","land","hit","hurt","success","switch","warning"})audio[name]=Resources.Load<AudioClip>("Return/Audio/"+name);
            var tex=new Texture2D(1,1);tex.SetPixel(0,0,Color.white);tex.Apply();pixel=Sprite.Create(tex,new Rect(0,0,1,1),Vector2.one*.5f,64);
            var cam=new GameObject("640 x 360 Pixel Camera");cam.transform.SetParent(transform);cameraWorld=cam.AddComponent<Camera>();cam.AddComponent<AudioListener>();
            cameraWorld.orthographic=true;cameraWorld.orthographicSize=180f/64;cameraWorld.transform.position=new Vector3(5,180f/64,-10);
            cameraWorld.backgroundColor=Color.black;cameraWorld.clearFlags=CameraClearFlags.SolidColor;
            target=new RenderTexture(640,360,16,RenderTextureFormat.ARGB32){filterMode=FilterMode.Point};target.Create();cameraWorld.targetTexture=target;
            var presentation=new GameObject("Display");presentation.transform.SetParent(transform);var display=presentation.AddComponent<Camera>();
            display.cullingMask=0;display.depth=1;display.clearFlags=CameraClearFlags.SolidColor;display.backgroundColor=Color.black;
            speaker=gameObject.AddComponent<AudioSource>();speaker.playOnAwake=false;speaker.volume=.3f;
            LoadPixelUi();
            DrawWorld();if(uiReview)StartCoroutine(ReviewCompactUi());else if(smoke)StartCoroutine(Smoke());else if(tiqueReview)StartCoroutine(ReviewTique());else if(readabilityReview)StartCoroutine(ReviewReadability());
        }
        Sprite Load(string path)
        {
            var t=Resources.Load<Texture2D>(path);if(t==null)throw new InvalidOperationException("Missing V2 art: "+path);
            t.filterMode=FilterMode.Point;return Sprite.Create(t,new Rect(0,0,t.width,t.height),Vector2.one*.5f,64);
        }
        void Restart(){Model=new ReworkModel(book);Model.Sound=Sound;ResetPuzzleGuide();FlushInput();inputEpoch=Model.inputEpoch;}
        void Sound(string name){if(!Model.muted&&speaker!=null&&audio.TryGetValue(name,out var clip))speaker.PlayOneShot(clip,name=="land"?.2f:.8f);}
        bool Down(KeyCode a,KeyCode b)=>Input.GetKeyDown(a)||Input.GetKeyDown(b);
        void Update()
        {
            if(uiReview||tiqueReview||readabilityReview){DrawWorld();return;}
            if(smoke&&Time.realtimeSinceStartup<smokeStart){DrawWorld();return;}
            if(Screen.width<640||Screen.height<360)Screen.SetResolution(Math.Max(640,Screen.width),Math.Max(360,Screen.height),false);
            if(Input.GetKeyDown(KeyCode.F11))Screen.fullScreen=!Screen.fullScreen;
            if(Input.GetKeyDown(KeyCode.M))Model.muted=!Model.muted;
            if(Input.GetKeyDown(KeyCode.Escape)){Model.paused=!Model.paused;FlushInput();inputEpoch=Model.inputEpoch;}
            if(!smoke&&HandleMenuKeys()){DrawWorld();return;}
            if(Model.paused)return;
            if(!smoke)
            {
                pending.interact|=Model.phase==Journey.Opening||Model.phase==Journey.Arrival||Model.phase==Journey.RoomClear?Input.GetKeyDown(KeyCode.Return):Input.GetKeyDown(KeyCode.E);
                pending.undo|=Down(KeyCode.Z,KeyCode.Backspace);pending.restart|=Input.GetKeyDown(KeyCode.R);
                pending.jump|=Down(KeyCode.Space,KeyCode.UpArrow)||Input.GetKeyDown(KeyCode.Z);pending.dash|=Input.GetKeyDown(KeyCode.C);pending.attack|=Input.GetKeyDown(KeyCode.X);
                pending.axis=(Input.GetKey(KeyCode.RightArrow)?1:0)-(Input.GetKey(KeyCode.LeftArrow)?1:0);
                int dir=-1;
                if(Input.GetKey(KeyCode.LeftArrow)||Input.GetKey(KeyCode.A))dir=0;
                if(Input.GetKey(KeyCode.RightArrow)||Input.GetKey(KeyCode.D))dir=1;
                if(Input.GetKey(KeyCode.UpArrow)||Input.GetKey(KeyCode.W))dir=2;
                if(Input.GetKey(KeyCode.DownArrow)||Input.GetKey(KeyCode.S))dir=3;
                keyRepeat-=Time.unscaledDeltaTime;
                if(dir>=0&&(dir!=heldDirection||keyRepeat<=0)){pending.grid=dir;keyRepeat=dir!=heldDirection?.23f:.16f;}
                heldDirection=dir;
            }
            if(!smoke&&releaseGate)
            {
                bool held=Input.GetKey(KeyCode.Return)||Input.GetKey(KeyCode.E)||Input.GetKey(KeyCode.X)||Input.GetKey(KeyCode.C)||Input.GetKey(KeyCode.Z)||Input.GetKey(KeyCode.Space)||Input.GetKey(KeyCode.LeftArrow)||Input.GetKey(KeyCode.RightArrow)||Input.GetKey(KeyCode.UpArrow)||Input.GetKey(KeyCode.DownArrow);
                pending=ReworkCommand.Empty;heldDirection=-1;if(!held)releaseGate=false;
            }
            accumulator+=Mathf.Min(.1f,Time.unscaledDeltaTime);
            while(accumulator>=1f/120)
            {
                int axis=pending.axis;var command=smoke?pilot.Next(Model):pending;
                Model.Tick(1f/120,command);guidance.Observe(Model,command,smoke?command.grid:heldDirection);
                pending=ReworkCommand.Empty;pending.axis=axis;accumulator-=1f/120;
                if(inputEpoch!=Model.inputEpoch){inputEpoch=Model.inputEpoch;FlushInput();break;}
            }
            DrawWorld();
        }
        void OnApplicationFocus(bool focus){if(!focus&&!uiReview&&!smoke&&!tiqueReview&&!readabilityReview&&Model!=null&&Model.phase!=Journey.Title){Model.paused=true;FlushInput();inputEpoch=Model.inputEpoch;}}
        void Draw(string id,Sprite sprite,float x,float y,int layer,Color? tint=null,bool flip=false,float width=0,float height=0)
        {
            if(!pool.TryGetValue(id,out var r)){var go=new GameObject(id);go.transform.SetParent(transform);r=go.AddComponent<SpriteRenderer>();pool[id]=r;}
            float w=width>0?width:sprite.rect.width,h=height>0?height:sprite.rect.height;
            r.enabled=true;r.sprite=sprite;r.sortingOrder=layer;r.color=tint??Color.white;r.flipX=flip;
            r.transform.position=new Vector3((Mathf.Round(x)+w*.5f)/64,(360-Mathf.Round(y)-h*.5f)/64,0);
            r.transform.localScale=new Vector3(w/sprite.rect.width,h/sprite.rect.height,1);
        }
        void Prop(string id,string sprite,float x,float y,int layer=4,Color? tint=null){Draw(id,art[sprite],x,y,layer,tint);}
        void StateProp(string id,string state,float age,float x,float y,int layer=4,bool loop=false,bool flip=false)
        {
            if(smoke)seenArtStates.Add(state);
            string key="state-"+state;int frame=WardenAnimation.FrameAt(durations[key],age,loop:loop);
            Draw(id,animations[key][frame],x,y,layer,Color.white,flip);
        }
        void Bar(string id,float x,float y,float w,float h,Color color,int layer=3){Draw(id,pixel,x,y,layer,color,false,Mathf.Max(1,w),Mathf.Max(1,h));}
        void Tique(float x,float y,string clip,int frame,int layer=1000,bool flip=false)
        {
            if(TiqueAnimation.ShouldBlinkBody(Model))return;
            Color color=Color.white;
            Draw("tique",animations[clip][frame],x-32,y-56,layer,color,flip);
        }
        void DrawWorld()
        {
            foreach(var r in pool.Values)r.enabled=false;var m=Model;
            StateProp("bg",m.InArena?(m.phase==Journey.Restored||m.phase==Journey.Ending?"arena-restored":"arena-dark"):
                "workshop-power-"+WorldArtState.WorkshopPower(m),0,0,0,0);
            cameraWorld.transform.position=new Vector3((320+(m.shake>0&&!m.reducedEffects?Mathf.Round(Mathf.Sin(m.clock*90)*2):0))/64,180f/64,-10);
            if(m.phase==Journey.Title)
            {
                // Reuse the approved workshop and idle hero; do not put a live
                // puzzle board behind a menu that has not started the journey.
                Tique(94,288,"Idle",WardenAnimation.FrameAt(durations["Idle"],m.clock,loop:true),20);return;
            }
            if(!m.InArena)
            {
                const float bx=194,by=64,cell=36;
                var p=m.puzzle;float duration=p.motionDuration;
                float t=1-Mathf.Clamp01(p.motion/duration);t=t*t*(3-2*t);
                for(int pos=0;pos<49;pos++)
                {
                    float x=bx+pos%7*cell,y=by+pos/7*cell;
                    if(readabilityArt)StateProp("tile"+pos,p.Wall(pos)?"wall-"+WorldArtState.WallMask(p,pos).ToString("00"):"floor",0,x,y,p.Wall(pos)?10+pos/7*20:1);
                    else Prop("tile"+pos,p.Wall(pos)?"wall":"floor",x,y,p.Wall(pos)?10+pos/7*20:1,p.Wall(pos)?new Color(.5f,.62f,.72f):new Color(.62f,.69f,.76f));
                }
                for(int i=0;i<p.room.goals.Length;i++)
                {
                    int pos=p.room.goals[i];string socket=WorldArtState.Socket(p,i,out float socketAge);
                    StateProp("goal"+i,socket,socketAge,bx+pos%7*cell,by+pos/7*cell,2);
                }
                for(int i=0;i<p.boxes.Length;i++)
                {
                    float x=Mathf.Lerp(p.previousBoxes[i]%7,p.boxes[i]%7,t),y=Mathf.Lerp(p.previousBoxes[i]/7,p.boxes[i]/7,t);
                    bool orb=p.room.types[i]==1;string box=WorldArtState.Box(p,i,out float boxAge);
                    StateProp("box"+i,box,boxAge,bx+x*cell+(orb?5:3),by+y*cell+(orb?6:0),15+Mathf.RoundToInt(y*20),true);
                }
                // Brief physical travel trail, never a solver/goal preview.
                if(readabilityArt&&p.motion>0&&p.lastPushedBox>=0&&p.room.types[p.lastPushedBox]==1)
                {
                    int b=p.lastPushedBox,from=p.previousBoxes[b],end=p.boxes[b];int travelled=Mathf.Max(Mathf.Abs(end%7-from%7),Mathf.Abs(end/7-from/7));
                    int exposed=Mathf.FloorToInt(travelled*t);
                    for(int j=1;j<=exposed;j++)
                    {float x=bx+(from%7+OpeningSequence.DirectionX(p.lastDirection)*j)*cell+18,y=by+(from/7+OpeningSequence.DirectionY(p.lastDirection)*j)*cell+31;
                        Bar("orb-path"+j,x-1,y,3,1,new Color(.19f,.38f,.40f),3);}
                }
                float ht=Mathf.Clamp01(p.visualAge/.15f);ht=ht*ht*(3-2*ht);
                float px=Mathf.Lerp(p.previousPlayer%7,p.player%7,ht),py=Mathf.Lerp(p.previousPlayer/7,p.player/7,ht);
                float footX=OpeningSequence.FootX(px),footY=OpeningSequence.FootY(py);
                string clip="Idle";int frame=WardenAnimation.FrameAt(durations[clip],m.clock,loop:true);
                if(p.visualAge<.15f){clip="Walk";frame=WardenAnimation.FrameAt(durations[clip],p.walkAge,loop:true);}
                if(p.lastPushedBox>=0&&p.visualAge<.15f){clip="fx-push-"+(p.lastDirection==2?"up":p.lastDirection==3?"down":"side");frame=WardenAnimation.FrameAt(durations[clip],p.walkAge,loop:true);}
                if(p.blockedAge<.12f&&Array.IndexOf(p.boxes,CorePuzzle.Next(p.player,p.lastDirection))>=0){clip="fx-push-brace-"+(p.lastDirection==2?"up":p.lastDirection==3?"down":"side");frame=0;}
                if(m.phase==Journey.Opening)
                {
                    StateFeedback("chute",0,footX-24,0,3);
                    Bar("opening-shadow",footX-9,footY,18,2,new Color(.06f,.1f,.12f),2);
                    footY+=OpeningSequence.DropOffset(m.age,footY);int jump=OpeningSequence.LandingFrame(m.age);
                    if(jump>=0){clip="Jump";frame=jump;}else if(m.age>=3.4f&&m.age<3.66f){clip=m.age<3.48f||m.age>=3.58f?"fx-blink-half":"fx-blink-closed";frame=0;}
                }
                else if(p.motion<=0&&p.blockedAge>.12f&&(m.clock%5.5f)<.26f&&p.moves>0){clip=m.clock%5.5f<.08f||m.clock%5.5f>=.18f?"fx-blink-half":"fx-blink-closed";frame=0;}
                if(m.phase!=Journey.Title)Tique(footX,footY,clip,frame,18+Mathf.RoundToInt(py*20),p.lastDirection==0);
            }
            else
            {
                Bar("floor",0,282,640,1,new Color(.4f,.47f,.52f),3);
                Draw("ledge-l",art["floor"],44,236,3,Color.white,false,48,6);Draw("ledge-r",art["floor"],548,236,3,Color.white,false,48,6);
                string exit=WorldArtState.Exit(m,out float exitAge);StateProp("exit-door",exit,exitAge,576,186,3);
                for(int i=0;i<2;i++)
                {
                    string pylon=WorldArtState.Pylon(m,i,out float pylonAge);
                    StateProp("pylon"+i,pylon,pylonAge,m.pylons[i]-21,222,5,pylon=="pylon-expiring");
                }
                int bossFrame=WardenAnimation.Select(m,durations,out string bossClip);
                // Boot plays the collapse backwards while the lights come on.
                if(m.phase==Journey.Arrival){bossClip="iron-boot";bossFrame=WardenAnimation.FrameAt(durations[bossClip],Mathf.Min(2.399f,m.age));}
                float bossLeft=m.bossX-WardenAnimation.CanvasWidth/2,bossTop=m.bossY-WardenAnimation.Baseline;
                Draw("iron-maw",animations[bossClip][bossFrame],bossLeft,bossTop,10,Color.white,m.bossFacing>0);
                // The core is painted into the held Open pose; a hit flashes just those pixels.
                if(m.Vulnerable&&m.clock-m.lastCoreHitAt<.14f)
                    Draw("core-flash",animations["iron-core-flash"][WardenAnimation.FrameAt(durations["iron-core-flash"],m.clock-m.lastCoreHitAt)],bossLeft,bossTop,11,Color.white,m.bossFacing>0);
                if(m.Vulnerable)
                {
                    // Same held core and real attack point for both routes.
                    // Four small native-pixel brackets do not cover core artwork.
                    float wx=m.WeakX,wy=m.WeakY;
                    Bar("core-top-l",wx-12,wy-12,5,1,ink,13);Bar("core-left-t",wx-12,wy-12,1,5,ink,13);
                    Bar("core-top-r",wx+8,wy-12,5,1,ink,13);Bar("core-right-t",wx+12,wy-12,1,5,ink,13);
                    Bar("core-bot-l",wx-12,wy+12,5,1,ink,13);Bar("core-left-b",wx-12,wy+8,1,5,ink,13);
                    Bar("core-bot-r",wx+8,wy+12,5,1,ink,13);Bar("core-right-b",wx+12,wy+8,1,5,ink,13);
                }
                if(m.bossMove==IronMove.ChargeAim)
                {
                    float start=m.bossFacing<0?24:m.bossX,end=m.bossFacing<0?m.bossX:616;
                    for(int i=0;start+i*32+32<=end;i++)StateProp("charge-tick"+i,"warning-charge",m.bossAge,start+i*32,274,12,true,m.bossFacing<0);
                }
                if(m.bossMove==IronMove.SlamAim||m.bossMove==IronMove.Slam)
                {
                    StateProp("slam-area","warning-slam",m.bossAge,m.aimX-68,266,12,true);
                }
                if(m.bossMove==IronMove.WaveAim||(m.bossMove==IronMove.Wave&&m.Rage>=2&&m.bossAge>=.92f&&m.bossAge<1.1f))for(int i=0;i<15;i++)StateProp("wave-warn"+i,"warning-wave",m.bossAge,20+i*41,274,12,true);
                for(int i=0;i<m.waves.Count;i++)StateProp("wave"+i,"wave-spin",m.clock,m.waves[i].x-12,260,12,true,m.waves[i].direction<0);
                int f=TiqueAnimation.Select(m.hero,durations,out string pose);
                if(m.phase==Journey.Dead){pose="fx-power-down";f=WardenAnimation.FrameAt(durations[pose],m.age);}
                else if(TiqueAnimation.InitialHurtVisible(m)){pose="fx-hurt-pose";f=WardenAnimation.FrameAt(durations[pose],m.clock-m.hurtAt);}
                else if(m.idleAge>2.5f&&(m.idleAge-2.5f)%5.5f<.26f&&m.bossMove==IronMove.Rest&&!m.reducedEffects){float blink=(m.idleAge-2.5f)%5.5f;pose=blink<.08f||blink>=.18f?"fx-blink-half":"fx-blink-closed";f=0;}
                if(m.hero.Dashing&&!m.reducedEffects)for(int i=1;i<=2;i++)Draw("ghost"+i,animations["fx-dash-ghost"][f],m.hero.x-32-m.hero.facing*i*9,m.hero.y-56,19,new Color(1,1,1,i==1?.28f:.12f),m.hero.facing<0);
                Tique(m.hero.x,m.hero.y,pose,f,20,m.hero.facing<0);
                if(m.hero.invincible>0&&m.phase==Journey.Combat)StateFeedback("protect",0,m.hero.x-12,m.hero.y-27,21); // ring centred on the heart (15px above the feet)
                bool chargeLock=m.bossMove==IronMove.ChargeAim&&m.bossAge>=.35f;
                bool slamLock=(m.bossMove==IronMove.SlamAim&&m.bossAge>=.45f)||m.bossMove==IronMove.Slam;
                if(chargeLock||slamLock){float left=slamLock?m.aimX-68:m.bossFacing<0?24:m.bossX;float right=slamLock?m.aimX+68:m.bossFacing<0?m.bossX:616;
                    Bar("lock-left",left,265,2,10,gold,13);Bar("lock-left-cap",left,265,8,2,gold,13);Bar("lock-right",right-2,265,2,10,gold,13);Bar("lock-right-cap",right-8,265,8,2,gold,13);}
            }
            if(!m.InArena&&m.hintLevel>0)foreach(int goal in m.puzzle.room.goals){float x=194+goal%7*36,y=64+goal/7*36;Bar("hint-l"+goal,x,y,2,36,gold,200);Bar("hint-r"+goal,x+34,y,2,36,gold,200);}
            // Contact and miss feedback are emitted by the actual 120–220ms
            // outcome window; no premature, unconditional miss effect is drawn.
            foreach(var cue in m.feedback.cues)
            {
                if(cue.kind=="bridge")
                {
                    // Captured endpoints, native 1px stepped wire; never follows a moving hand.
                    Color electric=cue.age<.03f?ink:cyan;float mid=(cue.x+cue.endX)/2;
                    Bar("bridge-a"+cue.serial,Mathf.Min(cue.x,mid),cue.y,Mathf.Abs(mid-cue.x)+1,1,electric,202);
                    Bar("bridge-b"+cue.serial,mid,Mathf.Min(cue.y,cue.endY),1,Mathf.Abs(cue.y-cue.endY)+1,electric,202);
                    Bar("bridge-c"+cue.serial,Mathf.Min(mid,cue.endX),cue.endY,Mathf.Abs(cue.endX-mid)+1,1,electric,202);
                    StateFeedback("bridge",cue.age,cue.endX-16,cue.endY-16,202);continue;
                }
                if(cue.kind=="blocked"||cue.kind=="undo"||cue.kind=="reset")
                {string icon=cue.kind=="blocked"?"icon-locked":"icon-"+cue.kind;Draw("cue"+cue.serial,animations["fx-"+icon][0],cue.x-6,cue.y-6,202);continue;}
                if(cue.kind=="shutdown")continue;
                string key="fx-"+cue.kind;if(!animations.ContainsKey(key))continue;int index=WardenAnimation.FrameAt(durations[key],cue.age);var sprite=animations[key][index];
                bool ground=cue.kind.Contains("dust")||cue.kind=="friction"||cue.kind=="wall-brake"||cue.kind=="weight-settle";
                Draw("cue"+cue.serial,sprite,cue.x-sprite.rect.width/2,cue.y-(ground?sprite.rect.height-2:sprite.rect.height/2),ground?4:202,Color.white,cue.direction<0);
            }
            RecordInput();
        }
        void StateFeedback(string clip,float age,float x,float y,int layer,bool flip=false)
        {
            string key="fx-"+clip;int f=WardenAnimation.FrameAt(durations[key],age);Draw("feedback-"+clip,animations[key][f],x,y,layer,Color.white,flip);
        }
        IEnumerator Capture(string folder,string name)
        {
            if(!screenshots.Add(name))yield break;
            Texture2D texture;
            if(offscreenCapture)
            {
                // QA only: render the real production world camera without
                // operating a desktop window. Excludes IMGUI and presentation.
                cameraWorld.Render();var previous=RenderTexture.active;
                try
                {
                    RenderTexture.active=target;texture=new Texture2D(target.width,target.height,TextureFormat.RGBA32,false);
                    texture.ReadPixels(new Rect(0,0,target.width,target.height),0,0);texture.Apply();
                }
                finally{RenderTexture.active=previous;}
            }
            else
            {
                yield return new WaitForEndOfFrame();texture=ScreenCapture.CaptureScreenshotAsTexture();
                if(texture==null)throw new InvalidOperationException("Visible player capture failed");
            }
            File.WriteAllBytes(Path.Combine(folder,name+".png"),texture.EncodeToPNG());Destroy(texture);
        }
        IEnumerator Smoke()
        {
            string[] args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"--qa-dir");string folder=n>=0?args[n+1]:Path.Combine(Application.persistentDataPath,"ReturnV2QA");Directory.CreateDirectory(folder);
            yield return Capture(folder,"01-title");float deadline=Time.realtimeSinceStartup+210;
            while(Model.phase!=Journey.Ending&&Model.phase!=Journey.Dead&&Time.realtimeSinceStartup<deadline)
            {
                if(Model.phase==Journey.Opening)
                {
                    if(Model.age>.1f)yield return Capture(folder,"opening-01-mask");
                    if(Model.age>1.82f&&Model.age<2)yield return Capture(folder,"opening-02-fall");
                    if(Model.age>2.01f&&Model.age<2.16f)yield return Capture(folder,"opening-03-land");
                    if(Model.age>3.5f&&Model.age<3.58f)yield return Capture(folder,"opening-04-eyes");
                    if(Model.age>6.1f&&Model.age<9)yield return Capture(folder,"opening-05-record");
                    if(Model.age>11.1f)yield return Capture(folder,"opening-06-tutorial");
                }
                foreach(var cue in new List<FeedbackCue>(Model.feedback.cues))if(cue.age<.05f)yield return Capture(folder,"fx-"+cue.kind);
                if(Model.phase==Journey.Puzzle)yield return Capture(folder,"02-puzzle-"+(Model.roomIndex+1));
                if((Model.phase==Journey.Puzzle||Model.phase==Journey.RoomClear)&&Model.puzzle.lastPushedBox>=0&&Model.puzzle.visualAge>.025f&&Model.puzzle.visualAge<.12f)
                    yield return Capture(folder,"push-"+(Model.puzzle.lastDirection==2?"up":Model.puzzle.lastDirection==3?"down":"side"));
                if(Model.phase==Journey.Arrival)yield return Capture(folder,"03-guardian");
                if(Model.bossMove==IronMove.ChargeAim)yield return Capture(folder,"04-charge-warning");
                if(Model.bossMove==IronMove.Open)yield return Capture(folder,"05-armor-open");
                if(Model.bossMove==IronMove.Wave)yield return Capture(folder,"06-wave");
                if(Model.bossMove==IronMove.SlamAim)yield return Capture(folder,"07-slam");
                if(Model.bossMove==IronMove.ChargeAim&&Model.bossAge>.2f)yield return Capture(folder,"09-authored-charge-brace");
                if(Model.bossMove==IronMove.Open&&Model.bossAge>.3f)yield return Capture(folder,"10-authored-open-hold");
                if(Model.Vulnerable&&Model.openingSource==CoreOpeningSource.SlamCounter)yield return Capture(folder,"22-slam-counter-ready");
                if(Model.counterHits>0&&Model.clock-Model.lastCoreHitAt<.14f)yield return Capture(folder,"23-slam-counter-hit");
                if(Model.bossMove==IronMove.SlamAim&&Model.bossAge>.4f)yield return Capture(folder,"11-authored-air-tuck");
                if(Model.bossMove==IronMove.Recover&&Model.bossSequence=="slam"&&Model.bossAge<.06f)yield return Capture(folder,"12-authored-landing");
                if(Model.phase==Journey.RoomClear&&Model.age>.66f&&Model.age<.8f)yield return Capture(folder,"13-connected-room-"+(Model.roomIndex+1));
                if(Model.phase==Journey.Puzzle&&Model.puzzle.motion>0&&Model.roomIndex>0)
                    for(int i=0;i<Model.puzzle.boxes.Length;i++)if(Model.puzzle.room.types[i]==1&&Model.puzzle.boxes[i]!=Model.puzzle.previousBoxes[i])yield return Capture(folder,"14-orb-sliding");
                if(Model.phase==Journey.Combat)
                {
                    for(int i=0;i<2;i++)
                    {
                        string state=WorldArtState.Pylon(Model,i,out float stateAge);
                        if(state=="pylon-charging"&&stateAge>.12f)yield return Capture(folder,"15-pylon-charging");
                        if(state=="pylon-armed")yield return Capture(folder,"16-pylon-armed");
                        if(state=="pylon-discharge"&&stateAge>.08f)yield return Capture(folder,"17-pylon-discharge");
                        if(state=="pylon-cooldown")yield return Capture(folder,"18-pylon-cooldown");
                    }
                    if(Model.Vulnerable&&Model.clock-Model.lastCoreHitAt<.2f)yield return Capture(folder,"19-core-hit");
                }
                if(Model.phase==Journey.Restored)
                {
                    float exitAge=Model.clock-Model.restoredAt;
                    if(exitAge>.18f&&exitAge<.8f)yield return Capture(folder,"20-exit-opening");
                    if(exitAge>=.8f)yield return Capture(folder,"21-exit-open-restored");
                }
                yield return null;
            }
            bool pass=Model.phase==Journey.Ending&&Model.bossHealth==0&&Model.events.Exists(e=>e.EndsWith(":armor-break"));
            if(Array.IndexOf(args,"--require-readability-v2")>=0)pass&=readabilityArt&&readabilityResourceRoot=="ReturnV2/ReadabilityArtV2/";
            yield return Capture(folder,pass?"08-ending":"failure");
            File.WriteAllText(Path.Combine(folder,"result.json"),"{\"passed\":"+pass.ToString().ToLowerInvariant()+",\"artRoot\":\""+readabilityResourceRoot+"\",\"phase\":\""+Model.phase+"\",\"health\":"+Model.health+",\"breaks\":"+Model.breaks+",\"playSeconds\":"+Model.playTime.ToString("F2",System.Globalization.CultureInfo.InvariantCulture)+"}");
            var observed=new List<string>(seenArtStates);observed.Sort();File.WriteAllLines(Path.Combine(folder,"observed-art-states.txt"),observed);
            File.WriteAllLines(Path.Combine(folder,"events.txt"),Model.events);Debug.Log("RETURN_V2_SMOKE "+(pass?"PASS":"FAIL"));Application.Quit(pass?0:2);
        }
        void RecordInput()
        {
            if(smoke)return;string[] args=Environment.GetCommandLineArgs();int k=Array.IndexOf(args,"--return-input-log");if(k<0)return;
            foreach(KeyCode key in new[]{KeyCode.Return,KeyCode.Escape,KeyCode.LeftArrow,KeyCode.RightArrow,KeyCode.UpArrow,KeyCode.DownArrow,KeyCode.Z,KeyCode.Space,KeyCode.X,KeyCode.C,KeyCode.E,KeyCode.R,KeyCode.H})if(Input.GetKeyDown(key))
            {string file=args[k+1];Directory.CreateDirectory(Path.GetDirectoryName(file));File.AppendAllText(file,JsonUtility.ToJson(new InputObservation{key=key.ToString(),phase=Model.phase.ToString(),clock=Model.clock,x=Model.hero.x,y=Model.hero.y,moves=Model.puzzle.moves,paused=Model.paused,attack=Model.hero.Attacking,dash=Model.hero.Dashing,jumps=Model.hero.jumps,charged=Model.charged})+"\n");StartCoroutine(Capture(Path.GetDirectoryName(file),"key-"+Path.GetFileNameWithoutExtension(file)+"-"+(manualShot++).ToString("00")+"-"+key));}
        }
        [Serializable] sealed class InputObservation{public string key,phase;public float clock,x,y;public int moves,jumps,charged;public bool paused,attack,dash;}
        void OnDestroy(){if(target!=null){target.Release();Destroy(target);}}
    }
}
