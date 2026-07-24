using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.U2D;

namespace Clockwork
{
    public sealed class CaligoVillageWorkshopRouteProbe : MonoBehaviour
    {
        private static readonly string[] PlazaLayerNames =
        {
            "Layer_00_PlazaApproachEnvironment",
            "Layer_30_SharedWoodDoor"
        };

        private static readonly string[] GateWatchLayerNames =
        {
            "Layer_00_GateWatchEnvironment"
        };

        private static readonly string[] BridgeLayerNames =
        {
            "Layer_00_BgFar",
            "Layer_10_BgMid",
            "Layer_30_Gameplay",
            "Layer_40_Props",
            "Layer_80_ToxicFx"
        };

        private static readonly string[] ScrapPlainLayerNames =
        {
            "Layer_00_BgFar",
            "Layer_10_BgMid",
            "Layer_20_RearStructures",
            "Layer_30_Gameplay",
            "Layer_40_Props",
            "Layer_60_Foreground",
            "Layer_80_DustFx"
        };

        private static readonly string[] WorkshopLayerNames =
        {
            "Layer_00_Environment",
            "Layer_30_SharedWoodDoor",
            "Layer_40_Morbi"
        };

        private static bool active;

        [SerializeField] private Transform initialLayerRoot;
        [SerializeField] private Camera initialCamera;
        [SerializeField] private TiqueMotor initialPlayer;

        private void Awake()
        {
            string[] arguments = Environment.GetCommandLineArgs();
            bool requested = arguments.Contains("-clockworkCaligoRouteSmoke")
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkWorkshopCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkExteriorCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkPlazaCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkGateWatchCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkBridgeGateCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkBridgeCrossingCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkBridgeCombatCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkScrapPlainWestCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkScrapPlainCenterCapturePath"))
                || !string.IsNullOrWhiteSpace(ReadArgument(arguments, "-clockworkScrapPlainEastCapturePath"));
            if (!requested) return;
            if (active)
            {
                Destroy(gameObject);
                return;
            }

            active = true;
            DontDestroyOnLoad(gameObject);
        }

