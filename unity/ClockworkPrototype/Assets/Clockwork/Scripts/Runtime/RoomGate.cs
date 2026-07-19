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
        public bool IsOpen => string.IsNullOrEmpty(requiredFlag)
            || (GameSession.Instance != null && GameSession.Instance.HasFlag(requiredFlag));

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
