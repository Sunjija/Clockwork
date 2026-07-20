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
                && settledPosition.y > -3.2f && partValid;

            TiqueHealth health = FindAnyObjectByType<TiqueHealth>();
            bool healthValid = health != null && health.CurrentHealth == health.MaxHealth;
            if (healthValid)
            {
                health.TakeDamage(1, health.transform.position + Vector3.right);
                healthValid = health.CurrentHealth == health.MaxHealth - 1;
                health.TakeDamage(1, health.transform.position + Vector3.right);
                healthValid &= health.CurrentHealth == health.MaxHealth - 1;
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
                    && rats.Length >= 3
                    && bridgeHealth != null && bridgeHealth.CurrentHealth == bridgeHealth.MaxHealth - 1;
                Debug.Log($"CLOCKWORK_BRIDGE_PROBE valid={bridgeValid} rats={rats.Length} " +
                    $"pos={(bridgeMotor == null ? Vector3.zero : bridgeMotor.transform.position)} " +
                    $"hp={(bridgeHealth == null ? -1 : bridgeHealth.CurrentHealth)}");
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

            valid = valid && healthValid && bridgeValid && shaftValid;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
