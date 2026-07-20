using UnityEngine;

namespace Clockwork
{
    public sealed class DirectionalCameraTarget : MonoBehaviour
    {
        [SerializeField] private Transform player;
        [SerializeField] private TiqueMotor motor;
        [SerializeField] private float horizontalLead = 0.8f;
        [SerializeField] private float response = 4.5f;

        public void Configure(Transform targetPlayer, TiqueMotor targetMotor, float lead)
        {
            player = targetPlayer;
            motor = targetMotor;
            horizontalLead = Mathf.Max(0f, lead);
            Snap();
        }

        private void LateUpdate()
        {
            if (player == null || motor == null) return;
            Vector3 target = player.position + Vector3.right * (motor.Facing * horizontalLead);
            target.z = 0f;
            transform.position = Vector3.Lerp(
                transform.position, target, 1f - Mathf.Exp(-response * Time.unscaledDeltaTime));
        }

        private void Snap()
        {
            if (player == null || motor == null) return;
            Vector3 target = player.position + Vector3.right * (motor.Facing * horizontalLead);
            transform.position = new Vector3(target.x, target.y, 0f);
        }
    }
}
