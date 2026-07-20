using System;
using System.Collections.Generic;
using UnityEngine;

namespace Clockwork
{
    public readonly struct CombatHitResult
    {
        public CombatHitResult(EnemyHealth enemy, int damage, bool defeated)
        {
            Enemy = enemy;
            Damage = damage;
            Defeated = defeated;
        }

        public EnemyHealth Enemy { get; }
        public int Damage { get; }
        public bool Defeated { get; }
    }

    [RequireComponent(typeof(TiqueMotor), typeof(TiqueInputReader))]
    public sealed class TiqueCombat : MonoBehaviour
    {
        [SerializeField] private AttackDefinition[] attacks;
        [SerializeField] private ComboDefinition[] combos;
        [SerializeField] private WeaponDefinition[] weapons;
        [SerializeField] private LineRenderer hitboxRenderer;
        [SerializeField] private LineRenderer trailRenderer;
        [SerializeField] private float damagedDamageMultiplier = 0.6f;

        private readonly HashSet<EnemyHealth> struckEnemies = new HashSet<EnemyHealth>();
        private readonly Collider2D[] overlapResults = new Collider2D[12];
        private TiqueMotor motor;
        private TiqueInputReader input;
        private TiqueEnergyGauge energy;
        private ContactFilter2D hitFilter;
        private int selectedAttack;
        private int comboStepIndex;
        private float attackTimer;
        private bool attackQueued;
        private ComboDefinition activeTransitionCombo;
        private ComboDefinition queuedTransitionCombo;
        private int pendingWeaponIndex = -1;
        private float pendingTransitionEnergyCost;
        private bool showHitboxes;

        public WeaponDefinition CurrentWeapon => weapons != null && weapons.Length > 0
            ? weapons[Mathf.Clamp(selectedAttack, 0, weapons.Length - 1)]
            : null;
        public ComboDefinition CurrentCombo => activeTransitionCombo ?? CurrentWeapon?.BasicCombo
            ?? (combos != null && combos.Length > 0
                ? combos[Mathf.Clamp(selectedAttack, 0, combos.Length - 1)]
                : null);
        public ComboStep CurrentComboStep => CurrentCombo?.StepAt(comboStepIndex);
        public AttackDefinition CurrentAttack => CurrentComboStep?.Attack
            ?? (attacks != null && attacks.Length > 0
                ? attacks[Mathf.Clamp(selectedAttack, 0, attacks.Length - 1)]
                : null);
        public bool IsAttacking => attackTimer > 0f && CurrentAttack != null;
        public float AttackProgress => !IsAttacking ? 0f : 1f - Mathf.Clamp01(attackTimer / CurrentAttack.Duration);
        public string SelectedWeaponName => CurrentWeapon?.DisplayName
            ?? (CurrentCombo == null ? CurrentAttack?.DisplayName ?? "None" : CurrentCombo.DisplayName);
        public int CurrentComboStepIndex => comboStepIndex;
        public int CurrentComboStepCount => CurrentCombo?.StepCount ?? (CurrentAttack == null ? 0 : 1);
        public bool IsAttackQueued => attackQueued;
        public bool IsWeaponTransitionActive => activeTransitionCombo != null;
        public bool IsWeaponTransitionQueued => queuedTransitionCombo != null;
        public float PendingTransitionEnergyCost => pendingTransitionEnergyCost;
        public string PendingWeaponName => pendingWeaponIndex >= 0 && pendingWeaponIndex < (weapons?.Length ?? 0)
            ? weapons[pendingWeaponIndex].DisplayName
            : string.Empty;
        public bool IsComboInputWindow => IsAttacking
            && CurrentComboStep != null
            && !CurrentCombo.CyclesAcrossInputs
            && comboStepIndex + 1 < CurrentComboStepCount
            && CurrentComboStep.CanQueueAt(AttackProgress);
        public bool IsWeaponTransitionWindow => IsAttacking
            && activeTransitionCombo == null
            && CurrentWeapon != null
            && CurrentWeapon.HasTransitions
            && CurrentCombo == CurrentWeapon.BasicCombo
            && CurrentComboStep != null;
        public event Action<CombatHitResult> AttackLanded;
        public event Action<int, int, bool> AttackStepStarted;
        public float CurrentDamageMultiplier => GameSession.Instance != null
            && GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired)
                ? 1f
                : damagedDamageMultiplier;

