using System;
using System.Collections;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using static UnityEngine.Object;

namespace Clockwork
{
    public static class CombatLabSmokeProbe
    {
        public static IEnumerator Run(Action<bool> complete)
        {
            GameSession session = GameSession.Instance;
            bool loaded = session != null && session.LoadCombatLab();
            float deadline = Time.realtimeSinceStartup + 4f;
            while (loaded && SceneManager.GetActiveScene().name != "CombatLab"
                && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            yield return null;
            yield return null;
            float transitionDeadline = Time.realtimeSinceStartup + 2f;
            while (session != null && session.IsTransitioning
                && Time.realtimeSinceStartup < transitionDeadline)
            {
                yield return null;
            }

            TiqueCombat combat = FindAnyObjectByType<TiqueCombat>();
            TiqueComboPulse pulse = FindAnyObjectByType<TiqueComboPulse>();
            EnemyHealth[] dummies = FindObjectsByType<EnemyHealth>(FindObjectsSortMode.None)
                .Where(enemy => enemy.name.StartsWith("TrainingDummy", StringComparison.Ordinal))
                .ToArray();
            bool valid = loaded && SceneManager.GetActiveScene().name == "CombatLab"
                && combat != null && pulse != null && dummies.Length == 3
                && dummies.All(dummy => dummy.Indestructible && dummy.IsAlive);

            if (valid)
            {
                EnemyHealth target = dummies[0];
                bool defeatedOnce = target.TakeDamage(999, 1f);
                bool defeatedTwice = target.TakeDamage(999, -1f);
                valid &= defeatedOnce && defeatedTwice && target.IsAlive
                    && target.CurrentHealth == target.MaxHealth;
            }

            Debug.Log($"CLOCKWORK_COMBAT_LAB_PROBE valid={valid} dummies={dummies.Length} "
                + $"comboPulse={pulse != null}");
            complete(valid);
        }
    }
}
