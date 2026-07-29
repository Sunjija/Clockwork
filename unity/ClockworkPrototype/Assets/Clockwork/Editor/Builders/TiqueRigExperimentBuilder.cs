using System;
using System.IO;
using System.Linq;
using Clockwork;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace ClockworkEditor
{
    public static class TiqueRigExperimentBuilder
    {
        private const string Root = "Assets/Clockwork";
        private const string PartRoot = Root + "/Art/Tique/RigExperiment/Parts";
        private const string BakedRoot = Root + "/Art/Tique/RigExperiment/Baked";
        private const string PrefabPath = Root + "/Prefabs/TiqueRigidRigExperiment.prefab";
        private const string ScenePath = Root + "/Scenes/TiqueRigExperiment.unity";
        private const string ApprovedRoot = Root + "/Art/Tique/Approved";
        private const string BackgroundPath = Root
            + "/Art/Environment/ACT1OpeningCaligo/RegisteredCaligoVillagePlazaV5/00-plaza-approach-environment.png";
        private const float DisplayScale = 0.22f;

        [MenuItem("Clockwork/Art/Build Tique Rig Experiment")]
        public static void BuildExperiment()
        {
            ConfigurePartTextures();
            GameObject prefab = BuildRigPrefab();
            BakeFrames(prefab);
            ConfigureBakedTextures();
            BuildComparisonScene(prefab);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("CLOCKWORK_TIQUE_RIG_ASSETS_OK");
        }

        public static void BuildAllFromCommandLine()
        {
            BuildExperiment();
            string outputPath = ReadArgument("-clockworkTiqueRigBuildPath");
            if (string.IsNullOrWhiteSpace(outputPath))
                outputPath = Path.GetFullPath(Path.Combine(Application.dataPath,
                    "../../Builds/ClockworkTiqueRigExperiment.exe"));

            Directory.CreateDirectory(Path.GetDirectoryName(outputPath) ?? ".");
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.runInBackground = true;

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = outputPath,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
                throw new InvalidOperationException("Tique rig experiment build failed: "
                    + report.summary.result);

            Debug.Log($"CLOCKWORK_TIQUE_RIG_BUILD_OK {report.summary.totalSize} {outputPath}");
        }

        private static void ConfigurePartTextures()
        {
            ConfigureTexture(PartRoot + "/body.png",
                new Vector2(0.5f, 32f / 512f), SpriteMeshType.Tight);
            ConfigureTexture(PartRoot + "/far-arm.png",
                new Vector2(0.5f, 0.94f), SpriteMeshType.Tight);
            ConfigureTexture(PartRoot + "/near-arm.png",
                new Vector2(0.5f, 0.94f), SpriteMeshType.Tight);
            ConfigureTexture(PartRoot + "/far-leg.png",
                new Vector2(0.45f, 0.9f), SpriteMeshType.Tight);
            ConfigureTexture(PartRoot + "/near-leg.png",
                new Vector2(0.45f, 0.9f), SpriteMeshType.Tight);
        }

        private static void ConfigureBakedTextures()
        {
            foreach (string path in Directory.GetFiles(ToAbsolutePath(BakedRoot), "*.png",
                         SearchOption.AllDirectories).Select(ToAssetPath))
            {
                ConfigureTexture(path, new Vector2(0.5f, 32f / 512f), SpriteMeshType.Tight);
            }
        }

        private static void ConfigureTexture(string assetPath, Vector2 pivot, SpriteMeshType meshType)
        {
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null) throw new InvalidOperationException("Missing texture: " + assetPath);
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 100f;
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.filterMode = FilterMode.Bilinear;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = 1024;
            TextureImporterSettings settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteAlignment = (int)SpriteAlignment.Custom;
            settings.spritePivot = pivot;
            settings.spriteMeshType = meshType;
            importer.SetTextureSettings(settings);
            importer.SaveAndReimport();
        }

        private static GameObject BuildRigPrefab()
        {
            Directory.CreateDirectory(ToAbsolutePath(Path.GetDirectoryName(PrefabPath)));
            GameObject rig = BuildRigObject("TiqueRigidRig");
            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(rig, PrefabPath);
            UnityEngine.Object.DestroyImmediate(rig);
            return prefab;
        }

        private static GameObject BuildRigObject(string name)
        {
            GameObject root = new GameObject(name);
            Transform farArm = CreatePart(root.transform, "Bone_FarArm", "far-arm.png",
                new Vector2(0.63f, 1.13f), 22);
            Transform farLeg = CreatePart(root.transform, "Bone_FarLeg", "far-leg.png",
                new Vector2(0.26f, 0.32f), 9);
            Transform body = CreatePart(root.transform, "Rigid_HeadBodyCore", "body.png",
                Vector2.zero, 20);
            Transform nearLeg = CreatePart(root.transform, "Bone_NearLeg", "near-leg.png",
                new Vector2(0.46f, 0.32f), 10);
            Transform nearArm = CreatePart(root.transform, "Bone_NearArm", "near-arm.png",
                new Vector2(-0.30f, 1.17f), 21);

            TiqueRigidRigExperiment rig = root.AddComponent<TiqueRigidRigExperiment>();
            rig.Configure(body, farArm, nearArm, farLeg, nearLeg);
            rig.SetManualPose(TiqueRigidRigExperiment.MotionMode.Idle, 0f);
            return root;
        }

        private static Transform CreatePart(
            Transform parent, string name, string fileName, Vector2 position, int sortingOrder)
        {
            GameObject part = new GameObject(name);
            part.transform.SetParent(parent, false);
            part.transform.localPosition = new Vector3(position.x, position.y, 0f);
            SpriteRenderer renderer = part.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(PartRoot + "/" + fileName);
            if (renderer.sprite == null) throw new InvalidOperationException("Missing rig part: " + fileName);
            renderer.sortingOrder = sortingOrder;
            return part.transform;
        }

        private static void BakeFrames(GameObject prefab)
        {
            string idleFolder = BakedRoot + "/Idle";
            string walkFolder = BakedRoot + "/Walk";
            Directory.CreateDirectory(ToAbsolutePath(idleFolder));
            Directory.CreateDirectory(ToAbsolutePath(walkFolder));

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "TiqueRigBakeTemp";
            GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (instance == null) throw new InvalidOperationException("Unable to instantiate rig prefab.");
            instance.transform.position = Vector3.zero;
            instance.transform.localScale = Vector3.one;
            TiqueRigidRigExperiment rig = instance.GetComponent<TiqueRigidRigExperiment>();

            GameObject cameraObject = new GameObject("BakeCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 2.56f;
            // The source baseline is 32 pixels above the bottom of a 640x512 canvas.
            camera.transform.position = new Vector3(0f, 2.24f, -10f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0f, 0f, 0f, 0f);
            camera.allowHDR = false;
            camera.allowMSAA = false;

            RenderTexture target = new RenderTexture(640, 512, 24, RenderTextureFormat.ARGB32,
                RenderTextureReadWrite.sRGB);
            target.Create();
            camera.targetTexture = target;

            BakeMotion(camera, target, rig, TiqueRigidRigExperiment.MotionMode.Idle, 4, idleFolder, "idle");
            BakeMotion(camera, target, rig, TiqueRigidRigExperiment.MotionMode.Walk, 12, walkFolder, "walk");

            camera.targetTexture = null;
            target.Release();
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(cameraObject);
            UnityEngine.Object.DestroyImmediate(instance);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
        }

        private static void BakeMotion(
            Camera camera,
            RenderTexture target,
            TiqueRigidRigExperiment rig,
            TiqueRigidRigExperiment.MotionMode mode,
            int frameCount,
            string folder,
            string prefix)
        {
            RenderTexture previous = RenderTexture.active;
            for (int i = 0; i < frameCount; i++)
            {
                rig.SetManualPose(mode, i / (float)frameCount);
                camera.Render();
                RenderTexture.active = target;
                Texture2D frame = new Texture2D(640, 512, TextureFormat.RGBA32, false, false);
                frame.ReadPixels(new Rect(0, 0, 640, 512), 0, 0);
                frame.Apply(false, false);
                RemoveFlatBakeBackground(frame);
                string path = ToAbsolutePath(folder + $"/{prefix}-{i + 1:00}.png");
                File.WriteAllBytes(path, frame.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(frame);
            }
            RenderTexture.active = previous;
        }

        private static void RemoveFlatBakeBackground(Texture2D frame)
        {
            Color32[] pixels = frame.GetPixels32();
            Color32 background = pixels[0];
            int foregroundPixels = 0;
            for (int i = 0; i < pixels.Length; i++)
            {
                int difference = Mathf.Max(
                    Mathf.Abs(pixels[i].r - background.r),
                    Mathf.Abs(pixels[i].g - background.g),
                    Mathf.Abs(pixels[i].b - background.b));
                pixels[i].a = difference <= 2
                    ? (byte)0
                    : (byte)Mathf.Clamp(difference * 8, 0, 255);
                if (pixels[i].a > 8) foregroundPixels++;
            }
            if (foregroundPixels < 64)
                throw new InvalidOperationException(
                    "Tique rig bake returned an empty frame. Run Unity with graphics enabled.");
            frame.SetPixels32(pixels);
            frame.Apply(false, false);
        }

        private static void BuildComparisonScene(GameObject prefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "TiqueRigExperiment";

            Light2D globalLight = new GameObject("TiqueRigExperimentGlobalLight")
                .AddComponent<Light2D>();
            globalLight.lightType = Light2D.LightType.Global;
            globalLight.intensity = 1f;
            globalLight.color = new Color(0.94f, 0.91f, 0.86f);

            Sprite backgroundSprite = AssetDatabase.LoadAssetAtPath<Sprite>(BackgroundPath);
            if (backgroundSprite == null) throw new InvalidOperationException("Missing QA background.");
            GameObject background = new GameObject("CaligoPlazaBackground");
            SpriteRenderer backgroundRenderer = background.AddComponent<SpriteRenderer>();
            backgroundRenderer.sprite = backgroundSprite;
            backgroundRenderer.sortingOrder = -100;

            const float baseline = -0.671875f;
            SpriteRenderer approved = CreateComparisonSprite("ApprovedFrames", -7.5f, baseline, 20);
            SpriteRenderer baked = CreateComparisonSprite("BakedRigFrames", -2.5f, baseline, 20);

            GameObject liveObject = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
            if (liveObject == null) throw new InvalidOperationException("Unable to instantiate live rig.");
            liveObject.name = "LiveRigidRig";
            liveObject.transform.position = new Vector3(-5f, baseline, 0f);
            liveObject.transform.localScale = Vector3.one * DisplayScale;
            TiqueRigidRigExperiment liveRig = liveObject.GetComponent<TiqueRigidRigExperiment>();

            Sprite[] approvedIdle = LoadSprites(ApprovedRoot + "/Idle");
            Sprite[] approvedWalk = LoadSprites(ApprovedRoot + "/Walk");
            Sprite[] bakedIdle = LoadSprites(BakedRoot + "/Idle");
            Sprite[] bakedWalk = LoadSprites(BakedRoot + "/Walk");
            approved.sprite = approvedIdle.FirstOrDefault();
            baked.sprite = bakedIdle.FirstOrDefault();

            TiqueRigComparisonPlayback playback = new GameObject("TiqueRigComparisonPlayback")
                .AddComponent<TiqueRigComparisonPlayback>();
            playback.Configure(approved, baked, liveRig,
                approvedIdle, approvedWalk, bakedIdle, bakedWalk);

            CreateLabel("APPROVED", new Vector2(-7.5f, 0.25f));
            CreateLabel("LIVE RIG", new Vector2(-5f, 0.25f));
            CreateLabel("BAKED FRAMES", new Vector2(-2.5f, 0.25f));

            GameObject cameraObject = new GameObject("TiqueRigExperimentCamera");
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 2.8125f;
            camera.transform.position = new Vector3(-5f, 0f, -10f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.035f, 0.045f);
            cameraObject.AddComponent<AudioListener>();

            new GameObject("TiqueRigExperimentProbe").AddComponent<TiqueRigExperimentProbe>();
            Directory.CreateDirectory(ToAbsolutePath(Path.GetDirectoryName(ScenePath)));
            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        private static SpriteRenderer CreateComparisonSprite(
            string name, float x, float baseline, int sortingOrder)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.position = new Vector3(x, baseline, 0f);
            gameObject.transform.localScale = Vector3.one * DisplayScale;
            SpriteRenderer renderer = gameObject.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = sortingOrder;
            return renderer;
        }

        private static void CreateLabel(string text, Vector2 position)
        {
            GameObject gameObject = new GameObject("Label_" + text.Replace(" ", string.Empty));
            gameObject.transform.position = new Vector3(position.x, position.y, 0f);
            TextMesh label = gameObject.AddComponent<TextMesh>();
            label.text = text;
            label.anchor = TextAnchor.MiddleCenter;
            label.alignment = TextAlignment.Center;
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            label.fontSize = 48;
            label.characterSize = 0.035f;
            label.color = new Color(0.83f, 0.79f, 0.68f);
            label.GetComponent<MeshRenderer>().sortingOrder = 50;
        }

        private static Sprite[] LoadSprites(string folder)
        {
            return AssetDatabase.FindAssets("t:Sprite", new[] { folder })
                .Select(AssetDatabase.GUIDToAssetPath)
                .OrderBy(path => path, StringComparer.Ordinal)
                .Select(AssetDatabase.LoadAssetAtPath<Sprite>)
                .Where(sprite => sprite != null)
                .ToArray();
        }

        private static string ReadArgument(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (string.Equals(args[i], key, StringComparison.OrdinalIgnoreCase))
                    return args[i + 1];
            return null;
        }

        private static string ToAbsolutePath(string assetPath)
        {
            if (string.IsNullOrWhiteSpace(assetPath)) return Application.dataPath;
            if (Path.IsPathRooted(assetPath)) return assetPath;
            return Path.GetFullPath(Path.Combine(Application.dataPath, "..", assetPath));
        }

        private static string ToAssetPath(string absolutePath)
        {
            string normalized = absolutePath.Replace('\\', '/');
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."))
                .Replace('\\', '/').TrimEnd('/');
            return normalized.StartsWith(project + "/", StringComparison.OrdinalIgnoreCase)
                ? normalized.Substring(project.Length + 1)
                : normalized;
        }
    }
}