        private void Awake()
        {
            motor = GetComponent<TiqueMotor>();
            input = GetComponent<TiqueInputReader>();
            energy = GetComponent<TiqueEnergyGauge>();
            hitFilter = new ContactFilter2D
            {
                useTriggers = false,
                useLayerMask = true,
                layerMask = Physics2D.AllLayers
            };
        }

        private void Update()
        {
            if (input.Slot1Pressed) TrySelectWeapon(0);
            if (input.Slot2Pressed) TrySelectWeapon(1);
            if (input.Slot3Pressed) TrySelectWeapon(2);
            if (input.DebugHitboxesPressed) showHitboxes = !showHitboxes;

            if (input.AttackPressed)
            {
                TryAttack();
            }

            ApplyAttackDamage();
            bool wasAttacking = IsAttacking;
            attackTimer = Mathf.Max(0f, attackTimer - Time.deltaTime);
            if (wasAttacking && attackTimer <= 0f)
            {
                CompleteAttackStep();
            }
            UpdateDebugRenderers();
        }

        public bool TryAttack()
        {
            if (CurrentAttack == null || motor.IsDashing || motor.IsStunned) return false;

            if (!IsAttacking)
            {
                StartAttackStep();
                return true;
            }

            bool hasNextStep = CurrentCombo != null
                && (comboStepIndex + 1 < CurrentCombo.StepCount || CurrentCombo.CyclesAcrossInputs);
            bool canQueue = CurrentCombo != null && CurrentCombo.CyclesAcrossInputs
                || CurrentComboStep != null && CurrentComboStep.CanQueueAt(AttackProgress);
            if (!hasNextStep || !canQueue)
            {
                return false;
            }

            attackQueued = true;
            return true;
        }

        private void StartAttackStep()
        {
            attackTimer = CurrentAttack.Duration;
            struckEnemies.Clear();
            AttackStepStarted?.Invoke(comboStepIndex, CurrentComboStepCount, activeTransitionCombo != null);
        }

        private void CompleteAttackStep()
        {
            if (queuedTransitionCombo != null && pendingWeaponIndex >= 0)
            {
                ComboDefinition transition = queuedTransitionCombo;
                queuedTransitionCombo = null;
                bool spent = pendingTransitionEnergyCost <= 0f
                    || energy != null && energy.TrySpend(pendingTransitionEnergyCost);
                pendingTransitionEnergyCost = 0f;
                if (spent)
                {
                    activeTransitionCombo = transition;
                    comboStepIndex = 0;
                    attackQueued = false;
                    StartAttackStep();
                    return;
                }

                pendingWeaponIndex = -1;
            }

            if (attackQueued && CurrentCombo != null
                && (comboStepIndex + 1 < CurrentCombo.StepCount || CurrentCombo.CyclesAcrossInputs))
            {
                comboStepIndex = (comboStepIndex + 1) % CurrentCombo.StepCount;
                attackQueued = false;
                StartAttackStep();
                return;
            }

            if (activeTransitionCombo != null && pendingWeaponIndex >= 0)
            {
                selectedAttack = pendingWeaponIndex;
                pendingWeaponIndex = -1;
                activeTransitionCombo = null;
            }

            comboStepIndex = CurrentCombo != null && CurrentCombo.CyclesAcrossInputs
                ? (comboStepIndex + 1) % CurrentCombo.StepCount
                : 0;
            attackQueued = false;
        }

        private void ApplyAttackDamage()
        {
            if (!IsAttacking || !CurrentAttack.IsActiveAt(AttackProgress)) return;

            Vector2 offset = CurrentAttack.HitboxCenter;
            offset.x *= motor.Facing;
            Vector2 center = (Vector2)transform.position + offset;
            int count = Physics2D.OverlapBox(center, CurrentAttack.HitboxSize, 0f, hitFilter, overlapResults);
            for (int i = 0; i < count; i++)
            {
                EnemyHealth enemy = overlapResults[i].GetComponentInParent<EnemyHealth>();
                if (enemy != null && enemy.IsAlive && struckEnemies.Add(enemy))
                {
                    int damage = Mathf.Max(1, Mathf.CeilToInt(CurrentAttack.Damage * CurrentDamageMultiplier));
                    bool defeated = enemy.TakeDamage(damage, motor.Facing);
                    AttackLanded?.Invoke(new CombatHitResult(enemy, damage, defeated));
                }
            }
        }

