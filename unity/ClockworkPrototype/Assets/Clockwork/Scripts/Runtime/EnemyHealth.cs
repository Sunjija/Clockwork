using UnityEngine;

namespace Clockwork
{
    public sealed class EnemyHealth : MonoBehaviour
    {
        [SerializeField] private int maxHealth = 2;
        [SerializeField] private float flashDuration = 0.12f;
        [SerializeField] private Vector2 hitKnockback = new Vector2(2.6f, 2.2f);

        private SpriteRenderer spriteRenderer;
        private Color baseColor;
        private float flashTimer;
        private int currentHealth;

        public bool IsAlive => currentHealth > 0;

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

        public void TakeDamage(int amount, float knockbackDirection)
        {
            if (!IsAlive || amount <= 0) return;
            currentHealth -= amount;
            flashTimer = flashDuration;

            Rigidbody2D body = GetComponent<Rigidbody2D>();
            if (body != null)
            {
                body.linearVelocity = new Vector2(knockbackDirection * hitKnockback.x, hitKnockback.y);
            }

            if (currentHealth <= 0)
            {
                Destroy(gameObject);
            }
        }

#if UNITY_EDITOR
        public void Configure(int health)
        {
            maxHealth = health;
        }
#endif
    }
}
