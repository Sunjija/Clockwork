using UnityEngine;

namespace Clockwork
{
    public sealed class RegisteredLayerPulse2D : MonoBehaviour
    {
        [SerializeField] private SpriteRenderer target;
        [SerializeField] private float framesPerSecond = 8f;
        [SerializeField] private float minimumAlpha = 0.82f;
        [SerializeField] private float maximumAlpha = 0.98f;

        private Color baseColor = Color.white;

        private void Awake()
        {
            if (target != null) baseColor = target.color;
        }

        private void Update()
        {
            if (target == null) return;
            float steppedTime = Mathf.Floor(Time.unscaledTime * framesPerSecond) / framesPerSecond;
            float blend = 0.5f + 0.5f * Mathf.Sin(steppedTime * Mathf.PI * 1.35f);
            Color color = baseColor;
            color.a = Mathf.Lerp(minimumAlpha, maximumAlpha, blend);
            target.color = color;
        }

#if UNITY_EDITOR
        public void Configure(SpriteRenderer targetRenderer, float fps, float minAlpha, float maxAlpha)
        {
            target = targetRenderer;
            framesPerSecond = Mathf.Max(1f, fps);
            minimumAlpha = Mathf.Clamp01(minAlpha);
            maximumAlpha = Mathf.Clamp(maxAlpha, minimumAlpha, 1f);
            baseColor = target == null ? Color.white : target.color;
        }
#endif
    }
}
