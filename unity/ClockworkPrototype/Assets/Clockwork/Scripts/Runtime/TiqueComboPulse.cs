using UnityEngine;

namespace Clockwork
{
    public sealed class TiqueComboPulse : MonoBehaviour
    {
        private const int OuterSegments = 64;
        private const int InnerSegments = 48;

        [SerializeField] private TiqueCombat combat;
        [SerializeField] private LineRenderer outerRing;
        [SerializeField] private LineRenderer innerRing;
        [SerializeField] private float coreHeight = 0.34f;
        [SerializeField] private float finisherDuration = 0.34f;
        [SerializeField] private Color windowColor = new(0.43f, 0.93f, 1f, 1f);
        [SerializeField] private Color finisherColor = new(0.98f, 0.72f, 0.22f, 1f);

        private float finisherTimer;

        private void OnEnable()
        {
            if (combat != null) combat.AttackStepStarted += OnAttackStepStarted;
        }

        private void OnDisable()
        {
            if (combat != null) combat.AttackStepStarted -= OnAttackStepStarted;
            SetVisible(false);
        }

        private void LateUpdate()
        {
            if (combat == null || outerRing == null || innerRing == null)
            {
                SetVisible(false);
                return;
            }

            if (finisherTimer > 0f)
            {
                finisherTimer = Mathf.Max(0f, finisherTimer - Time.deltaTime);
                DrawFinisher(1f - finisherTimer / finisherDuration);
                return;
            }

            if (combat.IsWeaponTransitionQueued)
            {
                DrawInputWindow();
                return;
            }

            SetVisible(false);
        }

        public void Configure(TiqueCombat sourceCombat, LineRenderer outer, LineRenderer inner)
        {
            if (isActiveAndEnabled && combat != null) combat.AttackStepStarted -= OnAttackStepStarted;
            combat = sourceCombat;
            outerRing = outer;
            innerRing = inner;
            if (isActiveAndEnabled && combat != null) combat.AttackStepStarted += OnAttackStepStarted;
            SetVisible(false);
        }

        private void OnAttackStepStarted(int stepIndex, int stepCount, bool isTransition)
        {
            if (!isTransition && stepCount >= 3 && stepIndex == stepCount - 1)
            {
                finisherTimer = finisherDuration;
            }
        }

        private void DrawInputWindow()
        {
            SetVisible(true);
            float breathe = 0.5f + Mathf.Sin(Time.time * 16f) * 0.5f;
            Vector3 center = transform.position + Vector3.up * coreHeight;
            DrawGearRing(outerRing, center, 0.16f + breathe * 0.018f, Time.time * 0.4f,
                windowColor, 0.68f);
            DrawCircle(innerRing, center, 0.1f, windowColor, 0.44f);
        }

        private void DrawFinisher(float progress)
        {
            SetVisible(true);
            float eased = 1f - Mathf.Pow(1f - progress, 3f);
            float alpha = Mathf.Clamp01(1f - progress) * 0.92f;
            Vector3 center = transform.position + Vector3.up * coreHeight;
            DrawGearRing(outerRing, center, Mathf.Lerp(0.13f, 0.58f, eased),
                eased, finisherColor, alpha);
            DrawCircle(innerRing, center, Mathf.Lerp(0.08f, 0.36f, eased),
                finisherColor, alpha * 0.72f);
        }

        private static void DrawGearRing(
            LineRenderer line, Vector3 center, float radius, float phase, Color baseColor, float alpha)
        {
            line.positionCount = OuterSegments + 1;
            Color color = new(baseColor.r, baseColor.g, baseColor.b, alpha);
            line.startColor = color;
            line.endColor = color;
            for (int i = 0; i <= OuterSegments; i++)
            {
                float angle = Mathf.PI * 2f * i / OuterSegments;
                float tooth = Mathf.Max(0f, Mathf.Cos(angle * 8f + phase)) * 0.03f;
                float pointRadius = radius + tooth;
                line.SetPosition(i, center + new Vector3(Mathf.Cos(angle), Mathf.Sin(angle)) * pointRadius);
            }
        }

        private static void DrawCircle(
            LineRenderer line, Vector3 center, float radius, Color baseColor, float alpha)
        {
            line.positionCount = InnerSegments + 1;
            Color color = new(baseColor.r, baseColor.g, baseColor.b, alpha);
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
