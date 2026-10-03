using System.Text.Json;
using TiqueReturn;

string root = Path.GetFullPath(args.Length > 0 ? args[0] : "../..");
// Optional isolated output root prevents a targeted art audit from replacing
// earlier production evidence. With no second argument, keep the legacy path.
string qa = Path.GetFullPath(args.Length > 1 ? args[1] : Path.Combine(root, "QA"));
Directory.CreateDirectory(qa);
var passed = ReturnChecks.Run(Console.WriteLine);
var jsonOptions = new JsonSerializerOptions { IncludeFields = true, WriteIndented = true };
var clips = JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(Path.Combine(root,"Assets/Resources/Return/clips.json")),jsonOptions);
var durations = clips.clips.ToDictionary(c=>c.name,c=>c.durations);
void Assert(bool result,string message){if(!result)throw new Exception(message);}
void PoseCheck(ReturnModel m)
{
    string pose=m.Pose(durations,out int frame);
    Assert(frame>=0&&frame<durations[pose].Length,"Out-of-bounds frame: "+pose+" "+frame);
}
var stress = new ReturnModel();stress.Start();
for(int n=0;n<3600;n++)
{
    stress.Tick(1f/120,new Command {axis=n%240<120?1:-1,jump=n%90==0,attack=n%77==0,dash=n%140==0});
    PoseCheck(stress);
}
passed.Add("30 seconds of mixed input keeps all animation indices valid");
var m = new ReturnModel();
var pilot = new ReturnPilot();
var snapshots = new List<object>();
string previous = "";
for(int n=0;n<120*180&&m.phase!=Phase.Ending&&m.phase!=Phase.Dead;n++)
{
    m.Tick(1f/120,pilot.Next(m));PoseCheck(m);
    string key=m.phase+"/"+m.bossMove+"/"+m.overload;
    if(previous!=key)
    {
        snapshots.Add(new { tick=n, phase=m.phase.ToString(), boss=m.bossMove.ToString(), m.x,m.y,m.hp,m.overload,m.aimX,m.arenaMagnet });
        previous=key;
    }
}
File.WriteAllText(Path.Combine(qa,"model-playthrough.json"),JsonSerializer.Serialize(new {
    scope="Pure C# production model with ordinary input commands; not a Unity runtime test",
    passed=m.phase==Phase.Ending, finalPhase=m.phase.ToString(), m.hp, m.playTime,
    snapshots, events=m.events
},jsonOptions));
Assert(m.phase==Phase.Ending,"Playthrough ended in "+m.phase+", HP "+m.hp+", overload "+m.overload);
Assert(m.events.Any(e=>e.EndsWith(":magnet-capture")),"Playthrough must exercise optional magnet capture");
Assert(m.events.Any(e=>e.EndsWith(":practice-hit")),"Playthrough must exercise the practice terminal");
Assert(m.events.Any(e=>e.EndsWith(":dash")),"Playthrough must dodge with dash");
Assert(m.events.Any(e=>e.EndsWith(":jump")),"Playthrough must jump over a floor wave");
Assert(m.hp==4,"Scripted playthrough should finish without damage");
passed.Add("input-only puzzle, practice, magnet trap, dash, wave jump, six hits, rescan, ending");
File.WriteAllText(Path.Combine(qa,"model-checks.json"),JsonSerializer.Serialize(new {
    passed=true, count=passed.Count, scope="Same C# model used by Unity; renderer, assets and input devices excluded", checks=passed
},jsonOptions));
Console.WriteLine($"PASS {passed.Count} checks; input-only playthrough {m.playTime:F2}s, HP {m.hp}/4. Unity runtime still unverified.");

var book=JsonSerializer.Deserialize<PuzzleBook>(File.ReadAllText(Path.Combine(root,"Assets/Resources/ReturnV2/puzzles.json")),jsonOptions);
var guidanceChecks=AdaptiveGuidanceChecks.Run(book,Console.WriteLine);
var uiChecks=CompactUiLayoutChecks.Run(book,Console.WriteLine);
Directory.CreateDirectory(Path.Combine(qa,"CompactUi"));
CompactUiLayoutChecks.ExportSnapshots(book,Path.Combine(qa,"CompactUi/draw-plan-fixtures.json"));
File.WriteAllText(Path.Combine(qa,"CompactUi/layout-checks.json"),JsonSerializer.Serialize(new{passed=true,count=uiChecks.Count,checks=uiChecks,scope="Shared production draw-plan geometry/text/actions; offline layout, not live Unity GUI"},jsonOptions));
File.WriteAllText(Path.Combine(qa,"CompactUi/guidance-checks.json"),JsonSerializer.Serialize(new{passed=true,count=guidanceChecks.Count,checks=guidanceChecks,scope="Read-only automatic support layer over actual puzzle/combat models; not a Unity runtime test"},jsonOptions));
var v2Checks=ReworkChecks.Run(book,Console.WriteLine);
var v2=new ReworkModel(book);var v2Pilot=new ReworkPilot();
for(int n=0;n<120*210&&v2.phase!=Journey.Ending&&v2.phase!=Journey.Dead;n++)v2.Tick(1f/120,v2Pilot.Next(v2));
Directory.CreateDirectory(Path.Combine(qa,"V2"));
File.WriteAllText(Path.Combine(qa,"V2/model-result.json"),JsonSerializer.Serialize(new{passed=v2.phase==Journey.Ending,phase=v2.phase.ToString(),v2.health,v2.bossHealth,v2.breaks,v2.playTime,checks=v2Checks,events=v2.events},jsonOptions));
Assert(v2.phase==Journey.Ending,"V2 input-only playthrough ended in "+v2.phase+" hp="+v2.health+" boss="+v2.bossHealth);
Assert(v2.breaks>=1,"Input-only mixed route must still exercise a pillar armor break");
Assert(v2.events.Any(e=>e.EndsWith(":wave-release"))&&v2.events.Any(e=>e.EndsWith(":boss-Slam")),"All boss patterns exercised");
Console.WriteLine($"V2 PASS {v2Checks.Count} checks + complete input playthrough; HP {v2.health}/5, time {v2.playTime:F2}s.");

