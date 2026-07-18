using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class TiqueSpriteAnimator : MonoBehaviour
    {
        [SerializeField] private TiqueMotor motor;
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private SpriteSequence idle;
        [SerializeField] private SpriteSequence walk;
        [SerializeField] private SpriteSequence jump;
        [SerializeField] private SpriteSequence doubleJump;
        [SerializeField] private SpriteSequence dash;

        private SpriteRenderer spriteRenderer;
        private SpriteSequence activeSequence;
        private float sequenceTime;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
        }

        private void LateUpdate()
        {
            SpriteSequence next = ResolveSequence();
            if (next != activeSequence)
            {
                activeSequence = next;
                sequenceTime = 0f;
            }
            else
            {
                sequenceTime += Time.deltaTime;
            }

            if (activeSequence == null)
            {
                return;
            }

            float normalized = ResolveNormalizedTime(activeSequence);
            spriteRenderer.sprite = activeSequence.FrameAt(normalized);
            spriteRenderer.flipX = motor.Facing < 0;
            transform.localScale = Vector3.one * activeSequence.RenderScale;
        }

        private SpriteSequence ResolveSequence()
        {
            if (combat.IsAttacking && combat.CurrentAttack != null) return combat.CurrentAttack.Sequence;
            if (motor.IsDashing) return dash;
            if (motor.IsDoubleJumping) return doubleJump;
            if (!motor.Grounded || motor.IsTakingOff || motor.IsLanding) return jump;
            if (Mathf.Abs(motor.HorizontalSpeed) > 0.24f) return walk;
            return idle;
        }

        private float ResolveNormalizedTime(SpriteSequence sequence)
        {
            if (combat.IsAttacking && combat.CurrentAttack != null && sequence == combat.CurrentAttack.Sequence)
                return combat.AttackProgress;
            if (sequence == dash) return motor.DashProgress;
            if (sequence == doubleJump) return motor.DoubleJumpProgress;
            if (sequence == jump)
            {
                if (motor.IsLanding) return Mathf.Lerp(0.9f, 1f, motor.LandingProgress);
                if (motor.IsTakingOff) return Mathf.Lerp(0f, 0.18f, motor.TakeoffProgress);
                if (motor.VerticalSpeed > 0.95f) return 0.38f;
                if (motor.VerticalSpeed > -0.95f) return 0.55f;
                return 0.78f;
            }
            if (sequence == walk)
            {
                const float cycleDistance = 1.55f;
                return Mathf.Repeat(motor.TravelDistance / cycleDistance, 1f);
            }
            return sequenceTime / sequence.Duration;
        }

#if UNITY_EDITOR
        public void Configure(
            TiqueMotor playerMotor,
            TiqueCombat playerCombat,
            SpriteSequence idleSequence,
            SpriteSequence walkSequence,
            SpriteSequence jumpSequence,
            SpriteSequence doubleJumpSequence,
            SpriteSequence dashSequence)
        {
            motor = playerMotor;
            combat = playerCombat;
            idle = idleSequence;
            walk = walkSequence;
            jump = jumpSequence;
            doubleJump = doubleJumpSequence;
            dash = dashSequence;
        }
#endif
    }
}

