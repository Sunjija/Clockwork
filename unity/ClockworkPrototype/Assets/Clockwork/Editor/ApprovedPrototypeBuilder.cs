using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Clockwork;
using Unity.Cinemachine;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.Tilemaps;
using UnityEngine.U2D;

namespace ClockworkEditor
{
    public static partial class ApprovedPrototypeBuilder
    {
        private const string Root = "Assets/Clockwork";
        private const string ArtRoot = Root + "/Art/Tique/Approved";
        private const string SequenceRoot = Root + "/Data/Sequences";
        private const string AttackRoot = Root + "/Data/Attacks";
        private const string ComboRoot = Root + "/Data/Combos";
        private const string WeaponRoot = Root + "/Data/Weapons";
        private const string ScenePath = Root + "/Scenes/CaligoMaintenanceShaft.unity";
        private const string BridgeScenePath = Root + "/Scenes/LimbusCaligoBridge.unity";
        private const string LimbusScenePath = Root + "/Scenes/Limbus.unity";
        private const string VillageScenePath = Root + "/Scenes/CaligoVillage.unity";
        private const string PlazaScenePath = Root + "/Scenes/CaligoPlaza.unity";
        private const string DropShaftScenePath = Root + "/Scenes/CaligoDropShaft.unity";
        private const string GrappleLabScenePath = Root + "/Scenes/GrappleLab.unity";
        private const string CombatLabScenePath = Root + "/Scenes/CombatLab.unity";
        private const string PrefabPath = Root + "/Prefabs/TiqueApproved.prefab";
        private const string RatPrefabPath = Root + "/Prefabs/RatEnemy.prefab";
        private const string BackgroundPath = Root + "/Art/Backgrounds/caligo-maintenance-shaft.png";
        private const string PlazaBackgroundPath = Root + "/Art/Backgrounds/caligo-plaza-concept-v1.png";
        private const string PlatformSpritePath = Root + "/Art/platform-debug.png";
        private const string TileSpritePath = Root + "/Art/tile-placeholder-32.png";
        private const string RatSpritePath = Root + "/Art/rat-placeholder.png";
        private const string TileAssetPath = Root + "/Data/Tiles/CaligoPlaceholder.asset";
        private const string RoomAssetPath = Root + "/Data/Rooms/CaligoMaintenanceShaft.asset";
        private const string BridgeRoomAssetPath = Root + "/Data/Rooms/LimbusCaligoBridge.asset";
        private const string LimbusRoomAssetPath = Root + "/Data/Rooms/Limbus.asset";
        private const string VillageRoomAssetPath = Root + "/Data/Rooms/CaligoVillage.asset";
        private const string PlazaRoomAssetPath = Root + "/Data/Rooms/CaligoPlaza.asset";
        private const string DropShaftRoomAssetPath = Root + "/Data/Rooms/CaligoDropShaft.asset";
        private const string RendererAssetPath = Root + "/Settings/ClockworkRenderer2D.asset";
        private const string PipelineAssetPath = Root + "/Settings/ClockworkURP.asset";
        private const string LineMaterialPath = Root + "/Art/prototype-lines.mat";
        private const string PreviewPath = Root + "/QA/caligo-unity-preview.png";
        private const string PlazaPreviewPath = Root + "/QA/caligo-plaza-art-benchmark.png";