string guardianVersion=File.Exists(Path.Combine(root,"Assets/Resources/ReturnV2/WardenV8/clips.json"))?"V8":"V7";
var authored=JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(Path.Combine(root,"Assets/Resources/ReturnV2/Warden"+guardianVersion+"/clips.json")),jsonOptions);
var bossTimes=authored.clips.ToDictionary(c=>"iron-"+c.name,c=>c.durations);
Assert(bossTimes["iron-boot"].Sum()==2400,"Boot keeps the 2.4s arrival");
var visual=new ReworkModel(book);
int selections=0;
foreach(bool assist in new[]{false,true})
foreach(IronMove move in Enum.GetValues<IronMove>())
foreach(string sequence in new[]{"attack","charge","slam","stagger"})
{
    visual.assisted=assist;visual.bossMove=move;visual.bossSequence=sequence;visual.bossHealth=3;
    for(int i=0;i<1200;i++)
    {
        visual.bossAge=visual.age=visual.clock=i/120f;int frame=WardenAnimation.Select(visual,bossTimes,out string clip);
        Assert(frame>=0&&frame<bossTimes[clip].Length,"Guardian frame outside clip "+clip);selections++;
    }
}
visual.assisted=false;visual.bossHealth=9;
int Pick(IronMove move,float age,string sequence,out string clip){visual.bossMove=move;visual.bossSequence=sequence;visual.bossAge=visual.age=age;return WardenAnimation.Select(visual,bossTimes,out clip);}
Assert(Pick(IronMove.Wave,0,"attack",out var waveClip)==0&&waveClip=="iron-wave-strike","Wave release shows the jaw hitting the floor");
visual.bossHealth=3;Assert(Pick(IronMove.Wave,1.1f,"attack",out _)==0,"Second phase-three wave shows a second jaw strike");visual.bossHealth=9;
Assert(Pick(IronMove.WaveAim,.6f,"attack",out _)==2&&Pick(IronMove.WaveAim,1.03f,"attack",out _)==3,"Wave telegraph holds the rear-up, swings down in the last 30ms");
Assert(Pick(IronMove.ChargeAim,1.2f,"charge",out var aimClip)==2&&aimClip=="iron-charge-aim","Charge telegraph holds the curled ball");
Assert(Pick(IronMove.SlamAim,.12f,"slam",out _)<=1,"Slam stays on the grounded crouch for the 130ms brace");
Assert(Pick(IronMove.Recover,0,"slam",out var slamClip)==0&&slamClip=="iron-slam-land","Ground contact shows the authored landing pose");
Assert(Pick(IronMove.Recover,.84f,"slam",out _)==2,"Landing ends on the idle stance");
Assert(Pick(IronMove.Open,3,"stagger",out var openClip)==3&&openClip=="iron-stagger-open","Exposed core pose holds for the whole window");
visual.openingSource=CoreOpeningSource.SlamCounter;
Assert(Pick(IronMove.CounterSettle,.1f,"slam",out var settleClip)==0&&settleClip=="iron-slam-land","Counter settle holds authored landing pose");
Assert(Pick(IronMove.Open,ReworkModel.CounterOpenWarmup,"stagger",out _)==3,"Counter attack permission starts on the held authored core pose");
Assert(Pick(IronMove.Open,ReworkModel.CounterOpenWarmup-.01f,"stagger",out _)<3,"Counter preparation runs forward through authored transition");
visual.openingSource=CoreOpeningSource.None;
Assert(Pick(IronMove.Recover,0,"charge",out var crashClip)==0&&crashClip=="iron-charge-crash","Plain wall crash recoils");
Assert(Pick(IronMove.Down,2,"stagger",out _)==bossTimes["iron-defeat"].Length-1,"Defeat holds the collapsed frame");
visual.clock=.5f;Assert(Pick(IronMove.Rest,0,"charge",out var idleClip)>=0&&idleClip=="iron-idle","Rest selects the authored idle loop");
var lift=new ReworkModel(book);lift.BeginArena();lift.phase=Journey.Combat;lift.bossMove=IronMove.SlamAim;
for(int i=0;i<12;i++)lift.Tick(1f/120,ReworkCommand.Empty);
Assert(lift.bossY==ReworkModel.Floor,"Landing attack must brace before leaving floor");
for(int i=0;i<12;i++)lift.Tick(1f/120,ReworkCommand.Empty);
Assert(lift.bossY<ReworkModel.Floor,"Lift follows the 130ms brace exposures");
Directory.CreateDirectory(Path.Combine(qa,guardianVersion));
File.WriteAllText(Path.Combine(qa,guardianVersion,"animation-model-checks.json"),JsonSerializer.Serialize(new{passed=true,selections,clips=authored.clips.Length,frames=authored.clips.Sum(c=>c.durations.Length),resourceVersion=guardianVersion,scope="Pure C# frame selection over Warden"+guardianVersion+"; game execution and subjective motion approval excluded"},jsonOptions));
// Trace one input-only fight for the offline preview (tools render it with the real frames).
var trace=new ReworkModel(book);var tracePilot=new ReworkPilot();var rows=new List<object>();
for(int n=0;n<120*240&&trace.phase!=Journey.Ending;n++)
{
    trace.Tick(1f/120,tracePilot.Next(trace));
    if(!trace.InArena||n%4!=0)continue;
    string clip;int frame;
    if(trace.phase==Journey.Arrival){clip="iron-boot";frame=WardenAnimation.FrameAt(bossTimes[clip],Math.Min(2.399f,trace.age));}
    else frame=WardenAnimation.Select(trace,bossTimes,out clip);
    rows.Add(new{t=Math.Round(trace.clock,3),phase=trace.phase.ToString(),move=trace.bossMove.ToString(),clip,frame,bx=Math.Round(trace.bossX,1),by=Math.Round(trace.bossY,1),face=trace.bossFacing,
        hx=Math.Round(trace.hero.x,1),hy=Math.Round(trace.hero.y,1),hf=trace.hero.facing,flash=trace.Vulnerable&&trace.clock-trace.lastCoreHitAt<.14f,waves=trace.waves.Select(w=>Math.Round(w.x)).ToArray()});
}
File.WriteAllText(Path.Combine(qa,guardianVersion,"fight-trace.json"),JsonSerializer.Serialize(rows));
Console.WriteLine($"PASS guardian {guardianVersion} clips: {selections} state/time selections, wave impact, telegraph holds, slam brace/landing, core hold, crash, defeat, idle; trace {rows.Count} rows.");

