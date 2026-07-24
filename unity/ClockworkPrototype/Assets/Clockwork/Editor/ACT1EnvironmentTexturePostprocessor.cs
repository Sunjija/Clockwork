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
            bool usesProductionMetrics =
                assetPath.Contains("/RegisteredWaterStorage/")
                || assetPath.Contains("/RegisteredCaligoVillageExterior/")
                || assetPath.Contains("/RegisteredMorbiWorkshop/")
                || assetPath.Contains("/RegisteredCaligoVillageExteriorV2/")
                || assetPath.Contains("/RegisteredCaligoVillageExteriorV3/")
                || assetPath.Contains("/RegisteredCaligoVillageExteriorV4/")
                || assetPath.Contains("/RegisteredCaligoVillagePlazaV5/")
                || assetPath.Contains("/RegisteredCaligoGateWatchV5/")
                || assetPath.Contains("/RegisteredLimbusCaligoBridgeV6/")
                || assetPath.Contains("/RegisteredLimbusBridgeCombat/")
                || assetPath.Contains("/RegisteredLimbusScrapPlainGreybox/")
                || assetPath.Contains("/RegisteredLimbusScrapPlain/")
                || assetPath.Contains("/RegisteredMorbiWorkshopV2/")
                || assetPath.Contains("/SharedCaligoRouteV2/");
            bool usesGroundPivot =
                assetPath.Contains("/Platforms/")
                || assetPath.Contains("/Props/")
                || assetPath.EndsWith(
                    "/shared-morbi-wood-door.png", System.StringComparison.Ordinal);
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = usesProductionMetrics ? 64f : 32f;
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
