using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.U2D;

namespace Clockwork
{
    public sealed class CaligoWaterStorageRegisteredProbe : MonoBehaviour
    {
        private static readonly string[] ExpectedLayerNames =
        {
            "Layer_00_Far",
            "Layer_10_Mid",
            "Layer_18_Foundation",
            "Layer_20_Reservoir",
            "Layer_30_Gameplay",
            "Layer_40_Props",
            "Layer_70_Foreground",
            "Layer_80_FX"
        };

        [SerializeField] private Transform registrationRoot;
        [SerializeField] private Camera roomCamera;
        [SerializeField] private TiqueMotor playerMotor;

        private IEnumerator Start()
        {
            string[] arguments = Environment.GetCommandLineArgs();
            bool runSmoke = arguments.Contains("-clockworkWaterStorageSmoke");
            string capturePath = ReadArgument(arguments, "-clockworkCapturePath");
            if (!runSmoke && string.IsNullOrWhiteSpace(capturePath)) yield break;

            yield return null;
            yield return new WaitForFixedUpdate();
            yield return new WaitForSecondsRealtime(0.35f);

            bool valid = Validate(out string details);
            Debug.Log($"CLOCKWORK_WATER_STORAGE_PROBE valid={valid} {details}");

            if (!string.IsNullOrWhiteSpace(capturePath))
            {
                string fullPath = Path.GetFullPath(capturePath);
                string directory = Path.GetDirectoryName(fullPath);
                if (!string.IsNullOrEmpty(directory)) Directory.CreateDirectory(directory);
                int captureWidth = ReadIntArgument(arguments, "-screen-width", 1280);
                int captureHeight = ReadIntArgument(arguments, "-screen-height", 720);
                yield return CaptureCamera(fullPath, captureWidth, captureHeight);

                bool captured = File.Exists(fullPath) && new FileInfo(fullPath).Length > 0;
                valid &= captured;
                Debug.Log($"CLOCKWORK_WATER_STORAGE_CAPTURE valid={captured} " +
                    $"size={captureWidth}x{captureHeight} path={fullPath}");
            }

            Application.Quit(valid ? 0 : 2);
        }

        private bool Validate(out string details)
        {
            List<string> failures = new List<string>();
            if (registrationRoot == null)
            {
                failures.Add("missing-root");
            }
            else
            {
                Dictionary<string, SpriteRenderer> renderers = registrationRoot
                    .GetComponentsInChildren<SpriteRenderer>(true)
                    .ToDictionary(renderer => renderer.gameObject.name, StringComparer.Ordinal);
                foreach (string layerName in ExpectedLayerNames)
                {
                    if (!renderers.TryGetValue(layerName, out SpriteRenderer renderer))
                    {
                        failures.Add($"missing-{layerName}");
                        continue;
                    }

                    Transform layer = renderer.transform;
                    if (layer.localPosition.sqrMagnitude > 0.000001f) failures.Add($"position-{layerName}");
                    if (Quaternion.Angle(layer.localRotation, Quaternion.identity) > 0.001f)
                        failures.Add($"rotation-{layerName}");
                    if ((layer.localScale - Vector3.one).sqrMagnitude > 0.000001f)
                        failures.Add($"scale-{layerName}");

                    Sprite sprite = renderer.sprite;
                    if (sprite == null)
                    {
                        failures.Add($"sprite-{layerName}");
                        continue;
                    }

                    if (sprite.texture.width != 800 || sprite.texture.height != 450)
                        failures.Add($"canvas-{layerName}");
                    if (Mathf.Abs(sprite.pixelsPerUnit - 64f) > 0.001f)
                        failures.Add($"ppu-{layerName}");
                    if ((sprite.pivot - new Vector2(400f, 225f)).sqrMagnitude > 0.01f)
                        failures.Add($"pivot-{layerName}");
                }

                if (renderers.Count != ExpectedLayerNames.Length) failures.Add("layer-count");
            }

            if (roomCamera == null || !roomCamera.orthographic
                || Mathf.Abs(roomCamera.orthographicSize - 2.8125f) > 0.0001f)
            {
                failures.Add("camera");
            }
            else
            {
                PixelPerfectCamera pixelPerfect = roomCamera.GetComponent<PixelPerfectCamera>();
                if (pixelPerfect == null || pixelPerfect.assetsPPU != 64
                    || pixelPerfect.refResolutionX != 640 || pixelPerfect.refResolutionY != 360)
                {
                    failures.Add("pixel-perfect");
                }

                Vector3 center = roomCamera.WorldToScreenPoint(Vector3.zero);
                if (Mathf.Abs(center.x - Screen.width * 0.5f) > 1f
                    || Mathf.Abs(center.y - Screen.height * 0.5f) > 1f)
                {
                    failures.Add("screen-origin");
                }
            }

            if (playerMotor == null || !playerMotor.Grounded) failures.Add("player-grounding");
            if (playerMotor != null && (playerMotor.transform.localScale - Vector3.one).sqrMagnitude > 0.000001f)
                failures.Add("player-root-scale");

            details = $"layers={ExpectedLayerNames.Length} " +
                $"screen={Screen.width}x{Screen.height} " +
                $"player={(playerMotor == null ? Vector3.zero : playerMotor.transform.position)} " +
                $"grounded={(playerMotor != null && playerMotor.Grounded)} " +
                $"failures={(failures.Count == 0 ? "none" : string.Join(",", failures))}";
            return failures.Count == 0;
        }

        private static string ReadArgument(string[] arguments, string name)
        {
            for (int i = 0; i < arguments.Length - 1; i++)
            {
                if (string.Equals(arguments[i], name, StringComparison.Ordinal))
                    return arguments[i + 1];
            }
            return null;
        }

        private IEnumerator CaptureCamera(string path, int width, int height)
        {
            if (roomCamera == null) yield break;

            RenderTexture target = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32)
            {
                filterMode = FilterMode.Point,
                name = "RegisteredWaterStorageCapture"
            };
            target.Create();
            RenderTexture previousActive = RenderTexture.active;
            RenderTexture previousTarget = roomCamera.targetTexture;
            roomCamera.targetTexture = target;

            yield return null;
            yield return new WaitForEndOfFrame();

            RenderTexture.active = target;
            Texture2D capture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            capture.ReadPixels(new Rect(0f, 0f, width, height), 0, 0, false);
            capture.Apply(false, false);
            File.WriteAllBytes(path, capture.EncodeToPNG());

            roomCamera.targetTexture = previousTarget;
            RenderTexture.active = previousActive;
            Destroy(capture);
            target.Release();
            Destroy(target);
        }

        private static int ReadIntArgument(string[] arguments, string name, int fallback)
        {
            string value = ReadArgument(arguments, name);
            return int.TryParse(value, out int parsed) && parsed > 0 ? parsed : fallback;
        }

#if UNITY_EDITOR
        public void Configure(Transform layerRoot, Camera targetCamera, TiqueMotor targetPlayer)
        {
            registrationRoot = layerRoot;
            roomCamera = targetCamera;
            playerMotor = targetPlayer;
        }
#endif
    }
}
