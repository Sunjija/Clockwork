using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed partial class ReworkGame
    {
        [Serializable] sealed class TiqueReviewRow
        {
            public string scenario,clip,file;public int frame;
            public float time,x,y,velocity;public bool grounded;
        }
        [Serializable] sealed class TiqueReviewResult
        {
            public bool passed;public string scope,artRoot;
            public List<TiqueReviewRow> observations=new List<TiqueReviewRow>();
        }

        // Explicit command-line review fixture. Normal Play.cmd and the editor
        // title never enter this mode. It sends production commands at 120Hz,
        // samples the renderer at 60Hz and saves actual complete game frames.
        IEnumerator ReviewTique()
        {
            string[] args=Environment.GetCommandLineArgs();int k=Array.IndexOf(args,"--qa-dir");
            string folder=k>=0&&k+1<args.Length?args[k+1]:Path.Combine(Application.persistentDataPath,"TiqueAnimationReview");
            Directory.CreateDirectory(folder);
            var result=new TiqueReviewResult{passed=true,artRoot=tiqueResourceRoot,scope=offscreenCapture
                ?"Scripted production-input fixture and actual Unity world-camera RenderTexture GPU captures. IMGUI, desktop presentation, physical keys and human motion approval excluded."
                :"Scripted production-input fixture and actual Unity game renders; not physical key testing or human motion approval."};
            void Observe(string scenario,string clip,int frame,float time,float x,float y,float velocity,bool grounded)
            {
                // The same exposure may recur later at a different position.
                // Never reuse its first capture for a new observation.
                string file=scenario+"-"+result.observations.Count.ToString("0000")+"-"+clip+"-"+frame.ToString("00");
                result.observations.Add(new TiqueReviewRow{scenario=scenario,clip=clip,file=file,frame=frame,time=time,x=x,y=y,velocity=velocity,grounded=grounded});
                StartCoroutine(Capture(folder,file));
            }
            foreach(string scenario in new[]{"idle","walk","jump","double-jump","moving-landing","dash","moving-dash","air-dash","air-attack","attack","hurt"})
            {
                Model=new ReworkModel(book);Model.BeginArena();Model.phase=Journey.Combat;
                Model.hero.x=100;Model.hero.grounded=true;Model.hero.landAge=9;Model.hero.dashAge=9;Model.hero.attackAge=9;
                // The normal arena handoff grants temporary protection. This
                // explicit art fixture needs an unobscured silhouette; gameplay
                // protection and blinking still run unchanged in normal play.
                Model.hero.invincible=0;
                Model.Sound=Sound;Model.muted=true;
                string previous="";float previousX=float.NaN,previousY=float.NaN;
                for(int tick=0;tick<144;tick+=2)
                {
                    for(int sub=0;sub<2;sub++)
                    {
                        int n=tick+sub;var command=ReworkCommand.Empty;
                        if(scenario=="walk"||scenario=="moving-landing"||scenario=="moving-dash")command.axis=1;
                        if(n==0&&(scenario=="jump"||scenario=="double-jump"||scenario=="moving-landing"||scenario=="air-dash"||scenario=="air-attack"))command.jump=true;
                        if(scenario=="double-jump"&&n==24)command.jump=true;
                        if((scenario=="dash"||scenario=="moving-dash")&&n==0||scenario=="air-dash"&&n==20)command.dash=true;
                        if(scenario=="attack"&&n==0||scenario=="air-attack"&&n==20)command.attack=true;
                        if(scenario=="hurt"&&n==12){Model.hurtAt=Model.clock;Model.hero.invincible=.85f;}
                        // Keep the distant guardian waiting in this presentation
                        // fixture; no production pattern timings are changed.
                        Model.bossMove=IronMove.Rest;Model.bossAge=0;
                        Model.Tick(1f/120,command);
                    }
                    string clip;int frame=TiqueAnimation.Select(Model.hero,durations,out clip);
                    if(TiqueAnimation.InitialHurtVisible(Model)){clip="fx-hurt-pose";frame=WardenAnimation.FrameAt(durations[clip],Model.clock-Model.hurtAt);}
                    string key=clip+"-"+frame.ToString("00");
                    DrawWorld();
                    if(key!=previous||Model.hero.x!=previousX||Model.hero.y!=previousY)
                    {
                        Observe(scenario,clip,frame,Model.clock,Model.hero.x,Model.hero.y,Model.hero.vy,Model.hero.grounded);
                        previous=key;previousX=Model.hero.x;previousY=Model.hero.y;
                    }
                    yield return null;
                }
            }
            // Board one's saved production solution contains all three push
            // directions. Replay it from the normal title/skip handoff, without
            // assigning a tile, box or visual position in the review fixture.
            foreach(int direction in new[]{0,2,3})
            {
                string scenario="push-"+(direction==0?"side":direction==2?"up":"down");
                Model=new ReworkModel(book);Model.Sound=Sound;Model.muted=true;
                var enter=ReworkCommand.Empty;enter.interact=true;
                Model.Tick(1f/120,enter);Model.Tick(1f/120,enter);
                bool captured=false;
                foreach(char step in book.levels[0].solution)
                {
                    int before=Model.puzzle.pushes;var move=ReworkCommand.Empty;move.grid=step-'0';
                    Model.Tick(1f/120,move);Model.Tick(1f/120,ReworkCommand.Empty);
                    bool requestedPush=Model.puzzle.pushes>before&&move.grid==direction;
                    float started=Model.clock;
                    while(Model.puzzle.motion>0||Model.stepLock>0)
                    {
                        DrawWorld();
                        if(requestedPush&&Model.puzzle.visualAge<.15f)
                        {
                            var p=Model.puzzle;float t=Mathf.Clamp01(p.visualAge/.15f);t=t*t*(3-2*t);
                            float x=OpeningSequence.FootX(Mathf.Lerp(p.previousPlayer%7,p.player%7,t));
                            float y=OpeningSequence.FootY(Mathf.Lerp(p.previousPlayer/7,p.player/7,t));
                            string clip="fx-push-"+(direction==0?"side":direction==2?"up":"down");
                            int frame=WardenAnimation.FrameAt(durations[clip],p.walkAge,loop:true);
                            Observe(scenario,clip,frame,Model.clock-started,x,y,0,true);captured=true;
                        }
                        yield return null;
                        Model.Tick(1f/120,ReworkCommand.Empty);Model.Tick(1f/120,ReworkCommand.Empty);
                    }
                    if(captured)break;
                }
                if(!captured)result.passed=false;
            }
            if(offscreenCapture)yield return null;else yield return new WaitForEndOfFrame();
            var files=new HashSet<string>();
            foreach(var row in result.observations)
                if(!files.Add(row.file)||!File.Exists(Path.Combine(folder,row.file+".png")))result.passed=false;
            File.WriteAllText(Path.Combine(folder,"result.json"),JsonUtility.ToJson(result,true));
            Debug.Log("TIQUE_ANIMATION_REVIEW "+(result.passed?"PASS":"FAIL")+" samples="+result.observations.Count);
            Application.Quit(result.passed?0:2);
        }
    }
}
