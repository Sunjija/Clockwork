using System;
using UnityEngine;

namespace Clockwork
{
    [Serializable]
    public sealed class ComboStep
    {
        [SerializeField] private AttackDefinition attack;
        [SerializeField, Range(0f, 1f)] private float queueStart = 0.3f;
        [SerializeField, Range(0f, 1f)] private float queueEnd = 0.9f;

        public AttackDefinition Attack => attack;

        public bool CanQueueAt(float normalizedTime)
        {
            return normalizedTime >= queueStart && normalizedTime <= queueEnd;
        }

#if UNITY_EDITOR
        public void Configure(AttackDefinition stepAttack, float windowStart, float windowEnd)
        {
            attack = stepAttack;
            queueStart = Mathf.Clamp01(windowStart);
            queueEnd = Mathf.Clamp(windowEnd, queueStart, 1f);
        }
#endif
    }

    [CreateAssetMenu(menuName = "Clockwork/Combo Definition")]
    public sealed class ComboDefinition : ScriptableObject
    {
        [SerializeField] private string comboId;
        [SerializeField] private string displayName;
        [SerializeField] private ComboStep[] steps = Array.Empty<ComboStep>();
        [SerializeField] private bool cyclesAcrossInputs;

        public string ComboId => comboId;
        public string DisplayName => displayName;
        public int StepCount => steps?.Length ?? 0;
        public bool CyclesAcrossInputs => cyclesAcrossInputs;

        public ComboStep StepAt(int index)
        {
            return StepCount == 0 ? null : steps[Mathf.Clamp(index, 0, StepCount - 1)];
        }

#if UNITY_EDITOR
        public void Configure(
            string id,
            string label,
            AttackDefinition[] stepAttacks,
            float queueStart,
            float queueEnd,
            bool shouldCycleAcrossInputs = false)
        {
            comboId = id;
            displayName = label;
            cyclesAcrossInputs = shouldCycleAcrossInputs;
            steps = new ComboStep[stepAttacks?.Length ?? 0];
            for (int i = 0; i < steps.Length; i++)
            {
                steps[i] = new ComboStep();
                steps[i].Configure(stepAttacks[i], queueStart, queueEnd);
            }
        }
#endif
    }
}
