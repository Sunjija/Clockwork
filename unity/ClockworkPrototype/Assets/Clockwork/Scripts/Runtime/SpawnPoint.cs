using UnityEngine;

namespace Clockwork
{
    public sealed class SpawnPoint : MonoBehaviour
    {
        [SerializeField] private string spawnId;
        [SerializeField] private int facing;

        public string SpawnId => spawnId;
        public int Facing => facing;

#if UNITY_EDITOR
        public void Configure(string id, int direction = 0)
        {
            spawnId = id;
            facing = direction == 0 ? 0 : direction < 0 ? -1 : 1;
        }
#endif
    }
}
