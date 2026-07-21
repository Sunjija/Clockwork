using UnityEditor;
using UnityEngine;

internal sealed class CaligoNPCPrototypeTexturePostprocessor : AssetPostprocessor
{
    private const string AssetRoot = "/Clockwork/Art/Characters/CaligoNPCPrototype/";

    private void OnPreprocessTexture()
    {
        if (!assetPath.Contains(AssetRoot) || !assetPath.EndsWith(".png"))
        {
            return;
        }

        var importer = (TextureImporter)assetImporter;
        importer.textureType = TextureImporterType.Sprite;
        importer.spriteImportMode = SpriteImportMode.Single;
        importer.spritePixelsPerUnit = 32;
        importer.filterMode = FilterMode.Point;
        importer.wrapMode = TextureWrapMode.Clamp;
        importer.mipmapEnabled = false;
        importer.alphaIsTransparency = true;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
    }
}
