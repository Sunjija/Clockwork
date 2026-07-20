using UnityEngine;
using UnityEngine.InputSystem;

namespace Clockwork
{
    public sealed class PrototypeHud : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private RepairSavePoint savePoint;
        [SerializeField] private TiqueHealth health;
        [SerializeField] private TiqueEnergyGauge energy;
        [SerializeField] private MysteryPartPickup partPickup;
        private GUIStyle panelStyle;
        private GUIStyle titleStyle;
        private GUIStyle textStyle;
        private bool resetRequested;

        private void Update()
        {
            if (Keyboard.current != null && Keyboard.current.f1Key.wasPressedThisFrame)
            {
                RequestReset();
            }
            if (Keyboard.current != null && Keyboard.current.f2Key.wasPressedThisFrame)
            {
                GameSession.Instance?.LoadGrappleLab();
            }
            if (Keyboard.current != null && Keyboard.current.f3Key.wasPressedThisFrame)
            {
                GameSession.Instance?.LoadCombatLab();
            }
        }

        private void OnGUI()
        {
            EnsureStyles();
            Rect panel = new Rect(Screen.width - 330f, 18f, 312f, 326f);
            GUI.Box(panel, GUIContent.none, panelStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 12f, 280f, 24f), "CLOCKWORK / Unity Foundation", titleStyle);
            GUI.Label(new Rect(panel.x + 16f, panel.y + 42f, 280f, 76f),
                "A/D Move   Z Jump / Double Jump\nX Attack   C Dash   W Interact\n1 Fist   2 Greatsword   3 Hammer\nH Hitboxes   R Reload", textStyle);
            string hearts = health == null
                ? "-"
                : new string('●', health.CurrentHealth) + new string('○', Mathf.Max(0, health.MaxHealth - health.CurrentHealth));
            GUI.Label(new Rect(panel.x + 16f, panel.y + 124f, 280f, 20f), $"HP: {hearts}", titleStyle);
            string weapon = combat == null ? "-" : combat.SelectedWeaponName;
            if (combat != null && combat.IsWeaponTransitionQueued)
            {
                weapon += $" > {combat.PendingWeaponName} (-{combat.PendingTransitionEnergyCost:0})";
            }
            GUI.Label(new Rect(panel.x + 16f, panel.y + 144f, 280f, 20f), $"Weapon: {weapon}", titleStyle);
            string state = GameSession.Instance != null && GameSession.Instance.HasFlag(GameFlagIds.TiqueRepaired)
                ? "Tique: repaired" : "Tique: critical damage";
            if (GameSession.Instance != null && GameSession.Instance.HasFlag(GameFlagIds.MysteryPartIdentified))
            {
                state += " / Part: MOD attached";
            }
            else if (GameSession.Instance != null && GameSession.Instance.HasFlag(GameFlagIds.LimbusMysteryPart))
            {
                state += " / Part: unidentified";
            }
            if (savePoint != null && savePoint.PlayerNearby) state += " / W: repair and save";
            if (partPickup != null && partPickup.PlayerNearby && !partPickup.Collected) state += " / W: take part";
            GUI.Label(new Rect(panel.x + 16f, panel.y + 164f, 280f, 20f), state, textStyle);
            DrawComboGauge(new Rect(panel.x + 16f, panel.y + 190f, 280f, 12f));
            DrawEnergyGauge(new Rect(panel.x + 16f, panel.y + 210f, 280f, 16f));
            GUI.enabled = !resetRequested && GameSession.Instance != null
                && !GameSession.Instance.IsTransitioning;
            if (GUI.Button(new Rect(panel.x + 16f, panel.y + 234f, 280f, 24f), "RESET TO START  [F1]"))
            {
                RequestReset();
            }
            if (GUI.Button(new Rect(panel.x + 16f, panel.y + 262f, 280f, 24f), "GRAPPLE LAB  [F2]"))
            {
                GameSession.Instance?.LoadGrappleLab();
            }
            if (GUI.Button(new Rect(panel.x + 16f, panel.y + 290f, 280f, 24f), "COMBAT LAB  [F3]"))
            {
                GameSession.Instance?.LoadCombatLab();
            }
            GUI.enabled = true;
        }

        private void DrawComboGauge(Rect rect)
        {
            const int steps = 3;
            const float gap = 5f;
            float width = (rect.width - gap * (steps - 1)) / steps;
            Color previous = GUI.color;
            for (int i = 0; i < steps; i++)
            {
                bool current = combat != null && combat.IsAttacking
                    && i == Mathf.Min(combat.CurrentComboStepIndex, steps - 1);
                bool completed = combat != null && i < combat.CurrentComboStepIndex;
                bool transitionReady = combat != null && combat.IsWeaponTransitionWindow
                    && i == steps - 1;
                GUI.color = current || transitionReady
                        ? new Color(0.98f, 0.72f, 0.22f, 1f)
                        : completed
                            ? new Color(0.72f, 0.5f, 0.18f, 1f)
                            : new Color(0.2f, 0.25f, 0.28f, 1f);
                GUI.DrawTexture(new Rect(rect.x + i * (width + gap), rect.y, width, rect.height),
                    Texture2D.whiteTexture);
            }
            GUI.color = previous;
        }

        private void DrawEnergyGauge(Rect rect)
        {
            int count = energy == null ? 20 : energy.SegmentCount;
            int filled = energy == null ? 0 : energy.FilledSegmentCount;
            int reserved = energy == null || combat == null || !combat.IsWeaponTransitionQueued
                ? 0
                : Mathf.CeilToInt(combat.PendingTransitionEnergyCost / energy.EnergyPerSegment);
            int reservedStart = Mathf.Max(0, filled - reserved);
            const float gap = 2f;
            float width = (rect.width - gap * (count - 1)) / count;
            Color previous = GUI.color;
            for (int i = 0; i < count; i++)
            {
                GUI.color = i >= reservedStart && i < filled && reserved > 0
                    ? new Color(1f, 0.42f, 0.2f, 1f)
                    : i < filled
                        ? new Color(0.95f, 0.72f, 0.24f, 1f)
                        : new Color(0.2f, 0.25f, 0.28f, 1f);
                GUI.DrawTexture(new Rect(rect.x + i * (width + gap), rect.y, width, rect.height),
                    Texture2D.whiteTexture);
            }
            GUI.color = previous;
        }

        private void RequestReset()
        {
            if (resetRequested || GameSession.Instance == null) return;
            resetRequested = GameSession.Instance.ResetToOpening();
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
        public void Configure(
            TiqueCombat playerCombat,
            RepairSavePoint roomSavePoint,
            TiqueHealth playerHealth,
            MysteryPartPickup roomPartPickup = null)
        {
            combat = playerCombat;
            energy = playerCombat == null ? null : playerCombat.GetComponent<TiqueEnergyGauge>();
            savePoint = roomSavePoint;
            health = playerHealth;
            partPickup = roomPartPickup;
        }
#endif
    }
}
