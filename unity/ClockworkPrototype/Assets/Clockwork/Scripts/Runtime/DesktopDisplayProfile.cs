using UnityEngine;

namespace Clockwork
{
    public static class DesktopDisplayProfile
    {
        public const int Width = 1280;
        public const int Height = 720;
        public const float Aspect = Width / (float)Height;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Apply()
        {
#if UNITY_EDITOR_WIN || UNITY_STANDALONE_WIN
            Screen.SetResolution(Width, Height, FullScreenMode.Windowed);
#endif
        }
    }
}
