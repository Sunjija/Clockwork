using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Clockwork
{
    // Scripted opening shutdown (canon EVT-010 / v5.5 A-1): Tique reaches the bridge
    // already critically damaged by the fall. A finite rat pack exhausts his remaining
    // power; even a clean win ends in shutdown. Morbi repairs him during the blackout.
    [RequireComponent(typeof(Collider2D))]
    public sealed class BridgeCollapseDirector : MonoBehaviour
    {
        [SerializeField] private GameObject ratPrefab;
        [SerializeField] private float postCombatShutdownDelay = 0.9f;
        [SerializeField] private float ratSpawnY = -2f;
        [SerializeField] private string rescueRoomId = "caligo";
        [SerializeField] private string rescueSpawnId = "caligo-workshop";

        private readonly List<GameObject> rats = new List<GameObject>();
        private bool shutdownQueued;
        private bool collapsing;
        private float collapseClock;
        private GUIStyle logStyle;

        private static bool Repaired => GameSession.Instance != null
            && GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired);

        private void Start()
        {
            SpawnRat(new Vector2(2f, ratSpawnY), 1, 0.7f);
            SpawnRat(new Vector2(-2.6f, ratSpawnY), 1, 0.95f);
            SpawnRat(new Vector2(-3.6f, ratSpawnY), -1, 0.95f);

            if (!Repaired)
            {
                TiqueHealth playerHealth = FindAnyObjectByType<TiqueHealth>();
                if (playerHealth != null)
                {
                    playerHealth.DeathOverride = TriggerCollapse;
                }
            }
        }

        private void Update()
        {
            if (Repaired || collapsing || shutdownQueued) return;

            rats.RemoveAll(rat => rat == null);
            if (rats.Count == 0)
            {
                shutdownQueued = true;
                StartCoroutine(ShutdownAfterCombat());
            }
        }

        private void SpawnRat(Vector2 position, int direction, float speed)
        {
            if (ratPrefab == null) return;
            GameObject rat = Instantiate(ratPrefab, position, Quaternion.identity);
            RatEnemy enemy = rat.GetComponent<RatEnemy>();
            if (enemy != null) enemy.Initialize(direction, speed);
            rats.Add(rat);
        }

        private IEnumerator ShutdownAfterCombat()
        {
            yield return new WaitForSeconds(postCombatShutdownDelay);
            TriggerCollapse();
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            if (Repaired || collapsing) return;
            if (other.GetComponentInParent<TiqueMotor>() != null)
            {
                TriggerCollapse();
            }
        }

        public void TriggerCollapse()
        {
            if (collapsing || Repaired) return;
            collapsing = true;
            StartCoroutine(CollapseRoutine());
        }

        private IEnumerator CollapseRoutine()
        {
            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            if (motor != null) motor.Stun(30f);
            collapseClock = 0f;

            yield return new WaitForSecondsRealtime(0.5f);
            yield return ScreenFader.Instance.FadeRoutine(1f, 1.8f);
            yield return new WaitForSecondsRealtime(1.4f);

            GameSession session = GameSession.Instance;
            if (session != null)
            {
                // Morbi repairs Tique during the blackout (canon: rescue -> workshop repair).
                session.SetFlag(GameFlagIds.TiqueRepaired, true);
                session.RuntimeHealth = -1;
                session.SaveAt(rescueRoomId, rescueSpawnId);
                session.LoadRoom(rescueRoomId, rescueSpawnId);
            }
        }

        private void OnGUI()
        {
            if (!collapsing) return;
            collapseClock += Time.unscaledDeltaTime;
            EnsureStyle();
            GUI.depth = -200;
            string line = collapseClock < 2.4f
                ? "…잔여 동력 임계치. 구동계 정지."
                : "…외부 개입 감지. 운반 중.";
            GUI.Label(new Rect(0f, Screen.height * 0.46f, Screen.width, 30f), line, logStyle);
        }

        private void EnsureStyle()
        {
            if (logStyle != null) return;
            logStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 15,
                alignment = TextAnchor.MiddleCenter,
                normal = { textColor = new Color(0.62f, 0.7f, 0.76f) }
            };
        }

#if UNITY_EDITOR
        public void Configure(GameObject prefab)
        {
            ratPrefab = prefab;
        }

        public void Configure(
            GameObject prefab, float spawnY, string destinationRoom, string destinationSpawn)
        {
            ratPrefab = prefab;
            ratSpawnY = spawnY;
            rescueRoomId = destinationRoom;
            rescueSpawnId = destinationSpawn;
        }
#endif
    }
}
