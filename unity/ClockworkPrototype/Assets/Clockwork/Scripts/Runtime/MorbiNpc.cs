using UnityEngine;

namespace Clockwork
{
    // Morbi, the Caligo engineer. Dialogue is deliberately dry (canon §8 tone).
    // Identification beat (v5.5 B-3): the Limbus mystery part is revealed as a MOD here.
    public sealed class MorbiNpc : MonoBehaviour
    {
        private static readonly string[] GreetingLines =
        {
            "모르비: …움직이는 고물은 오랜만이군.",
            "모르비: 정수장치가 멈춘 지 오래다. 물이 끊겼어.",
            "모르비: 림부스에서 쓸 만한 부품을 보면 주워 와라."
        };

        private static readonly string[] IdentifyLines =
        {
            "모르비: …그 부품, 이리 줘 봐.",
            "모르비: 개조 부품이군. 인간은 못 쓰는 물건이야.",
            "모르비: 네 몸에는 맞는다. 장착해 주지.",
            "기록: 개조 장착 — 유형 미상. 제공자: 모르비."
        };

        private static readonly string[] QuestLines =
        {
            "모르비: 물이 필요하다. 교차로 너머, 정수장치다.",
            "모르비: 잠긴 문은 신경 쓰지 마라. 물이 빠지면 열린다."
        };

        private TiqueInputReader nearbyInput;
        private string[] activeLines;
        private int lineIndex;
        private bool identificationPending;
        private GUIStyle panelStyle;
        private GUIStyle lineStyle;
        private GUIStyle hintStyle;

        public bool PlayerNearby => nearbyInput != null;
        public bool IsTalking => activeLines != null;

        private void Update()
        {
            if (nearbyInput != null && nearbyInput.InteractPressed)
            {
                Interact();
            }
        }

        private void OnTriggerEnter2D(Collider2D other)
        {
            TiqueMotor motor = other.GetComponentInParent<TiqueMotor>();
            if (motor != null)
            {
                nearbyInput = motor.GetComponent<TiqueInputReader>();
            }
        }

        private void OnTriggerExit2D(Collider2D other)
        {
            if (other.GetComponentInParent<TiqueMotor>() != null)
            {
                nearbyInput = null;
                EndDialogue();
            }
        }

        public void Interact()
        {
            if (!IsTalking)
            {
                activeLines = SelectLines();
                lineIndex = 0;
                return;
            }

            lineIndex++;
            if (lineIndex >= activeLines.Length)
            {
                EndDialogue();
            }
        }

        private string[] SelectLines()
        {
            GameSession session = GameSession.Instance;
            bool hasPart = session != null && session.HasFlag(GameFlagIds.LimbusMysteryPart);
            bool identified = session != null && session.HasFlag(GameFlagIds.MysteryPartIdentified);
            if (hasPart && !identified)
            {
                identificationPending = true;
                return IdentifyLines;
            }
            return hasPart ? QuestLines : GreetingLines;
        }

        private void EndDialogue()
        {
            activeLines = null;
            lineIndex = 0;
            if (identificationPending)
            {
                identificationPending = false;
                GameSession.Instance?.SetFlag(GameFlagIds.MysteryPartIdentified, true);
            }
        }

        private void OnGUI()
        {
            EnsureStyles();
            if (IsTalking)
            {
                float width = Mathf.Min(680f, Screen.width - 80f);
                Rect panel = new Rect((Screen.width - width) * 0.5f, Screen.height - 118f, width, 84f);
                GUI.Box(panel, GUIContent.none, panelStyle);
                GUI.Label(new Rect(panel.x + 20f, panel.y + 16f, width - 40f, 40f), activeLines[lineIndex], lineStyle);
                GUI.Label(new Rect(panel.x + 20f, panel.y + 52f, width - 40f, 22f), "W ▸", hintStyle);
            }
            else if (PlayerNearby)
            {
                Rect hint = new Rect(Screen.width * 0.5f - 60f, Screen.height - 64f, 120f, 24f);
                GUI.Label(hint, "W: 대화", hintStyle);
            }
        }

        private void EnsureStyles()
        {
            if (panelStyle != null) return;
            panelStyle = new GUIStyle(GUI.skin.box);
            panelStyle.normal.background = Texture2D.blackTexture;
            lineStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 15,
                normal = { textColor = new Color(0.92f, 0.9f, 0.84f) }
            };
            hintStyle = new GUIStyle(GUI.skin.label)
            {
                fontSize = 12,
                alignment = TextAnchor.MiddleCenter,
                normal = { textColor = new Color(0.96f, 0.82f, 0.48f) }
            };
        }
    }
}
