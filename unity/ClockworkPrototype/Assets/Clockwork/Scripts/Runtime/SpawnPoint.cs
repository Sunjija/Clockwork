using UnityEngine;

namespace Clockwork
{
    public sealed class SpawnPoint : MonoBehaviour
    {
        [SerializeField] private string spawnId;

        public string SpawnId => spawnId;

#if UNITY_EDITOR
        public void Configure(string id)
        {
            spawnId = id;
        }
#endif
    }
}
