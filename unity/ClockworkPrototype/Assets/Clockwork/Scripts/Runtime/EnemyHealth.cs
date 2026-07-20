using UnityEngine;

namespace Clockwork
{
    public sealed class EnemyHealth : MonoBehaviour
    {
        [SerializeField] private int maxHealth = 2;
        [SerializeField] private bool indestructible;
        [SerializeField] private float flashDuration = 0.12f;
        [SerializeField] private Vector2 hitKnockback = new Vector2(2.6f, 2.2f);

        private SpriteRenderer spriteRenderer;
        private Color baseColor;
        private float flashTimer;
        private int currentHealth;

        public bool IsAlive => currentHealth > 0;
        public int CurrentHealth => currentHealth;
        public int MaxHealth => maxHealth;
        public bool Indestructible => indestructible;

        private void Awake()
        {
            currentHealth = maxHealth;
            spriteRenderer = GetComponentInChildren<SpriteRenderer>();
            if (spriteRenderer != null) baseColor = spriteRenderer.color;
        }

        private void Update()
        {
            if (spriteRenderer == null || flashTimer <= 0f) return;
            flashTimer -= Time.deltaTime;
            spriteRenderer.color = flashTimer > 0f ? Color.white : baseColor;
        }

        public bool TakeDamage(int amount, float knockbackDirection)
        {
            if (!IsAlive || amount <= 0) return false;
            currentHealth -= amount;
            flashTimer = flashDuration;

            Rigidbody2D body = GetComponent<Rigidbody2D>();
            if (body != null && body.bodyType == RigidbodyType2D.Dynamic)
            {
                body.linearVelocity = new Vector2(knockbackDirection * hitKnockback.x, hitKnockback.y);
            }

            if (currentHealth <= 0)
            {
                if (indestructible)
                {
                    currentHealth = maxHealth;
                    return true;
                }

                Destroy(gameObject);
                return true;
            }

            return false;
        }

#if UNITY_EDITOR
        public void Configure(int health, bool canBeDestroyed = true)
        {
            maxHealth = health;
            indestructible = !canBeDestroyed;
        }
#endif
    }
}
