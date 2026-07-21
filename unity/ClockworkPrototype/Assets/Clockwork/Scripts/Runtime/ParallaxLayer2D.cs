using UnityEngine;

namespace Clockwork
{
    public sealed class ParallaxLayer2D : MonoBehaviour
    {
        [SerializeField] private Camera trackingCamera;
        [SerializeField, Range(0f, 1f)] private float horizontalFactor;
        [SerializeField, Range(0f, 1f)] private float verticalFactor;

        private Vector3 layerOrigin;
        private Vector3 cameraOrigin;

        public float HorizontalFactor => horizontalFactor;
        public float VerticalFactor => verticalFactor;

        private void Awake()
        {
            CaptureOrigins();
        }

        private void LateUpdate()
        {
            if (trackingCamera == null) trackingCamera = Camera.main;
            if (trackingCamera == null) return;

            Vector3 cameraDelta = trackingCamera.transform.position - cameraOrigin;
            transform.position = layerOrigin + new Vector3(
                cameraDelta.x * horizontalFactor,
                cameraDelta.y * verticalFactor,
                0f);
        }

        public void Configure(Camera camera, float horizontal, float vertical)
        {
            trackingCamera = camera;
            horizontalFactor = Mathf.Clamp01(horizontal);
            verticalFactor = Mathf.Clamp01(vertical);
            CaptureOrigins();
        }

        private void CaptureOrigins()
        {
            if (trackingCamera == null) trackingCamera = Camera.main;
            layerOrigin = transform.position;
            cameraOrigin = trackingCamera == null ? Vector3.zero : trackingCamera.transform.position;
        }
    }
}
