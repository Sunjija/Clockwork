using System.Collections.Generic;

namespace Clockwork
{
    // This is the single runtime index of room ids backed by playable Unity scenes.
    // Gates to ids absent from this registry intentionally remain data-only.
    public static class RoomSceneRegistry
    {
        private static readonly Dictionary<string, string> Scenes = new Dictionary<string, string>
        {
            { "limbus", "Limbus" },
            { "limbus-caligo-bridge", "LimbusCaligoBridge" },
            { "caligo-maintenance-shaft", "CaligoMaintenanceShaft" },
            { "caligo", "CaligoVillage" },
            { "caligo-plaza", "CaligoPlaza" },
            { "caligo-drop-shaft", "CaligoDropShaft" },
            { "caligo-village-exterior-registered", "CaligoVillageExteriorRegistered" },
            { "caligo-gate-watch-registered", "CaligoGateWatchRegistered" },
            { "limbus-caligo-bridge-registered", "LimbusCaligoBridgeRegistered" },
            { "limbus-bridge-combat-registered", "LimbusBridgeCombatRegistered" },
            { "limbus-scrap-plain-registered", "LimbusScrapPlainRegistered" },
            { "morbi-workshop-registered", "MorbiWorkshopRegistered" }
        };

        public static bool Contains(string roomId)
        {
            return roomId != null && Scenes.ContainsKey(roomId);
        }

        public static bool TryGetScene(string roomId, out string sceneName)
        {
            if (roomId == null)
            {
                sceneName = null;
                return false;
            }

            return Scenes.TryGetValue(roomId, out sceneName);
        }
    }
}
