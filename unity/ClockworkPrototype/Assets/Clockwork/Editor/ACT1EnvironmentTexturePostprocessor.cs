using UnityEditor;
using UnityEngine;

namespace Clockwork.Editor
{
    public sealed class ACT1EnvironmentTexturePostprocessor : AssetPostprocessor
    {
        private const string AssetRoot =
            "Assets/Clockwork/Art/Environment/ACT1OpeningCaligo/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(AssetRoot, System.StringComparison.Ordinal))
            {
                return;
            }

            var importer = (TextureImporter)assetImporter;
            bool usesGroundPivot =
                assetPath.Contains("/Platforms/") || assetPath.Contains("/Props/");
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 32f;
            importer.spritePivot = usesGroundPivot
                ? new Vector2(0.5f, 0f)
                : new Vector2(0.5f, 0.5f);
            var settings = new TextureImporterSettings();
            importer.ReadTextureSettings(settings);
            settings.spriteMeshType = SpriteMeshType.FullRect;
            importer.SetTextureSettings(settings);
            importer.filterMode = FilterMode.Point;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.mipmapEnabled = false;
            importer.alphaIsTransparency = true;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
        }
    }
}
