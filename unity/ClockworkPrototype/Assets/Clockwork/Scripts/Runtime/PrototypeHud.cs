using UnityEngine;

namespace Clockwork
{
    public sealed class PrototypeHud : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private RepairSavePoint savePoint;
        private GUIStyle panelStyle;
        private GUIStyle titleStyle;
        private GUIStyle textStyle;

        private void OnGUI()
        {
            EnsureStyles();
            Rect panel = new Rect(Screen.width - 330f, 18f, 312f, 166f);
            GUI.Box(panel, GUIContent.none, panelStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 12f, 280f, 24f), "CLOCKWORK / Unity Foundation", titleStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 42f, 280f, 76f),
                "A/D Move   Z Jump / Double Jump\nX Attack   C Dash   W Interact\n1 Fist   2 Greatsword   3 Hammer\nH Hitboxes   R Reload", textStyle);
            string weapon = combat == null ? "-" : combat.SelectedWeaponName;
            GUI.Label(new Rect(panel.x + 16f, panel.y + 124f, 280f, 20f), $"Weapon: {weapon}", titleStyle);
            string state = GameSession.Instance != null && GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired)
                ? "Tique: repaired" : "Tique: damaged";
            if (savePoint != null && savePoint.PlayerNearby) state += " / W: repair and save";
            GUI.Label(new Rect(panel.x + 16f, panel.y + 144f, 280f, 20f), state, textStyle);
        }

        private void EnsureStyles()
        {
            if (panelStyle != null) return;
            panelStyle = new GUIStyle(GUI.skin.box);
            panelStyle.normal.background = Texture2D.blackTexture;
            panelStyle.normal.textColor = Color.white;
            titleStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 13,
                fontStyle = FontStyle.Bold,
                normal = { textColor = new Color(0.96f, 0.82f, 0.48f) }
            };
            textStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 12,
                normal = { textColor = new Color(0.82f, 0.88f, 0.9f) }
            };
        }

#if UNITY_EDITOR
        public void Configure(TiqueCombat playerCombat, RepairSavePoint roomSavePoint)
        {
            combat = playerCombat;
            savePoint = roomSavePoint;
        }
#endif
    }
}
