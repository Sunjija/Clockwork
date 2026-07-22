using System;
using System.IO;
using Clockwork;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private const string RegisteredBridgeArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredLimbusCaligoBridgeV6";
        private const string RegisteredBridgeScenePath =
            Root + "/Scenes/LimbusCaligoBridgeRegistered.unity";
        private const string RegisteredBridgeCombatArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredLimbusBridgeCombat";
        private const string RegisteredBridgeCombatScenePath =
            Root + "/Scenes/LimbusBridgeCombatRegistered.unity";
        private const string RegisteredBridgeCombatRatSpritePath =
            RegisteredBridgeCombatArtRoot + "/bridge-sewer-rat-idle.png";
        private const string RegisteredBridgeCombatRatPrefabPath =
            Root + "/Prefabs/RegisteredBridgeRat.prefab";

        private static readonly RouteLayerSpec[] RegisteredBridgeLayers =
        {
            new RouteLayerSpec("Layer_00_BgFar", "00-bg-far.png", -100),
            new RouteLayerSpec("Layer_10_BgMid", "10-bg-mid.png", -80),
            new RouteLayerSpec("Layer_30_Gameplay", "30-gameplay.png", -40),
            new RouteLayerSpec("Layer_40_Props", "40-props.png", -20),
            new RouteLayerSpec("Layer_80_ToxicFx", "80-fx.png", -10)
        };

        private static readonly RouteLayerSpec[] RegisteredBridgeCombatLayers =
        {
            new RouteLayerSpec("Layer_00_BgFar", "00-bg-far.png", -100),
            new RouteLayerSpec("Layer_10_BgMid", "10-bg-mid.png", -80),
            new RouteLayerSpec("Layer_30_Gameplay", "30-gameplay.png", -40),
            new RouteLayerSpec("Layer_40_Props", "40-props.png", -20),
            new RouteLayerSpec("Layer_80_ToxicFx", "80-fx.png", -10)
        };

        private static void BuildLimbusCaligoBridgeRegisteredScene(
            GameObject playerPrefab, GameObject ratPrefab)
        {
            GameObject registeredRatPrefab = BuildRegisteredBridgeRatPrefab(ratPrefab);
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "LimbusCaligoBridgeRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "LimbusCaligoBridgeGlobalLight", new Color(0.77f, 0.84f, 0.88f), 0.96f);
            BuildRegisteredRouteLayers(
                "RegisteredBridgeLayers_1280x360_PPU64", RegisteredBridgeArtRoot,
                RegisteredBridgeLayers);

            GameObject collisionRoot = new GameObject("LimbusCaligoBridgeCollision");
            BuildRouteBox(collisionRoot.transform, "BridgeContinuousDeck",
                new Vector2(0f, -0.921875f), new Vector2(20f, 0.5f));
            BuildRouteBox(collisionRoot.transform, "BridgeCaligoWall",
                new Vector2(-10.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "BridgeLimbusBenchmarkWall",
                new Vector2(10.15f, 0f), new Vector2(0.2f, 5.625f));

            BuildSpawnPoint("CaligoGateExit", new Vector2(-8.75f, -0.671875f), 1);
            BuildSpawnPoint("LimbusRoute", new Vector2(8.75f, -0.671875f), -1);
            BuildInvisibleRoomGate(
                "GateToGateWatch", new Vector2(-9.65f, 0f),
                "caligo-gate-watch-registered", "BridgeEntry", new Vector2(0.4f, 1.25f));
            BuildInvisibleRoomGate(
                "GateToBridgeCombat", new Vector2(9.65f, 0f),
                "limbus-bridge-combat-registered", "CombatEntry", new Vector2(0.4f, 1.25f));

            GameObject player = BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_CaligoGateExit",
                new Vector2(-8.75f, -0.671875f));
            Camera camera = BuildRegisteredRouteCamera(
                "LimbusCaligoBridgeCamera", new Vector2(-5f, 0f));
            camera.gameObject.AddComponent<RegisteredRouteCameraFollow2D>()
                .ConfigureSmooth(
                    player.transform, -5f, 5f, 0f, 0f, 64f,
                    0f, 0.1f, 20f);

            Directory.CreateDirectory(
                Path.GetDirectoryName(RegisteredBridgeScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredBridgeScenePath);

            BuildLimbusBridgeCombatRegisteredScene(playerPrefab, registeredRatPrefab);
        }

        private static GameObject BuildRegisteredBridgeRatPrefab(GameObject sourcePrefab)
        {
            GameObject instance = PrefabUtility.InstantiatePrefab(sourcePrefab) as GameObject;
            if (instance == null) throw new InvalidOperationException("Unable to clone rat prefab.");
            SpriteRenderer renderer = instance.GetComponent<SpriteRenderer>();
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(
                RegisteredBridgeCombatRatSpritePath);
            if (renderer == null || sprite == null)
            {
                UnityEngine.Object.DestroyImmediate(instance);
                throw new InvalidOperationException("Missing registered bridge rat sprite.");
            }
            renderer.sprite = sprite;
            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(
                instance, RegisteredBridgeCombatRatPrefabPath);
            UnityEngine.Object.DestroyImmediate(instance);
            return prefab;
        }

        private static void BuildLimbusBridgeCombatRegisteredScene(
            GameObject playerPrefab, GameObject ratPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "LimbusBridgeCombatRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "LimbusBridgeCombatGlobalLight", new Color(0.7f, 0.8f, 0.82f), 0.88f);
            BuildRegisteredRouteLayers(
                "RegisteredBridgeCombatLayers_1280x360_PPU64",
                RegisteredBridgeCombatArtRoot, RegisteredBridgeCombatLayers);

            GameObject collisionRoot = new GameObject("LimbusBridgeCombatCollision");
            BuildRouteBox(collisionRoot.transform, "CombatContinuousDeck",
                new Vector2(0f, -0.921875f), new Vector2(20f, 0.5f));
            BuildRouteBox(collisionRoot.transform, "CombatBridgeBodyWall",
                new Vector2(-10.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "CombatLimbusBenchmarkWall",
                new Vector2(10.15f, 0f), new Vector2(0.2f, 5.625f));

            BuildSpawnPoint("CombatEntry", new Vector2(-8.75f, -0.671875f), 1);
            BuildSpawnPoint("BridgeBodyExit", new Vector2(-8.75f, -0.671875f), 1);
            BuildSpawnPoint("LimbusContinuation", new Vector2(8.75f, -0.671875f), -1);
            BuildInvisibleRoomGate(
                "GateToBridgeBody", new Vector2(-9.65f, 0f),
                "limbus-caligo-bridge-registered", "LimbusRoute", new Vector2(0.4f, 1.25f));
            BuildInvisibleRoomGate(
                "GateToScrapPlain", new Vector2(9.65f, 0f),
                "limbus-scrap-plain-registered", "BridgeEntry", new Vector2(0.4f, 1.25f));

            GameObject player = BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_CombatEntry",
                new Vector2(-8.75f, -0.671875f));
            Camera camera = BuildRegisteredRouteCamera(
                "LimbusBridgeCombatCamera", new Vector2(-5f, 0f));
            camera.gameObject.AddComponent<RegisteredRouteCameraFollow2D>()
                .ConfigureSmooth(
                    player.transform, -5f, 5f, 0f, 0f, 64f,
                    0f, 0.1f, 20f);

            GameObject directorObject = new GameObject("BridgeCollapseDirector");
            directorObject.transform.position = new Vector3(9.15f, -0.1f, 0f);
            BoxCollider2D collapseTrigger = directorObject.AddComponent<BoxCollider2D>();
            collapseTrigger.isTrigger = true;
            collapseTrigger.size = new Vector2(0.5f, 1.8f);
            collapseTrigger.enabled = false;
            directorObject.AddComponent<BridgeCollapseDirector>().Configure(
                ratPrefab, -0.671875f, "morbi-workshop-registered", "RepairTable");

            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(
                player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());

            Directory.CreateDirectory(
                Path.GetDirectoryName(RegisteredBridgeCombatScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredBridgeCombatScenePath);
        }
    }
}
