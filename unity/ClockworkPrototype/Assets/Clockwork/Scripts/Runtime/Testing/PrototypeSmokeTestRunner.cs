using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    public static class PrototypeSmokeTestRunner
    {
        public static IEnumerator Run()
        {
            bool openingValid = false;
            yield return OpeningSmokeProbe.Run(result => openingValid = result);

            bool caligoRouteValid = false;
            yield return CaligoRouteSmokeProbe.Run(result => caligoRouteValid = result);

            bool combatLabValid = false;
            yield return CombatLabSmokeProbe.Run(result => combatLabValid = result);

            bool grappleValid = false;
            yield return GrappleSmokeProbe.Run(result => grappleValid = result);

            bool resetStarted = GameSession.Instance != null && GameSession.Instance.ResetToOpening();
            float resetDeadline = Time.realtimeSinceStartup + 4f;
            while (resetStarted
                && SceneManager.GetActiveScene().name != "Limbus"
                && Time.realtimeSinceStartup < resetDeadline)
            {
                yield return null;
            }
            yield return null;
            yield return null;

            GameSaveData resetData = GameSession.Instance?.Current;
            TiqueHealth resetHealth = Object.FindAnyObjectByType<TiqueHealth>();
            TiqueEnergyGauge resetEnergy = Object.FindAnyObjectByType<TiqueEnergyGauge>();
            bool resetValid = resetStarted
                && SceneManager.GetActiveScene().name == "Limbus"
                && resetData != null
                && resetData.roomId == "limbus"
                && resetData.spawnId == "start-awakening"
                && resetData.flags.Count == 0
                && resetData.abilities.Count == 0
                && resetHealth != null
                && resetHealth.CurrentHealth == resetHealth.DamagedStartingHealth
                && GameSession.Instance.RuntimeHealth == resetHealth.DamagedStartingHealth
                && resetEnergy != null
                && Mathf.Approximately(resetEnergy.CurrentEnergy, 0f)
                && Mathf.Approximately(GameSession.Instance.RuntimeEnergy, 0f);
            Debug.Log(
                $"CLOCKWORK_RESET_PROBE valid={resetValid} scene={SceneManager.GetActiveScene().name} "
                + $"room={resetData?.roomId} spawn={resetData?.spawnId} "
                + $"flags={resetData?.flags.Count} abilities={resetData?.abilities.Count} "
                + $"hp={resetHealth?.CurrentHealth} energy={resetEnergy?.CurrentEnergy}");

            bool valid = openingValid && caligoRouteValid && combatLabValid && grappleValid && resetValid;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
