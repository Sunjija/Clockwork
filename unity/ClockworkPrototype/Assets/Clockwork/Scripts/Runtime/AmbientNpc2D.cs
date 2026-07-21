using UnityEngine;

namespace Clockwork
{
    public sealed class AmbientNpc2D : MonoBehaviour
    {
        [SerializeField] private SpriteRenderer spriteRenderer;
        [SerializeField] private Sprite[] idleFrames;
        [SerializeField] private Sprite[] roleFrames;
        [SerializeField] private float idleFps = 4f;
        [SerializeField] private float roleFps = 6f;
        [SerializeField] private float roleIntervalMin = 3.5f;
        [SerializeField] private float roleIntervalMax = 6f;
        [SerializeField] private bool patrol;
        [SerializeField] private float patrolDistance = 0.75f;
        [SerializeField] private float patrolSpeed = 0.32f;

        private Vector3 origin;
        private float stateStartedAt;
        private float nextRoleAt;
        private float patrolWait;
        private int patrolDirection = 1;
        private bool playingRole;

        public bool IsPatrolling => patrol;
        public int IdleFrameCount => idleFrames == null ? 0 : idleFrames.Length;
        public int RoleFrameCount => roleFrames == null ? 0 : roleFrames.Length;

        public void Configure(
            SpriteRenderer targetRenderer,
            Sprite[] idle,
            Sprite[] role,
            float idleFramesPerSecond,
            float roleFramesPerSecond,
            float minimumRoleInterval,
            float maximumRoleInterval,
            bool usesPatrol,
            float distance,
            float speed)
        {
            spriteRenderer = targetRenderer;
            idleFrames = idle;
            roleFrames = role;
            idleFps = Mathf.Max(1f, idleFramesPerSecond);
            roleFps = Mathf.Max(1f, roleFramesPerSecond);
            roleIntervalMin = Mathf.Max(0.5f, minimumRoleInterval);
            roleIntervalMax = Mathf.Max(roleIntervalMin, maximumRoleInterval);
            patrol = usesPatrol;
            patrolDistance = Mathf.Max(0f, distance);
            patrolSpeed = Mathf.Max(0.01f, speed);
        }

        private void Awake()
        {
            origin = transform.position;
            stateStartedAt = Time.time;
            ScheduleRole();
            ApplyFrame(idleFrames, idleFps, true);
        }

        private void Update()
        {
            if (spriteRenderer == null) return;

            if (patrol)
            {
                UpdatePatrol();
            }
            else
            {
                UpdateWorkLoop();
            }
        }

        private void UpdateWorkLoop()
        {
            if (!playingRole && Time.time >= nextRoleAt && HasFrames(roleFrames))
            {
                playingRole = true;
                stateStartedAt = Time.time;
            }

            if (playingRole)
            {
                float duration = roleFrames.Length / roleFps;
                if (Time.time - stateStartedAt >= duration)
                {
                    playingRole = false;
                    stateStartedAt = Time.time;
                    ScheduleRole();
                }
            }

            ApplyFrame(playingRole ? roleFrames : idleFrames, playingRole ? roleFps : idleFps, !playingRole);
        }

        private void UpdatePatrol()
        {
            if (patrolWait > 0f)
            {
                patrolWait -= Time.deltaTime;
                ApplyFrame(idleFrames, idleFps, true);
                return;
            }

            Vector3 position = transform.position;
            position.x += patrolDirection * patrolSpeed * Time.deltaTime;
            float minimum = origin.x - patrolDistance;
            float maximum = origin.x + patrolDistance;
            if (position.x <= minimum || position.x >= maximum)
            {
                position.x = Mathf.Clamp(position.x, minimum, maximum);
                patrolDirection *= -1;
                patrolWait = 1.1f + Mathf.Abs(GetEntityId().GetHashCode() % 7) * 0.11f;
                stateStartedAt = Time.time;
            }

            transform.position = position;
            spriteRenderer.flipX = patrolDirection < 0;
            ApplyFrame(roleFrames, roleFps, true);
        }

        private void ApplyFrame(Sprite[] frames, float fps, bool loop)
        {
            if (!HasFrames(frames)) return;
            int index = Mathf.FloorToInt((Time.time - stateStartedAt) * fps);
            index = loop ? index % frames.Length : Mathf.Min(index, frames.Length - 1);
            spriteRenderer.sprite = frames[index];
        }

        private void ScheduleRole()
        {
            float phase = Mathf.Abs(GetEntityId().GetHashCode() % 100) / 100f;
            nextRoleAt = Time.time + Mathf.Lerp(roleIntervalMin, roleIntervalMax, phase);
        }

        private static bool HasFrames(Sprite[] frames)
        {
            return frames != null && frames.Length > 0;
        }
    }
}
