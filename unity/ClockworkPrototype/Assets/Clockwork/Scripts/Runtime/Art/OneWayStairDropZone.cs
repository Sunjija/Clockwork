using System.Collections;
using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(BoxCollider2D))]
    public sealed class OneWayStairDropZone : MonoBehaviour
    {
        [SerializeField] private Collider2D oneWayPlatform;
        [SerializeField] private float ignoreDuration = 0.4f;
        [SerializeField] private float downwardNudge = 0.18f;
        [SerializeField] private float downwardSpeed = 2f;

        private Collider2D ignoredPlayerCollider;
        private Coroutine restoreRoutine;

        public Collider2D OneWayPlatform => oneWayPlatform;

        private void Reset()
        {
            GetComponent<BoxCollider2D>().isTrigger = true;
        }

        private void OnTriggerStay2D(Collider2D other)
        {
            TiqueMotor player = other.GetComponentInParent<TiqueMotor>();
            if (player == null) return;
            TiqueInputReader input = player.GetComponent<TiqueInputReader>();
            if (input != null && input.DescendPressed) BeginDrop(player);
        }

        public bool BeginDrop(TiqueMotor player)
        {
            if (player == null || oneWayPlatform == null || restoreRoutine != null) return false;
            Collider2D playerCollider = player.GetComponent<Collider2D>();
            Rigidbody2D body = player.GetComponent<Rigidbody2D>();
            if (playerCollider == null || body == null) return false;

            ignoredPlayerCollider = playerCollider;
            Physics2D.IgnoreCollision(playerCollider, oneWayPlatform, true);
            body.position += Vector2.down * downwardNudge;
            body.linearVelocity = new Vector2(body.linearVelocity.x, -downwardSpeed);
            Physics2D.SyncTransforms();
            restoreRoutine = StartCoroutine(RestoreCollision());
            return true;
        }

        private IEnumerator RestoreCollision()
        {
            yield return new WaitForSeconds(ignoreDuration);
            RestoreNow();
        }

        private void OnDisable()
        {
            RestoreNow();
        }

        private void RestoreNow()
        {
            if (ignoredPlayerCollider != null && oneWayPlatform != null)
                Physics2D.IgnoreCollision(ignoredPlayerCollider, oneWayPlatform, false);
            ignoredPlayerCollider = null;
            restoreRoutine = null;
        }

#if UNITY_EDITOR
        public void Configure(Collider2D platform)
        {
            oneWayPlatform = platform;
            GetComponent<BoxCollider2D>().isTrigger = true;
        }
#endif
    }
}