        [MenuItem("Clockwork/Build Approved Prototype")]
        public static void BuildApprovedPrototype()
        {
            EnsureDirectories();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureApprovedTextures();
            EnsurePlatformSprite();
            Sprite ratSprite = EnsureRatSprite();
            RuleTile collisionTile = EnsureCollisionTile();
            EnsureUniversalRenderPipeline();
            Material lineMaterial = EnsureLineMaterial();
            RoomDefinition room = EnsureRoomDefinition();
            RoomDefinition bridgeRoom = EnsureBridgeRoomDefinition();
            RoomDefinition limbusRoom = EnsureLimbusRoomDefinition();
            RoomDefinition villageRoom = EnsureVillageRoomDefinition();
            RoomDefinition plazaRoom = EnsurePlazaRoomDefinition();
            RoomDefinition dropShaftRoom = EnsureDropShaftRoomDefinition();

            SpriteSequence idle = CreateSequence(
                "Idle", ArtRoot + "/Idle", 1.6f, true, 0.3f,
                0.34f, 0.5f, 0.68f, 1f);
            SpriteSequence walk = CreateSequence(
                "Walk", ArtRoot + "/Walk", 0.72f, true, 0.3f,
                0.0833f, 0.1667f, 0.25f, 0.3333f, 0.4167f, 0.5f,
                0.5833f, 0.6667f, 0.75f, 0.8333f, 0.9167f, 1f);
            SpriteSequence jump = CreateSequence(
                "Jump", ArtRoot + "/Jump", 0.6f, false, 0.3f,
                0.18f, 0.3f, 0.48f, 0.62f, 0.9f, 1f);
            SpriteSequence doubleJump = CreateSequenceFromFiles(
                "DoubleJump",
                new[]
                {
                    ArtRoot + "/DoubleJump/double-jump-01-compress.png",
                    ArtRoot + "/DoubleJump/double-jump-03-extend.png",
                    ArtRoot + "/DoubleJump/double-jump-03-extend.png",
                    ArtRoot + "/DoubleJump/double-jump-04-recover.png"
                },
                0.34f, false, 0.3f,
                0.1471f, 0.3529f, 0.6471f, 1f);
            SpriteSequence dash = CreateSequence(
                "Dash", ArtRoot + "/Dash", 0.32f, false, 0.3f,
                0.0938f, 0.2813f, 0.6875f, 1f);
            SpriteSequence fistSequence = CreateSequence(
                "FistAttack", ArtRoot + "/Fist", 0.36f, false, 0.31f,
                0.1f, 0.22f, 0.34f, 0.46f, 0.58f, 0.7f, 0.84f, 1f);
            SpriteSequence greatswordSequence = CreateSequence(
                "GreatswordAttack", ArtRoot + "/Greatsword", 0.68f, false, 0.36f,
                0.12f, 0.25f, 0.36f, 0.46f, 0.54f, 0.62f, 0.78f, 1f);
            SpriteSequence hammerSequence = CreateSequence(
                "HammerAttack", ArtRoot + "/Hammer", 0.86f, false, 0.36f,
                0.14f, 0.3f, 0.38f, 0.46f, 0.58f, 0.72f, 0.88f, 1f);

            AttackDefinition fistRight = CreateAttack(
                "FistRight", "fist-right", "오른손 직선타", fistSequence, 0.24f, 0.3f, 0.52f,
                new Vector2(0.4f, 0.46f), new Vector2(0.52f, 0.5f),
                new Color(0.78f, 0.95f, 1f), 1);
            AttackDefinition fistLeft = CreateAttack(
                "FistLeft", "fist-left", "왼손 직선타", fistSequence, 0.22f, 0.28f, 0.5f,
                new Vector2(0.4f, 0.39f), new Vector2(0.52f, 0.5f),
                new Color(0.78f, 0.95f, 1f), 1);
            AttackDefinition fistFinisher = CreateAttack(
                "FistFinisher", "fist-finisher", "양손 마무리", fistSequence, 0.3f, 0.3f, 0.54f,
                new Vector2(0.45f, 0.44f), new Vector2(0.66f, 0.6f),
                new Color(1f, 0.7f, 0.22f), 2);
            AttackDefinition greatsword = CreateAttack(
                "Greatsword", "greatsword", "대검", greatswordSequence, 0.68f, 0.38f, 0.62f,
                new Vector2(0.75f, 0.46f), new Vector2(1.3f, 1f),
                new Color(0.43f, 0.93f, 1f), 2);
            AttackDefinition hammer = CreateAttack(
                "Hammer", "hammer", "망치", hammerSequence, 0.86f, 0.38f, 0.58f,
                new Vector2(0.76f, 0.49f), new Vector2(1.36f, 1.02f),
                new Color(0.94f, 0.74f, 0.35f), 3);

            ComboDefinition fistCombo = CreateCombo(
                "FistCombo", "fist-basic", "주먹", new[] { fistRight, fistLeft, fistFinisher },
                0.1f, 0.9f, true);
            ComboDefinition greatswordCombo = CreateCombo(
                "GreatswordCombo", "greatsword-basic", "대검", new[] { greatsword }, 0.25f, 0.9f);
            ComboDefinition hammerCombo = CreateCombo(
                "HammerCombo", "hammer-basic", "망치", new[] { hammer }, 0.25f, 0.9f);
            ComboDefinition fistToGreatsword = CreateCombo(
                "FistToGreatsword", "fist-to-greatsword", "주먹→대검",
                new[] { greatsword }, 0.25f, 0.9f);
            ComboDefinition fistToHammer = CreateCombo(
                "FistToHammer", "fist-to-hammer", "주먹→망치",
                new[] { hammer }, 0.25f, 0.9f);

            WeaponDefinition fistWeapon = CreateWeapon(
                "Fist", "fist", "주먹", fistCombo,
                new[] { "greatsword", "hammer" }, new[] { fistToGreatsword, fistToHammer },
                new[] { 10f, 10f });
            WeaponDefinition greatswordWeapon = CreateWeapon(
                "Greatsword", "greatsword", "대검", greatswordCombo,
                Array.Empty<string>(), Array.Empty<ComboDefinition>(), Array.Empty<float>());
            WeaponDefinition hammerWeapon = CreateWeapon(
                "Hammer", "hammer", "망치", hammerCombo,
                Array.Empty<string>(), Array.Empty<ComboDefinition>(), Array.Empty<float>());

            GameObject prefab = BuildPlayerPrefab(
                new[] { fistRight, greatsword, hammer },
                new[] { fistCombo, greatswordCombo, hammerCombo },
                new[] { fistWeapon, greatswordWeapon, hammerWeapon },
                idle, walk, jump, doubleJump, dash,
                lineMaterial);
            GameObject ratPrefab = BuildRatPrefab(ratSprite);
            BuildScene(prefab, collisionTile, room);
            BuildBridgeScene(prefab, collisionTile, bridgeRoom, ratPrefab);
            BuildLimbusScene(prefab, collisionTile, limbusRoom);
            BuildVillageScene(prefab, collisionTile, villageRoom);
            BuildPlazaScene(prefab, collisionTile, plazaRoom);
            BuildDropShaftScene(prefab, collisionTile, dropShaftRoom);
            BuildGrappleLabScene(prefab, collisionTile);
            BuildCombatLabScene(prefab, collisionTile, ratSprite);
            ConfigureProject();
            ValidateApprovedAssets();
            AssetDatabase.SaveAssets();
            StripGeneratedYamlWhitespace(
                PrefabPath, ScenePath, BridgeScenePath, LimbusScenePath, VillageScenePath,
                PlazaScenePath, DropShaftScenePath, GrappleLabScenePath, CombatLabScenePath);
            AssetDatabase.Refresh();
            Debug.Log("CLOCKWORK_APPROVED_BUILD_OK");
        }

        public static void BuildFromCommandLine()
        {
            try
            {
                BuildApprovedPrototype();
            }
            catch (Exception exception)
            {
                Debug.LogException(exception);
                throw;
            }
        }

        public static void BuildWindowsFromCommandLine()
        {
            BuildApprovedPrototype();
            Directory.CreateDirectory("Builds/Windows");
            BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[]
                {
                    LimbusScenePath, BridgeScenePath, ScenePath, VillageScenePath,
                    PlazaScenePath, DropShaftScenePath, GrappleLabScenePath, CombatLabScenePath
                },
                locationPathName = "Builds/Windows/ClockworkPrototype.exe",
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded)
            {
                throw new InvalidOperationException($"Windows build failed: {report.summary.result}");
            }
            Debug.Log($"CLOCKWORK_WINDOWS_BUILD_OK {report.summary.totalSize}");
        }

        private static void EnsureDirectories()
        {
            foreach (string path in new[]
            {
                SequenceRoot, AttackRoot, ComboRoot, WeaponRoot, Root + "/Scenes", Root + "/Prefabs", Root + "/Art",
                Root + "/Data/Tiles", Root + "/Data/Rooms", Root + "/Settings"
            })
            {
                Directory.CreateDirectory(path);
            }
        }

