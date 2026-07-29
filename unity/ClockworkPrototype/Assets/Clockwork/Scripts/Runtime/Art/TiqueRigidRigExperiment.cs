using UnityEngine;

namespace Clockwork
{
    [ExecuteAlways]
    public sealed class TiqueRigidRigExperiment : MonoBehaviour
    {
        public enum MotionMode
        {
            Idle,
            Walk
        }

        [SerializeField] private Transform body;
        [SerializeField] private Transform farArm;
        [SerializeField] private Transform nearArm;
        [SerializeField] private Transform farLeg;
        [SerializeField] private Transform nearLeg;

        private Vector3 bodyBase;
        private Vector3 farArmBase;
        private Vector3 nearArmBase;
        private Vector3 farLegBase;
        private Vector3 nearLegBase;
        private bool configured;

        public bool IsConfigured => configured;

        private void OnEnable()
        {
            CaptureBasePose();
        }

        public void Configure(
            Transform bodyTransform,
            Transform farArmTransform,
            Transform nearArmTransform,
            Transform farLegTransform,
            Transform nearLegTransform)
        {
            body = bodyTransform;
            farArm = farArmTransform;
            nearArm = nearArmTransform;
            farLeg = farLegTransform;
            nearLeg = nearLegTransform;
            CaptureBasePose();
        }

        public void SetManualPose(MotionMode mode, float normalizedTime)
        {
            if (!configured) CaptureBasePose();
            if (!configured) return;

            float phase = Mathf.Repeat(normalizedTime, 1f);
            // The baked result uses twelve held poses. Quantizing the live rig to the same
            // cadence prevents subpixel shimmer around Tique's very short limbs.
            phase = Mathf.Floor(phase * 12f) / 12f;
            ResetPose();

            if (mode == MotionMode.Walk)
                ApplyWalk(phase);
            else
                ApplyIdle(phase);
        }

        private void CaptureBasePose()
        {
            configured = body != null && farArm != null && nearArm != null
                && farLeg != null && nearLeg != null;
            if (!configured) return;

            bodyBase = body.localPosition;
            farArmBase = farArm.localPosition;
            nearArmBase = nearArm.localPosition;
            farLegBase = farLeg.localPosition;
            nearLegBase = nearLeg.localPosition;
        }

        private void ResetPose()
        {
            body.localPosition = bodyBase;
            farArm.localPosition = farArmBase;
            nearArm.localPosition = nearArmBase;
            farLeg.localPosition = farLegBase;
            nearLeg.localPosition = nearLegBase;
            body.localRotation = Quaternion.identity;
            farArm.localRotation = Quaternion.identity;
            nearArm.localRotation = Quaternion.identity;
            farLeg.localRotation = Quaternion.identity;
            nearLeg.localRotation = Quaternion.identity;
        }

        private void ApplyIdle(float phase)
        {
            float wave = Mathf.Sin(phase * Mathf.PI * 2f);
            body.localPosition = bodyBase + new Vector3(0f, wave * 0.012f, 0f);
            body.localRotation = Quaternion.Euler(0f, 0f, wave * 0.35f);
            farArm.localRotation = Quaternion.Euler(0f, 0f, wave * 1.4f);
            nearArm.localRotation = Quaternion.Euler(0f, 0f, -wave * 1.8f);
        }

        private void ApplyWalk(float phase)
        {
            float wave = Mathf.Sin(phase * Mathf.PI * 2f);
            float stride = Mathf.Cos(phase * Mathf.PI * 2f);
            float nearLift = Mathf.Max(0f, wave);
            float farLift = Mathf.Max(0f, -wave);

            // Tique's stride reads through weight transfer and foot lift, not stretched legs.
            body.localPosition = bodyBase + new Vector3(
                Mathf.Sin(phase * Mathf.PI * 4f) * 0.008f,
                Mathf.Abs(wave) * 0.032f,
                0f);
            body.localRotation = Quaternion.Euler(0f, 0f, -wave * 1.15f);

            nearLeg.localPosition = nearLegBase + new Vector3(0f, nearLift * 0.055f, 0f);
            farLeg.localPosition = farLegBase + new Vector3(0f, farLift * 0.045f, 0f);
            nearLeg.localRotation = Quaternion.Euler(0f, 0f, stride * 11f);
            farLeg.localRotation = Quaternion.Euler(0f, 0f, -stride * 10f);

            nearArm.localRotation = Quaternion.Euler(0f, 0f, -stride * 8f);
            farArm.localRotation = Quaternion.Euler(0f, 0f, stride * 7f);
        }
    }
}
