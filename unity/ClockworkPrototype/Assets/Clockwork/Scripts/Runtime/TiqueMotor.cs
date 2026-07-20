using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    [RequireComponent(typeof(Rigidbody2D), typeof(Collider2D), typeof(TiqueInputReader))]
    public sealed class TiqueMotor : MonoBehaviour
    {
        [Header("Web prototype parity")]
        [SerializeField] private float normalMoveSpeed = 2.5f;
        [SerializeField] private float damagedMoveMultiplier = 0.86f;
        [SerializeField] private bool damaged;
        [SerializeField] private float groundResponse = 21f;
        [SerializeField] private float airResponse = 9f;
        [SerializeField] private float jumpVelocity = 5.75f;
        [SerializeField] private float doubleJumpVelocity = 5.5f;
        [SerializeField] private float ascentGravity = 18.4f;
        [SerializeField] private float fallGravity = 36.8f;
        [SerializeField] private float jumpCutGravity = 11.2f;
        [SerializeField] private float maxFallSpeed = 8.6f;
        [SerializeField] private float coyoteDuration = 0.11f;
        [SerializeField] private float jumpBufferDuration = 0.1f;
        [SerializeField] private float dashSpeed = 5.3f;
        [SerializeField] private float dashDuration = 0.32f;
        [SerializeField] private float dashCooldownDuration = 0.54f;
        [SerializeField] private float groundProbeDistance = 0.04f;

        private const float TakeoffDuration = 0.14f;
        private const float LandingDuration = 0.18f;
        private const float DoubleJumpAnimDuration = 0.34f;

        private readonly RaycastHit2D[] groundHits = new RaycastHit2D[8];
        private Rigidbody2D body;
        private Collider2D bodyCollider;
        private TiqueInputReader input;
        private ContactFilter2D groundFilter;
        private float moveInput;
        private bool jumpPressed;
        private bool dashPressed;
        private bool jumpHeld;
        private float coyoteTimer;
        private float jumpBufferTimer;
        private float dashTimer;
        private float dashCooldown;
        private float takeoffTimer;
        private float landingTimer;
        private float doubleJumpTimer;
        private bool wasGrounded;
        private int airJumps = 1;
        private float travelDistance;

        public int Facing { get; private set; } = 1;
        public bool Grounded { get; private set; }
        public bool IsDashing => dashTimer > 0f;
        public bool IsTakingOff => takeoffTimer > 0f;
        public bool IsLanding => landingTimer > 0f;
        public bool IsDoubleJumping => doubleJumpTimer > 0f;
        public float HorizontalSpeed => body == null ? 0f : body.linearVelocity.x;
        public float VerticalSpeed => body == null ? 0f : body.linearVelocity.y;
        public float TravelDistance => travelDistance;
        public float DashProgress => 1f - Mathf.Clamp01(dashTimer / dashDuration);
        public float DoubleJumpProgress => 1f - Mathf.Clamp01(doubleJumpTimer / DoubleJumpAnimDuration);
        public float TakeoffProgress => 1f - Mathf.Clamp01(takeoffTimer / TakeoffDuration);
        public float LandingProgress => 1f - Mathf.Clamp01(landingTimer / LandingDuration);
        public float CurrentMoveSpeed => damaged ? normalMoveSpeed * damagedMoveMultiplier : normalMoveSpeed;

        public void SetDamagedState(bool value)
        {
            damaged = value;
        }

        private void Awake()
        {
            body = GetComponent<Rigidbody2D>();
            bodyCollider = GetComponent<Collider2D>();
            input = GetComponent<TiqueInputReader>();
            body.gravityScale = 0f;
            body.freezeRotation = true;
            groundFilter = new ContactFilter2D
            {
                useTriggers = false,
                useLayerMask = true,
                layerMask = Physics2D.AllLayers
            };
        }

        private void Update()
        {
            moveInput = input.Move;
            jumpHeld = input.JumpHeld;
            jumpPressed |= input.JumpPressed;
            dashPressed |= input.DashPressed;

            if (Mathf.Abs(moveInput) > 0.01f)
            {
                Facing = moveInput > 0f ? 1 : -1;
            }

            if (input.ReloadPressed)
            {
                SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
            }
        }

        private void FixedUpdate()
        {
            float dt = Time.fixedDeltaTime;
            Grounded = ProbeGrounded();
            if (Grounded)
            {
                coyoteTimer = coyoteDuration;
                airJumps = 1;
            }
            else
            {
                coyoteTimer = Mathf.Max(0f, coyoteTimer - dt);
            }

            if (jumpPressed)
            {
                jumpBufferTimer = jumpBufferDuration;
            }
            else
            {
                jumpBufferTimer = Mathf.Max(0f, jumpBufferTimer - dt);
            }

            dashTimer = Mathf.Max(0f, dashTimer - dt);
            dashCooldown = Mathf.Max(0f, dashCooldown - dt);
            takeoffTimer = Mathf.Max(0f, takeoffTimer - dt);
            landingTimer = Mathf.Max(0f, landingTimer - dt);
            doubleJumpTimer = Mathf.Max(0f, doubleJumpTimer - dt);

            Vector2 velocity = body.linearVelocity;

            if (dashPressed && dashCooldown <= 0f)
            {
                dashTimer = dashDuration;
                dashCooldown = dashCooldownDuration;
                velocity.y = 0f;
            }

            if (jumpBufferTimer > 0f && !IsDashing)
            {
                if (coyoteTimer > 0f)
                {
                    velocity.y = jumpVelocity;
                    coyoteTimer = 0f;
                    jumpBufferTimer = 0f;
                    takeoffTimer = TakeoffDuration;
                    landingTimer = 0f;
                    Grounded = false;
                }
                else if (!Grounded && jumpPressed && airJumps > 0)
                {
                    velocity.y = doubleJumpVelocity;
                    airJumps--;
                    jumpBufferTimer = 0f;
                    doubleJumpTimer = DoubleJumpAnimDuration;
                    takeoffTimer = 0f;
                }
            }

            if (IsDashing)
            {
                velocity = new Vector2(Facing * dashSpeed, 0f);
            }
            else
            {
                float target = moveInput * CurrentMoveSpeed;
                float response = Grounded ? groundResponse : airResponse;
                velocity.x = Mathf.Lerp(velocity.x, target, Mathf.Clamp01(dt * response));

                float gravity = velocity.y > 0f ? ascentGravity : fallGravity;
                if (!jumpHeld && velocity.y > 1.8f)
                {
                    gravity += jumpCutGravity;
                }
                velocity.y = Mathf.Max(-maxFallSpeed, velocity.y - gravity * dt);
            }

            travelDistance += Mathf.Abs(velocity.x) * dt;
            body.linearVelocity = velocity;

            bool landed = !wasGrounded && Grounded;
            if (landed)
            {
                landingTimer = LandingDuration;
                takeoffTimer = 0f;
            }
            wasGrounded = Grounded;
            jumpPressed = false;
            dashPressed = false;
        }

        private bool ProbeGrounded()
        {
            int count = bodyCollider.Cast(Vector2.down, groundFilter, groundHits, groundProbeDistance);
            for (int i = 0; i < count; i++)
            {
                if (groundHits[i].collider != bodyCollider && groundHits[i].normal.y > 0.55f)
                {
                    return true;
                }
            }
            return false;
        }
    }
}
