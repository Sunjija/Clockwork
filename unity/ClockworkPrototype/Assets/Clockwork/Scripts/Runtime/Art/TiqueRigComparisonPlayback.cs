using UnityEngine;

namespace Clockwork
{
    public sealed class TiqueRigComparisonPlayback : MonoBehaviour
    {
        [SerializeField] private SpriteRenderer approvedRenderer;
        [SerializeField] private SpriteRenderer bakedRenderer;
        [SerializeField] private TiqueRigidRigExperiment liveRig;
        [SerializeField] private Sprite[] approvedIdle;
        [SerializeField] private Sprite[] approvedWalk;
        [SerializeField] private Sprite[] bakedIdle;
        [SerializeField] private Sprite[] bakedWalk;

        private bool probeWalk;

        public int ApprovedWalkFrameCount => approvedWalk == null ? 0 : approvedWalk.Length;
        public int BakedWalkFrameCount => bakedWalk == null ? 0 : bakedWalk.Length;
        public TiqueRigidRigExperiment LiveRig => liveRig;

        private void Update()
        {
            float elapsed = Time.unscaledTime;
            bool walking = probeWalk || Mathf.Repeat(elapsed, 6f) >= 2f;
            float normalized = walking
                ? Mathf.Repeat(elapsed / 0.72f, 1f)
                : Mathf.Repeat(elapsed / 1.6f, 1f);

            Sprite[] approved = walking ? approvedWalk : approvedIdle;
            Sprite[] baked = walking ? bakedWalk : bakedIdle;
            approvedRenderer.sprite = FrameAt(approved, normalized);
            bakedRenderer.sprite = FrameAt(baked, normalized);
            liveRig.SetManualPose(
                walking ? TiqueRigidRigExperiment.MotionMode.Walk
                    : TiqueRigidRigExperiment.MotionMode.Idle,
                normalized);
        }

        public void Configure(
            SpriteRenderer approved,
            SpriteRenderer baked,
            TiqueRigidRigExperiment rig,
            Sprite[] approvedIdleFrames,
            Sprite[] approvedWalkFrames,
            Sprite[] bakedIdleFrames,
            Sprite[] bakedWalkFrames)
        {
            approvedRenderer = approved;
            bakedRenderer = baked;
            liveRig = rig;
            approvedIdle = approvedIdleFrames;
            approvedWalk = approvedWalkFrames;
            bakedIdle = bakedIdleFrames;
            bakedWalk = bakedWalkFrames;
        }

        public void SetProbeWalk(bool enabled)
        {
            probeWalk = enabled;
        }

        private static Sprite FrameAt(Sprite[] frames, float normalized)
        {
            if (frames == null || frames.Length == 0) return null;
            int index = Mathf.Min(frames.Length - 1,
                Mathf.FloorToInt(Mathf.Repeat(normalized, 1f) * frames.Length));
            return frames[index];
        }
    }
}
