using System;
using System.Collections;
using UnityEngine;
using static UnityEngine.Object;

namespace Clockwork
{
    public static class OpeningSmokeProbe
    {
        public static IEnumerator Run(Action<bool> complete)
        {
            yield return null;
            yield return new WaitForSecondsRealtime(0.25f);
            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            TiqueCombat combat = FindAnyObjectByType<TiqueCombat>();
            TiqueSpriteAnimator animator = FindAnyObjectByType<TiqueSpriteAnimator>();
            TiqueInputReader input = FindAnyObjectByType<TiqueInputReader>();
            GameSession session = FindAnyObjectByType<GameSession>();
            MysteryPartPickup partPickup = FindAnyObjectByType<MysteryPartPickup>();
            UnityEngine.Tilemaps.TilemapCollider2D tilemapCollider =
                FindAnyObjectByType<UnityEngine.Tilemaps.TilemapCollider2D>();
            SpriteRenderer sprite = animator == null ? null : animator.GetComponent<SpriteRenderer>();
            Vector3 initialPosition = motor == null ? Vector3.zero : motor.transform.position;
            yield return new WaitForSecondsRealtime(1.5f);
            Vector3 settledPosition = motor == null ? Vector3.zero : motor.transform.position;
            Debug.Log($"CLOCKWORK_PLAYER_PROBE initial={initialPosition} settled={settledPosition} " +
                $"grounded={motor != null && motor.Grounded}");
            partPickup?.Collect();
            bool partValid = session != null && session.HasFlag(GameFlagIds.LimbusMysteryPart);
            bool playerValid = motor != null && combat != null && animator != null && input != null
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

            complete(playerValid && healthValid && bridgeValid && collapseValid);
        }
    }
}