var states=JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(Path.Combine(root,"Assets/Resources/ReturnV2/StateArt/clips.json")),jsonOptions);
var stateChecks=WorldArtChecks.Run(book,states);
Directory.CreateDirectory(Path.Combine(qa,"V4"));
File.WriteAllText(Path.Combine(qa,"V4/state-model-checks.json"),JsonSerializer.Serialize(new{passed=true,checks=stateChecks,states=states.clips.Length,frames=states.clips.Sum(c=>c.durations.Length)},jsonOptions));
foreach(string check in stateChecks)Console.WriteLine("STATE PASS "+check);

Directory.CreateDirectory(Path.Combine(qa,"WorkOrderV01"));
var orderResult=WorkOrderChecks.Run(book);
File.WriteAllText(Path.Combine(qa,"WorkOrderV01/model-checks.json"),JsonSerializer.Serialize(orderResult,jsonOptions));
Console.WriteLine("PASS work order model checks");

// While art is being authored the original manifest is a compatible fallback;
// final verification records the actual manifest used, rather than assuming it.
string tiqueManifest = Path.Combine(root,"Assets/Resources/ReturnV2/TiqueV10/clips.json");
if(!File.Exists(tiqueManifest)) tiqueManifest = Path.Combine(root,"Assets/Resources/ReturnV2/TiqueV9/clips.json");
if(!File.Exists(tiqueManifest)) tiqueManifest = Path.Combine(root,"Assets/Resources/ReturnV2/TiqueV8/clips.json");
if(!File.Exists(tiqueManifest)) tiqueManifest = Path.Combine(root,"Assets/Resources/Return/clips.json");
var tiqueClips = JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(tiqueManifest),jsonOptions);
var tiqueTimes = tiqueClips.clips.ToDictionary(c=>c.name,c=>c.durations);
var tiqueResult = TiqueAnimationChecks.Run(book,tiqueTimes);
string tiqueRevision=tiqueManifest.Contains("TiqueV10")?"V10":tiqueManifest.Contains("TiqueV9")?"V9":"V8";
Directory.CreateDirectory(Path.Combine(qa,tiqueRevision));
File.WriteAllText(Path.Combine(qa,tiqueRevision,"animation-model-checks.json"),JsonSerializer.Serialize(new{manifest=tiqueManifest,result=tiqueResult},jsonOptions));
Console.WriteLine("PASS Tique animation selector checks; manifest "+tiqueManifest);
