using UnityEngine;

namespace Clockwork
{
    public sealed class TiqueSwapChargeWave : MonoBehaviour
    {
        private const int Segments = 72;

        [SerializeField] private TiqueCombat combat;
        [SerializeField] private LineRenderer outerWave;
        [SerializeField] private LineRenderer innerWave;
        [SerializeField] private float duration = 0.42f;
        [SerializeField] private float centerHeight = 0.42f;
        [SerializeField] private Color waveColor = new(1f, 0.12f, 0.08f, 1f);

        private float timer;

        private void OnEnable()
        {
            if (combat != null) combat.WeaponTransitionStarted += OnTransitionStarted;
        }

        private void OnDisable()
        {
            if (combat != null) combat.WeaponTransitionStarted -= OnTransitionStarted;
            SetVisible(false);
        }

        private void LateUpdate()
        {
            if (timer <= 0f)
            {
                SetVisible(false);
                return;
            }

            timer = Mathf.Max(0f, timer - Time.deltaTime);
            float progress = 1f - timer / duration;
            float eased = 1f - Mathf.Pow(1f - progress, 3f);
            float alpha = Mathf.Clamp01(1f - progress);
            Vector3 center = transform.position + Vector3.up * centerHeight;
            DrawWave(outerWave, center, Mathf.Lerp(0.16f, 0.92f, eased), alpha * 0.92f, 0f);
            DrawWave(innerWave, center, Mathf.Lerp(0.08f, 0.62f, eased), alpha * 0.62f, Mathf.PI / 8f);
        }

        public void Configure(TiqueCombat sourceCombat, LineRenderer outer, LineRenderer inner)
        {
            if (isActiveAndEnabled && combat != null) combat.WeaponTransitionStarted -= OnTransitionStarted;
            combat = sourceCombat;
            outerWave = outer;
            innerWave = inner;
            if (isActiveAndEnabled && combat != null) combat.WeaponTransitionStarted += OnTransitionStarted;
            SetVisible(false);
        }

        private void OnTransitionStarted(float lentiumCost)
        {
            timer = duration;
            SetVisible(true);
        }

        private void DrawWave(
            LineRenderer line, Vector3 center, float radius, float alpha, float phase)
        {
            if (line == null) return;
            line.positionCount = Segments + 1;
            Color color = new(waveColor.r, waveColor.g, waveColor.b, alpha);
            line.startColor = color;
            line.endColor = color;
            for (int i = 0; i <= Segments; i++)
            {
                float angle = Mathf.PI * 2f * i / Segments;
                float distortion = Mathf.Sin(angle * 6f + phase) * 0.035f * alpha;
                float pointRadius = radius + distortion;
                line.SetPosition(i, center + new Vector3(Mathf.Cos(angle), Mathf.Sin(angle)) * pointRadius);
            }
        }

        private void SetVisible(bool visible)
        {
            if (outerWave != null) outerWave.enabled = visible;
            if (innerWave != null) innerWave.enabled = visible;
        }
    }
}
