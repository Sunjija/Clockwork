using System;
using System.Collections;
using UnityEngine;

namespace Clockwork
{
    public sealed class TiqueSpriteVfx : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private TiqueMotor motor;
        [SerializeField] private Texture2D hitSheet;
        [SerializeField] private Texture2D sparkSheet;
        [SerializeField] private Texture2D explosionSheet;
        [SerializeField] private Texture2D slashSheet;

        private void OnEnable()
        {
            Subscribe();
        }

        private void OnDisable()
        {
            Unsubscribe();
        }

        public void Configure(
            TiqueCombat sourceCombat,
            TiqueMotor sourceMotor,
            Texture2D hit,
            Texture2D sparks,
            Texture2D explosion,
            Texture2D slash)
        {
            Unsubscribe();
            combat = sourceCombat;
            motor = sourceMotor;
            hitSheet = hit;
            sparkSheet = sparks;
            explosionSheet = explosion;
            slashSheet = slash;
            Subscribe();
        }

        private void Subscribe()
        {
            if (!isActiveAndEnabled || combat == null) return;
            combat.AttackStepStarted -= OnAttackStepStarted;
            combat.AttackLanded -= OnAttackLanded;
            combat.WeaponTransitionStarted -= OnWeaponTransitionStarted;
            combat.AttackStepStarted += OnAttackStepStarted;
            combat.AttackLanded += OnAttackLanded;
            combat.WeaponTransitionStarted += OnWeaponTransitionStarted;
        }

        private void Unsubscribe()
        {
            if (combat == null) return;
            combat.AttackStepStarted -= OnAttackStepStarted;
            combat.AttackLanded -= OnAttackLanded;
            combat.WeaponTransitionStarted -= OnWeaponTransitionStarted;
        }

        private void OnAttackStepStarted(int stepIndex, int stepCount, bool isTransition)
        {
            string attackId = combat.CurrentAttack?.AttackId ?? string.Empty;
            if (!attackId.StartsWith("greatsword", StringComparison.Ordinal)) return;

            float facing = motor == null ? 1f : motor.Facing;
            Vector3 position = transform.position + new Vector3(0.56f * facing, 0.46f, 0f);
            StartCoroutine(PlaySheet(
                slashSheet, 64, 47, 18f, position, 1.2f, facing < 0f, Color.white));
        }

        private void OnAttackLanded(CombatHitResult hit)
        {
            string attackId = combat.CurrentAttack?.AttackId ?? string.Empty;
            Vector3 position = hit.Enemy == null
                ? transform.position + Vector3.up * 0.45f
                : hit.Enemy.transform.position + Vector3.up * 0.52f;

            if (attackId.StartsWith("hammer", StringComparison.Ordinal))
            {
                StartCoroutine(PlaySheet(
                    explosionSheet, 64, 64, 22f, position, 0.82f, false, Color.white));
                return;
            }

            Color tint = attackId == "fist-finisher"
                ? new Color(1f, 0.76f, 0.28f, 1f)
                : Color.white;
            StartCoroutine(PlaySheet(hitSheet, 64, 64, 24f, position, 0.7f, false, tint));
        }

        private void OnWeaponTransitionStarted(float lentiumCost)
        {
            Vector3 position = transform.position + Vector3.up * 0.42f;
            StartCoroutine(PlaySheet(
                sparkSheet, 64, 64, 30f, position, 0.78f, false,
                new Color(0.55f, 0.96f, 1f, 1f)));
        }

        private static IEnumerator PlaySheet(
            Texture2D sheet,
            int frameWidth,
            int frameHeight,
            float framesPerSecond,
            Vector3 position,
            float scale,
            bool flipX,
            Color tint)
        {
            if (sheet == null || frameWidth <= 0 || frameHeight <= 0) yield break;

            int columns = sheet.width / frameWidth;
            int rows = sheet.height / frameHeight;
            if (columns <= 0 || rows <= 0) yield break;

            Sprite[] frames = new Sprite[columns * rows];
            int index = 0;
            for (int row = rows - 1; row >= 0; row--)
            {
                for (int column = 0; column < columns; column++)
                {
                    Rect rect = new Rect(column * frameWidth, row * frameHeight, frameWidth, frameHeight);
                    frames[index++] = Sprite.Create(sheet, rect, new Vector2(0.5f, 0.5f), 64f);
                }
            }

            GameObject effect = new GameObject("PrototypeSpriteVfx");
            effect.transform.position = position;
            effect.transform.localScale = Vector3.one * scale;
            SpriteRenderer renderer = effect.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 40;
            renderer.flipX = flipX;
            renderer.color = tint;

            float delay = 1f / Mathf.Max(1f, framesPerSecond);
            foreach (Sprite frame in frames)
            {
                renderer.sprite = frame;
                yield return new WaitForSeconds(delay);
            }

            Destroy(effect);
            foreach (Sprite frame in frames) Destroy(frame);
        }
    }
}
