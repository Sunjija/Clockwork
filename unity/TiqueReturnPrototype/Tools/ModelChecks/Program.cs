using System.Text.Json;
using TiqueReturn;

string root = Path.GetFullPath(args.Length > 0 ? args[0] : "../..");
string qa = Path.Combine(root, "QA");
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
var v2Checks=ReworkChecks.Run(book,Console.WriteLine);
var v2=new ReworkModel(book);var v2Pilot=new ReworkPilot();
for(int n=0;n<120*210&&v2.phase!=Journey.Ending&&v2.phase!=Journey.Dead;n++)v2.Tick(1f/120,v2Pilot.Next(v2));
Directory.CreateDirectory(Path.Combine(qa,"V2"));
File.WriteAllText(Path.Combine(qa,"V2/model-result.json"),JsonSerializer.Serialize(new{passed=v2.phase==Journey.Ending,phase=v2.phase.ToString(),v2.health,v2.bossHealth,v2.breaks,v2.playTime,checks=v2Checks,events=v2.events},jsonOptions));
Assert(v2.phase==Journey.Ending,"V2 input-only playthrough ended in "+v2.phase+" hp="+v2.health+" boss="+v2.bossHealth);
Assert(v2.breaks>=3,"At least three armor breaks required");
Assert(v2.events.Any(e=>e.EndsWith(":wave-release"))&&v2.events.Any(e=>e.EndsWith(":boss-Slam")),"All boss patterns exercised");
Console.WriteLine($"V2 PASS {v2Checks.Count} checks + complete input playthrough; HP {v2.health}/5, time {v2.playTime:F2}s.");

var authored=JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(Path.Combine(root,"Assets/Resources/ReturnV2/WardenAuthored/clips.json")),jsonOptions);
var bossTimes=authored.clips.ToDictionary(c=>"iron-"+c.name,c=>c.durations);
var visual=new ReworkModel(book);
int selections=0;
foreach(bool assist in new[]{false,true})
foreach(IronMove move in Enum.GetValues<IronMove>())
foreach(string sequence in new[]{"attack","charge","slam","stagger"})
{
    visual.assisted=assist;visual.bossMove=move;visual.bossSequence=sequence;visual.bossHealth=3;
    for(int i=0;i<1200;i++)
    {
        visual.bossAge=i/120f;int frame=WardenAnimation.Select(visual,bossTimes,out string clip);
        Assert(frame>=0&&frame<bossTimes[clip].Length,"Guardian frame outside clip");selections++;
    }
}
visual.bossMove=IronMove.Wave;visual.bossAge=0;
Assert(WardenAnimation.Select(visual,bossTimes,out var waveClip)==4&&waveClip=="iron-attack","Wave release must show bite impact");
visual.bossAge=1.1f;Assert(WardenAnimation.Select(visual,bossTimes,out _) ==4,"Second wave must show second bite");
visual.bossMove=IronMove.Recover;visual.bossSequence="slam";visual.bossAge=0;
Assert(WardenAnimation.Select(visual,bossTimes,out var slamClip)==10&&slamClip=="iron-slam","Ground contact must show landing pose");
visual.bossAge=.84f;Assert(WardenAnimation.Select(visual,bossTimes,out _)==14,"Landing returns to exact base");
visual.bossMove=IronMove.Open;visual.bossAge=3;
Assert(WardenAnimation.Select(visual,bossTimes,out _)==6,"Exposed armor holds open, does not close mid-window");
visual.bossMove=IronMove.Rest;Assert(WardenAnimation.Select(visual,bossTimes,out _)==0,"Idle holds canonical base");
var lift=new ReworkModel(book);lift.BeginArena();lift.phase=Journey.Combat;lift.bossMove=IronMove.SlamAim;
for(int i=0;i<12;i++)lift.Tick(1f/120,ReworkCommand.Empty);
Assert(lift.bossY==ReworkModel.Floor,"Landing attack must brace before leaving floor");
for(int i=0;i<12;i++)lift.Tick(1f/120,ReworkCommand.Empty);
Assert(lift.bossY<ReworkModel.Floor,"Lift follows the 130ms brace exposures");
Directory.CreateDirectory(Path.Combine(qa,"V3"));
File.WriteAllText(Path.Combine(qa,"V3/animation-model-checks.json"),JsonSerializer.Serialize(new{passed=true,selections,frames=authored.clips.Sum(c=>c.durations.Length),waveReleaseFrame=4,landingFrame=10,exposedHoldFrame=6,braceMs=130,scope="Pure C# frame selection; subjective motion quality is not certified"},jsonOptions));
Console.WriteLine($"PASS guardian authored clips: {selections} state/time selections, wave impact, landing, open hold, static idle and grounded brace.");

var states=JsonSerializer.Deserialize<ClipFile>(File.ReadAllText(Path.Combine(root,"Assets/Resources/ReturnV2/StateArt/clips.json")),jsonOptions);
var stateChecks=WorldArtChecks.Run(book,states);
Directory.CreateDirectory(Path.Combine(qa,"V4"));
File.WriteAllText(Path.Combine(qa,"V4/state-model-checks.json"),JsonSerializer.Serialize(new{passed=true,checks=stateChecks,states=states.clips.Length,frames=states.clips.Sum(c=>c.durations.Length)},jsonOptions));
foreach(string check in stateChecks)Console.WriteLine("STATE PASS "+check);
