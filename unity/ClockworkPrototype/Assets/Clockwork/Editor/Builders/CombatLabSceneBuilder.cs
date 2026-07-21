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
        private static void BuildCombatLabScene(
            GameObject playerPrefab,
            bool usesLocalAtomicArt,
            Sprite dummySprite)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CombatLab";

            TileBase collisionTile = AssetDatabase.LoadAssetAtPath<RuleTile>(TileAssetPath);
            TileBase fallbackTopTile = AssetDatabase.LoadAssetAtPath<Tile>(IndustrialTopTileAssetPath);
            TileBase[] fillTiles = usesLocalAtomicArt
                ? LoadLocalAtomicTiles("Fill", AtomicFillSpritePaths)
                : new[] { collisionTile };
            TileBase[] topTiles = usesLocalAtomicArt
                ? LoadLocalAtomicTiles("Top", AtomicTopSpritePaths)
                : new[] { fallbackTopTile };

            new GameObject("PrototypeBootstrap").AddComponent<PrototypeBootstrap>();
            new GameObject("GameSession").AddComponent<GameSession>();
            BuildCombatLabTilemaps(collisionTile, fillTiles, topTiles, usesLocalAtomicArt);

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

            Camera camera = BuildCamera(player.transform, new Rect(-7f, -3f, 14f, 7f));
            camera.gameObject.AddComponent<AudioListener>();
            BuildCombatLabParallax(camera);
            PrototypeHud hud = new GameObject("PrototypeHUD").AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());
            EditorSceneManager.SaveScene(scene, CombatLabScenePath);
        }

        private static void BuildCombatLabParallax(Camera camera)
        {
            GameObject root = new GameObject("CombatLabParallax");
            BuildParallaxLayer(root.transform, camera, "Far", CombatLabFarPath, -120, 0.08f, 0.04f);
            BuildParallaxLayer(root.transform, camera, "Mid", CombatLabMidPath, -80, 0f, 0f);
        }

        private static void BuildParallaxLayer(
            Transform parent,
            Camera camera,
            string name,
            string spritePath,
            int sortingOrder,
            float horizontalFactor,
            float verticalFactor)
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(spritePath);
            if (sprite == null) throw new InvalidOperationException($"Missing parallax sprite: {spritePath}");

            GameObject layer = new GameObject($"Parallax{name}");
            layer.transform.SetParent(parent, false);
            layer.transform.position = new Vector3(0f, 0.25f, 0f);
            layer.transform.localScale = Vector3.one * 1.25f;
            SpriteRenderer renderer = layer.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = sortingOrder;
            renderer.color = Color.white;

            ParallaxLayer2D parallax = layer.AddComponent<ParallaxLayer2D>();
            parallax.Configure(camera, horizontalFactor, verticalFactor);
        }

        private static void BuildCombatLabTilemaps(
            TileBase collisionTile,
            TileBase[] fillTiles,
            TileBase[] topTiles,
            bool usesLocalAtomicArt)
        {
            if (collisionTile == null)
            {
                throw new InvalidOperationException("CombatLab collision tile is missing.");
            }
            if (fillTiles == null || fillTiles.Length == 0 || Array.Exists(fillTiles, tile => tile == null))
            {
                throw new InvalidOperationException("CombatLab fill tiles are missing.");
            }
            if (topTiles == null || topTiles.Length == 0 || Array.Exists(topTiles, tile => tile == null))
            {
                throw new InvalidOperationException("CombatLab top tiles are missing.");
            }

            Tilemap collisionMap = BuildCollisionTilemap(
                "CombatLabCollision", out TilemapCollider2D collider,
                out CompositeCollider2D composite);
            TileBase[] collisionTiles = { collisionTile };
            FillPattern(collisionMap, collisionTiles, -28, 27, -12, -9);
            FillPattern(collisionMap, collisionTiles, -28, -27, -8, 15);
            FillPattern(collisionMap, collisionTiles, 26, 27, -8, 15);
            FillHorizontalPattern(collisionMap, collisionTiles, -8, -2, 1);
            FillHorizontalPattern(collisionMap, collisionTiles, 10, 16, 3);
            FinalizeTilemap(collisionMap, collider, composite);

            GameObject visualGrid = new GameObject("CombatLabEnvironment");
            Grid grid = visualGrid.AddComponent<Grid>();
            grid.cellSize = new Vector3(0.25f, 0.25f, 1f);
            GameObject visualObject = new GameObject(usesLocalAtomicArt ? "AtomicRealmVisual" : "FallbackVisual");
            visualObject.transform.SetParent(visualGrid.transform, false);
            Tilemap visualMap = visualObject.AddComponent<Tilemap>();
            visualObject.AddComponent<TilemapRenderer>().sortingOrder = 1;
            FillPattern(visualMap, fillTiles, -28, 27, -12, -10);
            FillPattern(visualMap, fillTiles, -28, -27, -9, 15);
            FillPattern(visualMap, fillTiles, 26, 27, -9, 15);
            FillHorizontalPattern(visualMap, topTiles, -28, 27, -9);
            FillHorizontalPattern(visualMap, topTiles, -8, -2, 1);
            FillHorizontalPattern(visualMap, topTiles, 10, 16, 3);
            visualMap.CompressBounds();
            visualMap.RefreshAllTiles();
            if (visualMap.GetUsedTilesCount() == 0)
            {
                throw new InvalidOperationException("CombatLab visual tilemap was generated without tiles.");
            }

            collisionMap.GetComponent<TilemapRenderer>().enabled = false;
        }

        private static void FillPattern(
            Tilemap tilemap, TileBase[] tiles, int minX, int maxX, int minY, int maxY)
        {
            if (tiles == null || tiles.Length == 0) return;
            for (int y = minY; y <= maxY; y++)
            {
                for (int x = minX; x <= maxX; x++)
                {
                    int index = Mathf.Abs(x + y * 3) % tiles.Length;
                    tilemap.SetTile(new Vector3Int(x, y, 0), tiles[index]);
                }
            }
        }

        private static void FillHorizontalPattern(
            Tilemap tilemap, TileBase[] tiles, int minX, int maxX, int y)
        {
            if (tiles == null || tiles.Length == 0) return;
            for (int x = minX; x <= maxX; x++)
            {
                tilemap.SetTile(new Vector3Int(x, y, 0), tiles[(x - minX) % tiles.Length]);
            }
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
