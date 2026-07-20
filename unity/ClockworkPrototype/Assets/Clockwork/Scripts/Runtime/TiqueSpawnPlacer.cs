using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueMotor), typeof(Rigidbody2D))]
    public sealed class TiqueSpawnPlacer : MonoBehaviour
    {
        private void Start()
        {
            if (GameSession.Instance == null) return;
            string pendingId = GameSession.Instance.ConsumePendingSpawn(SceneManager.GetActiveScene().name);
            if (string.IsNullOrEmpty(pendingId)) return;

            foreach (SpawnPoint point in FindObjectsByType<SpawnPoint>(FindObjectsSortMode.None))
            {
                if (point.SpawnId == pendingId)
                {
                    transform.position = point.transform.position;
                    GetComponent<Rigidbody2D>().linearVelocity = Vector2.zero;
                    Debug.Log($"CLOCKWORK spawn placed scene={SceneManager.GetActiveScene().name} id={pendingId}");
                    return;
                }
            }
            Debug.LogWarning($"CLOCKWORK spawn id not found in scene: {pendingId}");
        }
    }
}
