using System;
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
        private static void BuildPlazaScene(GameObject playerPrefab, TileBase tile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoPlaza";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildPlazaTilemap(tile);
            BuildPlazaBackground();

            GameObject lightObject = new GameObject("PlazaGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.9f, 0.72f, 0.5f);
            light.intensity = 0.76f;

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

        private static void BuildPlazaBackground()
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(PlazaBackgroundPath);
            if (sprite == null) throw new InvalidOperationException("Caligo plaza concept background was not imported.");

            GameObject gameObject = new GameObject("CaligoPlazaConceptBackground");
            SpriteRenderer renderer = gameObject.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = -100;

            float scale = 14f / sprite.bounds.size.x;
            float height = sprite.bounds.size.y * scale;
            float sourceGroundFromBottom = (sprite.texture.height - 700f) / 100f * scale;
            float localGround = sourceGroundFromBottom - height * 0.5f;
            gameObject.transform.localScale = Vector3.one * scale;
            gameObject.transform.position = new Vector3(0f, -2f - localGround, 5f);
        }
    }
}
