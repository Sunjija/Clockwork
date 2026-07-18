using UnityEngine;

namespace Clockwork
{
    [CreateAssetMenu(menuName = "Clockwork/Attack Definition")]
    public sealed class AttackDefinition : ScriptableObject
    {
        [SerializeField] private string attackId;
        [SerializeField] private string displayName;
        [SerializeField] private SpriteSequence sequence;
        [SerializeField] private float duration = 0.4f;
        [SerializeField, Range(0f, 1f)] private float activeStart = 0.3f;
        [SerializeField, Range(0f, 1f)] private float activeEnd = 0.6f;
        [SerializeField] private Vector2 hitboxCenter;
        [SerializeField] private Vector2 hitboxSize = Vector2.one;
        [SerializeField] private Color trailColor = Color.white;

        public string AttackId => attackId;
        public string DisplayName => displayName;
        public SpriteSequence Sequence => sequence;
        public float Duration => Mathf.Max(0.01f, duration);
        public float ActiveStart => activeStart;
        public float ActiveEnd => activeEnd;
        public Vector2 HitboxCenter => hitboxCenter;
        public Vector2 HitboxSize => hitboxSize;
        public Color TrailColor => trailColor;

        public bool IsActiveAt(float normalizedTime)
        {
            return normalizedTime >= activeStart && normalizedTime <= activeEnd;
        }

#if UNITY_EDITOR
        public void Configure(
            string id,
            string label,
            SpriteSequence animation,
            float clipDuration,
            float windowStart,
            float windowEnd,
            Vector2 center,
            Vector2 size,
            Color color)
        {
            attackId = id;
            displayName = label;
            sequence = animation;
            duration = clipDuration;
            activeStart = windowStart;
            activeEnd = windowEnd;
            hitboxCenter = center;
            hitboxSize = size;
            trailColor = color;
        }
#endif
    }
}

