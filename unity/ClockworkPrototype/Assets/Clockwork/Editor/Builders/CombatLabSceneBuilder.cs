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
        private static void BuildCombatLabScene(GameObject playerPrefab, TileBase tile, Sprite dummySprite)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CombatLab";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildCombatLabTilemap(tile);

            GameObject lightObject = new GameObject("CombatLabGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.72f, 0.7f, 0.62f);
            light.intensity = 0.82f;

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(-5.2f, -2f, 0f);
            player.GetComponent<TiqueGrapple>().enabled = false;

            BuildSpawnPoint("lab-start", new Vector2(-5.2f, -2f), 1);
            BuildTrainingDummy("TrainingDummyLight", new Vector2(-1.8f, -2f), dummySprite,
                new Color(0.43f, 0.93f, 1f));
            BuildTrainingDummy("TrainingDummyMedium", new Vector2(1.2f, -2f), dummySprite,
                new Color(0.98f, 0.72f, 0.22f));
            BuildTrainingDummy("TrainingDummyHeavy", new Vector2(4.2f, -2f), dummySprite,
                new Color(0.92f, 0.38f, 0.3f));

            BuildCamera(player.transform, new Rect(-7f, -3f, 14f, 7f));
            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());
            EditorSceneManager.SaveScene(scene, CombatLabScenePath);
        }

        private static void BuildCombatLabTilemap(TileBase tile)
        {
            Tilemap tilemap = BuildCollisionTilemap("CombatLabTilemap", out TilemapCollider2D collider,
                out CompositeCollider2D composite);
            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 15);
            Fill(tilemap, tile, 26, 27, -8, 15);
            Fill(tilemap, tile, -8, -2, 1, 1);
            Fill(tilemap, tile, 10, 16, 3, 3);
            FinalizeTilemap(tilemap, collider, composite);
        }

        private static void BuildTrainingDummy(
            string name, Vector2 position, Sprite sprite, Color color)
        {
            GameObject root = new GameObject(name);
            root.transform.position = position;

            Rigidbody2D body = root.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Static;
            BoxCollider2D collider = root.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(0.62f, 1.05f);
            collider.offset = new Vector2(0f, 0.52f);
            root.AddComponent<EnemyHealth>().Configure(12, false);

            GameObject view = new GameObject("TargetView");
            view.transform.SetParent(root.transform, false);
            view.transform.localPosition = new Vector3(0f, 0.52f, 0f);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.color = color;
            renderer.sortingOrder = 7;
            view.transform.localScale = new Vector3(1.4f, 2.8f, 1f);
        }
    }
}
