using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(Rigidbody2D), typeof(Collider2D), typeof(EnemyHealth))]
    public sealed class RatEnemy : MonoBehaviour
    {
        [SerializeField] private float moveSpeed = 0.95f;
        [SerializeField] private float gravity = 26f;
        [SerializeField] private float maxFallSpeed = 8f;
        [SerializeField] private int contactDamage = 1;
        [SerializeField] private int startDirection = -1;
        [SerializeField] private float wallProbeDistance = 0.06f;
        [SerializeField] private float ledgeProbeDepth = 0.35f;

        private readonly RaycastHit2D[] probeHits = new RaycastHit2D[4];
        private Rigidbody2D body;
        private Collider2D bodyCollider;
        private SpriteRenderer spriteRenderer;
        private ContactFilter2D solidFilter;
        private int direction;

        private void Awake()
        {
            body = GetComponent<Rigidbody2D>();
            bodyCollider = GetComponent<Collider2D>();
            spriteRenderer = GetComponentInChildren<SpriteRenderer>();
            direction = startDirection >= 0 ? 1 : -1;
            solidFilter = new ContactFilter2D
            {
                useTriggers = false,
                useLayerMask = true,
                layerMask = Physics2D.AllLayers
            };
        }

        private void FixedUpdate()
        {
            float dt = Time.fixedDeltaTime;
            bool grounded = ProbeGrounded();
            if (grounded && (HitsWallAhead() || !HasGroundAhead()))
            {
                direction = -direction;
            }

            Vector2 velocity = body.linearVelocity;
            velocity.x = direction * moveSpeed;
            velocity.y = Mathf.Max(-maxFallSpeed, velocity.y - gravity * dt);
            body.linearVelocity = velocity;

            if (spriteRenderer != null)
            {
                spriteRenderer.flipX = direction > 0;
            }
        }

        private void OnCollisionStay2D(Collision2D collision)
        {
            TiqueHealth player = collision.collider.GetComponentInParent<TiqueHealth>();
            if (player != null)
            {
                player.TakeDamage(contactDamage, transform.position);
            }
        }

        private bool ProbeGrounded()
        {
            int count = bodyCollider.Cast(Vector2.down, solidFilter, probeHits, 0.05f);
            for (int i = 0; i < count; i++)
            {
                if (probeHits[i].collider != bodyCollider && probeHits[i].normal.y > 0.55f)
                {
                    return true;
                }
            }
            return false;
        }

        private bool HitsWallAhead()
        {
            int count = bodyCollider.Cast(new Vector2(direction, 0f), solidFilter, probeHits, wallProbeDistance);
            for (int i = 0; i < count; i++)
            {
                RaycastHit2D hit = probeHits[i];
                if (hit.collider == bodyCollider) continue;
                // Ignore the player: contact damage handles that collision instead of turning around.
                if (hit.collider.GetComponentInParent<TiqueHealth>() != null) continue;
                if (Mathf.Abs(hit.normal.x) > 0.55f) return true;
            }
            return false;
        }

        private bool HasGroundAhead()
        {
            Bounds bounds = bodyCollider.bounds;
            Vector2 origin = new Vector2(
                direction > 0 ? bounds.max.x + 0.04f : bounds.min.x - 0.04f,
                bounds.min.y + 0.02f);
            RaycastHit2D hit = Physics2D.Raycast(origin, Vector2.down, ledgeProbeDepth);
            return hit.collider != null && !hit.collider.isTrigger;
        }

#if UNITY_EDITOR
        public void Configure(int patrolDirection, float speed)
        {
            startDirection = patrolDirection;
            moveSpeed = speed;
        }
#endif
    }
}
