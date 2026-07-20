using UnityEngine;

namespace Clockwork
{
    [DefaultExecutionOrder(100)]
    [RequireComponent(typeof(Rigidbody2D), typeof(TiqueInputReader))]
    public sealed class TiqueGrapple : MonoBehaviour
    {
        [SerializeField] private LineRenderer ropeRenderer;
        [SerializeField] private float maxAttachDistance = 5.5f;
        [SerializeField] private float minimumRopeLength = 1.25f;
        [SerializeField] private float ropeTravelDuration = 0.1f;
        [SerializeField] private float reelRatio = 0.88f;
        [SerializeField] private float reelSpeed = 3.2f;
        [SerializeField] private float springStrength = 34f;
        [SerializeField] private float constraintDamping = 12f;
        [SerializeField] private float swingAcceleration = 8f;
        [SerializeField] private float allowedStretch = 0.16f;
        [SerializeField] private float maxPositionCorrection = 0.08f;

        private Rigidbody2D body;
        private TiqueInputReader input;
        private GrappleAnchor anchor;
        private float ropeLength;
        private float targetRopeLength;
        private float ropeTravelTimer;
        private Vector2 ropeTravelStart;

        public bool IsAttached => anchor != null;
        public GrappleAnchor CurrentAnchor => anchor;
        public float RopeLength => ropeLength;
        public bool IsTensioned => IsAttached && ropeTravelTimer <= 0f;

        private void Awake()
        {
            body = GetComponent<Rigidbody2D>();
            input = GetComponent<TiqueInputReader>();
            SetRopeVisible(false);
        }

        private void OnDisable()
        {
            Release();
        }

        private void Update()
        {
            if (input.GrapplePressed && !IsAttached)
            {
                TryAttach(FindBestAnchor());
            }
            if (input.GrappleReleased)
            {
                Release();
            }
            if (IsAttached && GetComponent<TiqueMotor>().IsDashing)
            {
                Release();
            }
            UpdateRopeView();
        }

        private void FixedUpdate()
        {
            if (!IsAttached) return;

            if (ropeTravelTimer > 0f)
            {
                ropeTravelTimer = Mathf.Max(0f, ropeTravelTimer - Time.fixedDeltaTime);
                return;
            }

            Vector2 anchorPosition = anchor.transform.position;
            Vector2 delta = body.position - anchorPosition;
            float distance = delta.magnitude;
            if (distance <= 0.001f) return;

            Vector2 outward = delta / distance;
            ropeLength = Mathf.MoveTowards(ropeLength, targetRopeLength, reelSpeed * Time.fixedDeltaTime);
            float stretch = Mathf.Max(0f, distance - ropeLength);
            Vector2 velocity = body.linearVelocity;
            if (stretch > 0f)
            {
                float inwardAcceleration = Mathf.Min(32f, stretch * springStrength);
                velocity -= outward * inwardAcceleration * Time.fixedDeltaTime;

                float outwardSpeed = Vector2.Dot(velocity, outward);
                if (outwardSpeed > 0f)
                {
                    float damping = 1f - Mathf.Exp(-constraintDamping * Time.fixedDeltaTime);
                    velocity -= outward * outwardSpeed * damping;
                }

                float excess = stretch - allowedStretch;
                if (excess > 0f)
                {
                    body.position -= outward * Mathf.Min(excess, maxPositionCorrection);
                }
            }

            Vector2 tangent = new Vector2(-outward.y, outward.x);
            float horizontalSign = Mathf.Abs(tangent.x) < 0.01f ? 1f : Mathf.Sign(tangent.x);
            velocity += tangent * (input.Move * horizontalSign * swingAcceleration * Time.fixedDeltaTime);
            body.linearVelocity = velocity;
        }

        public bool TryAttach(GrappleAnchor target)
        {
            if (!isActiveAndEnabled || target == null) return false;
            float distance = Vector2.Distance(body.position, target.transform.position);
            if (distance > maxAttachDistance) return false;

            anchor = target;
            ropeLength = Mathf.Max(minimumRopeLength, distance);
            targetRopeLength = Mathf.Max(minimumRopeLength, distance * reelRatio);
            ropeTravelTimer = ropeTravelDuration;
            ropeTravelStart = transform.position + Vector3.up * 0.42f;
            SetRopeVisible(true);
            UpdateRopeView();
            return true;
        }

        public void Release()
        {
            anchor = null;
            ropeLength = 0f;
            targetRopeLength = 0f;
            ropeTravelTimer = 0f;
            SetRopeVisible(false);
        }

        private GrappleAnchor FindBestAnchor()
        {
            GrappleAnchor best = null;
            float bestScore = float.NegativeInfinity;
            GrappleAnchor[] anchors = FindObjectsByType<GrappleAnchor>(FindObjectsSortMode.None);
            foreach (GrappleAnchor candidate in anchors)
            {
                float distance = Vector2.Distance(body.position, candidate.transform.position);
                if (distance > maxAttachDistance) continue;
                float heightBonus = Mathf.Max(0f, candidate.transform.position.y - body.position.y) * 0.35f;
                float score = candidate.SelectionPriority + heightBonus - distance;
                if (score > bestScore)
                {
                    bestScore = score;
                    best = candidate;
                }
            }
            return best;
        }

        private void UpdateRopeView()
        {
            if (ropeRenderer == null || !IsAttached) return;
            ropeRenderer.positionCount = 2;
            ropeRenderer.SetPosition(0, transform.position + Vector3.up * 0.42f);
            float progress = ropeTravelDuration <= 0f
                ? 1f
                : 1f - Mathf.Clamp01(ropeTravelTimer / ropeTravelDuration);
            ropeRenderer.SetPosition(1, Vector2.Lerp(ropeTravelStart, anchor.transform.position, progress));
        }

        private void SetRopeVisible(bool visible)
        {
            if (ropeRenderer != null) ropeRenderer.enabled = visible;
        }

#if UNITY_EDITOR
        public void Configure(LineRenderer renderer, float attachDistance)
        {
            ropeRenderer = renderer;
            maxAttachDistance = attachDistance;
        }
#endif
    }
}
