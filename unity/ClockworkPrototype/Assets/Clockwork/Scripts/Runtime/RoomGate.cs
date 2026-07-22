using UnityEngine;

namespace Clockwork
{
    public sealed class RoomGate : MonoBehaviour
    {
        [SerializeField] private string gateId;
        [SerializeField] private string destinationRoomId;
        [SerializeField] private string destinationSpawnId;
        [SerializeField] private string requiredFlag;

        public string GateId => gateId;
        public string DestinationRoomId => destinationRoomId;
        public string DestinationSpawnId => destinationSpawnId;
        public bool IsOpen => string.IsNullOrEmpty(requiredFlag)
            || (GameSession.Instance != null && GameSession.Instance.HasFlag(requiredFlag));
        public bool IsDestinationBuilt => GameSession.RoomSceneExists(destinationRoomId);

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (GameSession.Instance == null) return;
            if (other.GetComponentInParent<TiqueMotor>() == null) return;
            if (!IsOpen || !IsDestinationBuilt) return;
            GameSession.Instance.LoadRoom(destinationRoomId, destinationSpawnId);
        }

#if UNITY_EDITOR
        public void Configure(string id, string roomId, string spawnId, string flag = "")
        {
            gateId = id;
            destinationRoomId = roomId;
            destinationSpawnId = spawnId;
            requiredFlag = flag;
        }
#endif
    }
}
