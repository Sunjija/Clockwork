using System.Collections;
using UnityEngine;

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

            bool valid = openingValid && caligoRouteValid;
            Debug.Log(valid ? "CLOCKWORK_RUNTIME_SMOKE_OK" : "CLOCKWORK_RUNTIME_SMOKE_FAILED");
            Application.Quit(valid ? 0 : 2);
        }
    }
}
