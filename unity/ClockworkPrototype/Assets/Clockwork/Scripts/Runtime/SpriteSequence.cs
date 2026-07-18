using UnityEngine;

namespace Clockwork
{
    [CreateAssetMenu(menuName = "Clockwork/Sprite Sequence")]
    public sealed class SpriteSequence : ScriptableObject
    {
        [SerializeField] private Sprite[] frames;
        [SerializeField] private float[] normalizedFrameEnds;
        [SerializeField] private float duration = 0.5f;
        [SerializeField] private bool loop;
        [SerializeField] private float renderScale = 0.3f;

        public float Duration => Mathf.Max(0.01f, duration);
        public bool Loop => loop;
        public float RenderScale => renderScale;
        public int FrameCount => frames == null ? 0 : frames.Length;

        public Sprite FrameAt(float normalizedTime)
        {
            if (frames == null || frames.Length == 0)
            {
                return null;
            }

            float time = loop ? Mathf.Repeat(normalizedTime, 1f) : Mathf.Clamp01(normalizedTime);
            if (normalizedFrameEnds != null && normalizedFrameEnds.Length == frames.Length)
            {
                for (int i = 0; i < normalizedFrameEnds.Length; i++)
                {
                    if (time <= normalizedFrameEnds[i])
                    {
                        return frames[i];
                    }
                }
            }

            int index = Mathf.Min(frames.Length - 1, Mathf.FloorToInt(time * frames.Length));
            return frames[index];
        }

#if UNITY_EDITOR
        public void Configure(Sprite[] sourceFrames, float[] frameEnds, float clipDuration, bool shouldLoop, float scale)
        {
            frames = sourceFrames;
            normalizedFrameEnds = frameEnds;
            duration = clipDuration;
            loop = shouldLoop;
            renderScale = scale;
        }
#endif
    }
}

