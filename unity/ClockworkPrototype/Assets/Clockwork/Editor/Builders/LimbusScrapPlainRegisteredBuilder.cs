using System.IO;
using Clockwork;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private const string RegisteredScrapPlainArtRoot =
            Root + "/Art/Environment/ACT1OpeningCaligo/RegisteredLimbusScrapPlain";
        private const string RegisteredScrapPlainScenePath =
            Root + "/Scenes/LimbusScrapPlainRegistered.unity";

        private static readonly RouteLayerSpec[] RegisteredScrapPlainLayers =
        {
            new RouteLayerSpec("Layer_00_BgFar", "00-bg-far.png", -100),
            new RouteLayerSpec("Layer_10_BgMid", "10-bg-mid.png", -90),
            new RouteLayerSpec("Layer_20_RearStructures", "20-rear-structures.png", -80),
            new RouteLayerSpec("Layer_80_DustFx", "80-fx.png", -70),
            new RouteLayerSpec("Layer_30_Gameplay", "30-gameplay.png", -50),
            new RouteLayerSpec("Layer_40_Props", "40-props.png", -40),
            new RouteLayerSpec("Layer_60_Foreground", "60-foreground.png", 20)
        };

        private static void BuildLimbusScrapPlainRegisteredScene(GameObject playerPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "LimbusScrapPlainRegistered";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildRegisteredRouteLight(
                "LimbusScrapPlainLight", new Color(0.72f, 0.8f, 0.81f), 0.9f);
            BuildRegisteredRouteLayers(
                "RegisteredScrapPlain_3584x360_PPU64",
                RegisteredScrapPlainArtRoot, RegisteredScrapPlainLayers);

            GameObject collisionRoot = new GameObject("LimbusScrapPlainCollision");
            BuildRouteBox(collisionRoot.transform, "ScrapPlainContinuousGround",
                new Vector2(0f, -0.921875f), new Vector2(56f, 0.5f));
            BuildRouteBox(collisionRoot.transform, "ScrapPlainBridgeWall",
                new Vector2(-28.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildRouteBox(collisionRoot.transform, "ScrapPlainCrashBenchmarkWall",
                new Vector2(28.15f, 0f), new Vector2(0.2f, 5.625f));
            BuildSpawnPoint("BridgeEntry", new Vector2(-26.5f, -0.671875f), 1);
            BuildSpawnPoint("CrashApproach", new Vector2(26.5f, -0.671875f), -1);
            BuildInvisibleRoomGate(
                "GateToBridgeCombat", new Vector2(-27.65f, 0f),
                "limbus-bridge-combat-registered", "LimbusContinuation",
                new Vector2(0.4f, 1.25f));

            GameObject player = BuildRegisteredRoutePlayer(
                playerPrefab, "Tique_Approved_BridgeEntry",
                new Vector2(-26.5f, -0.671875f));
            Camera camera = BuildRegisteredRouteCamera(
                "LimbusScrapPlainCamera", new Vector2(-23f, 0f));
            camera.gameObject.AddComponent<RegisteredRouteCameraFollow2D>()
                .ConfigureSmooth(
                    player.transform, -23f, 23f, 0f, 0f, 64f,
                    0f, 0.1f, 20f);

            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(
                player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());

            Directory.CreateDirectory(
                Path.GetDirectoryName(RegisteredScrapPlainScenePath) ?? Root + "/Scenes");
            EditorSceneManager.SaveScene(scene, RegisteredScrapPlainScenePath);
        }
    }
}
