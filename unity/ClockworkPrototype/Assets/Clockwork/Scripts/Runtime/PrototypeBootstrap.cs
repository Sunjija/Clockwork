using System.Linq;
using UnityEngine;

namespace Clockwork
{
    public sealed class PrototypeBootstrap : MonoBehaviour
    {
        private static bool smokeStarted;

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Physics2D.gravity = Vector2.zero;

            if (!smokeStarted && System.Environment.GetCommandLineArgs().Contains("-clockworkSmokeTest"))
            {
                smokeStarted = true;
                DontDestroyOnLoad(gameObject);
                StartCoroutine(PrototypeSmokeTestRunner.Run());
            }
        }
    }
}
