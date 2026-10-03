using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace TiqueReturn
{
    public sealed partial class ReworkGame
    {
        // Opt-in game-internal rendering fixture. Normal gameplay never sets
        // this flag. Update and OnGUI keep using the production draw paths,
        // while physical input and model ticks are suspended by the caller.
        bool uiReview=false;
        string uiReviewHelp="";

        [Serializable] sealed class CompactUiReviewRow
        {
            public string file="",phase="",help="";
            public bool largeText,paused;
            public int screenWidth,screenHeight,integerScale,menuSelection;
            public float screenDpi;
            public string[] textSizes=Array.Empty<string>();
        }
        [Serializable] sealed class CompactUiReviewResult
        {
            public bool passed;
            public string scope="Actual complete Unity player renders including production OnGUI; scripted presentation fixtures, not human input testing or human visual approval.";
            public string captureApi="ScreenCapture.CaptureScreenshotAsTexture after WaitForEndOfFrame; no desktop/OS capture or native computer control.";
            public string outputDirectory="",tiqueArtRoot="",wardenArtRoot="",fontRoot="ReturnV2/UiV2/";
            public string humanAppearanceApproval="pending";
            public string passMeaning="All requested complete player-frame files were produced; this is not an assertion that typography or composition has human approval.";
            public string openingScope="The approved falling opening is not altered or fixture-tested by this review.";
            public int nativeWidth=640,nativeHeight=360;
            public List<CompactUiReviewRow> observations=new List<CompactUiReviewRow>();
        }
        sealed class CompactUiReviewFixture
        {
            public string name="",help="";
            public ReworkModel model;
            public bool large;
            public int selection;
        }

        IEnumerator ReviewCompactUi()
        {
            // Flatten nested Capture iterators so exceptions after an end-frame
            // wait cannot leave an automated review running without a result.
            var stack=new Stack<IEnumerator>();stack.Push(ReviewCompactUiFrames());
            while(stack.Count>0)
            {
                object instruction=null;bool failed=false;
                try
                {
                    var current=stack.Peek();
                    if(!current.MoveNext()){stack.Pop();continue;}
                    instruction=current.Current;
                    if(instruction is IEnumerator nested){stack.Push(nested);continue;}
                }
                catch(Exception exception)
                {
                    Debug.LogException(exception);Debug.LogError("COMPACT_UI_REVIEW FAIL");
                    failed=true;
                }
                if(failed){Application.Quit(2);yield break;}
                yield return instruction;
            }
        }

        IEnumerator ReviewCompactUiFrames()
        {
            if(!uiReview)throw new InvalidOperationException("Compact UI review requires --return-ui-review");
            if(Application.isBatchMode)throw new InvalidOperationException("Compact UI review needs a visible player render; do not launch with -batchmode or -nographics");
            if(smoke||tiqueReview||readabilityReview)
                throw new InvalidOperationException("Compact UI review cannot be combined with other review/smoke modes");
            // This fixture must capture the whole app render, not the old
            // world-only RenderTexture samples that exclude IMGUI entirely.
            offscreenCapture=false;
            string[] args=Environment.GetCommandLineArgs();int k=Array.IndexOf(args,"--qa-dir");
            string stamp=DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff",System.Globalization.CultureInfo.InvariantCulture)+"-"+Guid.NewGuid().ToString("N").Substring(0,8);
            string folder=k>=0&&k+1<args.Length?Path.GetFullPath(args[k+1]):
                Path.Combine(Application.persistentDataPath,"CompactUiReview",stamp);
            if(Directory.Exists(folder)&&Directory.GetFileSystemEntries(folder).Length>0)
                folder=Path.Combine(folder,"compact-ui-review-"+stamp);
            Directory.CreateDirectory(folder);
            Debug.Log("COMPACT_UI_REVIEW_BEGIN folder="+folder);

            var result=new CompactUiReviewResult{passed=true,outputDirectory=folder,
                tiqueArtRoot=tiqueResourceRoot,wardenArtRoot=wardenResourceRoot};
            var fixtures=new List<CompactUiReviewFixture>();
            ReworkModel Puzzle(int room)
            {
                var m=new ReworkModel(book){phase=Journey.Puzzle,roomIndex=room,
                    puzzle=new CorePuzzle(book.levels[room]),clock=10,age=3,muted=true};
                m.puzzle.visualAge=8;return m;
            }
            ReworkModel Arena()
            {
                var m=new ReworkModel(book);m.BeginArena();m.phase=Journey.Combat;
                m.clock=10;m.age=3;m.bossAge=1;m.muted=true;
                m.hero.grounded=true;m.hero.landAge=9;m.hero.dashAge=9;m.hero.attackAge=9;
                // The fixture needs an unobscured approved sprite. This does
                // not modify protection or blinking in normal gameplay.
                m.hero.invincible=0;return m;
            }
            void Add(string name,ReworkModel model,bool large=false,string help="",int selection=0)
            {fixtures.Add(new CompactUiReviewFixture{name=name,model=model,large=large,help=help,selection=selection});}
            string puzzleHelp="";string combatHelp="";
            foreach(string message in AdaptiveGuidance.MessagesForAudit())
            {
                if(puzzleHelp.Length==0)puzzleHelp=message;
                if(combatHelp.Length==0&&message.Contains("충격파"))combatHelp=message;
            }
            if(puzzleHelp.Length==0||combatHelp.Length==0)
                throw new InvalidOperationException("Compact UI review cannot find actual production guidance strings");

            Add("01-title",new ReworkModel(book){muted=true,clock=.8f});
            Add("02-title-large",new ReworkModel(book){muted=true,clock=.8f},true);
            for(int room=0;room<book.levels.Length;room++)
                Add("0"+(room+3)+"-puzzle-"+(room+1),Puzzle(room));
            Add("06-puzzle-auto-help",Puzzle(Math.Min(1,book.levels.Length-1)),false,puzzleHelp);
            Add("07-puzzle-auto-help-large",Puzzle(Math.Min(1,book.levels.Length-1)),true,puzzleHelp);
            var pause=Arena();pause.paused=true;
            Add("08-pause",pause,false,"",3);
            var pauseLarge=Arena();pauseLarge.paused=true;
            Add("09-pause-large",pauseLarge,true,"",4);
            Add("10-combat-rest",Arena());
            var exposed=Arena();exposed.bossMove=IronMove.Open;exposed.bossAge=.4f;
            exposed.openingSource=CoreOpeningSource.SlamCounter;exposed.bossSequence="stagger";
            exposed.hero.x=exposed.WeakX-38;
            Add("11-combat-core",exposed);
            Add("12-combat-auto-help",Arena(),false,combatHelp);
            Add("13-combat-auto-help-large",Arena(),true,combatHelp);
            var dead=Arena();dead.phase=Journey.Dead;dead.health=0;dead.age=1;
            Add("14-dead",dead);
            var ending=Arena();ending.phase=Journey.Ending;ending.bossMove=IronMove.Down;
            ending.bossHealth=0;ending.age=2;ending.restoredAt=8;ending.controlTime=326;
            Add("15-ending",ending);

            foreach(var fixture in fixtures)
            {
                Model=fixture.model;uiPreferences.largeText=fixture.large;uiPreferences.autoHelp=true;
                uiReviewHelp=fixture.help;menuSelection=fixture.selection;pressedButton=-1;
                menuPhase=Model.phase;menuWasPaused=Model.paused;inputEpoch=Model.inputEpoch;
                ResetPuzzleGuide();FlushInput(false);DrawWorld();
                // Let the production cameras and IMGUI repaint for multiple
                // visible app frames before the in-game end-of-frame capture.
                yield return new WaitForSecondsRealtime(.15f);
                yield return Capture(folder,fixture.name);
                var plan=CompactUiLayout.Build(Model,uiPreferences,uiReviewHelp,uiReviewHelp.Length>0);
                var sizes=new SortedSet<int>();
                foreach(var element in plan.elements)
                    if(element.kind=="text"||element.kind=="button")sizes.Add(element.size);
                var sizeDescriptions=new List<string>();
                foreach(int size in sizes)
                {
                    bool sized=sizedFontAtlases.TryGetValue(size,out var atlas);
                    if(!sized)atlas=fontAtlas;
                    sizeDescriptions.Add(size+"px:"+(sized?"sized-atlas":"base-atlas")+
                        ":"+atlas.width+"x"+atlas.height);
                }
                result.observations.Add(new CompactUiReviewRow{file=fixture.name+".png",phase=Model.phase.ToString(),
                    help=uiReviewHelp,largeText=fixture.large,paused=Model.paused,screenWidth=Screen.width,
                    screenHeight=Screen.height,screenDpi=Screen.dpi,integerScale=Math.Max(1,Math.Min(Screen.width/640,Screen.height/360)),
                    menuSelection=menuSelection,textSizes=sizeDescriptions.ToArray()});
                if(!File.Exists(Path.Combine(folder,fixture.name+".png")))result.passed=false;
            }
            uiReviewHelp="";
            File.WriteAllText(Path.Combine(folder,"result.json"),JsonUtility.ToJson(result,true));
            Debug.Log("COMPACT_UI_REVIEW "+(result.passed?"PASS":"FAIL")+" samples="+result.observations.Count+" folder="+folder);
            Application.Quit(result.passed?0:2);
        }
    }
}
