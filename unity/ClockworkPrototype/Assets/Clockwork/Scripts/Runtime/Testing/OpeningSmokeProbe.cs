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
            DirectionalCameraTarget cameraTarget = FindAnyObjectByType<DirectionalCameraTarget>();
            GameSession session = FindAnyObjectByType<GameSession>();
            MysteryPartPickup partPickup = FindAnyObjectByType<MysteryPartPickup>();
            UnityEngine.Tilemaps.TilemapCollider2D tilemapCollider =
                FindAnyObjectByType<UnityEngine.Tilemaps.TilemapCollider2D>();
            SpriteRenderer sprite = animator == null ? null : animator.GetComponent<SpriteRenderer>();
            Vector3 initialPosition = motor == null ? Vector3.zero : motor.transform.position;
            yield return new WaitForSecondsRealtime(1.5f);
            Vector3 settledPosition = motor == null ? Vector3.zero : motor.transform.position;
            Debug.Log($"CLOCKWORK_PLAYER_PROBE initial={initialPosition} settled={settledPosition} " +
                $"grounded={motor != null && motor.Grounded} facing={(motor == null ? 0 : motor.Facing)}");
            partPickup?.Collect();
            bool partValid = session != null && session.HasFlag(GameFlagIds.LimbusMysteryPart);
            bool playerValid = motor != null && combat != null && animator != null && input != null
                && sprite != null && sprite.enabled && sprite.sprite != null && tilemapCollider != null
                && settledPosition.y > -3.2f && partValid
                && motor.Facing < 0 && cameraTarget != null
                && cameraTarget.transform.position.x < motor.transform.position.x
                && combat.CurrentDamageMultiplier < 1f;

            TiqueEnergyGauge energy = FindAnyObjectByType<TiqueEnergyGauge>();
            GameObject energyDummy = new GameObject("EnergyProbeDummy");
            energyDummy.transform.position = motor == null
                ? Vector3.zero
                : motor.transform.position + new Vector3(motor.Facing * 0.39f, 0.44f, 0f);
            BoxCollider2D energyDummyCollider = energyDummy.AddComponent<BoxCollider2D>();
            energyDummyCollider.size = new Vector2(0.25f, 0.25f);
            energyDummy.AddComponent<EnemyHealth>();

            bool comboValid = combat != null
                && combat.CurrentCombo != null
                && combat.CurrentCombo.ComboId == "fist-basic"
                && combat.CurrentComboStepCount == 3
                && combat.TryAttack();
            if (comboValid)
            {
                comboValid &= combat.CurrentComboStepIndex == 0
                    && combat.CurrentAttack.AttackId == "fist-right"
                    && !combat.IsAttackQueued
                    && combat.TryAttack()
                    && combat.IsAttackQueued;
                float deadline = Time.realtimeSinceStartup + 0.6f;
                while (combat.CurrentComboStepIndex != 1
                    && Time.realtimeSinceStartup < deadline) yield return null;
                comboValid &= combat.CurrentComboStepIndex == 1
                    && combat.CurrentAttack.AttackId == "fist-left";
                deadline = Time.realtimeSinceStartup + 0.6f;
                while ((combat.IsAttacking || combat.CurrentComboStepIndex != 2)
                    && Time.realtimeSinceStartup < deadline) yield return null;
                comboValid &= combat.CurrentComboStepIndex == 2
                    && combat.CurrentAttack.AttackId == "fist-finisher"
                    && !combat.IsAttacking;
                yield return new WaitForSecondsRealtime(0.25f);
                comboValid &= combat.CurrentComboStepIndex == 2
                    && combat.TryAttack();
                comboValid &= !combat.IsWeaponTransitionQueued
                    && Mathf.Approximately(energy.CurrentEnergy, 15f)
                    && combat.TrySelectWeapon(2)
                    && combat.IsWeaponTransitionQueued
                    && Mathf.Approximately(combat.PendingTransitionEnergyCost, 10f);
                deadline = Time.realtimeSinceStartup + 0.7f;
                while (!combat.IsWeaponTransitionActive && Time.realtimeSinceStartup < deadline) yield return null;
                comboValid &= combat.IsWeaponTransitionActive
                    && combat.CurrentAttack != null
                    && combat.CurrentAttack.AttackId == "hammer"
                    && Mathf.Approximately(energy.CurrentEnergy, 5f);
                yield return new WaitForSecondsRealtime(0.9f);
                comboValid &= combat.CurrentWeapon != null
                    && combat.CurrentWeapon.WeaponId == "hammer"
                    && combat.CurrentComboStepIndex == 0
                    && !combat.IsAttacking;
                combat.SelectAttack(0);
            }
            bool energyValid = energy != null && Mathf.Approximately(energy.CurrentEnergy, 5f);
            Destroy(energyDummy);
            Debug.Log($"CLOCKWORK_COMBO_PROBE valid={comboValid} "
                + $"combo={combat?.CurrentCombo?.ComboId} steps={combat?.CurrentComboStepCount} "
                + $"weapon={combat?.CurrentWeapon?.WeaponId}");
            Debug.Log($"CLOCKWORK_ENERGY_PROBE valid={energyValid} "
                + $"energy={(energy == null ? -1f : energy.CurrentEnergy)}");

            float aspect = Screen.height <= 0 ? 0f : Screen.width / (float)Screen.height;
            bool displayValid = Application.isBatchMode
                || Screen.width >= Screen.height
                    && Mathf.Abs(aspect - DesktopDisplayProfile.Aspect) <= 0.05f;
            Debug.Log($"CLOCKWORK_DISPLAY_PROBE valid={displayValid} size={Screen.width}x{Screen.height} "
                + $"aspect={aspect:F2} batch={Application.isBatchMode}");

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

            complete(playerValid && comboValid && energyValid && displayValid
                && healthValid && bridgeValid && collapseValid);
        }
    }
}
