using UnityEngine;
using UnityEngine.InputSystem;

namespace Clockwork
{
    public sealed class TiqueInputReader : MonoBehaviour
    {
        private InputActionMap gameplay;
        private InputAction move;
        private InputAction jump;
        private InputAction attack;
        private InputAction dash;
        private InputAction interact;
        private InputAction descend;
        private InputAction slot1;
        private InputAction slot2;
        private InputAction slot3;
        private InputAction debugHitboxes;
        private InputAction reload;
        private InputAction grapple;

        public float Move => move?.ReadValue<float>() ?? 0f;
        public bool JumpHeld => jump?.IsPressed() ?? false;
        public bool JumpPressed => jump?.WasPressedThisFrame() ?? false;
        public bool AttackPressed => attack?.WasPressedThisFrame() ?? false;
        public bool DashPressed => dash?.WasPressedThisFrame() ?? false;
        public bool InteractPressed => interact?.WasPressedThisFrame() ?? false;
        public bool DescendPressed => descend?.WasPressedThisFrame() ?? false;
        public bool Slot1Pressed => slot1?.WasPressedThisFrame() ?? false;
        public bool Slot2Pressed => slot2?.WasPressedThisFrame() ?? false;
        public bool Slot3Pressed => slot3?.WasPressedThisFrame() ?? false;
        public bool DebugHitboxesPressed => debugHitboxes?.WasPressedThisFrame() ?? false;
        public bool ReloadPressed => reload?.WasPressedThisFrame() ?? false;
        public bool GrapplePressed => grapple?.WasPressedThisFrame() ?? false;
        public bool GrappleReleased => grapple?.WasReleasedThisFrame() ?? false;

        private void Awake()
        {
            gameplay = new InputActionMap("Gameplay");

            move = gameplay.AddAction("Move", InputActionType.Value);
            move.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/a")
                .With("Positive", "<Keyboard>/d");
            move.AddCompositeBinding("1DAxis")
                .With("Negative", "<Keyboard>/leftArrow")
                .With("Positive", "<Keyboard>/rightArrow");
            move.AddBinding("<Gamepad>/leftStick/x");
            move.AddBinding("<Gamepad>/dpad/x");

            jump = AddButton("Jump", "<Keyboard>/z", "<Gamepad>/buttonSouth");
            attack = AddButton("Attack", "<Keyboard>/x", "<Gamepad>/buttonWest");
            dash = AddButton("Dash", "<Keyboard>/c", "<Gamepad>/buttonEast");
            interact = AddButton("Interact", "<Keyboard>/w", "<Keyboard>/upArrow", "<Gamepad>/buttonNorth");
            descend = AddButton(
                "Descend", "<Keyboard>/s", "<Keyboard>/downArrow", "<Gamepad>/dpad/down");
            slot1 = AddButton("Weapon1", "<Keyboard>/1");
            slot2 = AddButton("Weapon2", "<Keyboard>/2");
            slot3 = AddButton("Weapon3", "<Keyboard>/3");
            debugHitboxes = AddButton("DebugHitboxes", "<Keyboard>/h");
            reload = AddButton("Reload", "<Keyboard>/r", "<Gamepad>/select");
            grapple = AddButton("Grapple", "<Keyboard>/e", "<Gamepad>/rightShoulder");
        }

        private InputAction AddButton(string name, params string[] bindings)
        {
            InputAction action = gameplay.AddAction(name, InputActionType.Button);
            foreach (string binding in bindings)
            {
                action.AddBinding(binding);
            }
            return action;
        }

        private void OnEnable()
        {
            gameplay?.Enable();
        }

        private void OnDisable()
        {
            gameplay?.Disable();
        }

        private void OnDestroy()
        {
            gameplay?.Dispose();
        }
    }
}
