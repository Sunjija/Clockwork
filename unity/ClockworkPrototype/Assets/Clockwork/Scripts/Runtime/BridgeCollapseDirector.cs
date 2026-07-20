using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace Clockwork
{
    // Scripted opening defeat (canon EVT-010 / v5.5 A-1): before repair the rat swarm
    // cannot be beaten — rats keep coming and accumulated damage drops Tique either at
    // 0 HP or at the west end of the bridge. Morbi repairs him during the blackout and
    // he wakes at the workshop. After repair the bridge holds a static, beatable pack.
    [RequireComponent(typeof(Collider2D))]
    public sealed class BridgeCollapseDirector : MonoBehaviour
    {
        [SerializeField] private GameObject ratPrefab;
        [SerializeField] private float respawnDelay = 1.6f;
        [SerializeField] private int preRepairPackSize = 3;

        private readonly List<GameObject> rats = new List<GameObject>();
        private TiqueHealth playerHealth;
        private float respawnTimer;
        private bool spawnFromEast = true;
        private bool collapsing;
        private float collapseClock;
        private GUIStyle logStyle;

        private static bool Repaired => GameSession.Instance != null
            && GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired);

        private void Start()
        {
            SpawnRat(new Vector2(2f, -2f), 1, 0.7f);
            SpawnRat(new Vector2(-2.6f, -2f), 1, 0.95f);
            SpawnRat(new Vector2(-3.6f, -2f), -1, 0.95f);

            if (!Repaired)
            {
                playerHealth = FindAnyObjectByType<TiqueHealth>();
                if (playerHealth != null)
                {
                    playerHealth.DeathOverride = TriggerCollapse;
                }
            }
        }

        private void Update()
        {
            if (Repaired || collapsing) return;

            respawnTimer -= Time.deltaTime;
            rats.RemoveAll(rat => rat == null);
            if (respawnTimer <= 0f && rats.Count < preRepairPackSize)
            {
                Vector2 edge = spawnFromEast ? new Vector2(5.6f, -2f) : new Vector2(-4.6f, -2f);
                SpawnRat(edge, spawnFromEast ? -1 : 1, 1f);
                spawnFromEast = !spawnFromEast;
                respawnTimer = respawnDelay;
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
                session.SaveAt("caligo", "caligo-workshop");
                session.LoadRoom("caligo", "caligo-workshop");
            }
        }

        private void OnGUI()
        {
            if (!collapsing) return;
            collapseClock += Time.unscaledDeltaTime;
            EnsureStyle();
            GUI.depth = -200;
            string line = collapseClock < 2.4f
                ? "…구동계 정지. 신호 미약."
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
#endif
    }
}
