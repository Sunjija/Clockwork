using UnityEngine;

namespace Clockwork
{
    public sealed class DoubleJumpCorePulse : MonoBehaviour
    {
        private const int OuterSegments = 64;
        private const int InnerSegments = 48;

        [SerializeField] private TiqueMotor motor;
        [SerializeField] private LineRenderer outerRing;
        [SerializeField] private LineRenderer innerRing;
        [SerializeField] private float coreHeight = 0.34f;
        [SerializeField] private Color pulseColor = new(0.43f, 0.93f, 1f, 1f);

        private void Awake()
        {
            SetVisible(false);
        }

        private void LateUpdate()
        {
            if (motor == null || outerRing == null || innerRing == null || !motor.IsDoubleJumping)
            {
                SetVisible(false);
                return;
            }

            SetVisible(true);
            float progress = motor.DoubleJumpProgress;
            float eased = 1f - Mathf.Pow(1f - progress, 3f);
            float alpha = Mathf.Clamp01(1f - progress) * 0.78f;
            Vector3 center = transform.position + Vector3.up * coreHeight;

            DrawGearRing(outerRing, center, Mathf.Lerp(0.12f, 0.46f, eased), eased, alpha);
            DrawCircle(innerRing, center, Mathf.Lerp(0.07f, 0.29f, eased), alpha * 0.72f);
        }

        public void Configure(TiqueMotor sourceMotor, LineRenderer outer, LineRenderer inner)
        {
            motor = sourceMotor;
            outerRing = outer;
            innerRing = inner;
        }

        private void DrawGearRing(LineRenderer line, Vector3 center, float radius, float progress, float alpha)
        {
            line.positionCount = OuterSegments + 1;
            Color color = new(pulseColor.r, pulseColor.g, pulseColor.b, alpha);
            line.startColor = color;
            line.endColor = color;

            for (int i = 0; i <= OuterSegments; i++)
            {
                float angle = Mathf.PI * 2f * i / OuterSegments;
                float tooth = Mathf.Max(0f, Mathf.Cos(angle * 8f + progress * 0.8f)) * 0.03f;
                float pointRadius = radius + tooth;
                line.SetPosition(i, center + new Vector3(Mathf.Cos(angle), Mathf.Sin(angle)) * pointRadius);
            }
        }

        private void DrawCircle(LineRenderer line, Vector3 center, float radius, float alpha)
        {
            line.positionCount = InnerSegments + 1;
            Color color = new(pulseColor.r, pulseColor.g, pulseColor.b, alpha);
            line.startColor = color;
            line.endColor = color;

            for (int i = 0; i <= InnerSegments; i++)
            {
                float angle = Mathf.PI * 2f * i / InnerSegments;
                line.SetPosition(i, center + new Vector3(Mathf.Cos(angle), Mathf.Sin(angle)) * radius);
            }
        }

        private void SetVisible(bool visible)
        {
            if (outerRing != null) outerRing.enabled = visible;
            if (innerRing != null) innerRing.enabled = visible;
        }
    }
}
