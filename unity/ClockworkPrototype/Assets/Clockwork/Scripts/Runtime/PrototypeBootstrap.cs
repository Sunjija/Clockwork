using System.Collections;
using System.Linq;
using UnityEngine;

namespace Clockwork
{
    public sealed class PrototypeBootstrap : MonoBehaviour
    {
        private static bool smokeStarted;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Physics2D.gravity = Vector2.zero;

            // The smoke runner survives room loads; scene copies of this bootstrap must not restart it.
            if (!smokeStarted && System.Environment.GetCommandLineArgs().Contains("-clockworkSmokeTest"))
            {
                smokeStarted = true;
                DontDestroyOnLoad(gameObject);
                StartCoroutine(RunSmokeTest());
            }
        }

        private static IEnumerator RunSmokeTest()
        {
            // Boot scene is Limbus (canon awakening); the run walks the opening route:
            // Limbus -> bridge -> maintenance shaft.
            yield return null;
            yield return new WaitForSecondsRealtime(0.25f);
            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            TiqueCombat combat = FindAnyObjectByType<TiqueCombat>();
            TiqueSpriteAnimator animator = FindAnyObjectByType<TiqueSpriteAnimator>();
            TiqueInputReader input = FindAnyObjectByType<TiqueInputReader>();
            GameSession session = FindAnyObjectByType<GameSession>();
            MysteryPartPickup partPickup = FindAnyObjectByType<MysteryPartPickup>();
            UnityEngine.Tilemaps.TilemapCollider2D tilemapCollider = FindAnyObjectByType<UnityEngine.Tilemaps.TilemapCollider2D>();
            SpriteRenderer sprite = animator == null ? null : animator.GetComponent<SpriteRenderer>();
            Vector3 initialPosition = motor == null ? Vector3.zero : motor.transform.position;
            yield return new WaitForSecondsRealtime(1.5f);
            Vector3 settledPosition = motor == null ? Vector3.zero : motor.transform.position;
            Debug.Log($"CLOCKWORK_PLAYER_PROBE initial={initialPosition} settled={settledPosition} grounded={motor != null && motor.Grounded}");
            partPickup?.Collect();
            bool partValid = session != null && session.HasFlag(GameFlagIds.LimbusMysteryPart);
            bool valid = motor != null && combat != null && animator != null && input != null
                && sprite != null && sprite.enabled && sprite.sprite != null && tilemapCollider != null
                && settledPosition.y > -3.2f && partValid
                && combat.CurrentDamageMultiplier < 1f;

            TiqueHealth health = FindAnyObjectByType<TiqueHealth>();
            bool healthValid = health != null
                && health.CurrentHealth == health.DamagedStartingHealth
                && health.CurrentHealth < health.MaxHealth;
            if (healthValid)
            {
                health.TakeDamage(1, health.transform.position + Vector3.right);
                healthValid = health.CurrentHealth == health.DamagedStartingHealth - 1;
                health.TakeDamage(1, health.transform.position + Vector3.right);
                healthValid &= health.CurrentHealth == health.DamagedStartingHealth - 1;
                health.HealFull();
            }
            Debug.Log($"CLOCKWORK_HEALTH_PROBE valid={healthValid} hp={(health == null ? -1 : health.CurrentHealth)}");

            bool bridgeValid = false;
            if (session != null && session.LoadRoom("limbus-caligo-bridge", "entry-limbus"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor bridgeMotor = FindAnyObjectByType<TiqueMotor>();
                TiqueHealth bridgeHealth = FindAnyObjectByType<TiqueHealth>();
                RatEnemy[] rats = FindObjectsByType<RatEnemy>(FindObjectsSortMode.None);
                yield return new WaitForSecondsRealtime(1f);
                bridgeValid = bridgeMotor != null && bridgeMotor.Grounded
                    && Mathf.Abs(bridgeMotor.transform.position.x - 6f) < 1.2f
                    && rats.Length == 3
                    && bridgeHealth != null && bridgeHealth.CurrentHealth == bridgeHealth.MaxHealth;
                Debug.Log($"CLOCKWORK_BRIDGE_PROBE valid={bridgeValid} rats={rats.Length} " +
                    $"pos={(bridgeMotor == null ? Vector3.zero : bridgeMotor.transform.position)} " +
                    $"hp={(bridgeHealth == null ? -1 : bridgeHealth.CurrentHealth)}");
            }

            bool collapseValid = false;
            if (bridgeValid && session != null)
            {
                // Simulate a clean tutorial win. The finite pack must stay gone and Tique's
                // residual power failure must carry him to Morbi without a forced death call.
                RatEnemy[] rats = FindObjectsByType<RatEnemy>(FindObjectsSortMode.None);
                foreach (RatEnemy rat in rats)
                {
                    if (rat != null) Destroy(rat.gameObject);
                }
                yield return new WaitForSecondsRealtime(6.2f);
                TiqueMotor wakeMotor = FindAnyObjectByType<TiqueMotor>();
                TiqueHealth wakeHealth = FindAnyObjectByType<TiqueHealth>();
                TiqueCombat wakeCombat = FindAnyObjectByType<TiqueCombat>();
                MorbiNpc wakeMorbi = FindAnyObjectByType<MorbiNpc>();
                collapseValid = session.HasFlag(GameFlagIds.TiqueRepaired)
                    && wakeMotor != null && Mathf.Abs(wakeMotor.transform.position.x - -2f) < 1.2f
                    && wakeMorbi != null
                    && wakeHealth != null && wakeHealth.CurrentHealth == wakeHealth.MaxHealth
                    && wakeCombat != null && Mathf.Approximately(wakeCombat.CurrentDamageMultiplier, 1f);
                Debug.Log($"CLOCKWORK_COLLAPSE_PROBE valid={collapseValid} " +
                    $"repaired={session.HasFlag(GameFlagIds.TiqueRepaired)} " +
                    $"pos={(wakeMotor == null ? Vector3.zero : wakeMotor.transform.position)} " +
                    $"hp={(wakeHealth == null ? -1 : wakeHealth.CurrentHealth)}");
            }

            bool shaftValid = false;
            if (session != null && session.LoadRoom("caligo-maintenance-shaft", "entry-bridge"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor shaftMotor = FindAnyObjectByType<TiqueMotor>();
                RepairSavePoint savePoint = FindAnyObjectByType<RepairSavePoint>();
                yield return new WaitForSecondsRealtime(1f);
                savePoint?.Activate();
                shaftValid = shaftMotor != null && shaftMotor.Grounded
                    && Mathf.Abs(shaftMotor.transform.position.x - 6f) < 1.2f
                    && session.HasFlag(GameFlagIds.TiqueRepaired);
                Debug.Log($"CLOCKWORK_SHAFT_PROBE valid={shaftValid} " +
                    $"pos={(shaftMotor == null ? Vector3.zero : shaftMotor.transform.position)} " +
                    $"repaired={session.HasFlag(GameFlagIds.TiqueRepaired)}");
            }

            bool villageValid = false;
            if (session != null && session.LoadRoom("caligo", "entry-maintenance-shaft"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor villageMotor = FindAnyObjectByType<TiqueMotor>();
                MorbiNpc morbi = FindAnyObjectByType<MorbiNpc>();
                for (int i = 0; morbi != null && i < 8; i++)
                {
                    morbi.Interact();
                }
                yield return new WaitForSecondsRealtime(0.5f);
                villageValid = villageMotor != null && villageMotor.Grounded
                    && Mathf.Abs(villageMotor.transform.position.x - 6f) < 1.2f
                    && morbi != null
                    && session.HasFlag(GameFlagIds.MysteryPartIdentified);
                Debug.Log($"CLOCKWORK_VILLAGE_PROBE valid={villageValid} " +
                    $"identified={session.HasFlag(GameFlagIds.MysteryPartIdentified)} " +
                    $"pos={(villageMotor == null ? Vector3.zero : villageMotor.transform.position)}");
            }

            valid = valid && healthValid && bridgeValid && collapseValid && shaftValid && villageValid;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
