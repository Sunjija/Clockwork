using UnityEngine;

namespace Clockwork
{
    public sealed class RegisteredRouteCameraFollow2D : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private float minimumX;
        [SerializeField] private float maximumX = 10f;
        [SerializeField] private float fixedY;
        [SerializeField] private float horizontalDeadZone = 3.75f;
        [SerializeField] private float pixelsPerUnit = 64f;
        [SerializeField] private bool smoothTracking;
        [SerializeField] private float lookAheadDistance = 0.85f;
        [SerializeField] private float lookAheadSmoothTime = 0.12f;
        [SerializeField] private float followSmoothTime = 0.16f;
        [SerializeField] private float maximumFollowSpeed = 10f;

        private TiqueMotor targetMotor;
        private float smoothX;
        private float followVelocity;
        private float currentLookAhead;
        private float lookAheadVelocity;
        private bool initialized;

        public Transform Target => target;
        public float MinimumX => minimumX;
        public float MaximumX => maximumX;
        public float HorizontalDeadZone => horizontalDeadZone;
        public bool SmoothTracking => smoothTracking;
        public float LookAheadDistance => lookAheadDistance;
        public float FollowSmoothTime => followSmoothTime;

        public void Configure(
            Transform followTarget, float minX, float maxX, float y,
            float deadZone, float snapPixelsPerUnit)
        {
            target = followTarget;
            minimumX = minX;
            maximumX = maxX;
            fixedY = y;
            horizontalDeadZone = Mathf.Max(0f, deadZone);
            pixelsPerUnit = Mathf.Max(1f, snapPixelsPerUnit);
            smoothTracking = false;
            InitializeTracking();
        }

        public void ConfigureSmooth(
            Transform followTarget, float minX, float maxX, float y,
            float deadZone, float snapPixelsPerUnit, float lookAhead,
            float smoothTime, float maxSpeed)
        {
            Configure(followTarget, minX, maxX, y, deadZone, snapPixelsPerUnit);
            smoothTracking = true;
            lookAheadDistance = Mathf.Max(0f, lookAhead);
            followSmoothTime = Mathf.Max(0.01f, smoothTime);
            maximumFollowSpeed = Mathf.Max(0.01f, maxSpeed);
            InitializeTracking();
        }

        private void OnEnable()
        {
            InitializeTracking();
        }

        private void InitializeTracking()
        {
            targetMotor = target == null ? null : target.GetComponent<TiqueMotor>();
            smoothX = transform.position.x;
            followVelocity = 0f;
            currentLookAhead = 0f;
            lookAheadVelocity = 0f;
            initialized = true;
        }

        private void LateUpdate()
        {
            if (target == null) return;

            if (!initialized) InitializeTracking();

            if (!smoothTracking)
            {
                FollowLegacy();
                return;
            }

            float renderedX = Mathf.Round(smoothX * pixelsPerUnit) / pixelsPerUnit;
            if (Mathf.Abs(transform.position.x - renderedX) > 0.05f)
            {
                smoothX = transform.position.x;
                followVelocity = 0f;
            }

            float direction = targetMotor == null || Mathf.Abs(targetMotor.HorizontalSpeed) < 0.05f
                ? 0f
                : Mathf.Sign(targetMotor.HorizontalSpeed);
            currentLookAhead = Mathf.SmoothDamp(
                currentLookAhead, direction * lookAheadDistance,
                ref lookAheadVelocity, lookAheadSmoothTime,
                Mathf.Infinity, Time.unscaledDeltaTime);

            float focusX = target.position.x + currentLookAhead;
            float desiredX = smoothX;
            if (focusX > smoothX + horizontalDeadZone)
                desiredX = focusX - horizontalDeadZone;
            else if (focusX < smoothX - horizontalDeadZone)
                desiredX = focusX + horizontalDeadZone;

            desiredX = Mathf.Clamp(desiredX, minimumX, maximumX);
            smoothX = Mathf.SmoothDamp(
                smoothX, desiredX, ref followVelocity, followSmoothTime,
                maximumFollowSpeed, Time.unscaledDeltaTime);
            smoothX = Mathf.Clamp(smoothX, minimumX, maximumX);

            float snappedX = Mathf.Round(smoothX * pixelsPerUnit) / pixelsPerUnit;
            transform.position = new Vector3(snappedX, fixedY, transform.position.z);
        }

        private void FollowLegacy()
        {
            float x = transform.position.x;
            if (target.position.x > x + horizontalDeadZone)
                x = target.position.x - horizontalDeadZone;
            else if (target.position.x < x - horizontalDeadZone)
                x = target.position.x + horizontalDeadZone;

            x = Mathf.Clamp(x, minimumX, maximumX);
            x = Mathf.Round(x * pixelsPerUnit) / pixelsPerUnit;
            transform.position = new Vector3(x, fixedY, transform.position.z);
        }
    }
}
