using UnityEngine;

namespace Clockwork
{
    // First MOD treasure (v5.5 B-3): an unidentified part picked up in Limbus.
    // Identification/attachment by Morbi happens later in the Caligo workshop scene.
    public sealed class MysteryPartPickup : MonoBehaviour
    {
        [SerializeField] private SpriteRenderer indicator;

        private TiqueInputReader nearbyInput;

        public bool PlayerNearby => nearbyInput != null;
        public bool Collected => GameSession.Instance != null
            && GameSession.Instance.HasFlag(GameFlagIds.LimbusMysteryPart);

        private void Start()
        {
            if (Collected) DimIndicator();
        }

        private void Update()
        {
            if (!Collected && nearbyInput != null && nearbyInput.InteractPressed)
            {
                Collect();
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            TiqueMotor motor = other.GetComponentInParent<TiqueMotor>();
            if (motor != null)
            {
                nearbyInput = motor.GetComponent<TiqueInputReader>();
            }
        }

        private void OnTriggerExit2D(Collider2D other)
        {
            if (other.GetComponentInParent<TiqueMotor>() != null)
            {
                nearbyInput = null;
            }
        }

        public void Collect()
        {
            if (GameSession.Instance == null || Collected) return;
            GameSession.Instance.SetFlag(GameFlagIds.LimbusMysteryPart, true);
            DimIndicator();
        }

        private void DimIndicator()
        {
            if (indicator != null)
            {
                indicator.color = new Color(0.35f, 0.32f, 0.4f, 0.45f);
            }
        }

#if UNITY_EDITOR
        public void Configure(SpriteRenderer targetIndicator)
        {
            indicator = targetIndicator;
        }
#endif
    }
}
