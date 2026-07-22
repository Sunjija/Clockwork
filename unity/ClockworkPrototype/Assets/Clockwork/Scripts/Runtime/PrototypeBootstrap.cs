using System.Linq;
using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    public sealed class PrototypeBootstrap : MonoBehaviour
    {
        private static bool smokeStarted;
        private static bool combatLabStarted;
        private static bool caligoPreviewStarted;
        private static bool bridgeGatePreviewStarted;
        private static bool scrapPlainPreviewStarted;

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

            if (!combatLabStarted
                && System.Environment.GetCommandLineArgs().Contains("-clockworkCombatLab"))
            {
                combatLabStarted = true;
                StartCoroutine(OpenCombatLab());
            }

            if (!caligoPreviewStarted
                && System.Environment.GetCommandLineArgs().Contains("-clockworkCaligoPreview"))
            {
                caligoPreviewStarted = true;
                DontDestroyOnLoad(gameObject);
                StartCoroutine(OpenCaligoPreview());
            }

            if (!bridgeGatePreviewStarted
                && System.Environment.GetCommandLineArgs().Contains("-clockworkBridgeGatePreview"))
            {
                bridgeGatePreviewStarted = true;
                DontDestroyOnLoad(gameObject);
                StartCoroutine(OpenBridgeGatePreview());
            }

            if (!scrapPlainPreviewStarted
                && System.Environment.GetCommandLineArgs().Contains("-clockworkScrapPlainPreview"))
            {
                scrapPlainPreviewStarted = true;
                DontDestroyOnLoad(gameObject);
                StartCoroutine(OpenScrapPlainPreview());
            }
        }

        private static IEnumerator OpenCombatLab()
        {
            yield return null;
            if (SceneManager.GetActiveScene().name == "CombatLab") yield break;

            float deadline = Time.realtimeSinceStartup + 2f;
            while (GameSession.Instance == null && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            GameSession.Instance?.LoadCombatLab();
        }

        private static IEnumerator OpenCaligoPreview()
        {
            yield return null;
            if (SceneManager.GetActiveScene().name == "CaligoPlaza") yield break;

            float deadline = Time.realtimeSinceStartup + 2f;
            while (GameSession.Instance == null && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            if (GameSession.Instance == null
                || !GameSession.Instance.LoadRoom("caligo-plaza", "entry-workshop"))
            {
                yield break;
            }

            deadline = Time.realtimeSinceStartup + 3f;
            while (SceneManager.GetActiveScene().name != "CaligoPlaza"
                && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            yield return new WaitForSecondsRealtime(1f);

            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            SpriteRenderer tique = motor == null ? null : motor.GetComponentInChildren<SpriteRenderer>();
            SpriteRenderer floor = GameObject.Find("FloorLeft")?.GetComponent<SpriteRenderer>();
            Camera camera = Camera.main;
            Debug.Log($"CLOCKWORK_CALIGO_PREVIEW_READY " +
                $"grounded={(motor != null && motor.Grounded)} " +
                $"pos={(motor == null ? Vector3.zero : motor.transform.position)} " +
                $"camera={(camera == null ? Vector3.zero : camera.transform.position)} " +
                $"tiqueBounds={(tique == null ? default : tique.bounds)} " +
                $"floorBounds={(floor == null ? default : floor.bounds)} " +
                $"tiqueScreen={(camera == null || motor == null ? Vector3.zero : camera.WorldToScreenPoint(motor.transform.position))}");
        }

        private static IEnumerator OpenBridgeGatePreview()
        {
            yield return null;
            if (SceneManager.GetActiveScene().name == "LimbusCaligoBridgeRegistered") yield break;

            float deadline = Time.realtimeSinceStartup + 2f;
            while (GameSession.Instance == null && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            GameSession.Instance?.LoadRoom(
                "limbus-caligo-bridge-registered", "CaligoGateExit");
        }

        private static IEnumerator OpenScrapPlainPreview()
        {
            yield return null;
            if (SceneManager.GetActiveScene().name == "LimbusScrapPlainRegistered") yield break;

            float deadline = Time.realtimeSinceStartup + 2f;
            while (GameSession.Instance == null && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            GameSession.Instance?.LoadRoom(
                "limbus-scrap-plain-registered", "BridgeEntry");
        }
    }
}
