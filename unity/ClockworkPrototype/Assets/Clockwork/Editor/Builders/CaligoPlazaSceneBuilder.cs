using System;
using System.Linq;
using Clockwork;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.Tilemaps;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private const float CaligoPlatformTopPadding = 7f / 32f;
        private const float CaligoBackgroundScale = 0.625f;
        private const float CaligoFarBackgroundY = 0.94f;
        private const float CaligoMidBackgroundY = -0.36f;
        private const float CaligoNpcFootY = -1.75f;
        private const float CaligoNpcVisualScale = 0.32f;
        private const float CaligoNpcVisualY = 0.59f;

        private static void BuildPlazaScene(GameObject playerPrefab, TileBase tile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoPlaza";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildPlazaTilemap(tile);

            GameObject lightObject = new GameObject("PlazaGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.96f, 0.84f, 0.7f);
            light.intensity = 1.02f;

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(0f, -2f, 0f);

            BuildRoomGate("GateToWorkshop", new Vector2(6.65f, -1.25f), "caligo", "caligo-workshop");
            BuildRoomGate("GateToDropShaft", new Vector2(-6.65f, -1.25f), "caligo-drop-shaft", "entry-plaza");
            BuildSpawnPoint("entry-workshop", new Vector2(6f, -2f));
            BuildSpawnPoint("entry-drop-shaft", new Vector2(-6f, -2f));
            BuildSpawnPoint("plaza-checkpoint", new Vector2(0.6f, -2f));

            RepairSavePoint checkpoint = BuildRepairSavePoint(
                "PlazaCheckpoint", new Vector2(0.6f, -2f), "caligo-plaza", "plaza-checkpoint");
            checkpoint.GetComponentInChildren<SpriteRenderer>().enabled = false;

            Camera camera = BuildCamera(player.transform, room.CameraBounds);
            BuildPlazaEnvironment(camera);
            BuildPlazaNpcLayer();
            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), checkpoint, player.GetComponent<TiqueHealth>());
            EditorSceneManager.SaveScene(scene, PlazaScenePath);
            if (SystemInfo.graphicsDeviceType != GraphicsDeviceType.Null)
            {
                SpriteRenderer playerRenderer = player.GetComponentInChildren<SpriteRenderer>();
                playerRenderer.enabled = false;
                CapturePreview(camera, PlazaPreviewPath);
                playerRenderer.enabled = true;
            }
        }

        private static void BuildDropShaftScene(GameObject playerPrefab, TileBase tile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoDropShaft";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildDropShaftTilemap(tile);

            GameObject lightObject = new GameObject("DropShaftGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.52f, 0.58f, 0.57f);
            light.intensity = 0.58f;

            BuildPlazaStructure("ServicePipeLeft", new Vector2(-2.5f, -2.2f), new Vector2(0.35f, 12f),
                new Color(0.35f, 0.24f, 0.18f, 0.9f), -15);
            BuildPlazaStructure("ServicePipeRight", new Vector2(2.25f, -4.2f), new Vector2(0.3f, 8f),
                new Color(0.24f, 0.34f, 0.34f, 0.9f), -15);

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(0f, 4.2f, 0f);

            // First traversal is deliberately one-way. Hook-based return remains deferred.
            BuildSpawnPoint("entry-plaza", new Vector2(0f, 4.2f));
            BuildSpawnPoint("drop-landing", new Vector2(0f, -9.95f));
            BuildRoomGate("GateToCrossingCavern", new Vector2(2.65f, -9.2f), "crossing-cavern", "entry-drop-shaft");

            BuildCamera(player.transform, room.CameraBounds);
            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());
            EditorSceneManager.SaveScene(scene, DropShaftScenePath);
        }

        private static RoomDefinition EnsurePlazaRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(PlazaRoomAssetPath);
            room.Configure(
                "caligo-plaza",
                "Caligo Village Plaza",
                new Rect(-7f, -3f, 14f, 6f),
                "act1-caligo-plaza");
            EditorUtility.SetDirty(room);
            return room;
        }

        private static RoomDefinition EnsureDropShaftRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(DropShaftRoomAssetPath);
            room.Configure(
                "caligo-drop-shaft",
                "Caligo Drop Shaft",
                new Rect(-4f, -11f, 8f, 17f),
                "act1-caligo-drop-shaft");
            EditorUtility.SetDirty(room);
            return room;
        }

        private static void BuildPlazaTilemap(TileBase tile)
        {
            Tilemap tilemap = BuildCollisionTilemap("PlazaRoomTilemap", out TilemapCollider2D tilemapCollider,
                out CompositeCollider2D composite);
            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 11);
            Fill(tilemap, tile, 26, 27, -8, 11);
            Fill(tilemap, tile, -9, -3, -8, -8);
            Fill(tilemap, tile, 8, 13, -8, -8);
            FinalizeTilemap(tilemap, tilemapCollider, composite);
            tilemap.GetComponent<TilemapRenderer>().enabled = false;
        }

        private static void BuildDropShaftTilemap(TileBase tile)
        {
            Tilemap tilemap = BuildCollisionTilemap("DropShaftTilemap", out TilemapCollider2D tilemapCollider,
                out CompositeCollider2D composite);
            Fill(tilemap, tile, -12, 11, -44, -41);
            Fill(tilemap, tile, -12, -11, -40, 24);
            Fill(tilemap, tile, 10, 11, -40, 24);
            Fill(tilemap, tile, -10, -5, -4, -4);
            Fill(tilemap, tile, 4, 9, -16, -16);
            Fill(tilemap, tile, -10, -5, -28, -28);
            FinalizeTilemap(tilemap, tilemapCollider, composite);
        }

        private static void BuildPlazaStructure(
            string name, Vector2 position, Vector2 size, Color color, int sortingOrder)
        {
            GameObject structure = new GameObject(name);
            SpriteRenderer renderer = structure.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = color;
            renderer.sortingOrder = sortingOrder;
            structure.transform.position = new Vector3(position.x, position.y, 2f);
            structure.transform.localScale = new Vector3(size.x, size.y, 1f);
        }

        private static void BuildPlazaEnvironment(Camera camera)
        {
            GameObject root = new GameObject("CaligoPlazaEnvironment");
            BuildPlazaBackgroundLayer(
                root.transform, camera, "Far", CaligoFarPath, -120, 0.75f, 0.25f,
                CaligoFarBackgroundY, new Color(1.35f, 1.35f, 1.35f, 1f));
            BuildPlazaBackgroundLayer(
                root.transform, camera, "Mid", CaligoMidPath, -80, 0f, 0f,
                CaligoMidBackgroundY, new Color(1.2f, 1.2f, 1.2f, 1f));

            BuildGroundedPlazaSprite(root.transform, "FloorLeft", CaligoPlatformRoot + "/strip-4.png", -2.1f, -2f, 1);
            BuildGroundedPlazaSprite(root.transform, "FloorRight", CaligoPlatformRoot + "/strip-2.png", 4.85f, -2f, 1);
            BuildGroundedPlazaSprite(root.transform, "WestStep", CaligoPlatformRoot + "/stair-left.png", -1.5f, -1.75f, 1);
            BuildGroundedPlazaSprite(root.transform, "EastLedge", CaligoPlatformRoot + "/low-ledge.png", 2.65f, -1.75f, 1);
        }

        private static void BuildPlazaBackgroundLayer(
            Transform parent,
            Camera camera,
            string name,
            string spritePath,
            int sortingOrder,
            float horizontalFactor,
            float verticalFactor,
            float verticalPosition,
            Color color)
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
            if (sprite == null) throw new InvalidOperationException($"Missing Caligo background layer: {spritePath}");

            GameObject gameObject = new GameObject($"Caligo{name}Layer");
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.position = new Vector3(0f, verticalPosition, 5f);
            gameObject.transform.localScale = Vector3.one * CaligoBackgroundScale;

            for (int panelIndex = -1; panelIndex <= 1; panelIndex++)
            {
                GameObject panel = new GameObject($"Panel{panelIndex + 2}");
                panel.transform.SetParent(gameObject.transform, false);
                panel.transform.localPosition = new Vector3(sprite.bounds.size.x * panelIndex, 0f, 0f);
                SpriteRenderer renderer = panel.AddComponent<SpriteRenderer>();
                renderer.sprite = sprite;
                renderer.sortingOrder = sortingOrder;
                renderer.color = color;
            }

            ParallaxLayer2D parallax = gameObject.AddComponent<ParallaxLayer2D>();
            parallax.Configure(camera, horizontalFactor, verticalFactor);
        }

        private static void BuildGroundedPlazaSprite(
            Transform parent, string name, string spritePath, float x, float topY, int sortingOrder)
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
            if (sprite == null) throw new InvalidOperationException($"Missing Caligo platform sprite: {spritePath}");

            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            gameObject.transform.position = new Vector3(
                x, topY - sprite.bounds.max.y + CaligoPlatformTopPadding, 0f);
            SpriteRenderer renderer = gameObject.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = sortingOrder;
        }

        private static void BuildPlazaNpcLayer()
        {
            GameObject root = new GameObject("CaligoAmbientResidents");
            BuildAmbientNpc(
                root.transform,
                "PipeMechanic",
                new Vector2(-4.45f, CaligoNpcFootY),
                CaligoNpcRoot + "/PipeMechanic/Frames/Idle",
                CaligoNpcRoot + "/PipeMechanic/Frames/RepairWork",
                4f, 6f, false, 0f, 0f);
            BuildAmbientNpc(
                root.transform,
                "WaterRationAttendant",
                new Vector2(0.65f, CaligoNpcFootY),
                CaligoNpcRoot + "/WaterRationAttendant/Frames/Idle",
                CaligoNpcRoot + "/WaterRationAttendant/Frames/RationWork",
                4f, 5f, false, 0f, 0f);
            BuildAmbientNpc(
                root.transform,
                "CleanWaterCarrier",
                new Vector2(4.25f, CaligoNpcFootY),
                CaligoNpcRoot + "/CleanWaterCarrier/Frames/Idle",
                CaligoNpcRoot + "/CleanWaterCarrier/Frames/WalkRight",
                4f, 8f, true, 0.72f, 0.3f);
        }

        private static void BuildAmbientNpc(
            Transform parent,
            string name,
            Vector2 footPosition,
            string idleFolder,
            string roleFolder,
            float idleFps,
            float roleFps,
            bool patrol,
            float patrolDistance,
            float patrolSpeed)
        {
            Sprite[] idle = LoadSprites(idleFolder);
            Sprite[] role = LoadSprites(roleFolder);
            if (idle.Length == 0 || role.Length == 0)
            {
                throw new InvalidOperationException($"Missing animation frames for Caligo NPC {name}.");
            }

            GameObject npc = new GameObject(name);
            npc.transform.SetParent(parent, false);
            npc.transform.position = new Vector3(footPosition.x, footPosition.y, 1f);

            GameObject visual = new GameObject("Visual");
            visual.transform.SetParent(npc.transform, false);
            visual.transform.localPosition = new Vector3(0f, CaligoNpcVisualY, 0f);
            visual.transform.localScale = Vector3.one * CaligoNpcVisualScale;
            SpriteRenderer renderer = visual.AddComponent<SpriteRenderer>();
            renderer.sprite = idle[0];
            renderer.sortingOrder = -40;
            renderer.color = new Color(0.95f, 0.96f, 1f, 0.98f);

            GameObject workLightObject = new GameObject("WorkLight");
            workLightObject.transform.SetParent(npc.transform, false);
            workLightObject.transform.localPosition = new Vector3(0f, 0.52f, 0f);
            Light2D workLight = workLightObject.AddComponent<Light2D>();
            workLight.lightType = Light2D.LightType.Point;
            workLight.color = new Color(1f, 0.72f, 0.42f);
            workLight.intensity = 0.34f;
            workLight.pointLightInnerRadius = 0.1f;
            workLight.pointLightOuterRadius = 0.82f;

            AmbientNpc2D ambient = npc.AddComponent<AmbientNpc2D>();
            ambient.Configure(
                renderer, idle, role, idleFps, roleFps, 3.5f, 6f,
                patrol, patrolDistance, patrolSpeed);
        }

        private static Sprite[] LoadSprites(string folder)
        {
            return AssetDatabase.FindAssets("t:Sprite", new[] { folder })
                .Select(AssetDatabase.GUIDToAssetPath)
                .OrderBy(path => path, StringComparer.Ordinal)
                .Select(path => AssetDatabase.LoadAssetAtPath<Sprite>(path))
                .Where(sprite => sprite != null)
                .ToArray();
        }
    }
}
