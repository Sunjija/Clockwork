using System;
using Clockwork;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.Tilemaps;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private static void BuildLimbusScene(GameObject playerPrefab, TileBase tile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "Limbus";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildLimbusTilemap(tile);
            BuildOpeningDirectionDressing();

            GameObject lightObject = new GameObject("LimbusGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.6f, 0.72f, 0.8f);
            light.intensity = 0.72f;

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(4.5f, -2f, 0f);
            TiqueMotor motor = player.GetComponent<TiqueMotor>();
            motor.SetFacing(-1);

            // The boot spawn faces west; a return from the bridge faces back into Limbus.
            BuildSpawnPoint("start-awakening", new Vector2(4.5f, -2f), -1);
            BuildSpawnPoint("entry-bridge", new Vector2(-6f, -2f), 1);
            BuildRoomGate("GateToBridge", new Vector2(-6.65f, -1.25f), "limbus-caligo-bridge", "entry-limbus");

            MysteryPartPickup partPickup = BuildMysteryPart(new Vector2(-3.25f, -1.25f));

            GameObject cameraTargetObject = new GameObject("LimbusDirectionalCameraTarget");
            DirectionalCameraTarget cameraTarget = cameraTargetObject.AddComponent<DirectionalCameraTarget>();
            cameraTarget.Configure(player.transform, motor, 0.8f);
            BuildCamera(cameraTarget.transform, room.CameraBounds);

            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>(), partPickup);

            EditorSceneManager.SaveScene(scene, LimbusScenePath);
        }

        private static void BuildOpeningDirectionDressing()
        {
            // The sealed chute is arrival history, not an available route.
            BuildOpeningMarker("DisposalChuteTerminus", new Vector2(5.9f, 0.35f),
                new Vector2(4.5f, 18f), new Color(0.16f, 0.2f, 0.27f, 0.9f), -20);
            BuildOpeningMarker("SealedChuteBraceA", new Vector2(6.02f, -0.25f),
                new Vector2(0.55f, 7.2f), new Color(0.42f, 0.25f, 0.15f, 0.95f), -18, 36f);
            BuildOpeningMarker("SealedChuteBraceB", new Vector2(6.02f, -0.25f),
                new Vector2(0.55f, 7.2f), new Color(0.42f, 0.25f, 0.15f, 0.95f), -18, -36f);

            // Repeated low lights pull the eye west without an instruction arrow.
            BuildOpeningMarker("WestTrailLightNear", new Vector2(3.45f, -1.64f),
                new Vector2(0.55f, 0.2f), new Color(0.28f, 0.76f, 0.82f, 0.9f), 3);
            BuildOpeningMarker("WestTrailLightMid", new Vector2(2.1f, -1.82f),
                new Vector2(0.42f, 0.16f), new Color(0.25f, 0.63f, 0.7f, 0.78f), 3);
            BuildOpeningMarker("WestTrailLightFar", new Vector2(0.75f, -1.92f),
                new Vector2(0.32f, 0.13f), new Color(0.22f, 0.52f, 0.6f, 0.68f), 3);
        }

        private static void BuildOpeningMarker(
            string name, Vector2 position, Vector2 scale, Color color, int sortingOrder, float rotation = 0f)
        {
            GameObject marker = new GameObject(name);
            SpriteRenderer renderer = marker.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = color;
            renderer.sortingOrder = sortingOrder;
            marker.transform.position = new Vector3(position.x, position.y, 1f);
            marker.transform.localScale = new Vector3(scale.x, scale.y, 1f);
            marker.transform.rotation = Quaternion.Euler(0f, 0f, rotation);
        }

        private static void BuildLimbusTilemap(TileBase tile)
        {
            GameObject gridObject = new GameObject("LimbusRoomTilemap");
            Grid grid = gridObject.AddComponent<Grid>();
            grid.cellSize = new Vector3(0.25f, 0.25f, 1f);

            GameObject collisionObject = new GameObject("Collision");
            collisionObject.transform.SetParent(gridObject.transform, false);
            Tilemap tilemap = collisionObject.AddComponent<Tilemap>();
            collisionObject.AddComponent<TilemapRenderer>().sortingOrder = 1;
            Rigidbody2D rigidbody = collisionObject.AddComponent<Rigidbody2D>();
            rigidbody.bodyType = RigidbodyType2D.Static;
            CompositeCollider2D composite = collisionObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            TilemapCollider2D tilemapCollider = collisionObject.AddComponent<TilemapCollider2D>();
            tilemapCollider.compositeOperation = Collider2D.CompositeOperation.Merge;

            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 11);
            Fill(tilemap, tile, 26, 27, -8, 11);
            Fill(tilemap, tile, 8, 12, -8, -8);
            Fill(tilemap, tile, 1, 4, -8, -7);
            Fill(tilemap, tile, -15, -11, -8, -6);
            FinalizeTilemap(tilemap, tilemapCollider, composite);
        }

        private static MysteryPartPickup BuildMysteryPart(Vector2 position)
        {
            GameObject root = new GameObject("LimbusMysteryPart");
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(1f, 1.1f);
            trigger.offset = new Vector2(0f, 0.45f);

            GameObject view = new GameObject("TemporaryPartView");
            view.transform.SetParent(root.transform, false);
            view.transform.localPosition = new Vector3(0f, 0.16f, 0f);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = new Color(0.72f, 0.5f, 0.95f, 0.9f);
            renderer.sortingOrder = 5;
            view.transform.localScale = new Vector3(1.1f, 1.1f, 1f);

            MysteryPartPickup pickup = root.AddComponent<MysteryPartPickup>();
            pickup.Configure(renderer);
            return pickup;
        }

        private static RoomDefinition EnsureLimbusRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(LimbusRoomAssetPath);
            room.Configure("limbus", "Limbus Scrap Plain", new Rect(-7f, -3f, 14f, 6f), "act1-limbus");
            EditorUtility.SetDirty(room);
            return room;
        }
    }
}
