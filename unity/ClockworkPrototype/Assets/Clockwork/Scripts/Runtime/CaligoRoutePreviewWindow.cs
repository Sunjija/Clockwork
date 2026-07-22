using System;
using System.Collections;
using System.Runtime.InteropServices;
using UnityEngine;

namespace Clockwork
{
    public sealed class CaligoRoutePreviewWindow : MonoBehaviour
    {
        private const int PreviewWidth = 1280;
        private const int PreviewHeight = 720;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Initialize()
        {
#if UNITY_STANDALONE_WIN && !UNITY_EDITOR
            if (Array.IndexOf(
                    Environment.GetCommandLineArgs(), "-clockworkCaligoRoutePreview") < 0)
            {
                return;
            }

            Screen.SetResolution(PreviewWidth, PreviewHeight, FullScreenMode.Windowed);
            GameObject host = new GameObject(nameof(CaligoRoutePreviewWindow));
            DontDestroyOnLoad(host);
            host.AddComponent<CaligoRoutePreviewWindow>();
#endif
        }

#if UNITY_STANDALONE_WIN && !UNITY_EDITOR
        private IEnumerator Start()
        {
            yield return null;
            yield return new WaitForEndOfFrame();
            CenterPlayerWindow();
            Destroy(gameObject);
        }

        private static void CenterPlayerWindow()
        {
            IntPtr window = GetActiveWindow();
            if (window == IntPtr.Zero || !GetWindowRect(window, out NativeRect windowRect)) return;

            IntPtr monitor = MonitorFromWindow(window, MonitorDefaultToNearest);
            MonitorInfo monitorInfo = new MonitorInfo
            {
                Size = Marshal.SizeOf<MonitorInfo>()
            };
            if (monitor == IntPtr.Zero || !GetMonitorInfo(monitor, ref monitorInfo)) return;

            int windowWidth = windowRect.Right - windowRect.Left;
            int windowHeight = windowRect.Bottom - windowRect.Top;
            int workWidth = monitorInfo.Work.Right - monitorInfo.Work.Left;
            int workHeight = monitorInfo.Work.Bottom - monitorInfo.Work.Top;
            int x = monitorInfo.Work.Left + Math.Max(0, (workWidth - windowWidth) / 2);
            int y = monitorInfo.Work.Top + Math.Max(0, (workHeight - windowHeight) / 2);
            SetWindowPos(
                window, IntPtr.Zero, x, y, 0, 0,
                SetWindowPositionFlags.NoSize
                | SetWindowPositionFlags.NoZOrder
                | SetWindowPositionFlags.NoActivate);
        }

        private const uint MonitorDefaultToNearest = 2;

        [Flags]
        private enum SetWindowPositionFlags : uint
        {
            NoSize = 0x0001,
            NoZOrder = 0x0004,
            NoActivate = 0x0010
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct NativeRect
        {
            public int Left;
            public int Top;
            public int Right;
            public int Bottom;
        }

        [StructLayout(LayoutKind.Sequential)]
        private struct MonitorInfo
        {
            public int Size;
            public NativeRect Monitor;
            public NativeRect Work;
            public uint Flags;
        }

        [DllImport("user32.dll")]
        private static extern IntPtr GetActiveWindow();

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool GetWindowRect(IntPtr window, out NativeRect rectangle);

        [DllImport("user32.dll")]
        private static extern IntPtr MonitorFromWindow(IntPtr window, uint flags);

        [DllImport("user32.dll", CharSet = CharSet.Auto)]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool GetMonitorInfo(IntPtr monitor, ref MonitorInfo monitorInfo);

        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool SetWindowPos(
            IntPtr window, IntPtr insertAfter, int x, int y, int width, int height,
            SetWindowPositionFlags flags);
#endif
    }
}
