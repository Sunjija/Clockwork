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
            SpriteRenderer sprite = animator == null ? null : animator.GetComponent<SpriteRenderer>();
            bool valid = motor != null && combat != null && animator != null && sprite != null && sprite.sprite != null;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
