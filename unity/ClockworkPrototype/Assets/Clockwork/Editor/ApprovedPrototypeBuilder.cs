using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Clockwork;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ClockworkEditor
{
    public static class ApprovedPrototypeBuilder
    {
        private const string Root = "Assets/Clockwork";
        private const string ArtRoot = Root + "/Art/Tique/Approved";
        private const string SequenceRoot = Root + "/Data/Sequences";
        private const string AttackRoot = Root + "/Data/Attacks";
        private const string ScenePath = Root + "/Scenes/CaligoMaintenanceShaft.unity";
        private const string PrefabPath = Root + "/Prefabs/TiqueApproved.prefab";
        private const string BackgroundPath = Root + "/Art/Backgrounds/caligo-maintenance-shaft.png";
        private const string PlatformSpritePath = Root + "/Art/platform-debug.png";
        private const string LineMaterialPath = Root + "/Art/prototype-lines.mat";
        private const string PreviewPath = Root + "/QA/caligo-unity-preview.png";

        [MenuItem("Clockwork/Build Approved Prototype")]
        public static void BuildApprovedPrototype()
        {
            EnsureDirectories();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            ConfigureApprovedTextures();
            EnsurePlatformSprite();
            Material lineMaterial = EnsureLineMaterial();

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

            AttackDefinition fist = CreateAttack(
                "Fist", "fist", "주먹", fistSequence, 0.36f, 0.3f, 0.56f,
                new Vector2(0.39f, 0.44f), new Vector2(0.54f, 0.56f),
                new Color(1f, 0.6f, 0.47f));
            AttackDefinition greatsword = CreateAttack(
                "Greatsword", "greatsword", "대검", greatswordSequence, 0.68f, 0.38f, 0.62f,
                new Vector2(0.75f, 0.46f), new Vector2(1.3f, 1f),
                new Color(0.43f, 0.93f, 1f));
            AttackDefinition hammer = CreateAttack(
                "Hammer", "hammer", "망치", hammerSequence, 0.86f, 0.38f, 0.58f,
                new Vector2(0.76f, 0.49f), new Vector2(1.36f, 1.02f),
                new Color(0.94f, 0.74f, 0.35f));

            GameObject prefab = BuildPlayerPrefab(
                new[] { fist, greatsword, hammer },
                idle, walk, jump, doubleJump, dash,
                lineMaterial);
            BuildScene(prefab);
            ConfigureProject();
            ValidateApprovedAssets();
            AssetDatabase.SaveAssets();
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
                scenes = new[] { ScenePath },
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
                SequenceRoot, AttackRoot, Root + "/Scenes", Root + "/Prefabs", Root + "/Art"
            })
            {
                Directory.CreateDirectory(path);
            }
        }

        private static void ConfigureApprovedTextures()
        {
            string[] texturePaths = Directory.GetFiles(ArtRoot, "*.png", SearchOption.AllDirectories)
                .Select(ToAssetPath)
                .Concat(new[] { BackgroundPath })
                .ToArray();

            foreach (string path in texturePaths)
            {
                bool background = path == BackgroundPath;
                bool greatsword = path.Contains("/Greatsword/", StringComparison.Ordinal);
                Vector2 pivot = greatsword
                    ? new Vector2(240f / 640f, (512f - 430f) / 512f)
                    : background ? new Vector2(0.5f, 0.5f) : new Vector2(0.5f, (512f - 480f) / 512f);
                ConfigureTexture(path, pivot, background ? FilterMode.Bilinear : FilterMode.Point, background ? 4096 : 1024);
            }
        }

        private static void ConfigureTexture(string path, Vector2 pivot, FilterMode filter, int maxSize)
        {
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            TextureImporter importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) throw new InvalidOperationException($"Texture importer missing: {path}");
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 100f;
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
            Color trailColor)
        {
            AttackDefinition attack = LoadOrCreate<AttackDefinition>($"{AttackRoot}/{assetName}.asset");
            attack.Configure(id, label, sequence, duration, activeStart, activeEnd, center, size, trailColor);
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

        private static GameObject BuildPlayerPrefab(
            AttackDefinition[] attacks,
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

            TiqueMotor motor = root.AddComponent<TiqueMotor>();
            TiqueCombat combat = root.AddComponent<TiqueCombat>();

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
            combat.Configure(attacks, hitbox, trail);

            LineRenderer pulseOuter = CreateLine("DoubleJumpCorePulseOuter", root.transform, lineMaterial, 0.025f, 20);
            LineRenderer pulseInner = CreateLine("DoubleJumpCorePulseInner", root.transform, lineMaterial, 0.012f, 19);
            DoubleJumpCorePulse pulse = root.AddComponent<DoubleJumpCorePulse>();
            pulse.Configure(motor, pulseOuter, pulseInner);

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

        private static void BuildScene(GameObject playerPrefab)
        {
            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "CaligoMaintenanceShaft";

            GameObject bootstrap = new GameObject("PrototypeBootstrap");
            bootstrap.AddComponent<PrototypeBootstrap>();

            GameObject cameraObject = new GameObject("Main Camera");
            Camera camera = cameraObject.AddComponent<Camera>();
            cameraObject.tag = "MainCamera";
            cameraObject.transform.position = new Vector3(0f, 0f, -10f);
            camera.orthographic = true;
            camera.orthographicSize = 3.6f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.052f, 0.064f);

            BuildBackground();
            BuildPlatforms();

            GameObject player = PrefabUtility.InstantiatePrefab(playerPrefab) as GameObject;
            if (player == null) throw new InvalidOperationException("Unable to instantiate approved Tique prefab.");
            player.transform.position = new Vector3(-5.36f, -2f, 0f);

            GameObject hudObject = new GameObject("PrototypeHUD");
            PrototypeHud hud = hudObject.AddComponent<PrototypeHud>();
            hud.Configure(player.GetComponent<TiqueCombat>());

            EditorSceneManager.SaveScene(scene, ScenePath);
            CapturePreview(camera);
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

        private static void BuildPlatforms()
        {
            CreatePlatform("Ground", 0f, -2.8f, 12.8f, 1.6f, new Color(0.1f, 0.23f, 0.25f, 0.22f));
            CreateWebPlatform("MaintenancePlatform01", 120f, 500f, 220f, 18f);
            CreateWebPlatform("MaintenancePlatform02", 390f, 440f, 220f, 18f);
            CreateWebPlatform("MaintenancePlatform03", 670f, 380f, 220f, 18f);
            CreateWebPlatform("MaintenancePlatform04", 950f, 320f, 210f, 18f);
        }

        private static void CreateWebPlatform(string name, float x, float y, float width, float height)
        {
            float centerX = (x + width * 0.5f - 640f) / 100f;
            float centerY = (360f - (y + height * 0.5f)) / 100f;
            CreatePlatform(name, centerX, centerY, width / 100f, height / 100f, new Color(0.95f, 0.66f, 0.22f, 0.42f));
        }

        private static void CreatePlatform(string name, float x, float y, float width, float height, Color color)
        {
            GameObject gameObject = new GameObject(name);
            gameObject.transform.position = new Vector3(x, y, 0f);
            BoxCollider2D collider = gameObject.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(width, height);

            GameObject view = new GameObject("PlatformView");
            view.transform.SetParent(gameObject.transform, false);
            SpriteRenderer renderer = view.AddComponent<SpriteRenderer>();
            renderer.sprite = AssetDatabase.LoadAssetAtPath<Sprite>(PlatformSpritePath);
            renderer.color = color;
            renderer.drawMode = SpriteDrawMode.Simple;
            Vector2 spriteSize = renderer.sprite.bounds.size;
            view.transform.localScale = new Vector3(width / spriteSize.x, height / spriteSize.y, 1f);
            renderer.sortingOrder = 1;
        }

        private static void ConfigureProject()
        {
            PlayerSettings.productName = "CLOCKWORK Approved Prototype";
            PlayerSettings.defaultScreenWidth = 1280;
            PlayerSettings.defaultScreenHeight = 720;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }

        private static void CapturePreview(Camera camera)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(PreviewPath) ?? Root);
            RenderTexture target = new RenderTexture(1280, 720, 24, RenderTextureFormat.ARGB32);
            Texture2D output = new Texture2D(1280, 720, TextureFormat.RGBA32, false);
            RenderTexture previous = RenderTexture.active;
            camera.targetTexture = target;
            camera.Render();
            RenderTexture.active = target;
            output.ReadPixels(new Rect(0f, 0f, 1280f, 720f), 0, 0);
            output.Apply();
            File.WriteAllBytes(PreviewPath, output.EncodeToPNG());
            camera.targetTexture = null;
            RenderTexture.active = previous;
            UnityEngine.Object.DestroyImmediate(target);
            UnityEngine.Object.DestroyImmediate(output);
            AssetDatabase.ImportAsset(PreviewPath, ImportAssetOptions.ForceSynchronousImport);
        }

        private static void ValidateApprovedAssets()
        {
            string[] forbiddenTokens =
            {
                "/v5/", "/v5.1/", "/v6/", "/v8-", "/v10-", "/weapons-test"
            };
            string[] dependencies = AssetDatabase.GetDependencies(ScenePath, true);
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
            ConfigureTexture(PlatformSpritePath, new Vector2(0.5f, 0.5f), FilterMode.Point, 32);
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

        private static string ToAssetPath(string path)
        {
            string normalized = path.Replace('\\', '/');
            int assetsIndex = normalized.IndexOf("Assets/", StringComparison.Ordinal);
            return assetsIndex >= 0 ? normalized.Substring(assetsIndex) : normalized;
        }
    }
}
