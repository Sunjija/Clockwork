using System;
using UnityEngine;

namespace Clockwork
{
    [Serializable]
    public sealed class WeaponTransitionDefinition
    {
        [SerializeField] private string targetWeaponId;
        [SerializeField] private ComboDefinition combo;
        [SerializeField] private float lentiumCost;

        public string TargetWeaponId => targetWeaponId;
        public ComboDefinition Combo => combo;
        public float LentiumCost => Mathf.Max(0f, lentiumCost);

#if UNITY_EDITOR
        public void Configure(string targetId, ComboDefinition transitionCombo, float energyCost)
        {
            targetWeaponId = targetId;
            combo = transitionCombo;
            lentiumCost = Mathf.Max(0f, energyCost);
        }
#endif
    }

    [CreateAssetMenu(menuName = "Clockwork/Weapon Definition")]
    public sealed class WeaponDefinition : ScriptableObject
    {
        [SerializeField] private string weaponId;
        [SerializeField] private string displayName;
        [SerializeField] private ComboDefinition basicCombo;
        [SerializeField] private WeaponTransitionDefinition[] transitions =
            Array.Empty<WeaponTransitionDefinition>();

        public string WeaponId => weaponId;
        public string DisplayName => displayName;
        public ComboDefinition BasicCombo => basicCombo;
        public bool HasTransitions => transitions != null && transitions.Length > 0;

        public bool TryGetTransition(
            string targetWeaponId, out ComboDefinition transitionCombo, out float lentiumCost)
        {
            foreach (WeaponTransitionDefinition transition in transitions)
            {
                if (transition != null && transition.TargetWeaponId == targetWeaponId
                    && transition.Combo != null)
                {
                    transitionCombo = transition.Combo;
                    lentiumCost = transition.LentiumCost;
                    return true;
                }
            }

            transitionCombo = null;
            lentiumCost = 0f;
            return false;
        }

#if UNITY_EDITOR
        public void Configure(
            string id,
            string label,
            ComboDefinition combo,
            string[] transitionTargetIds,
            ComboDefinition[] transitionCombos,
            float[] transitionEnergyCosts)
        {
            weaponId = id;
            displayName = label;
            basicCombo = combo;
            int count = Mathf.Min(transitionTargetIds?.Length ?? 0, transitionCombos?.Length ?? 0);
            transitions = new WeaponTransitionDefinition[count];
            for (int i = 0; i < count; i++)
            {
                transitions[i] = new WeaponTransitionDefinition();
                float energyCost = i < (transitionEnergyCosts?.Length ?? 0)
                    ? transitionEnergyCosts[i]
                    : 0f;
                transitions[i].Configure(transitionTargetIds[i], transitionCombos[i], energyCost);
            }
        }
#endif
    }
}
