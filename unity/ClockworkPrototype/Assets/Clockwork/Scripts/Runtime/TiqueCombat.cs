using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueMotor), typeof(TiqueInputReader))]
    public sealed class TiqueCombat : MonoBehaviour
    {
        [SerializeField] private AttackDefinition[] attacks;
        [SerializeField] private LineRenderer hitboxRenderer;
        [SerializeField] private LineRenderer trailRenderer;

        private TiqueMotor motor;
        private TiqueInputReader input;
        private int selectedAttack;
        private float attackTimer;
        private bool showHitboxes;

        public AttackDefinition CurrentAttack => attacks != null && attacks.Length > 0
            ? attacks[Mathf.Clamp(selectedAttack, 0, attacks.Length - 1)]
            : null;
        public bool IsAttacking => attackTimer > 0f && CurrentAttack != null;
        public float AttackProgress => !IsAttacking ? 0f : 1f - Mathf.Clamp01(attackTimer / CurrentAttack.Duration);
        public string SelectedWeaponName => CurrentAttack == null ? "None" : CurrentAttack.DisplayName;

        private void Awake()
        {
            motor = GetComponent<TiqueMotor>();
            input = GetComponent<TiqueInputReader>();
        }

        private void Update()
        {
            if (input.Slot1Pressed) SelectAttack(0);
            if (input.Slot2Pressed) SelectAttack(1);
            if (input.Slot3Pressed) SelectAttack(2);
            if (input.DebugHitboxesPressed) showHitboxes = !showHitboxes;

            if (input.AttackPressed && !IsAttacking && !motor.IsDashing && CurrentAttack != null)
            {
                attackTimer = CurrentAttack.Duration;
            }

            attackTimer = Mathf.Max(0f, attackTimer - Time.deltaTime);
            UpdateDebugRenderers();
        }

        public void SelectAttack(int index)
        {
            if (!IsAttacking && attacks != null && index >= 0 && index < attacks.Length)
            {
                selectedAttack = index;
            }
        }

        private void UpdateDebugRenderers()
        {
            bool active = IsAttacking && CurrentAttack.IsActiveAt(AttackProgress);
            if (hitboxRenderer != null)
            {
                hitboxRenderer.enabled = showHitboxes && active;
                if (hitboxRenderer.enabled)
                {
                    Vector2 offset = CurrentAttack.HitboxCenter;
                    offset.x *= motor.Facing;
                    DrawRectangle(hitboxRenderer, (Vector2)transform.position + offset, CurrentAttack.HitboxSize);
                    hitboxRenderer.startColor = CurrentAttack.TrailColor;
                    hitboxRenderer.endColor = CurrentAttack.TrailColor;
                }
            }

            if (trailRenderer != null)
            {
                trailRenderer.enabled = active && CurrentAttack.AttackId != "fist";
                if (trailRenderer.enabled)
                {
                    DrawTrail(trailRenderer, CurrentAttack.AttackId, CurrentAttack.TrailColor);
                }
            }
        }

        private static void DrawRectangle(LineRenderer line, Vector2 center, Vector2 size)
        {
            Vector2 half = size * 0.5f;
            line.positionCount = 5;
            line.SetPosition(0, center + new Vector2(-half.x, -half.y));
            line.SetPosition(1, center + new Vector2(-half.x, half.y));
            line.SetPosition(2, center + new Vector2(half.x, half.y));
            line.SetPosition(3, center + new Vector2(half.x, -half.y));
            line.SetPosition(4, center + new Vector2(-half.x, -half.y));
        }

        private void DrawTrail(LineRenderer line, string attackId, Color color)
        {
            const int points = 14;
            line.positionCount = points;
            line.startColor = color;
            line.endColor = new Color(color.r, color.g, color.b, 0.12f);

            for (int i = 0; i < points; i++)
            {
                float t = i / (points - 1f);
                Vector2 local;
                if (attackId == "hammer")
                {
                    float angle = Mathf.Lerp(145f, -35f, t) * Mathf.Deg2Rad;
                    local = new Vector2(Mathf.Cos(angle) * 1.15f, 0.72f + Mathf.Sin(angle) * 1.05f);
                }
                else
                {
                    Vector2 a = new Vector2(-0.5f, 0.67f);
                    Vector2 b = new Vector2(0.2f, 0.9f);
                    Vector2 c = new Vector2(0.88f, 0.18f);
                    local = Vector2.Lerp(Vector2.Lerp(a, b, t), Vector2.Lerp(b, c, t), t);
                }
                local.x *= motor.Facing;
                line.SetPosition(i, (Vector2)transform.position + local);
            }
        }

#if UNITY_EDITOR
        public void Configure(AttackDefinition[] approvedAttacks, LineRenderer hitbox, LineRenderer trail)
        {
            attacks = approvedAttacks;
            hitboxRenderer = hitbox;
            trailRenderer = trail;
        }
#endif
    }
}
