using UnityEngine;

namespace Clockwork
{
    public sealed class PrototypeHud : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        private GUIStyle panelStyle;
        private GUIStyle titleStyle;
        private GUIStyle textStyle;

        private void OnGUI()
        {
            EnsureStyles();
            Rect panel = new Rect(Screen.width - 310f, 18f, 292f, 142f);
            GUI.Box(panel, GUIContent.none, panelStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 12f, 260f, 24f), "CLOCKWORK / Unity Prototype", titleStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 42f, 260f, 74f),
                "A/D 이동   Z 점프·더블점프\nX 공격   C 대시   H 히트박스\n1 주먹   2 대검   3 망치   R 재시작", textStyle);
            string weapon = combat == null ? "-" : combat.SelectedWeaponName;
            GUI.Label(new Rect(panel.x + 16f, panel.y + 116f, 260f, 20f), $"현재 무기: {weapon}", titleStyle);
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
        public void Configure(TiqueCombat playerCombat)
        {
            combat = playerCombat;
        }
#endif
    }
}

