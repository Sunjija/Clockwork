using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueMotor))]
    public sealed class TiqueProgression : MonoBehaviour
    {
        private TiqueMotor motor;

        private void Awake()
        {
            motor = GetComponent<TiqueMotor>();
        }

        private void Start()
        {
            if (GameSession.Instance == null) return;
            GameSession.Instance.FlagChanged += OnFlagChanged;
            ApplyRepairState(GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired));
        }

        private void OnDestroy()
        {
            if (GameSession.Instance != null)
            {
                GameSession.Instance.FlagChanged -= OnFlagChanged;
            }
        }

        private void OnFlagChanged(string flagId, bool value)
        {
            if (flagId == GameFlagIds.TiqueRepaired)
            {
                ApplyRepairState(value);
            }
        }

        private void ApplyRepairState(bool repaired)
        {
            motor.SetDamagedState(!repaired);
        }
    }
}
