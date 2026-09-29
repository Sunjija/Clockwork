using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using TiqueReturn;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ReturnBuild
{
    const string Scene = "Assets/Scenes/TiqueReturn.unity";
    [MenuItem("Tique Return/Build Windows Prototype")]
    public static void Build()
    {
        Configure();
        RunChecks();
        EnsureScene();
        string[] args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"--return-output");
        string output=n>=0&&n+1<args.Length?args[n+1]:"Builds/Windows/TiqueReturn.exe";
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions {scenes=new[]{Scene},locationPathName=output,target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
        Debug.Log("RETURN_BUILD "+report.summary.result+" bytes="+report.summary.totalSize);
        if(report.summary.result!=BuildResult.Succeeded)throw new Exception("Windows build failed: "+report.summary.result);
    }
    [MenuItem("Tique Return/Open Prototype Scene")]
    public static void OpenScene()
    {
        if(!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())return;
        Configure();EnsureScene();EditorSceneManager.OpenScene(Scene);
    }
    static void Configure()
    {
        PlayerSettings.companyName="Clockwork";PlayerSettings.productName="Tique Return";
        PlayerSettings.defaultScreenWidth=1280;PlayerSettings.defaultScreenHeight=720;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;PlayerSettings.resizableWindow=true;
        PlayerSettings.runInBackground=true;
        PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
        var settings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
        var input=settings.FindProperty("activeInputHandler");if(input!=null){input.intValue=0;settings.ApplyModifiedPropertiesWithoutUndo();}
        foreach(string path in Directory.GetFiles("Assets/Resources/Return","*.png",SearchOption.AllDirectories))
        {
            string p=path.Replace('\\','/');var importer=(TextureImporter)AssetImporter.GetAtPath(p);
            importer.textureType=TextureImporterType.Default;importer.filterMode=FilterMode.Point;
            importer.mipmapEnabled=false;importer.wrapMode=TextureWrapMode.Clamp;importer.textureCompression=TextureImporterCompression.Uncompressed;
            importer.alphaIsTransparency=true;importer.npotScale=TextureImporterNPOTScale.None;importer.maxTextureSize=1024;
            importer.SaveAndReimport();
        }
        AssetDatabase.SaveAssets();
    }
    static void EnsureScene()
    {
        if(File.Exists(Scene))
        {
            EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Scene,true)};
            return;
        }
        Directory.CreateDirectory("Assets/Scenes");
        var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
        new GameObject("Tique Return - Game").AddComponent<ReturnGame>();
        EditorSceneManager.SaveScene(scene,Scene);
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Scene,true)};
        AssetDatabase.SaveAssets();
    }
    static void Assert(bool result,string text){if(!result)throw new Exception("RETURN_CHECK FAILED: "+text);}
    static ReturnModel Puzzle(){var m=new ReturnModel();m.Start();return m;}
    [MenuItem("Tique Return/Run Model Checks")]
    public static void RunChecks()
    {
        var results=ReturnChecks.Run(s=>Debug.Log(s));
        Action<string,Action> check=(name,test)=>{test();results.Add(name);Debug.Log("RETURN_CHECK PASS "+name);};
        ClipFile clips=JsonUtility.FromJson<ClipFile>(Resources.Load<TextAsset>("Return/clips").text);
        var durations=clips.clips.ToDictionary(c=>c.name,c=>c.durations);
        check("all imported Tique frames and pose indices valid",()=>{
            foreach(ClipSpec clip in clips.clips)for(int i=0;i<clip.durations.Length;i++)
            {var t=Resources.Load<Texture2D>("Return/Tique/"+clip.name+"/"+i.ToString("00"));Assert(t!=null&&t.width==64&&t.height==64,"native frame");}
            var m=Puzzle();for(int n=0;n<1800;n++){m.Tick(1f/120,new Command{axis=n%240<120?1:-1,jump=n%90==0,attack=n%77==0,dash=n%140==0});string p=m.Pose(durations,out int f);Assert(f>=0&&f<durations[p].Length,"pose bounds");}
        });
        Directory.CreateDirectory("QA");
        File.WriteAllText("QA/unity-import-checks.json","{\"passed\":true,\"count\":"+results.Count+",\"checks\":["+string.Join(",",results.Select(s=>"\""+s+"\""))+"]}");
    }
}
