using System;
using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueCombat))]
    public sealed class TiqueEnergyGauge : MonoBehaviour
    {
        [SerializeField] private float maxEnergy = 100f;
        [SerializeField] private float energyPerSegment = 5f;
        [SerializeField] private float energyPerHit = 5f;
        [SerializeField] private float defeatBonus = 5f;

        private TiqueCombat combat;

        public float CurrentEnergy { get; private set; }
        public float MaxEnergy => maxEnergy;
        public float EnergyPerSegment => energyPerSegment;
        public int SegmentCount => Mathf.Max(1, Mathf.RoundToInt(maxEnergy / energyPerSegment));
        public int FilledSegmentCount => Mathf.Clamp(
            Mathf.FloorToInt(CurrentEnergy / energyPerSegment), 0, SegmentCount);
        public event Action<float, float> EnergyChanged;

        public bool CanSpend(float amount)
        {
            return amount <= 0f || CurrentEnergy >= amount;
        }

        private void Awake()
        {
            combat = GetComponent<TiqueCombat>();
        }

        private void OnEnable()
        {
            if (combat != null) combat.AttackLanded += OnAttackLanded;
        }

        private void Start()
        {
            GameSession session = GameSession.Instance;
            CurrentEnergy = session != null && session.RuntimeEnergy >= 0f
                ? Mathf.Min(session.RuntimeEnergy, maxEnergy)
                : 0f;
            StoreEnergy();
        }

        private void OnDisable()
        {
            if (combat != null) combat.AttackLanded -= OnAttackLanded;
        }

        public bool TrySpend(float amount)
        {
            if (amount <= 0f || !CanSpend(amount)) return false;
            SetEnergy(CurrentEnergy - amount);
            return true;
        }

        private void OnAttackLanded(CombatHitResult hit)
        {
            SetEnergy(CurrentEnergy + energyPerHit + (hit.Defeated ? defeatBonus : 0f));
        }

        private void SetEnergy(float value)
        {
            float next = Mathf.Clamp(value, 0f, maxEnergy);
            if (Mathf.Approximately(next, CurrentEnergy)) return;
            CurrentEnergy = next;
            StoreEnergy();
            EnergyChanged?.Invoke(CurrentEnergy, maxEnergy);
        }

        private void StoreEnergy()
        {
            if (GameSession.Instance != null)
            {
                GameSession.Instance.RuntimeEnergy = CurrentEnergy;
            }
        }
    }
}
