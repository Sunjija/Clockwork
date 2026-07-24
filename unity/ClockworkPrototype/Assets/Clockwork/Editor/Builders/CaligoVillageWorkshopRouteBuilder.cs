using System;
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
        private const string RegisteredExteriorArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredCaligoVillagePlazaV5";
        private const string RegisteredGateWatchArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredCaligoGateWatchV5";
        private const string RegisteredWorkshopArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredMorbiWorkshopV2";
        private const string RegisteredSharedArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/SharedCaligoRouteV2";
        private const string RegisteredExteriorScenePath =
            Root + "/Scenes/CaligoVillageExteriorRegistered.unity";
        private const string RegisteredGateWatchScenePath =
            Root + "/Scenes/CaligoGateWatchRegistered.unity";
        private const string RegisteredWorkshopScenePath =
            Root + "/Scenes/MorbiWorkshopRegistered.unity";
        private const string RegisteredRouteDefaultBuildPath =
            "Builds/LimbusCaligoBridgeGateRouteV6/ClockworkLimbusCaligoBridgeGateRouteV6.exe";
        private const float RegisteredRouteTiqueVisualCompensation = 1.077f;

        private readonly struct RouteLayerSpec
        {
            public RouteLayerSpec(string objectName, string fileName, int sortingOrder)
                : this(objectName, fileName, sortingOrder, Vector2.zero, null, false)
            {
            }

            public RouteLayerSpec(
                string objectName, string fileName, int sortingOrder, Vector2 localPosition)
                : this(objectName, fileName, sortingOrder, localPosition, null, false)
            {
            }

            public RouteLayerSpec(
                string objectName, string fileName, int sortingOrder, Vector2 localPosition,
                string artRootOverride, bool groundPivot)
            {
                ObjectName = objectName;
                FileName = fileName;
                SortingOrder = sortingOrder;
                LocalPosition = localPosition;
                ArtRootOverride = artRootOverride;
                GroundPivot = groundPivot;
            }

            public string ObjectName { get; }
            public string FileName { get; }
            public int SortingOrder { get; }
            public Vector2 LocalPosition { get; }
            public string ArtRootOverride { get; }
            public bool GroundPivot { get; }

            public string ResolvePath(string defaultArtRoot)
            {
                return $"{(string.IsNullOrEmpty(ArtRootOverride) ? defaultArtRoot : ArtRootOverride)}/{FileName}";
            }
        }

        private static readonly RouteLayerSpec[] RegisteredExteriorLayers =
        {
            new RouteLayerSpec(
                "Layer_00_PlazaApproachEnvironment", "00-plaza-approach-environment.png", -100),
            new RouteLayerSpec(
                "Layer_30_SharedWoodDoor", "shared-morbi-wood-door.png", -20,
                new Vector2(7.4765625f, -1.984375f), RegisteredSharedArtRoot, true)
        };

        private static readonly RouteLayerSpec[] RegisteredGateWatchLayers =
        {
            new RouteLayerSpec(
                "Layer_00_GateWatchEnvironment", "00-gate-watch-environment.png", -100)
        };

        private static readonly RouteLayerSpec[] RegisteredWorkshopLayers =
        {
            new RouteLayerSpec("Layer_00_Environment", "00-environment.png", -100),
            new RouteLayerSpec(
                "Layer_30_SharedWoodDoor", "shared-morbi-wood-door.png", -20,
                new Vector2(-4.015625f, -1.40625f), RegisteredSharedArtRoot, true),
            new RouteLayerSpec("Layer_40_Morbi", "40-morbi.png", -5)
        };

        [MenuItem("Clockwork/Art/Build Caligo Village Workshop Route")]
        public static void BuildCaligoVillageWorkshopRoute()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureRegisteredRouteTextures(
                RegisteredExteriorArtRoot, RegisteredExteriorLayers, 2048);
            ConfigureRegisteredRouteTextures(
                RegisteredGateWatchArtRoot, RegisteredGateWatchLayers, 1024);
            ConfigureRegisteredRouteTextures(
                RegisteredBridgeArtRoot, RegisteredBridgeLayers, 2048);
            ConfigureRegisteredRouteTextures(
                RegisteredBridgeCombatArtRoot, RegisteredBridgeCombatLayers, 2048);
            ConfigureTexture(
                RegisteredBridgeCombatRatSpritePath, new Vector2(0.5f, 0f),
                FilterMode.Bilinear, 256, 64f);
            ConfigureRegisteredRouteTextures(
                RegisteredScrapPlainArtRoot, RegisteredScrapPlainLayers, 4096);
            ConfigureRegisteredRouteTextures(RegisteredWorkshopArtRoot, RegisteredWorkshopLayers);

            GameObject playerPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
            if (playerPrefab == null)
            {
                throw new InvalidOperationException($"Missing approved Tique prefab: {PrefabPath}");
            }
            GameObject ratPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(RatPrefabPath);
            if (ratPrefab == null)
            {
                throw new InvalidOperationException($"Missing rat prefab: {RatPrefabPath}");
            }

            BuildMorbiWorkshopRegisteredScene(playerPrefab);
            BuildCaligoVillageExteriorRegisteredScene(playerPrefab);
            BuildCaligoGateWatchRegisteredScene(playerPrefab);
            BuildLimbusCaligoBridgeRegisteredScene(playerPrefab, ratPrefab);
            BuildLimbusScrapPlainRegisteredScene(playerPrefab);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("CLOCKWORK_CALIGO_ROUTE_SCENES_OK");
        }

        public static void BuildCaligoVillageWorkshopRouteFromCommandLine()
        {
            BuildCaligoVillageWorkshopRoute();
        }

        public static void BuildCaligoVillageWorkshopRouteWindowsFromCommandLine()
        {
            BuildCaligoVillageWorkshopRoute();
            string outputPath = Environment.GetEnvironmentVariable("CLOCKWORK_CALIGO_ROUTE_BUILD");
            if (string.IsNullOrWhiteSpace(outputPath)) outputPath = RegisteredRouteDefaultBuildPath;

            string outputDirectory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(outputDirectory)) Directory.CreateDirectory(outputDirectory);

            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[]
                {
                    RegisteredWorkshopScenePath,
                    RegisteredExteriorScenePath,
                    RegisteredGateWatchScenePath,
                    RegisteredBridgeScenePath,
                    RegisteredBridgeCombatScenePath,
                    RegisteredScrapPlainScenePath
                },
                locationPathName = outputPath,
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new InvalidOperationException($"Caligo route Windows build failed: {report.summary.result}");
            }

            Debug.Log($"CLOCKWORK_CALIGO_ROUTE_BUILD_OK {report.summary.totalSize} {outputPath}");
        }

        private static void BuildMorbiWorkshopRegisteredScene(GameObject playerPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "MorbiWorkshopRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "MorbiWorkshopGlobalLight", new Color(0.94f, 0.87f, 0.78f), 1f);
            Transform layers = BuildRegisteredRouteLayers(
                "RegisteredWorkshopLayers_640x360_PPU64", RegisteredWorkshopArtRoot,
                RegisteredWorkshopLayers);

            GameObject collisionRoot = new GameObject("MorbiWorkshopCollision");
            BuildRouteBox(collisionRoot.transform, "WorkshopMainFloor",
                new Vector2(0f, -1.65625f), new Vector2(10f, 0.5f));
            BuildRouteBox(collisionRoot.transform, "WorkshopLeftWall",
                new Vector2(-5.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "WorkshopRightWall",
                new Vector2(5.15f, 0f), new Vector2(0.2f, 5.625f));

            BuildSpawnPoint("RepairTable", new Vector2(1.796875f, -1.40625f), -1);
            BuildSpawnPoint("PlazaEntry", new Vector2(-3.28125f, -1.40625f), 1);
            BuildInvisibleRoomGate(
                "GateToVillageSquare", new Vector2(-4.015625f, -0.7f),
                "caligo-village-exterior-registered", "WorkshopStair");
            BuildMorbiInteraction(new Vector2(0.703125f, -1.40625f));

            GameObject player = BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_RepairTable", new Vector2(1.796875f, -1.40625f));
            Camera camera = BuildRegisteredRouteCamera("MorbiWorkshopCamera", Vector2.zero);
            CaligoVillageWorkshopRouteProbe probe = new GameObject("CaligoRouteProbe")
                .AddComponent<CaligoVillageWorkshopRouteProbe>();
            probe.Configure(layers, camera, player.GetComponent<TiqueMotor>());

            Directory.CreateDirectory(Path.GetDirectoryName(RegisteredWorkshopScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredWorkshopScenePath);
        }

        private static void BuildCaligoVillageExteriorRegisteredScene(GameObject playerPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoVillageExteriorRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "CaligoVillageExteriorGlobalLight", new Color(0.88f, 0.9f, 0.92f), 1f);
            Transform layers = BuildRegisteredRouteLayers(
                "RegisteredPlazaLayers_1280x360_PPU64", RegisteredExteriorArtRoot,
                RegisteredExteriorLayers);

            GameObject collisionRoot = new GameObject("CaligoVillageExteriorCollision");
            BuildRouteBox(collisionRoot.transform, "VillageSquareDeck",
                new Vector2(-2.421875f, -0.921875f), new Vector2(15.15625f, 0.5f));
            BuildRouteEdge(collisionRoot.transform, "WorkshopStairSlope",
                new Vector2(5.15625f, -0.671875f), new Vector2(7.3125f, -1.96875f));
            BuildRouteBox(collisionRoot.transform, "WorkshopLowerLanding",
                new Vector2(8.65625f, -2.21875f), new Vector2(2.6875f, 0.5f));
            EdgeCollider2D workshopUpperBypass = BuildRouteOneWayEdge(
                collisionRoot.transform, "WorkshopUpperBypass",
                new Vector2(5.15625f, -0.671875f), new Vector2(10f, -0.671875f));
            BuildWorkshopStairDropZone(workshopUpperBypass);
            BuildRouteBox(collisionRoot.transform, "WorkshopLowerRetainingWall",
                new Vector2(10.05f, -2.05f), new Vector2(0.1f, 1.75f));
            BuildRouteBox(collisionRoot.transform, "ExteriorLeftWall",
                new Vector2(-10.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "ExteriorRightWall",
                new Vector2(10.15f, -0.25f), new Vector2(0.2f, 5.125f));

            BuildSpawnPoint("WorkshopStair", new Vector2(7.5f, -1.96875f), -1);
            BuildSpawnPoint("VillageSquareCenter", new Vector2(-5f, -0.671875f), 1);
            BuildSpawnPoint("WaterServiceStair", new Vector2(-6.5f, -0.671875f), 1);
            BuildSpawnPoint("GateArchExit", new Vector2(8.75f, -0.671875f), -1);
            BuildInvisibleRoomGate(
                "GateToMorbiWorkshop", new Vector2(7.5f, -1.55f),
                "morbi-workshop-registered", "PlazaEntry", new Vector2(0.45f, 0.75f));
            BuildInvisibleRoomGate(
                "GateToGateWatch", new Vector2(9.65f, -0.65f),
                "caligo-gate-watch-registered", "VillageArchExit", new Vector2(0.4f, 1.25f));

            GameObject player = BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_WorkshopStair", new Vector2(7.5f, -1.96875f));
            Camera camera = BuildRegisteredRouteCamera(
                "CaligoVillageExteriorCamera", new Vector2(5f, 0f));
            camera.gameObject.AddComponent<RegisteredRouteCameraFollow2D>()
                .ConfigureSmooth(
                    player.transform, -5f, 5f, 0f, 0f, 64f,
                    0f, 0.1f, 20f);

            Directory.CreateDirectory(Path.GetDirectoryName(RegisteredExteriorScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredExteriorScenePath);
        }

        private static void BuildCaligoGateWatchRegisteredScene(GameObject playerPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoGateWatchRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "CaligoGateWatchGlobalLight", new Color(0.86f, 0.89f, 0.92f), 1f);
            BuildRegisteredRouteLayers(
                "RegisteredGateWatchLayers_640x360_PPU64", RegisteredGateWatchArtRoot,
                RegisteredGateWatchLayers);

            GameObject collisionRoot = new GameObject("CaligoGateWatchCollision");
            BuildRouteBox(collisionRoot.transform, "GateWatchDeck",
                new Vector2(0f, -0.921875f), new Vector2(10f, 0.5f));
            BuildRouteBox(collisionRoot.transform, "GateWatchLeftWall",
                new Vector2(-5.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "GateWatchRightWall",
                new Vector2(5.15f, 0f), new Vector2(0.2f, 5.625f));

            BuildSpawnPoint("VillageArchExit", new Vector2(-4.1f, -0.671875f), 1);
            BuildSpawnPoint("BridgeEntry", new Vector2(4.1f, -0.671875f), -1);
            BuildSpawnPoint("DropShaftGate", new Vector2(1.75f, -0.671875f), -1);
            BuildInvisibleRoomGate(
                "GateToVillageSquare", new Vector2(-4.7f, -0.65f),
                "caligo-village-exterior-registered", "GateArchExit", new Vector2(0.4f, 1.25f));
            BuildInvisibleRoomGate(
                "GateToBridge", new Vector2(4.7f, -0.65f),
                "limbus-caligo-bridge-registered", "CaligoGateExit",
                new Vector2(0.4f, 1.25f));

            BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_VillageArchExit", new Vector2(-4.1f, -0.671875f));
            BuildRegisteredRouteCamera("CaligoGateWatchCamera", Vector2.zero);

            Directory.CreateDirectory(Path.GetDirectoryName(RegisteredGateWatchScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredGateWatchScenePath);
        }

        private static void ConfigureRegisteredRouteTextures(
            string artRoot, RouteLayerSpec[] layerSpecs, int maxSize = 1024)
        {
            foreach (RouteLayerSpec layer in layerSpecs)
            {
                string path = layer.ResolvePath(artRoot);
                if (AssetDatabase.LoadAssetAtPath<Texture2D>(path) == null)
                {
                    throw new FileNotFoundException($"Missing Caligo route layer: {path}");
                }

                ConfigureTexture(
                    path,
                    layer.GroundPivot ? new Vector2(0.5f, 0f) : new Vector2(0.5f, 0.5f),
                    FilterMode.Point,
                    maxSize,
                    64f);
            }
        }

        private static Transform BuildRegisteredRouteLayers(
            string rootName, string artRoot, RouteLayerSpec[] layerSpecs)
        {
            GameObject root = new GameObject(rootName);
            foreach (RouteLayerSpec layer in layerSpecs)
            {
                string path = layer.ResolvePath(artRoot);
                Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(path);
                if (sprite == null) throw new InvalidOperationException($"Unable to load route layer: {path}");

                GameObject layerObject = new GameObject(layer.ObjectName);
                layerObject.transform.SetParent(root.transform, false);
                layerObject.transform.localPosition = layer.LocalPosition;
                layerObject.transform.localRotation = Quaternion.identity;
                layerObject.transform.localScale = Vector3.one;
                SpriteRenderer renderer = layerObject.AddComponent<SpriteRenderer>();
                renderer.sprite = sprite;
                renderer.sortingOrder = layer.SortingOrder;
                if (layer.FileName == "80-fx.png")
                {
                    layerObject.AddComponent<RegisteredLayerPulse2D>()
                        .Configure(renderer, 8f, 0.82f, 1f);
                }
            }

            return root.transform;
        }

        private static void BuildMorbiInteraction(Vector2 position)
        {
            GameObject root = new GameObject("MorbiNpcInteraction");
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(1.5f, 1.4f);
            trigger.offset = new Vector2(0f, 0.65f);
            root.AddComponent<MorbiNpc>();
        }

        private static GameObject BuildRegisteredRoutePlayer(
            GameObject playerPrefab, string objectName, Vector2 position)
        {
            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.name = objectName;
            player.transform.position = position;
            player.transform.localScale = Vector3.one;

            SpriteRenderer visual = player.GetComponentInChildren<SpriteRenderer>();
            if (visual == null) throw new InvalidOperationException("Approved Tique renderer is missing.");
            GameObject compensation = new GameObject("VisualOnly_44pxCompensation");
            compensation.transform.SetParent(player.transform, false);
            compensation.transform.localScale = Vector3.one * RegisteredRouteTiqueVisualCompensation;
            visual.transform.SetParent(compensation.transform, true);
            visual.transform.localPosition = Vector3.zero;
            visual.transform.localRotation = Quaternion.identity;
            return player;
        }

        private static Camera BuildRegisteredRouteCamera(string name, Vector2 position)
        {
            GameObject cameraObject = new GameObject(name);
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(position.x, position.y, -10f);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 2.8125f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.035f, 0.045f);
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

        private static void BuildRegisteredRouteLight(string name, Color color, float intensity)
        {
            Light2D light = new GameObject(name).AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = color;
            light.intensity = intensity;
        }

        private static void BuildRouteBox(Transform parent, string name, Vector2 position, Vector2 size)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.localPosition = position;
            gameObject.AddComponent<BoxCollider2D>().size = size;
        }

        private static void BuildRouteEdge(Transform parent, string name, Vector2 start, Vector2 end)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            EdgeCollider2D edge = gameObject.AddComponent<EdgeCollider2D>();
            edge.points = new[] { start, end };
            edge.edgeRadius = 0.025f;
        }

        private static EdgeCollider2D BuildRouteOneWayEdge(
            Transform parent, string name, Vector2 start, Vector2 end)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            EdgeCollider2D edge = gameObject.AddComponent<EdgeCollider2D>();
            edge.points = new[] { start, end };
            edge.edgeRadius = 0.025f;
            edge.usedByEffector = true;

            PlatformEffector2D effector = gameObject.AddComponent<PlatformEffector2D>();
            effector.useOneWay = true;
            effector.surfaceArc = 170f;
            return edge;
        }

        private static void BuildWorkshopStairDropZone(Collider2D oneWayPlatform)
        {
            GameObject zone = new GameObject("WorkshopStairDropZone");
            zone.transform.position = new Vector2(5.85f, -0.05f);
            BoxCollider2D trigger = zone.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(1.35f, 1.35f);
            zone.AddComponent<OneWayStairDropZone>().Configure(oneWayPlatform);
        }

        private static void BuildInvisibleRoomGate(
            string name, Vector2 position, string destinationRoom, string destinationSpawn,
            Vector2? triggerSize = null)
        {
            GameObject root = new GameObject(name);
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = triggerSize ?? new Vector2(0.45f, 1.6f);
            root.AddComponent<RoomGate>().Configure(name, destinationRoom, destinationSpawn);
        }
    }
}
