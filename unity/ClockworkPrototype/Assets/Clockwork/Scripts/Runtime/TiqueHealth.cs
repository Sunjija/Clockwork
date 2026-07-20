using System.Collections;
using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(TiqueMotor), typeof(Rigidbody2D))]
    public sealed class TiqueHealth : MonoBehaviour
    {
        [SerializeField] private int maxHealth = 5;
        [SerializeField] private int damagedStartingHealth = 2;
        [SerializeField] private float invulnerabilityDuration = 1f;
        [SerializeField] private Vector2 knockback = new Vector2(4.2f, 3.4f);
        [SerializeField] private float hitStunDuration = 0.24f;
        [SerializeField] private float respawnDelay = 0.9f;

        private TiqueMotor motor;
        private Rigidbody2D body;
        private SpriteRenderer spriteRenderer;
        private float invulnerabilityTimer;

        public int MaxHealth => maxHealth;
        public int DamagedStartingHealth => Mathf.Clamp(damagedStartingHealth, 1, maxHealth);
        public int CurrentHealth { get; private set; }
        public bool IsRespawning { get; private set; }

        // When set (e.g. the scripted bridge collapse), it replaces the normal death respawn.
        public System.Action DeathOverride { get; set; }

        private void Awake()
        {
            motor = GetComponent<TiqueMotor>();
            body = GetComponent<Rigidbody2D>();
            spriteRenderer = GetComponentInChildren<SpriteRenderer>();
            CurrentHealth = maxHealth;
        }

        private void Start()
        {
            // Runtime health carries across room loads through GameSession; -1 means unset.
            GameSession session = GameSession.Instance;
            if (session != null && session.RuntimeHealth > 0)
            {
                CurrentHealth = Mathf.Min(session.RuntimeHealth, maxHealth);
            }
            else if (session != null && !session.HasFlag(GameFlagIds.TiqueRepaired))
            {
                CurrentHealth = DamagedStartingHealth;
            }
            StoreHealth();
        }

        private void Update()
        {
            invulnerabilityTimer = Mathf.Max(0f, invulnerabilityTimer - Time.deltaTime);
            if (spriteRenderer != null)
            {
                bool blinkHidden = invulnerabilityTimer > 0f && Mathf.Repeat(Time.time, 0.16f) < 0.08f;
                spriteRenderer.enabled = !blinkHidden;
            }
        }

        public void TakeDamage(int amount, Vector2 sourcePosition)
        {
            if (IsRespawning || invulnerabilityTimer > 0f || amount <= 0) return;

            CurrentHealth = Mathf.Max(0, CurrentHealth - amount);
            StoreHealth();
            invulnerabilityTimer = invulnerabilityDuration;

            float direction = transform.position.x >= sourcePosition.x ? 1f : -1f;
            body.linearVelocity = new Vector2(direction * knockback.x, knockback.y);
            motor.Stun(hitStunDuration);

            if (CurrentHealth <= 0)
            {
                if (DeathOverride != null)
                {
                    IsRespawning = true;
                    motor.Stun(respawnDelay);
                    DeathOverride();
                }
                else
                {
                    StartCoroutine(Respawn());
                }
            }
        }

        public void HealFull()
        {
            CurrentHealth = maxHealth;
            StoreHealth();
        }

        private void StoreHealth()
        {
            if (GameSession.Instance != null)
            {
                GameSession.Instance.RuntimeHealth = CurrentHealth;
            }
        }

        private IEnumerator Respawn()
        {
            IsRespawning = true;
            motor.Stun(respawnDelay);
            yield return new WaitForSeconds(respawnDelay);
            if (GameSession.Instance != null)
            {
                GameSession.Instance.RespawnAtLastSave();
            }
            else
            {
                CurrentHealth = maxHealth;
                IsRespawning = false;
            }
        }
    }
}
