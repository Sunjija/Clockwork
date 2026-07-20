using System.Collections;
using UnityEngine;

namespace Clockwork
{
    public sealed class ScreenFader : MonoBehaviour
    {
        private static ScreenFader instance;
        private float alpha;

        public static ScreenFader Instance
        {
            get
            {
                if (instance == null)
                {
                    GameObject holder = new GameObject("ScreenFader");
                    DontDestroyOnLoad(holder);
                    instance = holder.AddComponent<ScreenFader>();
                }
                return instance;
            }
        }

        public IEnumerator FadeRoutine(float targetAlpha, float duration)
        {
            float start = alpha;
            float elapsed = 0f;
            while (elapsed < duration)
            {
                elapsed += Time.unscaledDeltaTime;
                alpha = Mathf.Lerp(start, targetAlpha, Mathf.Clamp01(elapsed / duration));
                yield return null;
            }
            alpha = targetAlpha;
        }

        private void OnGUI()
        {
            if (alpha <= 0f) return;
            GUI.depth = -100;
            Color previous = GUI.color;
            GUI.color = new Color(0f, 0f, 0f, alpha);
            GUI.DrawTexture(new Rect(0f, 0f, Screen.width, Screen.height), Texture2D.whiteTexture);
            GUI.color = previous;
        }
    }
}
