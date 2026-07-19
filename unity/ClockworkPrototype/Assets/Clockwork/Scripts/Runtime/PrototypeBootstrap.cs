using System.Collections;
using System.Linq;
using UnityEngine;

namespace Clockwork
{
    public sealed class PrototypeBootstrap : MonoBehaviour
    {
        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Physics2D.gravity = Vector2.zero;

            if (System.Environment.GetCommandLineArgs().Contains("-clockworkSmokeTest"))
            {
                StartCoroutine(RunSmokeTest());
            }
        }

        private static IEnumerator RunSmokeTest()
        {
            yield return null;
            yield return new WaitForSecondsRealtime(0.25f);
            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            TiqueCombat combat = FindAnyObjectByType<TiqueCombat>();
            TiqueSpriteAnimator animator = FindAnyObjectByType<TiqueSpriteAnimator>();
            TiqueInputReader input = FindAnyObjectByType<TiqueInputReader>();
            GameSession session = FindAnyObjectByType<GameSession>();
            RepairSavePoint savePoint = FindAnyObjectByType<RepairSavePoint>();
            UnityEngine.Tilemaps.TilemapCollider2D tilemapCollider = FindAnyObjectByType<UnityEngine.Tilemaps.TilemapCollider2D>();
            SpriteRenderer sprite = animator == null ? null : animator.GetComponent<SpriteRenderer>();
            Vector3 initialPosition = motor == null ? Vector3.zero : motor.transform.position;
            yield return new WaitForSecondsRealtime(1.5f);
            Vector3 settledPosition = motor == null ? Vector3.zero : motor.transform.position;
            Debug.Log($"CLOCKWORK_PLAYER_PROBE initial={initialPosition} settled={settledPosition} grounded={motor != null && motor.Grounded}");
            savePoint?.Activate();
            bool progressionValid = session != null && session.HasFlag(GameFlagIds.TiqueRepaired);
            bool valid = motor != null && combat != null && animator != null && input != null
                && sprite != null && sprite.enabled && sprite.sprite != null && tilemapCollider != null
                && settledPosition.y > -3.2f && progressionValid;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