        private static void ConfigureApprovedTextures()
        {
            string[] texturePaths = Directory.GetFiles(ArtRoot, "*.png", SearchOption.AllDirectories)
                .Select(ToAssetPath)
                .Concat(new[] { BackgroundPath, PlazaBackgroundPath })
                .ToArray();

            foreach (string path in texturePaths)
            {
                bool background = path == BackgroundPath || path == PlazaBackgroundPath;
                bool greatsword = path.Contains("/Greatsword/", StringComparison.Ordinal);
                Vector2 pivot = greatsword
                    ? new Vector2(240f / 640f, (512f - 430f) / 512f)
                    : background ? new Vector2(0.5f, 0.5f) : new Vector2(0.5f, (512f - 480f) / 512f);
                ConfigureTexture(path, pivot, background ? FilterMode.Bilinear : FilterMode.Point, background ? 4096 : 1024, 100f);
            }
        }

        private static void ConfigureTexture(string path, Vector2 pivot, FilterMode filter, int maxSize, float pixelsPerUnit)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException($"Texture importer missing: {path}");
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = pixelsPerUnit;
            TextureImporterSettings settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteAlignment = (int)SpriteAlignment.Custom;
            settings.spritePivot = pivot;
            settings.spriteMeshType = SpriteMeshType.FullRect;
            importer.SetTextureSettings(settings);
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.filterMode = filter;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = maxSize;
            importer.SaveAndReimport();
        }

        private static SpriteSequence CreateSequence(
            string name,
            string folder,
            float duration,
            bool loop,
            float renderScale,
            params float[] frameEnds)
        {
            Sprite[] frames = Directory.GetFiles(folder, "*.png", SearchOption.TopDirectoryOnly)
                .OrderBy(path => Path.GetFileName(path), StringComparer.Ordinal)
                .Select(path => AssetDatabase.LoadAssetAtPath<Sprite>(ToAssetPath(path)))
                .ToArray();
            if (frames.Length != frameEnds.Length || frames.Any(frame => frame == null))
            {
                throw new InvalidOperationException($"Sequence {name} expected {frameEnds.Length} approved frames, found {frames.Length}.");
            }

            string assetPath = $"{SequenceRoot}/{name}.asset";
            SpriteSequence sequence = LoadOrCreate<SpriteSequence>(assetPath);
            sequence.Configure(frames, frameEnds, duration, loop, renderScale);
            EditorUtility.SetDirty(sequence);
            return sequence;
        }

        private static SpriteSequence CreateSequenceFromFiles(
            string name,
            string[] paths,
            float duration,
            bool loop,
            float renderScale,
            params float[] frameEnds)
        {
            Sprite[] frames = paths
                .Select(AssetDatabase.LoadAssetAtPath<Sprite>)
                .ToArray();
            if (frames.Length != frameEnds.Length || frames.Any(frame => frame == null))
            {
                throw new InvalidOperationException($"Sequence {name} expected {frameEnds.Length} approved frames, found {frames.Length}.");
            }

            string assetPath = $"{SequenceRoot}/{name}.asset";
            SpriteSequence sequence = LoadOrCreate<SpriteSequence>(assetPath);
            sequence.Configure(frames, frameEnds, duration, loop, renderScale);
            EditorUtility.SetDirty(sequence);
            return sequence;
        }

        private static AttackDefinition CreateAttack(
            string assetName,
            string id,
            string label,
            SpriteSequence sequence,
            float duration,
            float activeStart,
            float activeEnd,
            Vector2 center,
            Vector2 size,
            Color trailColor,
            int damage)
        {
            AttackDefinition attack = LoadOrCreate<AttackDefinition>($"{AttackRoot}/{assetName}.asset");
            attack.Configure(id, label, sequence, duration, activeStart, activeEnd, center, size, trailColor, damage);
            EditorUtility.SetDirty(attack);
            return attack;
        }

        private static T LoadOrCreate<T>(string path) where T : ScriptableObject
        {
            T asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset != null) return asset;
            asset = ScriptableObject.CreateInstance<T>();
            AssetDatabase.CreateAsset(asset, path);
            return asset;
        }

        private static ComboDefinition CreateCombo(
            string assetName,
            string id,
            string label,
            AttackDefinition[] steps,
            float queueStart,
            float queueEnd,
            bool cyclesAcrossInputs = false)
        {
            ComboDefinition combo = LoadOrCreate<ComboDefinition>($"{ComboRoot}/{assetName}.asset");
            combo.Configure(id, label, steps, queueStart, queueEnd, cyclesAcrossInputs);
            EditorUtility.SetDirty(combo);
            return combo;
        }

        private static WeaponDefinition CreateWeapon(
            string assetName,
            string id,
            string label,
            ComboDefinition basicCombo,
            string[] transitionTargetIds,
            ComboDefinition[] transitionCombos,
            float[] transitionEnergyCosts)
        {
            WeaponDefinition weapon = LoadOrCreate<WeaponDefinition>($"{WeaponRoot}/{assetName}.asset");
            weapon.Configure(
                id, label, basicCombo, transitionTargetIds, transitionCombos, transitionEnergyCosts);
            EditorUtility.SetDirty(weapon);
            return weapon;
        }

        private static GameObject BuildPlayerPrefab(
            AttackDefinition[] attacks,
            ComboDefinition[] combos,
            WeaponDefinition[] weapons,
            SpriteSequence idle,
            SpriteSequence walk,
            SpriteSequence jump,
            SpriteSequence doubleJump,
            SpriteSequence dash,
            Material lineMaterial)
        {
            GameObject root = new GameObject("TiqueApproved");
            Rigidbody2D body = root.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Dynamic;
            body.gravityScale = 0f;
            body.freezeRotation = true;
            body.interpolation = RigidbodyInterpolation2D.Interpolate;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;

            CapsuleCollider2D collider = root.AddComponent<CapsuleCollider2D>();
            collider.direction = CapsuleDirection2D.Vertical;
            collider.size = new Vector2(0.36f, 0.64f);
            collider.offset = new Vector2(0f, 0.32f);

            root.AddComponent<TiqueInputReader>();
            TiqueMotor motor = root.AddComponent<TiqueMotor>();
            root.AddComponent<TiqueProgression>();
            root.AddComponent<TiqueHealth>();
            root.AddComponent<TiqueSpawnPlacer>();
            TiqueCombat combat = root.AddComponent<TiqueCombat>();
            root.AddComponent<TiqueEnergyGauge>();

            GameObject visual = new GameObject("ApprovedSprite");
            visual.transform.SetParent(root.transform, false);
            SpriteRenderer spriteRenderer = visual.AddComponent<SpriteRenderer>();
            spriteRenderer.sortingOrder = 10;
            spriteRenderer.sprite = idle.FrameAt(0f);
            visual.transform.localScale = Vector3.one * idle.RenderScale;
            TiqueSpriteAnimator animator = visual.AddComponent<TiqueSpriteAnimator>();
            animator.Configure(motor, combat, idle, walk, jump, doubleJump, dash);

            LineRenderer hitbox = CreateLine("HitboxDebug", root.transform, lineMaterial, 0.018f, 30);
            LineRenderer trail = CreateLine("WeaponTrail", root.transform, lineMaterial, 0.065f, 9);
            trail.numCapVertices = 4;
            trail.numCornerVertices = 4;
            combat.Configure(attacks, combos, weapons, hitbox, trail);

            LineRenderer rope = CreateLine("GrappleRope", root.transform, lineMaterial, 0.035f, 25);
            rope.startColor = new Color(0.78f, 0.82f, 0.76f, 1f);
            rope.endColor = new Color(0.95f, 0.72f, 0.24f, 1f);
            TiqueGrapple grapple = root.AddComponent<TiqueGrapple>();
            grapple.Configure(rope, 5.5f);
            grapple.enabled = false;

            LineRenderer pulseOuter = CreateLine("DoubleJumpCorePulseOuter", root.transform, lineMaterial, 0.025f, 20);
            LineRenderer pulseInner = CreateLine("DoubleJumpCorePulseInner", root.transform, lineMaterial, 0.012f, 19);
            DoubleJumpCorePulse pulse = root.AddComponent<DoubleJumpCorePulse>();
            pulse.Configure(motor, pulseOuter, pulseInner);

            LineRenderer comboOuter = CreateLine("ComboCorePulseOuter", root.transform, lineMaterial, 0.025f, 22);
            LineRenderer comboInner = CreateLine("ComboCorePulseInner", root.transform, lineMaterial, 0.012f, 21);
            TiqueComboPulse comboPulse = root.AddComponent<TiqueComboPulse>();
            comboPulse.Configure(combat, comboOuter, comboInner);

            LineRenderer punchPrimary = CreateLine("PunchImpactPrimary", root.transform, lineMaterial, 0.035f, 24);
            LineRenderer punchSecondary = CreateLine("PunchImpactSecondary", root.transform, lineMaterial, 0.022f, 23);
            TiquePunchImpact punchImpact = root.AddComponent<TiquePunchImpact>();
            punchImpact.Configure(combat, punchPrimary, punchSecondary);

            LineRenderer swapWaveOuter = CreateLine(
                "SwapChargeWaveOuter", root.transform, lineMaterial, 0.045f, 27);
            LineRenderer swapWaveInner = CreateLine(
                "SwapChargeWaveInner", root.transform, lineMaterial, 0.024f, 26);
            TiqueSwapChargeWave swapChargeWave = root.AddComponent<TiqueSwapChargeWave>();
            swapChargeWave.Configure(combat, swapWaveOuter, swapWaveInner);

            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
            UnityEngine.Object.DestroyImmediate(root);
            return prefab;
        }

        private static LineRenderer CreateLine(string name, Transform parent, Material material, float width, int order)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.SetParent(parent, false);
            LineRenderer line = gameObject.AddComponent<LineRenderer>();
            line.material = material;
            line.useWorldSpace = true;
            line.loop = false;
            line.startWidth = width;
            line.endWidth = width;
            line.sortingOrder = order;
            line.enabled = false;
            return line;
        }

        private static void BuildScene(GameObject playerPrefab, TileBase collisionTile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoMaintenanceShaft";

            GameObject bootstrap = new GameObject("PrototypeBootstrap");
            bootstrap.AddComponent<PrototypeBootstrap>();
            GameObject session = new GameObject("GameSession");
            session.AddComponent<GameSession>();

            BuildBackground();
            BuildTilemapRoom(collisionTile);
            BuildLighting();

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(-5.36f, -2f, 0f);

            RepairSavePoint savePoint = BuildRepairSavePoint(
                "CaligoRepairWorkbench", new Vector2(3.55f, -2f), "caligo-maintenance-shaft", "caligo-workbench");
            BuildRoomGates();
            BuildSpawnPoint("entry-limbus", new Vector2(-5.36f, -2f));
            BuildSpawnPoint("caligo-workbench", new Vector2(3.55f, -2f));
            BuildSpawnPoint("entry-bridge", new Vector2(6f, -2f));
            BuildSpawnPoint("entry-caligo-village", new Vector2(-6f, -2f));
            Camera camera = BuildCamera(player.transform, room.CameraBounds);

            GameObject hudObject = new GameObject("PrototypeHUD");
            PrototypeHud hud = hudObject.AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), savePoint, player.GetComponent<TiqueHealth>());

            EditorSceneManager.SaveScene(scene, ScenePath);
            if (!Application.isBatchMode && SystemInfo.graphicsDeviceType != GraphicsDeviceType.Null)
            {
                CapturePreview(camera);
            }
        }

        private static void BuildBridgeScene(GameObject playerPrefab, TileBase tile, RoomDefinition room, GameObject ratPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "LimbusCaligoBridge";

            GameObject bootstrap = new GameObject("PrototypeBootstrap");
            bootstrap.AddComponent<PrototypeBootstrap>();
            GameObject session = new GameObject("GameSession");
            session.AddComponent<GameSession>();

            BuildBridgeTilemap(tile);

            // Placeholder mood only — the sewage-waterfall crossing art (v5.5 B-1) is still missing by design.
            GameObject lightObject = new GameObject("BridgeGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.55f, 0.66f, 0.84f);
            light.intensity = 0.7f;

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(-5.36f, -2f, 0f);

            // Map orientation: Caligo lies west of the bridge, Limbus east (maps are canon).
            BuildRoomGate("GateToMaintenanceShaft", new Vector2(-6.65f, -1.25f), "caligo-maintenance-shaft", "entry-bridge");
            BuildRoomGate("GateToLimbus", new Vector2(6.65f, -1.25f), "limbus", "entry-bridge");
            BuildSpawnPoint("entry-caligo", new Vector2(-6f, -2f));
            BuildSpawnPoint("entry-limbus", new Vector2(6f, -2f));

            // A finite tutorial pack exhausts the already-crippled Tique before repair.
            // After repair the same pack is a normal, beatable encounter.
            GameObject directorObject = new GameObject("BridgeCollapseDirector");
            directorObject.transform.position = new Vector3(-5.3f, -1.25f, 0f);
            BoxCollider2D collapseTrigger = directorObject.AddComponent<BoxCollider2D>();
            collapseTrigger.isTrigger = true;
            collapseTrigger.size = new Vector2(0.5f, 2.2f);
            directorObject.AddComponent<BridgeCollapseDirector>().Configure(ratPrefab);

            BuildCamera(player.transform, room.CameraBounds);

            GameObject hudObject = new GameObject("PrototypeHUD");
            PrototypeHud hud = hudObject.AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), null, player.GetComponent<TiqueHealth>());

            EditorSceneManager.SaveScene(scene, BridgeScenePath);
        }

        private static void BuildVillageScene(GameObject playerPrefab, TileBase tile, RoomDefinition room)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoVillage";

            GameObject bootstrap = new GameObject("PrototypeBootstrap");
            bootstrap.AddComponent<PrototypeBootstrap>();
            GameObject session = new GameObject("GameSession");
            session.AddComponent<GameSession>();

            BuildBridgeTilemap(tile);

            // Caligo: chosen poverty, calm warmth (canon §4). Placeholder dressing only.
            GameObject lightObject = new GameObject("VillageGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.88f, 0.74f, 0.55f);
            light.intensity = 0.74f;
            BuildVillageHut(new Vector2(-4.4f, -0.9f), new Vector2(3.4f, 2.6f));
            BuildVillageHut(new Vector2(0.6f, -1f), new Vector2(2.6f, 2.2f));
            BuildVillageHut(new Vector2(4.2f, -0.8f), new Vector2(3f, 2.8f));

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(6f, -2f, 0f);

            // Village lies west of the shaft; the plaza continues further west.
            BuildRoomGate("GateToMaintenanceShaft", new Vector2(6.65f, -1.25f), "caligo-maintenance-shaft", "entry-caligo-village");
            BuildRoomGate("GateToPlaza", new Vector2(-6.65f, -1.25f), "caligo-plaza", "entry-workshop");
            BuildSpawnPoint("entry-maintenance-shaft", new Vector2(6f, -2f));
            BuildSpawnPoint("caligo-workshop", new Vector2(-2f, -2f));

            RepairSavePoint savePoint = BuildRepairSavePoint(
                "MorbiWorkshopBench", new Vector2(-2f, -2f), "caligo", "caligo-workshop");
            BuildMorbi(new Vector2(-3.4f, -2f));

            BuildCamera(player.transform, room.CameraBounds);

            GameObject hudObject = new GameObject("PrototypeHUD");
            PrototypeHud hud = hudObject.AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>(), savePoint, player.GetComponent<TiqueHealth>());

            EditorSceneManager.SaveScene(scene, VillageScenePath);
        }

        private static void BuildVillageHut(Vector2 position, Vector2 size)
        {
            GameObject hut = new GameObject("VillageHutSilhouette");
            SpriteRenderer renderer = hut.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = new Color(0.2f, 0.16f, 0.13f, 0.9f);
            renderer.sortingOrder = -30;
            hut.transform.position = new Vector3(position.x, position.y, 2f);
            hut.transform.localScale = new Vector3(size.x, size.y, 1f);
        }

        private static void BuildMorbi(Vector2 position)
        {
            GameObject root = new GameObject("MorbiNpc");
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(1.6f, 1.5f);
            trigger.offset = new Vector2(0f, 0.6f);

            GameObject view = new GameObject("TemporaryMorbiView");
            view.transform.SetParent(root.transform, false);
            view.transform.localPosition = new Vector3(0f, 0.62f, 0f);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = new Color(0.62f, 0.44f, 0.3f, 0.95f);
            renderer.sortingOrder = 6;
            view.transform.localScale = new Vector3(0.55f, 1.35f, 1f);

            root.AddComponent<MorbiNpc>();
        }

        private static RoomDefinition EnsureVillageRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(VillageRoomAssetPath);
            room.Configure(
                "caligo",
                "Caligo Village",
                new Rect(-7f, -3f, 14f, 6f),
                "act1-caligo");
            EditorUtility.SetDirty(room);
            return room;
        }

        private static void BuildBridgeTilemap(TileBase tile)
        {
            GameObject gridObject = new GameObject("BridgeRoomTilemap");
            Grid grid = gridObject.AddComponent<Grid>();
            grid.cellSize = new Vector3(0.25f, 0.25f, 1f);

            GameObject collisionObject = new GameObject("Collision");
            collisionObject.transform.SetParent(gridObject.transform, false);
            Tilemap tilemap = collisionObject.AddComponent<Tilemap>();
            TilemapRenderer renderer = collisionObject.AddComponent<TilemapRenderer>();
            renderer.sortingOrder = 1;
            Rigidbody2D rigidbody = collisionObject.AddComponent<Rigidbody2D>();
            rigidbody.bodyType = RigidbodyType2D.Static;
            CompositeCollider2D composite = collisionObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            TilemapCollider2D tilemapCollider = collisionObject.AddComponent<TilemapCollider2D>();
            tilemapCollider.compositeOperation = Collider2D.CompositeOperation.Merge;

            // Flat crossing with side walls; the rats patrol the deck between the gates.
            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 11);
            Fill(tilemap, tile, 26, 27, -8, 11);
            tilemap.CompressBounds();
            tilemap.RefreshAllTiles();
            tilemapCollider.ProcessTilemapChanges();
            composite.GenerateGeometry();
        }

        private static Tilemap BuildCollisionTilemap(
            string name, out TilemapCollider2D tilemapCollider, out CompositeCollider2D composite)
        {
            GameObject gridObject = new GameObject(name);
            Grid grid = gridObject.AddComponent<Grid>();
            grid.cellSize = new Vector3(0.25f, 0.25f, 1f);

            GameObject collisionObject = new GameObject("Collision");
            collisionObject.transform.SetParent(gridObject.transform, false);
            Tilemap tilemap = collisionObject.AddComponent<Tilemap>();
            collisionObject.AddComponent<TilemapRenderer>().sortingOrder = 1;
            Rigidbody2D rigidbody = collisionObject.AddComponent<Rigidbody2D>();
            rigidbody.bodyType = RigidbodyType2D.Static;
            composite = collisionObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            tilemapCollider = collisionObject.AddComponent<TilemapCollider2D>();
            tilemapCollider.compositeOperation = Collider2D.CompositeOperation.Merge;
            return tilemap;
        }

        private static void FinalizeTilemap(
            Tilemap tilemap, TilemapCollider2D tilemapCollider, CompositeCollider2D composite)
        {
            tilemap.CompressBounds();
            tilemap.RefreshAllTiles();
            tilemapCollider.ProcessTilemapChanges();
            composite.GenerateGeometry();
        }

        private static void BuildSpawnPoint(string id, Vector2 position, int facing = 0)
        {
            GameObject point = new GameObject($"Spawn_{id}");
            point.transform.position = position;
            point.AddComponent<SpawnPoint>().Configure(id, facing);
        }

        private static GameObject BuildRatPrefab(Sprite sprite)
        {
            GameObject rat = new GameObject("RatEnemy");

            Rigidbody2D body = rat.AddComponent<Rigidbody2D>();
            body.bodyType = RigidbodyType2D.Dynamic;
            body.gravityScale = 0f;
            body.freezeRotation = true;
            body.interpolation = RigidbodyInterpolation2D.Interpolate;
            body.collisionDetectionMode = CollisionDetectionMode2D.Continuous;

            BoxCollider2D collider = rat.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(0.42f, 0.24f);
            collider.offset = new Vector2(0f, 0.12f);

            SpriteRenderer renderer = rat.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = 6;

            rat.AddComponent<EnemyHealth>().Configure(3);
            rat.AddComponent<RatEnemy>().Configure(-1, 0.95f);

            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(rat, RatPrefabPath);
            UnityEngine.Object.DestroyImmediate(rat);
            return prefab;
        }

        private static void BuildBackground()
        {
            Sprite sprite = AssetDatabase.LoadAssetAtPath<Sprite>(BackgroundPath);
            if (sprite == null) throw new InvalidOperationException("Caligo background sprite was not imported.");

            GameObject gameObject = new GameObject("CaligoMaintenanceShaftBackground");
            SpriteRenderer renderer = gameObject.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = -100;

            float scale = 13.568f / sprite.bounds.size.x;
            float height = sprite.bounds.size.y * scale;
            float sourceGroundFromBottom = (sprite.texture.height - 808f) / 100f * scale;
            float localGround = sourceGroundFromBottom - height * 0.5f;
            gameObject.transform.localScale = Vector3.one * scale;
            gameObject.transform.position = new Vector3(0f, -2f - localGround, 5f);
        }

        private static void BuildTilemapRoom(TileBase tile)
        {
            GameObject gridObject = new GameObject("CaligoRoomTilemap");
            Grid grid = gridObject.AddComponent<Grid>();
            grid.cellSize = new Vector3(0.25f, 0.25f, 1f);

            GameObject collisionObject = new GameObject("Collision");
            collisionObject.transform.SetParent(gridObject.transform, false);
            Tilemap tilemap = collisionObject.AddComponent<Tilemap>();
            TilemapRenderer renderer = collisionObject.AddComponent<TilemapRenderer>();
            renderer.sortingOrder = 1;
            Rigidbody2D rigidbody = collisionObject.AddComponent<Rigidbody2D>();
            rigidbody.bodyType = RigidbodyType2D.Static;
            CompositeCollider2D composite = collisionObject.AddComponent<CompositeCollider2D>();
            composite.geometryType = CompositeCollider2D.GeometryType.Polygons;
            TilemapCollider2D tilemapCollider = collisionObject.AddComponent<TilemapCollider2D>();
            tilemapCollider.compositeOperation = Collider2D.CompositeOperation.Merge;

            Fill(tilemap, tile, -28, 27, -12, -9);
            Fill(tilemap, tile, -28, -27, -8, 11);
            Fill(tilemap, tile, 26, 27, -8, 11);
            Fill(tilemap, tile, -20, -12, -6, -6);
            Fill(tilemap, tile, -10, -2, -4, -4);
            Fill(tilemap, tile, 1, 9, -2, -2);
            Fill(tilemap, tile, 12, 20, 0, 0);
            tilemap.CompressBounds();
            tilemap.RefreshAllTiles();
            tilemapCollider.ProcessTilemapChanges();
            composite.GenerateGeometry();
        }

        private static void Fill(Tilemap tilemap, TileBase tile, int minX, int maxX, int minY, int maxY)
        {
            for (int x = minX; x <= maxX; x++)
            {
                for (int y = minY; y <= maxY; y++)
                {
                    tilemap.SetTile(new Vector3Int(x, y, 0), tile);
                }
            }
        }

        private static Camera BuildCamera(Transform player, Rect bounds)
        {
            GameObject cameraObject = new GameObject("Main Camera");
            Camera camera = cameraObject.AddComponent<Camera>();
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(player.position.x, 0f, -10f);
            camera.orthographic = true;
            camera.orthographicSize = 2.8125f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.052f, 0.064f);
            cameraObject.AddComponent<CinemachineBrain>();
            UnityEngine.U2D.PixelPerfectCamera pixelPerfect = cameraObject.AddComponent<UnityEngine.U2D.PixelPerfectCamera>();
            pixelPerfect.assetsPPU = 32;
            pixelPerfect.refResolutionX = 320;
            pixelPerfect.refResolutionY = 180;
            pixelPerfect.cropFrameX = false;
            pixelPerfect.cropFrameY = false;

            GameObject boundary = new GameObject("CameraBoundary");
            PolygonCollider2D boundaryCollider = boundary.AddComponent<PolygonCollider2D>();
            boundaryCollider.isTrigger = true;
            boundaryCollider.points = new[]
            {
                new Vector2(bounds.xMin, bounds.yMin),
                new Vector2(bounds.xMin, bounds.yMax),
                new Vector2(bounds.xMax, bounds.yMax),
                new Vector2(bounds.xMax, bounds.yMin)
            };

            GameObject virtualObject = new GameObject("CaligoVirtualCamera");
            virtualObject.transform.position = new Vector3(player.position.x, 0f, -10f);
            CinemachineCamera virtualCamera = virtualObject.AddComponent<CinemachineCamera>();
            virtualCamera.Target.TrackingTarget = player;
            LensSettings lens = virtualCamera.Lens;
            lens.OrthographicSize = 2.8125f;
            virtualCamera.Lens = lens;
            CinemachinePositionComposer composer = virtualObject.AddComponent<CinemachinePositionComposer>();
            composer.Damping = new Vector3(0.28f, 0.4f, 0f);
            composer.CameraDistance = 10f;
            CinemachineConfiner2D confiner = virtualObject.AddComponent<CinemachineConfiner2D>();
            confiner.BoundingShape2D = boundaryCollider;
            confiner.Damping = 0.18f;
            return camera;
        }

        private static RepairSavePoint BuildRepairSavePoint(
            string name, Vector2 position, string roomId, string spawnId)
        {
            GameObject root = new GameObject(name);
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(1.25f, 1.35f);
            trigger.offset = new Vector2(0f, 0.55f);

            GameObject view = new GameObject("TemporaryWorkbenchView");
            view.transform.SetParent(root.transform, false);
            view.transform.localPosition = new Vector3(0f, 0.22f, 0f);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = new Color(0.93f, 0.66f, 0.22f, 0.86f);
            renderer.sortingOrder = 5;
            view.transform.localScale = new Vector3(2.5f, 3.5f, 1f);

            RepairSavePoint savePoint = root.AddComponent<RepairSavePoint>();
            savePoint.Configure(roomId, spawnId, renderer);
            return savePoint;
        }

        private static void BuildLighting()
        {
            GameObject lightObject = new GameObject("CaligoGlobalLight2D");
            Light2D light = lightObject.AddComponent<Light2D>();
            light.lightType = Light2D.LightType.Global;
            light.color = new Color(0.62f, 0.78f, 0.82f);
            light.intensity = 0.78f;
        }

        private static void BuildRoomGates()
        {
            // Map orientation: the Limbus bridge lies east of the shaft, the Caligo village west (maps are canon).
            BuildRoomGate("GateToLimbusBridge", new Vector2(6.65f, -1.25f), "limbus-caligo-bridge", "entry-caligo");
            BuildRoomGate("GateToCaligoVillage", new Vector2(-6.65f, -1.25f), "caligo", "entry-maintenance-shaft", GameFlagIds.TiqueRepaired);
        }

        private static void BuildRoomGate(string name, Vector2 position, string destinationRoom, string destinationSpawn, string requiredFlag = "")
        {
            GameObject root = new GameObject(name);
            root.transform.position = position;
            BoxCollider2D trigger = root.AddComponent<BoxCollider2D>();
            trigger.isTrigger = true;
            trigger.size = new Vector2(0.45f, 2.2f);
            RoomGate gate = root.AddComponent<RoomGate>();
            gate.Configure(name, destinationRoom, destinationSpawn, requiredFlag);

            GameObject view = new GameObject("TemporaryGateView");
            view.transform.SetParent(root.transform, false);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            renderer.color = string.IsNullOrEmpty(requiredFlag)
                ? new Color(0.2f, 0.78f, 0.82f, 0.48f)
                : new Color(0.92f, 0.46f, 0.2f, 0.62f);
            renderer.sortingOrder = 4;
            view.transform.localScale = new Vector3(1.25f, 8f, 1f);
        }

        private static RuleTile EnsureCollisionTile()
        {
            if (!File.Exists(TileSpritePath))
            {
                Texture2D texture = new Texture2D(32, 32, TextureFormat.RGBA32, false);
                for (int y = 0; y < 32; y++)
                {
                    for (int x = 0; x < 32; x++)
                    {
                        bool edge = x < 2 || y < 2 || x > 29 || y > 29;
                        bool seam = (x == 15 || x == 16) && y > 5;
                        Color color = edge ? new Color(0.12f, 0.3f, 0.32f)
                            : seam ? new Color(0.2f, 0.43f, 0.43f)
                            : new Color(0.17f, 0.36f, 0.37f);
                        texture.SetPixel(x, y, color);
                    }
                }
                texture.Apply();
                File.WriteAllBytes(TileSpritePath, texture.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(texture);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            }

            ConfigureTexture(TileSpritePath, new Vector2(0.5f, 0.5f), FilterMode.Point, 32, 128f);
            RuleTile tile = LoadOrCreate<RuleTile>(TileAssetPath);
            tile.m_DefaultSprite = AssetDatabase.LoadAssetAtPath<Sprite>(TileSpritePath);
            tile.m_DefaultColliderType = Tile.ColliderType.Grid;
            EditorUtility.SetDirty(tile);
            return tile;
        }

        private static RoomDefinition EnsureRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(RoomAssetPath);
            room.Configure(
                "caligo-maintenance-shaft",
                "Caligo Maintenance Shaft",
                new Rect(-7f, -3f, 14f, 6f),
                "act1-caligo-maintenance");
            EditorUtility.SetDirty(room);
            return room;
        }

        private static RoomDefinition EnsureBridgeRoomDefinition()
        {
            RoomDefinition room = LoadOrCreate<RoomDefinition>(BridgeRoomAssetPath);
            room.Configure(
                "limbus-caligo-bridge",
                "Limbus-Caligo Bridge",
                new Rect(-7f, -3f, 14f, 6f),
                "act1-limbus-bridge");
            EditorUtility.SetDirty(room);
            return room;
        }

        private static Sprite EnsureRatSprite()
        {
            if (!File.Exists(RatSpritePath))
            {
                const int width = 16;
                const int height = 10;
                Color clear = new Color(0f, 0f, 0f, 0f);
                Color fur = new Color(0.4f, 0.38f, 0.42f);
                Color furDark = new Color(0.28f, 0.26f, 0.3f);
                Color eye = new Color(0.95f, 0.3f, 0.25f);

                Texture2D texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
                for (int y = 0; y < height; y++)
                {
                    for (int x = 0; x < width; x++)
                    {
                        texture.SetPixel(x, y, clear);
                    }
                }

                // Facing left: rounded body, snout on the left, tail trailing right.
                for (int x = 2; x <= 12; x++)
                {
                    for (int y = 1; y <= 5; y++)
                    {
                        bool corner = (x == 2 || x == 12) && (y == 1 || y == 5);
                        if (!corner) texture.SetPixel(x, y, fur);
                    }
                }
                texture.SetPixel(1, 3, fur);
                texture.SetPixel(1, 2, fur);
                texture.SetPixel(0, 2, furDark);
                texture.SetPixel(4, 6, furDark);
                texture.SetPixel(10, 6, furDark);
                for (int x = 13; x <= 15; x++) texture.SetPixel(x, 2 + (x - 13) / 2, furDark);
                texture.SetPixel(3, 0, furDark);
                texture.SetPixel(6, 0, furDark);
                texture.SetPixel(9, 0, furDark);
                texture.SetPixel(11, 0, furDark);
                texture.SetPixel(3, 4, eye);
                texture.Apply();
                File.WriteAllBytes(RatSpritePath, texture.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(texture);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            }

            ConfigureTexture(RatSpritePath, new Vector2(0.5f, 0f), FilterMode.Point, 32, 32f);
            return AssetDatabase.LoadAssetAtPath<Sprite>(RatSpritePath);
        }

        private static void EnsureUniversalRenderPipeline()
        {
            Renderer2DData rendererData = AssetDatabase.LoadAssetAtPath<Renderer2DData>(RendererAssetPath);
            if (rendererData == null)
            {
                rendererData = ScriptableObject.CreateInstance<Renderer2DData>();
                rendererData.name = "ClockworkRenderer2D";
                AssetDatabase.CreateAsset(rendererData, RendererAssetPath);
            }

            UniversalRenderPipelineAsset pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(PipelineAssetPath);
            if (pipeline == null)
            {
                pipeline = UniversalRenderPipelineAsset.Create(rendererData);
                pipeline.name = "ClockworkURP";
                AssetDatabase.CreateAsset(pipeline, PipelineAssetPath);
            }

            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;
        }

        private static void ConfigureProject()
        {
            PlayerSettings.productName = "CLOCKWORK Approved Prototype";
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;
            // Limbus first: the game boots at the canon awakening point (v5.5 A-1).
            EditorBuildSettings.scenes = new[]
            {
                new EditorBuildSettingsScene(LimbusScenePath, true),
                new EditorBuildSettingsScene(BridgeScenePath, true),
                new EditorBuildSettingsScene(ScenePath, true),
                new EditorBuildSettingsScene(VillageScenePath, true),
                new EditorBuildSettingsScene(PlazaScenePath, true),
                new EditorBuildSettingsScene(DropShaftScenePath, true),
                new EditorBuildSettingsScene(GrappleLabScenePath, true),
                new EditorBuildSettingsScene(CombatLabScenePath, true)
            };
        }

        private static void CapturePreview(Camera camera, string outputPath = PreviewPath)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(outputPath) ?? Root);
            RenderTexture target = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32);
            Texture2D output = new Texture2D(1280, 720, TextureFormat.RGBA32, false);
            RenderTexture previous = RenderTexture.active;
            camera.targetTexture = target;
            camera.Render();
            RenderTexture.active = target;
            output.ReadPixels(new Rect(0f, 0f, 1280f, 720f), 0, 0);
            output.Apply();
            File.WriteAllBytes(outputPath, output.EncodeToPNG());
            camera.targetTexture = null;
            RenderTexture.active = previous;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(output);
            AssetDatabase.ImportAsset(outputPath, ImportAssetOptions.ForceSynchronousImport);
        }

        private static void ValidateApprovedAssets()
        {
            string[] forbiddenTokens =
            {
                "/v5/", "/v5.1/", "/v6/", "/v8-", "/v10-", "/weapons-test"
            };
            string[] dependencies = AssetDatabase.GetDependencies(
                new[]
                {
                    ScenePath, BridgeScenePath, LimbusScenePath, VillageScenePath,
                    PlazaScenePath, DropShaftScenePath, GrappleLabScenePath, CombatLabScenePath
                },
                true);
            foreach (string dependency in dependencies)
            {
                if (forbiddenTokens.Any(token => dependency.Contains(token, StringComparison.OrdinalIgnoreCase)))
                {
                    throw new InvalidOperationException($"Unapproved asset reached the Unity scene: {dependency}");
                }
            }

            int approvedFrames = Directory.GetFiles(ArtRoot, "*.png", SearchOption.AllDirectories).Length;
            if (approvedFrames != 54)
            {
                throw new InvalidOperationException($"Expected 54 approved Tique frames, found {approvedFrames}.");
            }
        }

        private static void EnsurePlatformSprite()
        {
            if (!File.Exists(PlatformSpritePath))
            {
                Texture2D texture = new Texture2D(8, 8, TextureFormat.RGBA32, false);
                Color[] pixels = Enumerable.Repeat(Color.white, 64).ToArray();
                texture.SetPixels(pixels);
                texture.Apply();
                File.WriteAllBytes(PlatformSpritePath, texture.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(texture);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            }
            ConfigureTexture(PlatformSpritePath, new Vector2(0.5f, 0.5f), FilterMode.Point, 32, 100f);
        }

        private static Material EnsureLineMaterial()
        {
            Material material = AssetDatabase.LoadAssetAtPath<Material>(LineMaterialPath);
            if (material != null) return material;
            Shader shader = Shader.Find("Sprites/Default");
            if (shader == null) throw new InvalidOperationException("Sprites/Default shader is unavailable.");
            material = new Material(shader) { name = "PrototypeLines" };
            AssetDatabase.CreateAsset(material, LineMaterialPath);
            return material;
        }

        private static void StripGeneratedYamlWhitespace(params string[] paths)
        {
            foreach (string path in paths)
            {
                string[] lines = File.ReadAllLines(path);
                for (int i = 0; i < lines.Length; i++)
                {
                    lines[i] = lines[i].TrimEnd();
                }
                File.WriteAllLines(path, lines);
            }
        }

        private static string ToAssetPath(string path)
        {
            string normalized = path.Replace('\\', '/');
            int assetsIndex = normalized.IndexOf("Assets/", StringComparison.Ordinal);
            return assetsIndex >= 0 ? normalized.Substring(assetsIndex) : normalized;
        }
    }
}
