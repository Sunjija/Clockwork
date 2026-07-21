using System;
using UnityEngine;

namespace Clockwork
{
    [RequireComponent(typeof(AudioSource))]
    public sealed class TiqueAudioFeedback : MonoBehaviour
    {
        [SerializeField] private TiqueCombat combat;
        [SerializeField] private AudioSource audioSource;
        [SerializeField] private AudioClip[] fistImpacts;
        [SerializeField] private AudioClip[] fistHeavyImpacts;
        [SerializeField] private AudioClip[] greatswordSwings;
        [SerializeField] private AudioClip[] hammerImpacts;
        [SerializeField] private AudioClip[] lentiumBursts;

        private int sequence;

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
            AudioSource source,
            AudioClip[] fist,
            AudioClip[] fistHeavy,
            AudioClip[] greatsword,
            AudioClip[] hammer,
            AudioClip[] lentium)
        {
            Unsubscribe();
            combat = sourceCombat;
            audioSource = source;
            fistImpacts = fist;
            fistHeavyImpacts = fistHeavy;
            greatswordSwings = greatsword;
            hammerImpacts = hammer;
            lentiumBursts = lentium;
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
            if (attackId.StartsWith("greatsword", StringComparison.Ordinal))
            {
                Play(greatswordSwings, 0.58f, 0.94f, 1.04f);
            }
        }

        private void OnAttackLanded(CombatHitResult hit)
        {
            string attackId = combat.CurrentAttack?.AttackId ?? string.Empty;
            if (attackId == "fist-finisher")
            {
                Play(fistHeavyImpacts, 0.92f, 0.9f, 0.98f);
            }
            else if (attackId.StartsWith("fist", StringComparison.Ordinal))
            {
                Play(fistImpacts, 0.72f, 0.96f, 1.05f);
            }
            else if (attackId.StartsWith("hammer", StringComparison.Ordinal))
            {
                Play(hammerImpacts, 0.88f, 0.88f, 0.96f);
            }
        }

        private void OnWeaponTransitionStarted(float lentiumCost)
        {
            Play(lentiumBursts, 0.78f, 0.92f, 1.02f);
        }

        private void Play(AudioClip[] clips, float volume, float minPitch, float maxPitch)
        {
            if (audioSource == null || clips == null || clips.Length == 0) return;
            AudioClip clip = clips[sequence++ % clips.Length];
            if (clip == null) return;
            audioSource.pitch = UnityEngine.Random.Range(minPitch, maxPitch);
            audioSource.PlayOneShot(clip, volume);
        }
    }
}
