using UnityEngine;

namespace Clockwork
{
    public sealed class RepairSavePoint : MonoBehaviour
    {
        [SerializeField] private string roomId = "caligo-maintenance-shaft";
        [SerializeField] private string spawnId = "caligo-workbench";
        [SerializeField] private SpriteRenderer indicator;

        private TiqueInputReader nearbyInput;
        public bool PlayerNearby => nearbyInput != null;
        public bool Activated { get; private set; }

        private void Update()
        {
            if (nearbyInput != null && nearbyInput.InteractPressed)
            {
                Activate();
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

        public void Activate()
        {
            if (GameSession.Instance == null) return;
            GameSession.Instance.SetFlag(GameFlagIds.TiqueRepaired, true);
            GameSession.Instance.SaveAt(roomId, spawnId);
            if (nearbyInput != null)
            {
                TiqueHealth health = nearbyInput.GetComponent<TiqueHealth>();
                if (health != null) health.HealFull();
            }
            Activated = true;
            if (indicator != null)
            {
                indicator.color = new Color(0.24f, 0.95f, 1f, 0.9f);
            }
        }

#if UNITY_EDITOR
        public void Configure(string targetRoomId, string targetSpawnId, SpriteRenderer targetIndicator)
        {
            roomId = targetRoomId;
            spawnId = targetSpawnId;
            indicator = targetIndicator;
        }
#endif
    }
}
