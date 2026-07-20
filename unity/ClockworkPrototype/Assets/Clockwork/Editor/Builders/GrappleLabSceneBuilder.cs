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
        private static void BuildGrappleLabScene(GameObject playerPrefab, TileBase tile)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "GrappleLab";

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildGrappleLabTilemap(tile);

            GameObject lightObject = new GameObject("GrappleLabGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.62f, 0.72f, 0.76f);
            light.intensity = 0.72f;

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(-5.2f, -2f, 0f);
            player.GetComponent<TiqueGrapple>().enabled = true;

            BuildSpawnPoint("lab-start", new Vector2(-5.2f, -2f), 1);
            BuildGrappleAnchor("AnchorWest", new Vector2(-2.6f, 1.8f), 0f);
            BuildGrappleAnchor("AnchorCenter", new Vector2(0.5f, 3.1f), 0.5f);
            BuildGrappleAnchor("AnchorEast", new Vector2(3.8f, 1.9f), 0f);

            BuildCamera(player.transform, new Rect(-7f, -3f, 14f, 8f));
            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());
            EditorSceneManager.SaveScene(scene, GrappleLabScenePath);
        }

        private static void BuildGrappleLabTilemap(TileBase tile)
        {
            Tilemap tilemap = BuildCollisionTilemap("GrappleLabTilemap", out TilemapCollider2D collider,
                out CompositeCollider2D composite);
            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 19);
            Fill(tilemap, tile, 26, 27, -8, 19);
            Fill(tilemap, tile, -24, -16, -5, -5);
            Fill(tilemap, tile, 16, 24, -5, -5);
            FinalizeTilemap(tilemap, collider, composite);
        }

        private static void BuildGrappleAnchor(string name, Vector2 position, float priority)
        {
            GameObject root = new GameObject(name);
            root.transform.position = position;
            GrappleAnchor anchor = root.AddComponent<GrappleAnchor>();
            anchor.Configure(priority);

            SpriteRenderer renderer = root.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = new Color(0.95f, 0.72f, 0.24f, 1f);
            renderer.sortingOrder = 8;
            root.transform.localScale = new Vector3(0.38f, 0.38f, 1f);
        }
    }
}