        public void SelectAttack(int index)
        {
            TrySelectWeapon(index);
        }

        public bool TrySelectWeapon(int index)
        {
            int weaponCount = weapons?.Length ?? attacks?.Length ?? 0;
            if (index < 0 || index >= weaponCount || index == selectedAttack) return false;

            if (!IsAttacking)
            {
                selectedAttack = index;
                comboStepIndex = 0;
                attackQueued = false;
                activeTransitionCombo = null;
                queuedTransitionCombo = null;
                pendingWeaponIndex = -1;
                pendingTransitionEnergyCost = 0f;
                return true;
            }

            if (CurrentWeapon == null || activeTransitionCombo != null
                || CurrentCombo != CurrentWeapon.BasicCombo
                || CurrentComboStep == null
                || !CurrentWeapon.TryGetTransition(
                    weapons[index].WeaponId, out ComboDefinition transition, out float lentiumCost)
                || energy == null
                || !energy.CanSpend(lentiumCost))
            {
                return false;
            }

            queuedTransitionCombo = transition;
            pendingWeaponIndex = index;
            pendingTransitionEnergyCost = lentiumCost;
            return true;
        }

        private void UpdateDebugRenderers()
        {
            bool active = IsAttacking && CurrentAttack.IsActiveAt(AttackProgress);
            if (hitboxRenderer != null)
            {
                hitboxRenderer.enabled = showHitboxes && active;
                if (hitboxRenderer.enabled)
                {
                    Vector2 offset = CurrentAttack.HitboxCenter;
                    offset.x *= motor.Facing;
                    DrawRectangle(hitboxRenderer, (Vector2)transform.position + offset, CurrentAttack.HitboxSize);
                    hitboxRenderer.startColor = CurrentAttack.TrailColor;
                    hitboxRenderer.endColor = CurrentAttack.TrailColor;
                }
            }

            if (trailRenderer != null)
            {
                trailRenderer.enabled = active
                    && !CurrentAttack.AttackId.StartsWith("fist", StringComparison.Ordinal);
                if (trailRenderer.enabled)
                {
                    DrawTrail(trailRenderer, CurrentAttack.AttackId, CurrentAttack.TrailColor);
                }
            }
        }

        private static void DrawRectangle(LineRenderer line, Vector2 center, Vector2 size)
        {
            Vector2 half = size * 0.5f;
            line.positionCount = 5;
            line.SetPosition(0, center + new Vector2(-half.x, -half.y));
            line.SetPosition(1, center + new Vector2(-half.x, half.y));
            line.SetPosition(2, center + new Vector2(half.x, half.y));
            line.SetPosition(3, center + new Vector2(half.x, -half.y));
            line.SetPosition(4, center + new Vector2(-half.x, -half.y));
        }

        private void DrawTrail(LineRenderer line, string attackId, Color color)
        {
            const int points = 14;
            line.positionCount = points;
            line.startColor = color;
            line.endColor = new Color(color.r, color.g, color.b, 0.12f);

            for (int i = 0; i < points; i++)
            {
                float t = i / (points - 1f);
                Vector2 local;
                if (attackId == "hammer")
                {
                    float angle = Mathf.Lerp(145f, -35f, t) * Mathf.Deg2Rad;
                    local = new Vector2(Mathf.Cos(angle) * 1.15f, 0.72f + Mathf.Sin(angle) * 1.05f);
                }
                else
                {
                    Vector2 a = new Vector2(-0.5f, 0.67f);
                    Vector2 b = new Vector2(0.2f, 0.9f);
                    Vector2 c = new Vector2(0.88f, 0.18f);
                    local = Vector2.Lerp(Vector2.Lerp(a, b, t), Vector2.Lerp(b, c, t), t);
                }
                local.x *= motor.Facing;
                line.SetPosition(i, (Vector2)transform.position + local);
            }
        }

#if UNITY_EDITOR
        public void Configure(
            AttackDefinition[] approvedAttacks,
            ComboDefinition[] approvedCombos,
            WeaponDefinition[] approvedWeapons,
            LineRenderer hitbox,
            LineRenderer trail)
        {
            attacks = approvedAttacks;
            combos = approvedCombos;
            weapons = approvedWeapons;
            hitboxRenderer = hitbox;
            trailRenderer = trail;
        }
#endif
    }
}
