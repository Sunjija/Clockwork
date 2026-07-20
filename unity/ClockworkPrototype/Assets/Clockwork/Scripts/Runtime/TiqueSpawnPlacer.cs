using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueMotor), typeof(Rigidbody2D))]
    public sealed class TiqueSpawnPlacer : MonoBehaviour
    {
        private void Start()
        {
            if (GameSession.Instance == null) return;
            string pendingId = GameSession.Instance.ConsumePendingSpawn();
            if (string.IsNullOrEmpty(pendingId)) return;

            foreach (SpawnPoint point in FindObjectsByType<SpawnPoint>(FindObjectsSortMode.None))
            {
                if (point.SpawnId == pendingId)
                {
                    transform.position = point.transform.position;
                    GetComponent<Rigidbody2D>().linearVelocity = Vector2.zero;
                    return;
                }
            }
            Debug.LogWarning($"CLOCKWORK spawn id not found in scene: {pendingId}");
        }
    }
}
