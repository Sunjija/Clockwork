using System;
using UnityEngine;

namespace Clockwork
{
    public sealed class TiquePunchImpact : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private LineRenderer primaryStroke;
        [SerializeField] private LineRenderer secondaryStroke;
        [SerializeField] private float impactDuration = 0.12f;

        private float impactTimer;
        private Vector3 impactCenter;
        private int impactStep;

        private void OnEnable()
        {
            if (combat != null) combat.AttackLanded += OnAttackLanded;
        }

        private void OnDisable()
        {
            if (combat != null) combat.AttackLanded -= OnAttackLanded;
            SetVisible(false);
        }

        private void LateUpdate()
        {
            if (impactTimer <= 0f)
            {
                SetVisible(false);
                return;
            }

            impactTimer = Mathf.Max(0f, impactTimer - Time.deltaTime);
            float progress = 1f - impactTimer / impactDuration;
            float alpha = 1f - progress;
            float size = Mathf.Lerp(0.08f, impactStep >= 2 ? 0.34f : 0.23f, progress);
            float angle = impactStep == 1 ? -28f : 28f;
            if (impactStep >= 2) angle = 0f;
            Color color = impactStep >= 2
                ? new Color(1f, 0.72f, 0.2f, alpha)
                : new Color(0.88f, 0.97f, 1f, alpha);
            DrawStroke(primaryStroke, impactCenter, size, angle, color);
            DrawStroke(secondaryStroke, impactCenter, size * 0.72f, angle + 90f, color);
        }

        public void Configure(TiqueCombat sourceCombat, LineRenderer primary, LineRenderer secondary)
        {
            if (isActiveAndEnabled && combat != null) combat.AttackLanded -= OnAttackLanded;
            combat = sourceCombat;
            primaryStroke = primary;
            secondaryStroke = secondary;
            if (isActiveAndEnabled && combat != null) combat.AttackLanded += OnAttackLanded;
            SetVisible(false);
        }

        private void OnAttackLanded(CombatHitResult hit)
        {
            if (combat.CurrentAttack == null
                || !combat.CurrentAttack.AttackId.StartsWith("fist", StringComparison.Ordinal))
            {
                return;
            }

            impactStep = combat.CurrentComboStepIndex;
            impactCenter = hit.Enemy == null
                ? transform.position + Vector3.up * 0.45f
                : hit.Enemy.transform.position + Vector3.up * 0.42f;
            impactTimer = impactDuration;
            SetVisible(true);
        }

        private static void DrawStroke(
            LineRenderer line, Vector3 center, float size, float angleDegrees, Color color)
        {
            if (line == null) return;
            float angle = angleDegrees * Mathf.Deg2Rad;
            Vector3 direction = new Vector3(Mathf.Cos(angle), Mathf.Sin(angle), 0f) * size;
            line.positionCount = 2;
            line.SetPosition(0, center - direction);
            line.SetPosition(1, center + direction);
            line.startColor = color;
            line.endColor = new Color(color.r, color.g, color.b, color.a * 0.2f);
        }

        private void SetVisible(bool visible)
        {
            if (primaryStroke != null) primaryStroke.enabled = visible;
            if (secondaryStroke != null) secondaryStroke.enabled = visible;
        }
    }
}