        private IEnumerator Start()
        {
            string[] arguments = Environment.GetCommandLineArgs();
            bool runSmoke = arguments.Contains("-clockworkCaligoRouteSmoke");
            string workshopCapture = ReadArgument(arguments, "-clockworkWorkshopCapturePath");
            string approachCapture = ReadArgument(arguments, "-clockworkExteriorCapturePath");
            string plazaCapture = ReadArgument(arguments, "-clockworkPlazaCapturePath");
            string gateWatchCapture = ReadArgument(arguments, "-clockworkGateWatchCapturePath");
            string bridgeGateCapture = ReadArgument(
                arguments, "-clockworkBridgeGateCapturePath");
            string bridgeCrossingCapture = ReadArgument(
                arguments, "-clockworkBridgeCrossingCapturePath");
            string bridgeCombatCapture = ReadArgument(
                arguments, "-clockworkBridgeCombatCapturePath");
            string scrapWestCapture = ReadArgument(
                arguments, "-clockworkScrapPlainWestCapturePath");
            string scrapCenterCapture = ReadArgument(
                arguments, "-clockworkScrapPlainCenterCapturePath");
            string scrapEastCapture = ReadArgument(
                arguments, "-clockworkScrapPlainEastCapturePath");
            if (!runSmoke && string.IsNullOrWhiteSpace(workshopCapture)
                && string.IsNullOrWhiteSpace(approachCapture)
                && string.IsNullOrWhiteSpace(plazaCapture)
                && string.IsNullOrWhiteSpace(gateWatchCapture)
                && string.IsNullOrWhiteSpace(bridgeGateCapture)
                && string.IsNullOrWhiteSpace(bridgeCrossingCapture)
                && string.IsNullOrWhiteSpace(bridgeCombatCapture)
                && string.IsNullOrWhiteSpace(scrapWestCapture)
                && string.IsNullOrWhiteSpace(scrapCenterCapture)
                && string.IsNullOrWhiteSpace(scrapEastCapture))
            {
                yield break;
            }

            yield return Settle();
            List<string> failures = new List<string>();
            ValidateWorkshop(initialLayerRoot, initialCamera, initialPlayer, "RepairTable", failures);
            if (!string.IsNullOrWhiteSpace(workshopCapture))
            {
                yield return CaptureCamera(initialCamera, workshopCapture, arguments);
                if (!CaptureExists(workshopCapture)) failures.Add("workshop-capture");
            }

            RoomGate workshopGate = FindGate("GateToVillageSquare");
            if (!EnterGate(initialPlayer, workshopGate))
            {
                failures.Add("enter-workshop-gate");
            }
            else
            {
                yield return WaitForScene("CaligoVillageExteriorRegistered", 4f);
                yield return Settle();
                ValidatePlaza("WorkshopStair", failures);

                if (!string.IsNullOrWhiteSpace(approachCapture))
                {
                    yield return CaptureCamera(Camera.main, approachCapture, arguments);
                    if (!CaptureExists(approachCapture)) failures.Add("approach-capture");
                }
                yield return ValidateWorkshopStairDrop(failures);

                if (!string.IsNullOrWhiteSpace(plazaCapture))
                {
                    TiqueMotor plazaPlayer = FindAnyObjectByType<TiqueMotor>();
                    MovePlayer(plazaPlayer, new Vector2(-8.75f, -0.671875f));
                    yield return Settle(0.5f);
                    MovePlayer(plazaPlayer, new Vector2(-5f, -0.671875f));
                    yield return Settle(0.2f);
                    yield return CaptureCamera(Camera.main, plazaCapture, arguments);
                    if (!CaptureExists(plazaCapture)) failures.Add("plaza-capture");
                    if (Camera.main == null
                        || Mathf.Abs(Camera.main.transform.position.x + 5f) > 0.02f)
                    {
                        failures.Add("plaza-camera-position");
                    }
                }

                TiqueMotor upperRoutePlayer = FindAnyObjectByType<TiqueMotor>();
                MovePlayer(upperRoutePlayer, new Vector2(5f, -0.671875f));
                yield return Settle(0.15f);
                if (SceneManager.GetActiveScene().name != "CaligoVillageExteriorRegistered")
                    failures.Add("upper-route-workshop-trigger-bleed");

                RoomGate gateWatchGate = FindGate("GateToGateWatch");
                if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), gateWatchGate))
                {
                    failures.Add("enter-gate-watch-gate");
                }
                else
                {
                    yield return WaitForScene("CaligoGateWatchRegistered", 4f);
                    yield return Settle();
                    ValidateGateWatch("VillageArchExit", failures);
                    if (!string.IsNullOrWhiteSpace(gateWatchCapture))
                    {
                        MovePlayer(FindAnyObjectByType<TiqueMotor>(), new Vector2(0f, -0.671875f));
                        yield return Settle(0.15f);
                        yield return CaptureCamera(Camera.main, gateWatchCapture, arguments);
                        if (!CaptureExists(gateWatchCapture)) failures.Add("gate-watch-capture");
                    }

                    RoomGate bridgeGate = FindGate("GateToBridge");
                    if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), bridgeGate))
                    {
                        failures.Add("enter-bridge-gate");
                    }
                    else
                    {
                        yield return WaitForScene("LimbusCaligoBridgeRegistered", 4f);
                        yield return Settle();
                        ValidateBridge("CaligoGateExit", failures);
                        if (!string.IsNullOrWhiteSpace(bridgeGateCapture))
                        {
                            yield return CaptureCamera(Camera.main, bridgeGateCapture, arguments);
                            if (!CaptureExists(bridgeGateCapture))
                                failures.Add("bridge-gate-capture");
                        }

                        if (!string.IsNullOrWhiteSpace(bridgeCrossingCapture))
                        {
                            MovePlayer(
                                FindAnyObjectByType<TiqueMotor>(),
                                new Vector2(8.75f, -0.671875f));
                            yield return Settle(1.5f);
                            yield return CaptureCamera(
                                Camera.main, bridgeCrossingCapture, arguments);
                            if (!CaptureExists(bridgeCrossingCapture))
                                failures.Add("bridge-crossing-capture");
                            if (Camera.main == null
                                || Mathf.Abs(Camera.main.transform.position.x - 5f) > 0.04f)
                            {
                                failures.Add("bridge-camera-position");
                            }
                        }

                        RoomGate combatGate = FindGate("GateToBridgeCombat");
                        if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), combatGate))
                        {
                            failures.Add("enter-bridge-combat-gate");
                        }
                        else
                        {
                            yield return WaitForScene("LimbusBridgeCombatRegistered", 4f);
                            yield return Settle(0.15f);
                            ValidateBridgeCombat("CombatEntry", failures);
                            if (!string.IsNullOrWhiteSpace(bridgeCombatCapture))
                            {
                                MovePlayer(
                                    FindAnyObjectByType<TiqueMotor>(),
                                    new Vector2(0f, -0.671875f));
                                yield return Settle(0.15f);
                                RegisteredRouteCameraFollow2D combatFollow =
                                    Camera.main == null ? null : Camera.main.GetComponent<
                                        RegisteredRouteCameraFollow2D>();
                                if (combatFollow != null) combatFollow.enabled = false;
                                if (Camera.main != null)
                                    Camera.main.transform.position = new Vector3(0f, 0f, -10f);
                                yield return CaptureCamera(
                                    Camera.main, bridgeCombatCapture, arguments);
                                if (!CaptureExists(bridgeCombatCapture))
                                    failures.Add("bridge-combat-capture");
                            }

                            RoomGate scrapGate = FindGate("GateToScrapPlain");
                            if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), scrapGate))
                            {
                                failures.Add("enter-scrap-plain-gate");
                            }
                            else
                            {
                                yield return WaitForScene(
                                    "LimbusScrapPlainRegistered", 4f);
                                yield return Settle(0.2f);
                                ValidateScrapPlain("BridgeEntry", failures);

                                RegisteredRouteCameraFollow2D scrapFollow =
                                    Camera.main == null ? null : Camera.main.GetComponent<
                                        RegisteredRouteCameraFollow2D>();
                                yield return ValidateScrapCameraMotion(
                                    scrapFollow, FindAnyObjectByType<TiqueMotor>(), failures);
                                if (scrapFollow != null) scrapFollow.enabled = false;
                                if (!string.IsNullOrWhiteSpace(scrapWestCapture))
                                {
                                    MovePlayer(
                                        FindAnyObjectByType<TiqueMotor>(),
                                        new Vector2(-23f, -0.671875f));
                                    Camera.main.transform.position = new Vector3(-23f, 0f, -10f);
                                    yield return CaptureCamera(
                                        Camera.main, scrapWestCapture, arguments);
                                    if (!CaptureExists(scrapWestCapture))
                                        failures.Add("scrap-west-capture");
                                }
                                if (!string.IsNullOrWhiteSpace(scrapCenterCapture))
                                {
                                    MovePlayer(
                                        FindAnyObjectByType<TiqueMotor>(),
                                        new Vector2(0f, -0.671875f));
                                    Camera.main.transform.position = new Vector3(0f, 0f, -10f);
                                    yield return CaptureCamera(
                                        Camera.main, scrapCenterCapture, arguments);
                                    if (!CaptureExists(scrapCenterCapture))
                                        failures.Add("scrap-center-capture");
                                }
                                if (!string.IsNullOrWhiteSpace(scrapEastCapture))
                                {
                                    MovePlayer(
                                        FindAnyObjectByType<TiqueMotor>(),
                                        new Vector2(23f, -0.671875f));
                                    Camera.main.transform.position = new Vector3(23f, 0f, -10f);
                                    yield return CaptureCamera(
                                        Camera.main, scrapEastCapture, arguments);
                                    if (!CaptureExists(scrapEastCapture))
                                        failures.Add("scrap-east-capture");
                                }

                                RoomGate scrapReturnGate = FindGate("GateToBridgeCombat");
                                if (!EnterGate(
                                    FindAnyObjectByType<TiqueMotor>(), scrapReturnGate))
                                {
                                    failures.Add("return-bridge-combat-gate");
                                }
                                else
                                {
                                    yield return WaitForScene(
                                        "LimbusBridgeCombatRegistered", 4f);
                                    yield return Settle(0.65f);
                                    ValidateBridgeCombat("LimbusContinuation", failures);
                                }
                            }

                            RoomGate combatReturnGate = FindGate("GateToBridgeBody");
                            if (!EnterGate(
                                FindAnyObjectByType<TiqueMotor>(), combatReturnGate))
                            {
                                failures.Add("return-bridge-body-gate");
                            }
                            else
                            {
                                yield return WaitForScene(
                                    "LimbusCaligoBridgeRegistered", 4f);
                                yield return Settle();
                                ValidateBridge("LimbusRoute", failures);
                            }
                        }

                        RoomGate returnGate = FindGate("GateToGateWatch");
                        if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), returnGate))
                        {
                            failures.Add("return-gate-watch-gate");
                        }
                        else
                        {
                            yield return WaitForScene("CaligoGateWatchRegistered", 4f);
                            yield return Settle();
                            ValidateGateWatch("BridgeEntry", failures);
                        }
                    }

                    if (SceneManager.GetActiveScene().name == "CaligoGateWatchRegistered")
                    {
                        RoomGate plazaGate = FindGate("GateToVillageSquare");
                        if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), plazaGate))
                        {
                            failures.Add("return-plaza-gate");
                        }
                        else
                        {
                            yield return WaitForScene("CaligoVillageExteriorRegistered", 4f);
                            yield return Settle();
                            ValidatePlaza("GateArchExit", failures);
                        }
                    }
                }
            }

            if (SceneManager.GetActiveScene().name == "CaligoVillageExteriorRegistered")
            {
                RoomGate exteriorGate = FindGate("GateToMorbiWorkshop");
                if (!EnterGate(FindAnyObjectByType<TiqueMotor>(), exteriorGate))
                {
                    failures.Add("enter-exterior-gate");
                }
                else
                {
                    yield return WaitForScene("MorbiWorkshopRegistered", 4f);
                    yield return Settle();
                    ValidatePlayerAt(
                        FindAnyObjectByType<TiqueMotor>(), "PlazaEntry", failures, "workshop-return");
                }
            }

            bool valid = failures.Count == 0;
            Debug.Log($"CLOCKWORK_CALIGO_ROUTE_PROBE valid={valid} " +
                $"scene={SceneManager.GetActiveScene().name} " +
                $"failures={(valid ? "none" : string.Join(",", failures))}");
            Application.Quit(valid ? 0 : 2);
        }

        private static IEnumerator Settle(float seconds = 0.45f)
        {
            yield return null;
            yield return new WaitForFixedUpdate();
            yield return new WaitForSecondsRealtime(seconds);
        }

        private static IEnumerator ValidateScrapCameraMotion(
            RegisteredRouteCameraFollow2D follow, TiqueMotor player,
            List<string> failures)
        {
            if (follow == null || player == null || Camera.main == null)
            {
                failures.Add("scrap-camera-motion-missing");
                yield break;
            }

            Rigidbody2D body = player.GetComponent<Rigidbody2D>();
            if (body == null)
            {
                failures.Add("scrap-camera-motion-body");
                yield break;
            }

            follow.enabled = true;
            MovePlayer(player, new Vector2(-22f, -0.671875f));
            Camera.main.transform.position = new Vector3(-23f, 0f, -10f);
            yield return null;

            float previousX = Camera.main.transform.position.x;
            float largestStep = 0f;
            float largestCenterOffset = 0f;
            bool movedBackward = false;
            const int steps = 240;
            for (int step = 1; step <= steps; step++)
            {
                float x = Mathf.Lerp(-22f, -12f, step / (float)steps);
                body.position = new Vector2(x, -0.671875f);
                body.linearVelocity = new Vector2(2.5f, 0f);
                Physics2D.SyncTransforms();
                yield return null;

                float currentX = Camera.main.transform.position.x;
                largestStep = Mathf.Max(largestStep, Mathf.Abs(currentX - previousX));
                if (step > 20)
                    largestCenterOffset = Mathf.Max(
                        largestCenterOffset, Mathf.Abs(currentX - x));
                if (currentX < previousX - 0.02f) movedBackward = true;
                previousX = currentX;
            }

            body.linearVelocity = Vector2.zero;
            yield return Settle(0.35f);
            float finalX = Camera.main.transform.position.x;
            if (largestStep > 0.22f) failures.Add("scrap-camera-motion-jump");
            if (largestCenterOffset > 0.65f)
                failures.Add("scrap-camera-not-centered");
            if (movedBackward) failures.Add("scrap-camera-motion-reverse");
            if (finalX < -13.75f || finalX > -11.75f)
                failures.Add("scrap-camera-motion-lag");

            MovePlayer(player, new Vector2(-23f, -0.671875f));
            Camera.main.transform.position = new Vector3(-23f, 0f, -10f);
            yield return null;
        }

        private static IEnumerator ValidateWorkshopStairDrop(List<string> failures)
        {
            OneWayStairDropZone stairDrop = FindAnyObjectByType<OneWayStairDropZone>();
            TiqueMotor player = FindAnyObjectByType<TiqueMotor>();
            if (stairDrop == null || player == null || stairDrop.OneWayPlatform == null)
            {
                failures.Add("plaza-workshop-stair-drop-missing");
                yield break;
            }

            Rigidbody2D body = player.GetComponent<Rigidbody2D>();
            Collider2D playerCollider = player.GetComponent<Collider2D>();
            if (body == null || playerCollider == null)
            {
                failures.Add("plaza-workshop-stair-drop-player");
                yield break;
            }

            MovePlayer(player, new Vector2(5.85f, -0.671875f));
            yield return null;
            float startingY = body.position.y;
            if (!stairDrop.BeginDrop(player))
            {
                failures.Add("plaza-workshop-stair-drop-start");
                yield break;
            }
            if (!Physics2D.GetIgnoreCollision(playerCollider, stairDrop.OneWayPlatform))
                failures.Add("plaza-workshop-stair-drop-ignore");

            yield return Settle(0.15f);
            if (body.position.y > startingY - 0.2f)
                failures.Add("plaza-workshop-stair-drop-distance");
            yield return Settle(0.35f);
            if (Physics2D.GetIgnoreCollision(playerCollider, stairDrop.OneWayPlatform))
                failures.Add("plaza-workshop-stair-drop-restore");

            MovePlayer(player, new Vector2(5f, -0.671875f));
            yield return null;
        }

        private static bool IsCenterFollow(RegisteredRouteCameraFollow2D follow)
        {
            return follow != null
                && follow.SmoothTracking
                && Mathf.Abs(follow.HorizontalDeadZone) <= 0.001f
                && Mathf.Abs(follow.LookAheadDistance) <= 0.001f
                && Mathf.Abs(follow.FollowSmoothTime - 0.1f) <= 0.001f;
        }

        private static void ValidateWorkshop(
            Transform layerRoot, Camera roomCamera, TiqueMotor player,
            string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "MorbiWorkshopRegistered")
                failures.Add("workshop-scene");
            ValidateRegistration(
                layerRoot, roomCamera, WorkshopLayerNames, 640, 360, failures, "workshop");
            ValidatePlayerAt(player, expectedSpawn, failures, "workshop");
            if (FindAnyObjectByType<MorbiNpc>() == null) failures.Add("workshop-morbi");

            RoomGate gate = FindGate("GateToVillageSquare");
            if (gate == null
                || gate.DestinationRoomId != "caligo-village-exterior-registered"
                || gate.DestinationSpawnId != "WorkshopStair")
            {
                failures.Add("workshop-gate");
            }
        }

        private static void ValidatePlaza(string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "CaligoVillageExteriorRegistered")
            {
                failures.Add("plaza-scene");
                return;
            }

            Transform root = GameObject.Find("RegisteredPlazaLayers_1280x360_PPU64")?.transform;
            ValidateRegistration(root, Camera.main, PlazaLayerNames, 1280, 360, failures, "plaza");
            TiqueMotor player = FindAnyObjectByType<TiqueMotor>();
            ValidatePlayerAt(player, expectedSpawn, failures, "plaza");

            string[] anchors =
            {
                "WorkshopStair", "VillageSquareCenter", "WaterServiceStair", "GateArchExit"
            };
            foreach (string anchor in anchors)
            {
                if (FindSpawn(anchor) == null) failures.Add($"anchor-{anchor}");
            }

            RoomGate workshopGate = FindGate("GateToMorbiWorkshop");
            RoomGate gateWatchGate = FindGate("GateToGateWatch");
            if (workshopGate == null
                || workshopGate.DestinationRoomId != "morbi-workshop-registered"
                || workshopGate.DestinationSpawnId != "PlazaEntry")
            {
                failures.Add("plaza-workshop-gate");
            }
            if (gateWatchGate == null
                || gateWatchGate.DestinationRoomId != "caligo-gate-watch-registered"
                || gateWatchGate.DestinationSpawnId != "VillageArchExit")
            {
                failures.Add("plaza-gate-watch-gate");
            }

            BoxCollider2D workshopTrigger = workshopGate == null
                ? null
                : workshopGate.GetComponent<BoxCollider2D>();
            if (workshopTrigger == null || workshopTrigger.bounds.max.y > -0.8f)
                failures.Add("plaza-workshop-trigger-height");

            RegisteredRouteCameraFollow2D follow = Camera.main == null
                ? null
                : Camera.main.GetComponent<RegisteredRouteCameraFollow2D>();
            TiqueMotor followedMotor = follow == null || follow.Target == null
                ? null
                : follow.Target.GetComponentInChildren<TiqueMotor>();
            if (follow == null || followedMotor != player
                || Mathf.Abs(follow.MinimumX + 5f) > 0.001f
                || Mathf.Abs(follow.MaximumX - 5f) > 0.001f
                || !IsCenterFollow(follow))
            {
                failures.Add("plaza-camera-follow");
            }

            GameObject bypass = GameObject.Find("WorkshopUpperBypass");
            EdgeCollider2D edge = bypass == null ? null : bypass.GetComponent<EdgeCollider2D>();
            PlatformEffector2D effector = bypass == null
                ? null
                : bypass.GetComponent<PlatformEffector2D>();
            if (edge == null || !edge.usedByEffector || effector == null || !effector.useOneWay)
                failures.Add("plaza-upper-bypass");
            OneWayStairDropZone stairDrop = FindAnyObjectByType<OneWayStairDropZone>();
            if (stairDrop == null || stairDrop.OneWayPlatform != edge)
                failures.Add("plaza-workshop-stair-drop");
        }

        private static void ValidateGateWatch(string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "CaligoGateWatchRegistered")
            {
                failures.Add("gate-watch-scene");
                return;
            }

            Transform root = GameObject.Find("RegisteredGateWatchLayers_640x360_PPU64")?.transform;
            ValidateRegistration(
                root, Camera.main, GateWatchLayerNames, 640, 360, failures, "gate-watch");
            ValidatePlayerAt(
                FindAnyObjectByType<TiqueMotor>(), expectedSpawn, failures, "gate-watch");

            foreach (string anchor in new[] { "VillageArchExit", "BridgeEntry", "DropShaftGate" })
            {
                if (FindSpawn(anchor) == null) failures.Add($"gate-watch-anchor-{anchor}");
            }

            RoomGate gate = FindGate("GateToVillageSquare");
            RoomGate bridgeGate = FindGate("GateToBridge");
            if (gate == null
                || gate.DestinationRoomId != "caligo-village-exterior-registered"
                || gate.DestinationSpawnId != "GateArchExit")
            {
                failures.Add("gate-watch-plaza-gate");
            }
            if (bridgeGate == null
                || bridgeGate.DestinationRoomId != "limbus-caligo-bridge-registered"
                || bridgeGate.DestinationSpawnId != "CaligoGateExit")
            {
                failures.Add("gate-watch-bridge-gate");
            }
            if (Camera.main != null
                && Camera.main.GetComponent<RegisteredRouteCameraFollow2D>() != null)
            {
                failures.Add("gate-watch-camera-follow");
            }
        }

        private static void ValidateBridge(string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "LimbusCaligoBridgeRegistered")
            {
                failures.Add("bridge-scene");
                return;
            }

            Transform root = GameObject.Find(
                "RegisteredBridgeLayers_1280x360_PPU64")?.transform;
            ValidateRegistration(
                root, Camera.main, BridgeLayerNames, 1280, 360, failures, "bridge");
            ValidateToxicFxBehindGameplay(root, failures, "bridge");
            TiqueMotor player = FindAnyObjectByType<TiqueMotor>();
            ValidatePlayerAt(player, expectedSpawn, failures, "bridge");

            foreach (string anchor in new[] { "CaligoGateExit", "LimbusRoute" })
            {
                if (FindSpawn(anchor) == null) failures.Add($"bridge-anchor-{anchor}");
            }

            RoomGate gate = FindGate("GateToGateWatch");
            if (gate == null
                || gate.DestinationRoomId != "caligo-gate-watch-registered"
                || gate.DestinationSpawnId != "BridgeEntry")
            {
                failures.Add("bridge-gate-watch-gate");
            }
            RoomGate combatGate = FindGate("GateToBridgeCombat");
            if (combatGate == null
                || combatGate.DestinationRoomId != "limbus-bridge-combat-registered"
                || combatGate.DestinationSpawnId != "CombatEntry")
            {
                failures.Add("bridge-combat-gate");
            }

            RegisteredRouteCameraFollow2D follow = Camera.main == null
                ? null
                : Camera.main.GetComponent<RegisteredRouteCameraFollow2D>();
            TiqueMotor followedMotor = follow == null || follow.Target == null
                ? null
                : follow.Target.GetComponentInChildren<TiqueMotor>();
            if (follow == null || followedMotor != player
                || Mathf.Abs(follow.MinimumX + 5f) > 0.001f
                || Mathf.Abs(follow.MaximumX - 5f) > 0.001f
                || !IsCenterFollow(follow))
            {
                failures.Add("bridge-camera-follow");
            }

            if (FindAnyObjectByType<BridgeCollapseDirector>() != null
                || FindAnyObjectByType<RatEnemy>() != null)
            {
                failures.Add("bridge-canon-gameplay-duplicated");
            }
        }

        private static void ValidateBridgeCombat(
            string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "LimbusBridgeCombatRegistered")
            {
                failures.Add("bridge-combat-scene");
                return;
            }

            Transform root = GameObject.Find(
                "RegisteredBridgeCombatLayers_1280x360_PPU64")?.transform;
            ValidateRegistration(
                root, Camera.main, BridgeLayerNames, 1280, 360,
                failures, "bridge-combat");
            ValidateToxicFxBehindGameplay(root, failures, "bridge-combat");
            ValidatePlayerAt(
                FindAnyObjectByType<TiqueMotor>(), expectedSpawn,
                failures, "bridge-combat");
            RegisteredRouteCameraFollow2D combatFollow = Camera.main == null
                ? null
                : Camera.main.GetComponent<RegisteredRouteCameraFollow2D>();
            if (!IsCenterFollow(combatFollow))
                failures.Add("bridge-combat-camera-follow");

            if (FindSpawn("CombatEntry") == null
                || FindSpawn("LimbusContinuation") == null)
            {
                failures.Add("bridge-combat-anchors");
            }
            RoomGate gate = FindGate("GateToBridgeBody");
            if (gate == null
                || gate.DestinationRoomId != "limbus-caligo-bridge-registered"
                || gate.DestinationSpawnId != "LimbusRoute")
            {
                failures.Add("bridge-combat-return-gate");
            }
            RoomGate scrapGate = FindGate("GateToScrapPlain");
            if (scrapGate == null
                || scrapGate.DestinationRoomId != "limbus-scrap-plain-registered"
                || scrapGate.DestinationSpawnId != "BridgeEntry")
            {
                failures.Add("bridge-combat-scrap-gate");
            }
            if (FindAnyObjectByType<BridgeCollapseDirector>() == null
                || FindObjectsByType<RatEnemy>(FindObjectsSortMode.None).Length != 3)
            {
                failures.Add("bridge-combat-canon-pack");
            }
        }

        private static void ValidateScrapPlain(
            string expectedSpawn, List<string> failures)
        {
            if (SceneManager.GetActiveScene().name != "LimbusScrapPlainRegistered")
            {
                failures.Add("scrap-plain-scene");
                return;
            }

            Transform root = GameObject.Find(
                "RegisteredScrapPlain_3584x360_PPU64")?.transform;
            ValidateRegistration(
                root, Camera.main, ScrapPlainLayerNames, 3584, 360,
                failures, "scrap-plain");
            TiqueMotor player = FindAnyObjectByType<TiqueMotor>();
            ValidatePlayerAt(player, expectedSpawn, failures, "scrap-plain");

            foreach (string anchor in new[] { "BridgeEntry", "CrashApproach" })
            {
                if (FindSpawn(anchor) == null) failures.Add($"scrap-anchor-{anchor}");
            }
            RoomGate gate = FindGate("GateToBridgeCombat");
            if (gate == null
                || gate.DestinationRoomId != "limbus-bridge-combat-registered"
                || gate.DestinationSpawnId != "LimbusContinuation")
            {
                failures.Add("scrap-bridge-gate");
            }

            RegisteredRouteCameraFollow2D follow = Camera.main == null
                ? null
                : Camera.main.GetComponent<RegisteredRouteCameraFollow2D>();
            if (follow == null || follow.Target != player.transform
                || Mathf.Abs(follow.MinimumX + 23f) > 0.001f
                || Mathf.Abs(follow.MaximumX - 23f) > 0.001f
                || !follow.SmoothTracking
                || Mathf.Abs(follow.HorizontalDeadZone) > 0.001f
                || Mathf.Abs(follow.LookAheadDistance) > 0.001f
                || Mathf.Abs(follow.FollowSmoothTime - 0.1f) > 0.001f)
            {
                failures.Add("scrap-camera-follow");
            }
            if (FindAnyObjectByType<BridgeCollapseDirector>() != null
                || FindAnyObjectByType<RatEnemy>() != null)
            {
                failures.Add("scrap-enemy-free");
            }
        }

        private static void ValidateRegistration(
            Transform root, Camera roomCamera, string[] expectedLayerNames,
            int expectedWidth, int expectedHeight, List<string> failures, string prefix)
        {
            if (root == null)
            {
                failures.Add($"{prefix}-layers");
                return;
            }

            Dictionary<string, SpriteRenderer> renderers = root
                .GetComponentsInChildren<SpriteRenderer>(true)
                .ToDictionary(renderer => renderer.gameObject.name, StringComparer.Ordinal);
            foreach (string layerName in expectedLayerNames)
            {
                if (!renderers.TryGetValue(layerName, out SpriteRenderer renderer))
                {
                    failures.Add($"{prefix}-{layerName}");
                    continue;
                }

                Transform layer = renderer.transform;
                bool sharedDoor = layerName == "Layer_30_SharedWoodDoor";
                Vector2 expectedPosition = sharedDoor
                    ? prefix == "plaza"
                        ? new Vector2(7.4765625f, -1.984375f)
                        : new Vector2(-4.015625f, -1.40625f)
                    : Vector2.zero;
                if (Vector2.Distance(layer.localPosition, expectedPosition) > 0.0001f)
                    failures.Add($"{prefix}-position-{layerName}");
                if ((layer.localScale - Vector3.one).sqrMagnitude > 0.000001f)
                    failures.Add($"{prefix}-scale");
                Sprite sprite = renderer.sprite;
                int layerWidth = sharedDoor ? 52 : expectedWidth;
                int layerHeight = sharedDoor ? 72 : expectedHeight;
                if (sprite == null || sprite.texture.width != layerWidth
                    || sprite.texture.height != layerHeight)
                {
                    failures.Add($"{prefix}-canvas");
                }
                else if (sharedDoor
                    && (Mathf.Abs(sprite.pivot.x - 26f) > 0.01f
                        || Mathf.Abs(sprite.pivot.y) > 0.01f))
                {
                    failures.Add($"{prefix}-shared-door-pivot");
                }
                else if (renderer.sprite.texture.filterMode != FilterMode.Point)
                {
                    failures.Add($"{prefix}-painterly-filter");
                }
                else if (Mathf.Abs(sprite.pixelsPerUnit - 64f) > 0.001f)
                {
                    failures.Add($"{prefix}-ppu");
                }
            }

            if (renderers.Count != expectedLayerNames.Length) failures.Add($"{prefix}-layer-count");
            if (root.GetComponentsInChildren<ParallaxLayer2D>(true).Length != 0)
                failures.Add($"{prefix}-parallax");
            if (roomCamera == null || !roomCamera.orthographic
                || Mathf.Abs(roomCamera.orthographicSize - 2.8125f) > 0.0001f)
            {
                failures.Add($"{prefix}-camera");
                return;
            }

            PixelPerfectCamera pixelPerfect = roomCamera.GetComponent<PixelPerfectCamera>();
            if (pixelPerfect == null || pixelPerfect.assetsPPU != 64
                || pixelPerfect.refResolutionX != 640 || pixelPerfect.refResolutionY != 360)
            {
                failures.Add($"{prefix}-pixel-perfect");
            }
        }

        private static void ValidatePlayerAt(
            TiqueMotor player, string spawnId, List<string> failures, string prefix)
        {
            SpawnPoint spawn = FindSpawn(spawnId);
            if (player == null || spawn == null)
            {
                failures.Add($"{prefix}-player");
                return;
            }

            if (Vector2.Distance(player.transform.position, spawn.transform.position) > 0.2f)
                failures.Add($"{prefix}-spawn-{spawnId}");
            if (!player.Grounded) failures.Add($"{prefix}-grounded");
            if ((player.transform.localScale - Vector3.one).sqrMagnitude > 0.000001f)
                failures.Add($"{prefix}-root-scale");
        }

        private static SpawnPoint FindSpawn(string id)
        {
            return FindObjectsByType<SpawnPoint>(FindObjectsSortMode.None)
                .FirstOrDefault(point => point.SpawnId == id);
        }

        private static RoomGate FindGate(string id)
        {
            return FindObjectsByType<RoomGate>(FindObjectsSortMode.None)
                .FirstOrDefault(gate => gate.GateId == id);
        }

        private static void ValidateToxicFxBehindGameplay(
            Transform root, List<string> failures, string prefix)
        {
            SpriteRenderer gameplay = root == null
                ? null
                : root.Find("Layer_30_Gameplay")?.GetComponent<SpriteRenderer>();
            SpriteRenderer toxicFx = root == null
                ? null
                : root.Find("Layer_80_ToxicFx")?.GetComponent<SpriteRenderer>();
            if (gameplay == null || toxicFx == null
                || toxicFx.sortingOrder >= gameplay.sortingOrder)
            {
                failures.Add($"{prefix}-toxic-fx-occludes-gameplay");
            }
        }

        private static bool EnterGate(TiqueMotor player, RoomGate gate)
        {
            if (player == null || gate == null) return false;
            return MovePlayer(player, gate.transform.position);
        }

        private static bool MovePlayer(TiqueMotor player, Vector2 target)
        {
            if (player == null) return false;
            Rigidbody2D body = player.GetComponent<Rigidbody2D>();
            if (body == null) return false;
            body.position = target;
            body.linearVelocity = Vector2.zero;
            Physics2D.SyncTransforms();
            return true;
        }

        private static IEnumerator WaitForScene(string sceneName, float timeout)
        {
            float deadline = Time.realtimeSinceStartup + timeout;
            while (SceneManager.GetActiveScene().name != sceneName
                && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
        }

        private static IEnumerator CaptureCamera(Camera camera, string path, string[] arguments)
        {
            if (camera == null) yield break;
            string fullPath = Path.GetFullPath(path);
            string directory = Path.GetDirectoryName(fullPath);
            if (!string.IsNullOrEmpty(directory)) Directory.CreateDirectory(directory);
            int width = ReadIntArgument(arguments, "-screen-width", 1280);
            int height = ReadIntArgument(arguments, "-screen-height", 720);

            RenderTexture target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32)
            {
                filterMode = FilterMode.Point,
                name = "CaligoVillagePlazaRouteV5Capture"
            };
            target.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = camera.targetTexture;
            camera.targetTexture = target;

            yield return null;
            camera.Render();
            yield return new WaitForEndOfFrame();

            RenderTexture.active = target;
            Texture2D capture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            capture.ReadPixels(new Rect(0f, 0f, width, height), 0, 0, false);
            capture.Apply(false, false);
            File.WriteAllBytes(fullPath, capture.EncodeToPNG());

            camera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            Destroy(capture);
            target.Release();
            Destroy(target);
        }

        private static bool CaptureExists(string path)
        {
            string fullPath = Path.GetFullPath(path);
            return File.Exists(fullPath) && new FileInfo(fullPath).Length > 0;
        }

        private static string ReadArgument(string[] arguments, string name)
        {
            for (int i = 0; i < arguments.Length - 1; i++)
            {
                if (string.Equals(arguments[i], name, StringComparison.Ordinal))
                    return arguments[i + 1];
            }
            return null;
        }

        private static int ReadIntArgument(string[] arguments, string name, int fallback)
        {
            string value = ReadArgument(arguments, name);
            return int.TryParse(value, out int parsed) && parsed > 0 ? parsed : fallback;
        }

#if UNITY_EDITOR
        public void Configure(Transform layerRoot, Camera roomCamera, TiqueMotor player)
        {
            initialLayerRoot = layerRoot;
            initialCamera = roomCamera;
            initialPlayer = player;
        }
#endif
    }
}
