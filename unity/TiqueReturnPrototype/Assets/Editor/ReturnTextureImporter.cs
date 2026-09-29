using UnityEditor;
using UnityEngine;

// Applies on first import, including opening the saved scene without using a build menu.
public sealed class ReturnTextureImporter : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        if(!assetPath.StartsWith("Assets/Resources/Return/"))return;
        var importer=(TextureImporter)assetImporter;
        importer.textureType=TextureImporterType.Default;
        importer.filterMode=FilterMode.Point;
        importer.mipmapEnabled=false;
        importer.wrapMode=TextureWrapMode.Clamp;
        importer.textureCompression=TextureImporterCompression.Uncompressed;
        importer.alphaIsTransparency=true;
        importer.npotScale=TextureImporterNPOTScale.None;
        importer.maxTextureSize=1024;
    }
}
