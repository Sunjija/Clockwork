using System;
using System.Collections.Generic;
using System.IO;
using Clockwork;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private const string RegisteredStorageArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredWaterStorage";
        private const string RegisteredStorageScenePath =
            Root + "/Scenes/CaligoWaterStorageRegistered.unity";
        private const string RegisteredStorageDefaultBuildPath =
            "Builds/CaligoWaterStorageRegistered/ClockworkCaligoWaterStorage.exe";
        private const float RegisteredStorageDeckY = -1.484375f;
        private const float RegisteredStorageTiqueVisualCompensation = 1.077f;

        private readonly struct RegisteredLayerSpec
        {
            public RegisteredLayerSpec(string objectName, string fileName, int sortingOrder)
            {
                ObjectName = objectName;
                FileName = fileName;
                SortingOrder = sortingOrder;
            }

            public string ObjectName { get; }
            public string FileName { get; }
            public int SortingOrder { get; }
            public string AssetPath => $"{RegisteredStorageArtRoot}/{FileName}";
        }

        private static readonly RegisteredLayerSpec[] RegisteredStorageLayers =
        {
            new RegisteredLayerSpec("Layer_00_Far", "00-bg-far.png", -100),
            new RegisteredLayerSpec("Layer_10_Mid", "10-bg-mid.png", -80),
            new RegisteredLayerSpec("Layer_18_Foundation", "18-bg-near-foundation.png", -60),
            new RegisteredLayerSpec("Layer_20_Reservoir", "20-bg-near.png", -50),
            new RegisteredLayerSpec("Layer_30_Gameplay", "30-gameplay-platform-v2.png", -20),
            new RegisteredLayerSpec("Layer_40_Props", "40-props.png", -10),
            new RegisteredLayerSpec("Layer_70_Foreground", "70-fg-occlusion.png", 20),
            new RegisteredLayerSpec("Layer_80_FX", "80-fx.png", 30)
        };

        [MenuItem("Clockwork/Art/Build Registered Water Storage")]
        public static void BuildCaligoWaterStorageRegistered()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureRegisteredStorageTextures();

            GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (playerPrefab == null)
            {
                throw new InvalidOperationException($"Missing approved Tique prefab: {PrefabPath}");
            }

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoWaterStorageRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            BuildRegisteredStorageLight();
            Transform layerRoot = BuildRegisteredStorageLayers(out SpriteRenderer fxRenderer);
            BuildRegisteredStorageCollision();
            GameObject player = BuildRegisteredStoragePlayer(playerPrefab);
            Camera camera = BuildRegisteredStorageCamera();

            RegisteredLayerPulse2D pulse = new GameObject("RegisteredAmbientMotion")
                .AddComponent<RegisteredLayerPulse2D>();
            pulse.Configure(fxRenderer, 8f, 0.82f, 0.98f);

            CaligoWaterStorageRegisteredProbe probe = new GameObject("RegisteredLayerProbe")
                .AddComponent<CaligoWaterStorageRegisteredProbe>();
            probe.Configure(layerRoot, camera, player.GetComponent<TiqueMotor>());

            Directory.CreateDirectory(Path.GetDirectoryName(RegisteredStorageScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredStorageScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("CLOCKWORK_WATER_STORAGE_SCENE_OK");
        }

        public static void BuildCaligoWaterStorageFromCommandLine()
        {
            BuildCaligoWaterStorageRegistered();
        }

        public static void BuildCaligoWaterStorageWindowsFromCommandLine()
        {
            BuildCaligoWaterStorageRegistered();
            string outputPath = Environment.GetEnvironmentVariable("CLOCKWORK_WATER_STORAGE_BUILD");
            if (string.IsNullOrWhiteSpace(outputPath))
            {
                outputPath = RegisteredStorageDefaultBuildPath;
            }

            string outputDirectory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(outputDirectory)) Directory.CreateDirectory(outputDirectory);

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { RegisteredStorageScenePath },
                locationPathName = outputPath,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new InvalidOperationException(
                    $"Registered water storage Windows build failed: {report.summary.result}");
            }

            Debug.Log($"CLOCKWORK_WATER_STORAGE_BUILD_OK {report.summary.totalSize} {outputPath}");
        }

        private static void ConfigureRegisteredStorageTextures()
        {
            foreach (RegisteredLayerSpec layer in RegisteredStorageLayers)
            {
                if (AssetDatabase.LoadAssetAtPath<Texture2D>(layer.AssetPath) == null)
                {
                    throw new FileNotFoundException($"Missing registered storage layer: {layer.AssetPath}");
                }

                ConfigureTexture(
                    layer.AssetPath,
                    new Vector2(0.5f, 0.5f),
                    FilterMode.Point,
                    1024,
                    64f);
            }
        }

        private static Transform BuildRegisteredStorageLayers(out SpriteRenderer fxRenderer)
        {
            GameObject root = new GameObject("RegisteredLayers_800x450_PPU64");
            fxRenderer = null;

            foreach (RegisteredLayerSpec layer in RegisteredStorageLayers)
            {
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(layer.AssetPath);
                if (sprite == null)
                {
                    throw new InvalidOperationException($"Unable to load registered layer: {layer.AssetPath}");
                }

                GameObject layerObject = new GameObject(layer.ObjectName);
                layerObject.transform.SetParent(root.transform, false);
                layerObject.transform.localPosition = Vector3.zero;
                layerObject.transform.localRotation = Quaternion.identity;
                layerObject.transform.localScale = Vector3.one;

                SpriteRenderer renderer = layerObject.AddComponent<SpriteRenderer>();
                renderer.sprite = sprite;
                renderer.sortingOrder = layer.SortingOrder;
                if (layer.FileName == "80-fx.png") fxRenderer = renderer;
            }

            if (fxRenderer == null) throw new InvalidOperationException("Registered FX layer was not created.");
            return root.transform;
        }

        private static void BuildRegisteredStorageLight()
        {
            Light2D light = new GameObject("RegisteredStorageGlobalLight").AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.96f, 0.9f, 0.82f);
            light.intensity = 1f;
        }

        private static void BuildRegisteredStorageCollision()
        {
            GameObject collisionRoot = new GameObject("RegisteredCollision");
            BuildRegisteredBoxCollider(
                collisionRoot.transform,
                "DeckCollider",
                new Vector2(0f, RegisteredStorageDeckY - 0.25f),
                new Vector2(12.5f, 0.5f));
            BuildRegisteredBoxCollider(
                collisionRoot.transform,
                "LeftWallCollider",
                new Vector2(-5.1f, 0f),
                new Vector2(0.2f, 5.625f));
            BuildRegisteredBoxCollider(
                collisionRoot.transform,
                "RightWallCollider",
                new Vector2(5.1f, 0f),
                new Vector2(0.2f, 5.625f));
        }

        private static void BuildRegisteredBoxCollider(
            Transform parent, string name, Vector2 position, Vector2 size)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localPosition = position;
            BoxCollider2D collider = gameObject.AddComponent<BoxCollider2D>();
            collider.size = size;
        }

        private static GameObject BuildRegisteredStoragePlayer(GameObject playerPrefab)
        {
            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.name = "Tique_Approved_RegisteredScale";
            player.transform.position = new Vector3(-1.5625f, RegisteredStorageDeckY, 0f);
            player.transform.localScale = Vector3.one;

            SpriteRenderer visual = player.GetComponentInChildren<SpriteRenderer>();
            if (visual == null) throw new InvalidOperationException("Approved Tique renderer is missing.");

            GameObject compensation = new GameObject("VisualOnly_44pxCompensation");
            compensation.transform.SetParent(player.transform, false);
            compensation.transform.localPosition = Vector3.zero;
            compensation.transform.localRotation = Quaternion.identity;
            compensation.transform.localScale = Vector3.one * RegisteredStorageTiqueVisualCompensation;
            visual.transform.SetParent(compensation.transform, true);
            visual.transform.localPosition = Vector3.zero;
            visual.transform.localRotation = Quaternion.identity;

            return player;
        }

        private static Camera BuildRegisteredStorageCamera()
        {
            GameObject cameraObject = new GameObject("Main Camera");
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0f, 0f, -10f);

            Camera camera = cameraObject.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 2.8125f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.052f, 0.064f);
            cameraObject.AddComponent<AudioListener>();

            UnityEngine.U2D.PixelPerfectCamera pixelPerfect =
                cameraObject.AddComponent<UnityEngine.U2D.PixelPerfectCamera>();
            pixelPerfect.assetsPPU = 64;
            pixelPerfect.refResolutionX = 640;
            pixelPerfect.refResolutionY = 360;
            pixelPerfect.cropFrameX = false;
            pixelPerfect.cropFrameY = false;
            return camera;
        }
    }
}
