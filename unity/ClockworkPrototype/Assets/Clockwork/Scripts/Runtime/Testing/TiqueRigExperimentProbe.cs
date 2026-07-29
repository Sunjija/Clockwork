using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    public sealed class TiqueRigExperimentProbe : MonoBehaviour
    {
        private IEnumerator Start()
        {
            int width = ReadIntArgument("-screen-width", 1280);
            int height = ReadIntArgument("-screen-height", 720);
            Screen.SetResolution(width, height, FullScreenMode.Windowed);
            yield return null;
            yield return null;

            string capturePath = ReadArgument("-clockworkTiqueRigCapturePath");
            string logPath = ReadArgument("-clockworkTiqueRigProbeLogPath");
            if (string.IsNullOrWhiteSpace(capturePath) && string.IsNullOrWhiteSpace(logPath))
                yield break;

            TiqueRigComparisonPlayback playback = FindAnyObjectByType<TiqueRigComparisonPlayback>();
            playback?.SetProbeWalk(true);
            yield return new WaitForSecondsRealtime(1.1f);

            List<string> failures = new List<string>();
            if (SceneManager.GetActiveScene().name != "TiqueRigExperiment") failures.Add("scene");
            if (playback == null) failures.Add("playback");
            if (playback != null && playback.ApprovedWalkFrameCount != 12) failures.Add("approved-walk-frames");
            if (playback != null && playback.BakedWalkFrameCount != 12) failures.Add("baked-walk-frames");
            if (playback == null || playback.LiveRig == null || !playback.LiveRig.IsConfigured)
                failures.Add("live-rig");

            if (!string.IsNullOrWhiteSpace(capturePath))
            {
                Directory.CreateDirectory(Path.GetDirectoryName(capturePath) ?? ".");
                ScreenCapture.CaptureScreenshot(capturePath);
                float timeout = Time.realtimeSinceStartup + 8f;
                while (!File.Exists(capturePath) && Time.realtimeSinceStartup < timeout)
                    yield return null;
                if (!File.Exists(capturePath)) failures.Add("capture");
            }

            string line = $"CLOCKWORK_TIQUE_RIG_PROBE valid={failures.Count == 0} "
                + $"scene={SceneManager.GetActiveScene().name} "
                + $"failures={(failures.Count == 0 ? "none" : string.Join(",", failures))}";
            Debug.Log(line);
            if (!string.IsNullOrWhiteSpace(logPath))
            {
                Directory.CreateDirectory(Path.GetDirectoryName(logPath) ?? ".");
                File.WriteAllText(logPath, line + Environment.NewLine);
            }

            yield return new WaitForSecondsRealtime(0.2f);
            Application.Quit(failures.Count == 0 ? 0 : 2);
        }

        private static string ReadArgument(string key)
        {
            string[] args = Environment.GetCommandLineArgs();
            for (int i = 0; i < args.Length - 1; i++)
                if (string.Equals(args[i], key, StringComparison.OrdinalIgnoreCase))
                    return args[i + 1];
            return null;
        }

        private static int ReadIntArgument(string key, int fallback)
        {
            string value = ReadArgument(key);
            return int.TryParse(value, out int parsed) && parsed > 0 ? parsed : fallback;
        }
    }
}
