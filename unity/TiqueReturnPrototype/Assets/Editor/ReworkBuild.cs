using System;
using System.IO;
using TiqueReturn;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ReworkBuild
{
    const string Scene="Assets/Scenes/TiqueReturnV2.unity";
    [MenuItem("Tique Return/Build Reworked Prototype")]
    public static void Build()
    {
        Configure();
        var book=JsonUtility.FromJson<PuzzleBook>(Resources.Load<TextAsset>("ReturnV2/puzzles").text);
        ReworkChecks.Run(book,s=>Debug.Log(s));
        EnsureScene();
        string[] args=Environment.GetCommandLineArgs();int n=Array.IndexOf(args,"--return-output");
        string output=n>=0&&n+1<args.Length?args[n+1]:"Builds/WindowsV3/TiqueReturn.exe";
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{Scene},locationPathName=output,target=BuildTarget.StandaloneWindows64,options=BuildOptions.None});
        Debug.Log("RETURN_V2_BUILD "+report.summary.result+" bytes="+report.summary.totalSize);
        if(report.summary.result!=BuildResult.Succeeded)throw new Exception("V2 Windows build failed");
    }
    static void Configure()
    {
        PlayerSettings.companyName="Clockwork";PlayerSettings.productName="Tique - Return Circuit";
        PlayerSettings.defaultScreenWidth=1280;PlayerSettings.defaultScreenHeight=720;
        PlayerSettings.fullScreenMode=FullScreenMode.Windowed;PlayerSettings.resizableWindow=true;PlayerSettings.runInBackground=true;
        PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
        var settings=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset")[0]);
        var input=settings.FindProperty("activeInputHandler");if(input!=null){input.intValue=0;settings.ApplyModifiedPropertiesWithoutUndo();}
        foreach(string path in Directory.GetFiles("Assets/Resources/ReturnV2","*.png",SearchOption.AllDirectories))
        {
            var importer=(TextureImporter)AssetImporter.GetAtPath(path.Replace('\\','/'));
            importer.textureType=TextureImporterType.Default;importer.filterMode=FilterMode.Point;importer.mipmapEnabled=false;
            importer.wrapMode=TextureWrapMode.Clamp;importer.textureCompression=TextureImporterCompression.Uncompressed;
            importer.alphaIsTransparency=true;importer.npotScale=TextureImporterNPOTScale.None;importer.maxTextureSize=1024;importer.SaveAndReimport();
        }
        AssetDatabase.SaveAssets();
    }
    [MenuItem("Tique Return/Open Reworked Prototype")]
    public static void Open(){if(!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())return;EnsureScene();EditorSceneManager.OpenScene(Scene);}
    static void EnsureScene()
    {
        if(!File.Exists(Scene))
        {
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            new GameObject("Tique Return V2").AddComponent<ReworkGame>();EditorSceneManager.SaveScene(scene,Scene);
        }
        EditorBuildSettings.scenes=new[]{new EditorBuildSettingsScene(Scene,true)};AssetDatabase.SaveAssets();
    }
}
