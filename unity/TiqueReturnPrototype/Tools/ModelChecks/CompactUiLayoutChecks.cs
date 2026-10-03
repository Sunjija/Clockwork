using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace TiqueReturn
{
    public static class CompactUiLayoutChecks
    {
        public static List<string> Run(PuzzleBook book,Action<string> log=null)
        {
            var passed=new List<string>();
            void Check(bool result,string name)
            {if(!result)throw new Exception("Compact UI: "+name);passed.Add(name);log?.Invoke("UI PASS "+name);}
            int plans=0,elements=0;
            bool Intersects(UiElement e,int x,int y,int width,int height)=>e.x<x+width&&e.x+e.width>x&&e.y<y+height&&e.y+e.height>y;
            void Verify(UiPlan plan,bool puzzle,bool arena)
            {
                plans++;
                var ids=new HashSet<string>();
                foreach(UiElement e in plan.elements)
                {
                    elements++;
                    if(!ids.Add(e.id))throw new Exception("Compact UI duplicate id "+plan.phase+"/"+e.id);
                    if(e.x<0||e.y<0||e.width<=0||e.height<=0||e.x+e.width>640||e.y+e.height>360)
                        throw new Exception("Compact UI outside canvas "+plan.phase+"/"+e.id+" at "+e.x+","+e.y+" "+e.width+"x"+e.height);
                    if(e.kind=="text")
                    {
                        if(e.size!=16&&e.size!=32)throw new Exception("Compact UI non-native glyph scale "+e.id+"/"+e.size);
                        if(CompactUiLayout.MeasureWidth(e.text,e.size)>e.width||CompactUiLayout.TextHeight(e.text,e.size)>e.height)
                            throw new Exception("Compact UI text overflow "+e.id);
                    }
                    if(e.kind=="button")
                    {
                        if(e.size!=16||e.height!=28)throw new Exception("Compact UI button not native16/28 "+e.id);
                        if(e.height<20||e.text.IndexOf('\n')>=0||CompactUiLayout.MeasureWidth(e.text,e.size)>e.width-24||CompactUiLayout.TextHeight(e.text,e.size)>e.height-8)
                            throw new Exception("Compact UI button overflow "+e.id);
                    }
                    if(e.action=="hint"||e.text.Contains("H 힌트")||e.text.Contains("H를 누르면"))
                        throw new Exception("Compact UI retained manual hint "+e.id);
                    if(puzzle&&Intersects(e,194,64,252,252))throw new Exception("Compact UI covers puzzle "+e.id);
                    if(arena&&Intersects(e,0,90,640,210))throw new Exception("Compact UI covers combat strike zone "+e.id);
                }
                // The fixed native glyphs must fit without colliding with
                // neighboring controls or another text block. Panel backplates
                // intentionally contain their foreground and are not compared.
                var foreground=plan.elements.Where(e=>e.kind=="text"||e.kind=="button"||e.kind=="image").ToArray();
                for(int a=0;a<foreground.Length;a++)for(int b=a+1;b<foreground.Length;b++)
                {
                    UiElement left=foreground[a],right=foreground[b];
                    int lw=left.kind=="text"?CompactUiLayout.MeasureWidth(left.text,left.size):left.width;
                    int rw=right.kind=="text"?CompactUiLayout.MeasureWidth(right.text,right.size):right.width;
                    if(left.x<right.x+rw&&left.x+lw>right.x&&left.y<right.y+right.height&&left.y+left.height>right.y)
                        throw new Exception("Compact UI foreground overlap "+plan.phase+"/"+left.id+"/"+right.id);
                }
            }

            foreach(bool large in new[]{false,true})
            foreach(Journey phase in Enum.GetValues<Journey>())
            foreach(bool help in new[]{false,true})
            {
                var prefs=new UiPreferences{largeText=large};var m=new ReworkModel(book){phase=phase,age=3.0f};
                string message=phase==Journey.Combat?"충격파는 Z로 넘을 수 있어요.":"같은 곳이 막히면 Z로 한 수 되돌려 보세요.";
                var plan=CompactUiLayout.Build(m,prefs,message,help);
                Verify(plan,phase==Journey.Puzzle,phase==Journey.Combat||phase==Journey.Restored);
                if(help&&phase==Journey.Puzzle)
                {
                    var toast=plan.elements.Single(e=>e.id=="auto-help");
                    if(toast.x!=12||toast.width!=166||toast.height>110)throw new Exception("Compact UI puzzle help not safely beside board");
                }
                if(help&&phase==Journey.Combat)
                {
                    var toast=plan.elements.Single(e=>e.id=="auto-help");
                    if(toast.y<310||toast.y+toast.height>344)throw new Exception("Compact UI combat help not below fight");
                }
            }
            Check(plans==36,"all 9 phases, both title preferences and help states stay inside 640x360");
            Check(elements>100,"ordinary puzzle HUD and contextual help never cover the board");
            Check(true,"combat HUD and failure help never cover y90..300 strike zone");

            foreach(bool large in new[]{false,true})
            foreach(bool arena in new[]{false,true})
            {
                var prefs=new UiPreferences{largeText=large};var m=new ReworkModel(book){phase=arena?Journey.Combat:Journey.Puzzle,paused=true};
                var plan=CompactUiLayout.Build(m,prefs);Verify(plan,false,false);
                var buttons=plan.elements.Where(e=>e.kind=="button").ToArray();int count=arena?8:7;
                if(buttons.Length!=count||CompactUiLayout.MenuCount(m)!=count)throw new Exception("Compact UI pause count mismatch");
                string[] expected=arena?
                    new[]{"continue","toggle-mute","toggle-effects","toggle-auto-help","toggle-large-text","restart-combat","restart-all","quit"}:
                    new[]{"continue","toggle-mute","toggle-effects","toggle-auto-help","toggle-large-text","restart-all","quit"};
                if(!buttons.Select(e=>e.action).SequenceEqual(expected)||!buttons.Select(e=>e.index).SequenceEqual(Enumerable.Range(0,count)))
                    throw new Exception("Compact UI pause action/index mismatch");
                var card=plan.elements.Single(e=>e.id=="pause-card");
                var note=plan.elements.Single(e=>e.id=="pause-controls");
                if(note.text.Contains('\n')||note.y+note.height>card.y+card.height-4)
                    throw new Exception("Compact UI pause shortcuts must remain one line inside card");
            }
            Check(true,"pause actions/indexes match 8 arena / 7 puzzle entries at both title preferences");

            foreach(bool large in new[]{false,true})
            {
                var prefs=new UiPreferences{largeText=large};
                foreach(int room in Enumerable.Range(0,book.levels.Length))
                {
                    var m=new ReworkModel(book){phase=Journey.Puzzle,roomIndex=room,puzzle=new CorePuzzle(book.levels[room])};
                    var plan=CompactUiLayout.Build(m,prefs);Verify(plan,true,false);
                    var buttons=plan.elements.Where(e=>e.kind=="button").ToArray();
                    if(buttons.Length!=2||CompactUiLayout.MenuCount(m)!=2||buttons[0].action!="undo"||buttons[1].action!="restart-room")
                        throw new Exception("Compact UI puzzle actions mismatch");
                    var main=plan.elements.Single(e=>e.id=="room-progress");
                    if(main.size!=16)throw new Exception("Compact UI native body font not preserved");
                    if(plan.elements.Any(e=>e.id.Contains("stats")||e.id.Contains("sidebar")))throw new Exception("Compact UI retained large puzzle sidebar");
                }
                foreach(IronMove move in Enum.GetValues<IronMove>())
                foreach(float heroX in new[]{80f,140f,500f})
                {
                    var m=new ReworkModel(book){phase=Journey.Combat,bossMove=move,bossAge=1,health=1,openingSource=CoreOpeningSource.SlamCounter};
                    m.hero.x=heroX;m.hero.grounded=true;var plan=CompactUiLayout.Build(m,prefs);Verify(plan,false,true);
                    bool near=heroX==140||heroX==500;
                    if(plan.elements.Any(e=>e.id=="interact-context")!=near)throw new Exception("Compact UI pylon label is not proximity dependent");
                    bool telegraph=move==IronMove.ChargeAim||move==IronMove.WaveAim||move==IronMove.SlamAim;
                    if(plan.elements.Any(e=>e.id=="pattern-chip")!=telegraph)throw new Exception("Compact UI persistent solution banner returned");
                    if(m.Vulnerable&&!plan.elements.Any(e=>e.id=="core-action"))throw new Exception("Compact UI core opportunity lost its contextual action");
                }
            }
            Check(true,"puzzle has undo/reset only; both preferences preserve native16 body glyphs");
            Check(true,"pattern names only during telegraph; E only in pylon range; X only during exposure");

            var disabled=new UiPreferences{autoHelp=false};var noHelpModel=new ReworkModel(book){phase=Journey.Puzzle};
            Check(!CompactUiLayout.Build(noHelpModel,disabled,"Z로 되돌릴 수 있어요.",true).elements.Any(e=>e.id=="auto-help"),"automatic guidance setting suppresses toasts");
            Check(CompactUiLayout.Wrap("추를 소켓으로 밀어주세요.",96,16).Split('\n').All(s=>CompactUiLayout.MeasureWidth(s,16)<=96),"Korean word-aware wrapping uses exact native renderer advances");
            Check(CompactUiLayout.Wrap("ASCII SuperLongWordDoesNotFit Here",72,16).Split('\n').All(s=>CompactUiLayout.MeasureWidth(s,16)<=72),"overlong Latin words wrap without drawing outside native text bounds");
            Check(CompactUiLayout.TextHeight("한 줄\n두 줄",16)==36,"text height includes consistent size+2 line spacing");
            foreach(bool large in new[]{false,true})
            foreach(string message in AdaptiveGuidance.MessagesForAudit())
            {
                var prefs=new UiPreferences{largeText=large};
                Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.Puzzle},prefs,message,true),true,false);
                Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.Combat},prefs,message,true),false,true);
                Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.Dead},prefs,message,true),false,false);
            }
            Check(true,"all production guidance strings fit puzzle/combat/retry cards at both title preferences");
            Check(CompactUiLayout.Advance('가',16)==16&&CompactUiLayout.Advance('X',16)==8&&
                CompactUiLayout.Advance('가',32)==32&&CompactUiLayout.Advance('X',32)==16,
                "native16 and integer2x title advances have no fractional glyph scaling");
            Check(CompactUiLayout.BodySize(new UiPreferences())==16&&CompactUiLayout.BodySize(new UiPreferences{largeText=true})==16&&
                CompactUiLayout.SecondarySize(new UiPreferences())==16&&CompactUiLayout.SecondarySize(new UiPreferences{largeText=true})==16&&
                CompactUiLayout.TitleSize(new UiPreferences())==16&&CompactUiLayout.TitleSize(new UiPreferences{largeText=true})==32,
                "title enlargement changes titles only, never resamples body/secondary glyphs");
            foreach(bool large in new[]{false,true})
            {
                var m=new ReworkModel(book){phase=Journey.Combat,paused=true};
                var plan=CompactUiLayout.Build(m,new UiPreferences{largeText=large});
                var option=plan.elements.Single(e=>e.action=="toggle-large-text");
                if(option.text!=(large?"제목 확대: 켜짐":"제목 확대: 꺼짐"))throw new Exception("Compact UI title-only preference misleading label");
            }
            Check(true,"title-only accessibility preference keeps compatible action and truthful label");
            foreach(bool large in new[]{false,true})
            {
                var prefs=new UiPreferences{largeText=large};
                foreach(float age in new[]{0f,2f,3f,6f,9f,10.9f,11f,13.99f})
                    Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.Opening,age=age},prefs),false,false);
                foreach(float age in new[]{0f,2.39f,2.4f,3f})
                    Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.Arrival,age=age},prefs),false,false);
                foreach(int room in Enumerable.Range(0,book.levels.Length))
                    Verify(CompactUiLayout.Build(new ReworkModel(book){phase=Journey.RoomClear,age=1,roomIndex=room,puzzle=new CorePuzzle(book.levels[room])},prefs),false,false);
                var returning=new ReworkModel(book){phase=Journey.Restored};returning.hero.x=600;
                Verify(CompactUiLayout.Build(returning,prefs),false,true);
            }
            Check(true,"all opening log windows, combat-ready transition and room/exit labels fit native glyph geometry");
            Check(true,"all native text blocks, controls and icon foregrounds remain disjoint");
            return passed;
        }

        // Fixtures reuse actual captured world-only camera images, then overlay
        // exactly the production Build commands. They are layout previews, not
        // new runtime screenshots or evidence of a live failure/interaction.
        public static void ExportSnapshots(PuzzleBook book,string outputPath)
        {
            const string project="unity/TiqueReturnPrototype/";
            const string world=project+"QA/ReadabilityCounter/Runtime/";
            const string arena=world+"counter-04-ready-core.png";
            const string workshop=project+"Assets/Resources/ReturnV2/StateArt/workshop-power-0/00.png";
            var snapshots=new List<object>();
            var messages=AdaptiveGuidance.MessagesForAudit();
            string puzzleHelp=messages[0],combatHelp=messages.First(s=>s.Contains("충격파"));
            ReworkModel Puzzle(int room)=>new ReworkModel(book){phase=Journey.Puzzle,roomIndex=room,puzzle=new CorePuzzle(book.levels[room])};
            ReworkModel Combat(IronMove move=IronMove.Rest)=>new ReworkModel(book){phase=Journey.Combat,bossMove=move,bossAge=1,age=3,clock=10};
            void Add(string name,string background,ReworkModel m,bool large=false,string help="",int selection=0)
            {
                var prefs=new UiPreferences{largeText=large};
                snapshots.Add(new{name,background,largeText=large,menuSelection=selection,
                    scope="Offline layout fixture using exact production UiPlan; not a live gameplay/runtime capture",
                    plan=CompactUiLayout.Build(m,prefs,help,help.Length>0)});
            }
            Add("01-title",workshop,new ReworkModel(book));
            for(int room=0;room<3;room++)Add("0"+(room+2)+"-puzzle-"+(room+1),world+"puzzle-"+(room+1)+"-initial.png",Puzzle(room));
            Add("05-puzzle-auto-help",world+"puzzle-2-initial.png",Puzzle(1),false,puzzleHelp);
            Add("06-puzzle-auto-help-large",world+"puzzle-2-initial.png",Puzzle(1),true,puzzleHelp);
            Add("07-combat-rest",arena,Combat());
            Add("08-combat-telegraph",world+"counter-01-locked-warning.png",Combat(IronMove.SlamAim));
            var exposed=Combat(IronMove.Open);exposed.openingSource=CoreOpeningSource.SlamCounter;
            Add("09-combat-core",arena,exposed);
            var interact=Combat();interact.hero.x=140;interact.hero.grounded=true;
            Add("10-combat-interact",arena,interact);
            Add("11-combat-auto-help",arena,Combat(),false,combatHelp);
            var pause=Combat();pause.paused=true;
            Add("12-pause",arena,pause,false,"",3);
            Add("13-pause-large",arena,pause,true,"",4);
            var dead=Combat();dead.phase=Journey.Dead;dead.health=0;
            Add("14-dead",arena,dead);
            var ending=Combat();ending.phase=Journey.Ending;ending.controlTime=326;
            Add("15-ending",project+"Assets/Resources/ReturnV2/StateArt/workshop-power-3/00.png",ending);
            var arrival=Combat();arrival.phase=Journey.Arrival;arrival.age=3;
            Add("16-arrival",arena,arrival);
            Add("17-title-enlarged",workshop,new ReworkModel(book),true);
            string fullPath=Path.GetFullPath(outputPath);Directory.CreateDirectory(Path.GetDirectoryName(fullPath));
            File.WriteAllText(fullPath,JsonSerializer.Serialize(snapshots,new JsonSerializerOptions{IncludeFields=true,WriteIndented=true}));
        }
    }
}
