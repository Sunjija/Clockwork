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
