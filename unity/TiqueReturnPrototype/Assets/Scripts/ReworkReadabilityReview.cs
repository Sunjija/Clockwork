using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed partial class ReworkGame
    {
        [Serializable] sealed class ReadabilityReviewResult
        {
            public bool passed;public string scope,artRoot;
            public int completedRooms,counterHits,bossHealth,health;
            public List<string> captures=new List<string>(),events=new List<string>();
        }
        // Explicit engine QA fixture, not a normal launch or a physical-input
        // test. Puzzle solutions run via commands; the counter starts from a
        // documented combat setup, then only axis/dash/attack commands are used.
        IEnumerator ReviewReadability()
        {
            string[] args=Environment.GetCommandLineArgs();int k=Array.IndexOf(args,"--qa-dir");
            string folder=k>=0&&k+1<args.Length?args[k+1]:Path.Combine(Application.persistentDataPath,"ReadabilityCounterQA");
            Directory.CreateDirectory(folder);
            var result=new ReadabilityReviewResult{artRoot=readabilityResourceRoot,scope=offscreenCapture
                ?"Actual Unity world-camera GPU captures and production-command fixtures. Puzzle solutions replayed; combat initial state explicitly staged. IMGUI, desktop, physical keys, subjective art approval and human playability excluded."
                :"Actual Unity game-render captures and production-command fixtures, with a staged initial combat setup; not physical-input or human playtesting."};
            Model=new ReworkModel(book);Model.Sound=Sound;Model.muted=true;ResetPuzzleGuide();
            var enter=ReworkCommand.Empty;enter.interact=true;
            Model.Tick(1f/120,enter);Model.Tick(1f/120,enter);
            for(int room=0;room<book.levels.Length;room++)
            {
                string initial="puzzle-"+(room+1)+"-initial";DrawWorld();yield return Capture(folder,initial);result.captures.Add(initial);
                bool orbSeen=false;
                foreach(char direction in book.levels[room].solution)
                {
                    var c=ReworkCommand.Empty;c.grid=direction-'0';Model.Tick(1f/120,c);
                    while(Model.puzzle.motion>0||Model.phase==Journey.Puzzle&&Model.stepLock>0)
                    {
                        Model.Tick(1f/120,ReworkCommand.Empty);Model.Tick(1f/120,ReworkCommand.Empty);DrawWorld();
                        int b=Model.puzzle.lastPushedBox;
                        if(!orbSeen&&b>=0&&Model.puzzle.room.types[b]==1&&Model.puzzle.visualAge>=.09f)
                        {string moving="puzzle-"+(room+1)+"-orb-moving";yield return Capture(folder,moving);result.captures.Add(moving);orbSeen=true;}
                        yield return null;
                    }
                }
                for(int tick=0;tick<100;tick++)Model.Tick(1f/120,ReworkCommand.Empty);
                if(Model.phase!=Journey.RoomClear||!Model.puzzle.Solved)throw new InvalidOperationException("Readability puzzle fixture failed "+room);
                result.completedRooms++;string solved="puzzle-"+(room+1)+"-connected";DrawWorld();yield return Capture(folder,solved);result.captures.Add(solved);
                Model.Tick(1f/120,enter);
            }
            // Staged initial setup only. All movement and the eventual hit below
            // use the exact command/Tick path used in the interactive game.
            Model=new ReworkModel(book);Model.BeginArena();Model.phase=Journey.Combat;Model.pattern=2;
            Model.hero.x=320;Model.hero.invincible=0;Model.Sound=Sound;Model.muted=true;
            bool hitCaptured=false;
            for(int tick=0;tick<120*8&&Model.counterHits==0;tick+=2)
            {
                for(int sub=0;sub<2;sub++)
                {
                    var c=ReworkCommand.Empty;
                    if(Model.bossMove==IronMove.SlamAim&&Model.bossAge>=.5f)
                    {c.axis=1;c.dash=Model.hero.dashReady&&Mathf.Abs(Model.hero.x-Model.aimX)<80;}
                    if(Model.bossMove==IronMove.Slam)c.axis=Model.hero.x<Model.aimX+110?1:0;
                    if(Model.bossMove==IronMove.CounterSettle||Model.bossMove==IronMove.Open)
                    {
                        float targetX=Model.WeakX+Model.bossFacing*32;
                        c.axis=Mathf.Abs(Model.hero.x-targetX)>2?Math.Sign(targetX-Model.hero.x):0;
                        if(Model.Vulnerable&&Mathf.Abs(Model.hero.x-targetX)<8)
                        {if(Model.hero.facing!=-Model.bossFacing)c.axis=-Model.bossFacing;c.attack=true;}
                    }
                    Model.Tick(1f/120,c);
                }
                DrawWorld();string shot=null;
                if(Model.bossMove==IronMove.SlamAim&&Model.bossAge>=.55f)shot="counter-01-locked-warning";
                if(Model.bossMove==IronMove.CounterSettle)shot="counter-02-land-miss";
                if(Model.bossMove==IronMove.Open&&!Model.Vulnerable)shot="counter-03-opening";
                if(Model.Vulnerable)shot="counter-04-ready-core";
                if(shot!=null&&!result.captures.Contains(shot)){yield return Capture(folder,shot);result.captures.Add(shot);}
                if(Model.counterHits>0){shot="counter-05-hit";yield return Capture(folder,shot);result.captures.Add(shot);hitCaptured=true;}
                yield return null;
            }
            result.counterHits=Model.counterHits;result.bossHealth=Model.bossHealth;result.health=Model.health;result.events.AddRange(Model.events);
            result.passed=readabilityArt&&result.completedRooms==3&&hitCaptured&&result.counterHits==1&&result.bossHealth==8&&result.health==5;
            if(Array.IndexOf(args,"--require-readability-v2")>=0)result.passed&=result.artRoot=="ReturnV2/ReadabilityArtV2/";
            foreach(string shot in result.captures)result.passed&=File.Exists(Path.Combine(folder,shot+".png"));
            File.WriteAllText(Path.Combine(folder,"result.json"),JsonUtility.ToJson(result,true));
            Debug.Log("READABILITY_COUNTER_REVIEW "+(result.passed?"PASS":"FAIL")+" captures="+result.captures.Count);
            Application.Quit(result.passed?0:2);
        }
    }
}
