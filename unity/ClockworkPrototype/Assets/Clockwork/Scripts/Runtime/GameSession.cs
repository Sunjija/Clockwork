using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Clockwork
{
    [Serializable]
    public sealed class GameSaveData
    {
        public int schemaVersion = 1;
        public string roomId = "limbus";
        public string spawnId = "start-awakening";
        public List<string> flags = new List<string>();
        public List<string> abilities = new List<string>();
    }

    public static class GameFlagIds
    {
        public const string TiqueRepaired = "TIQUE_REPAIRED";
        public const string LimbusMysteryPart = "LIMBUS_MYSTERY_PART";
        public const string MysteryPartIdentified = "LIMBUS_MYSTERY_PART_IDENTIFIED";
    }

    public sealed class GameSession : MonoBehaviour
    {
        private const string SaveFileName = "clockwork-save-01.json";
        private static GameSession instance;

        [SerializeField] private GameSaveData current = new GameSaveData();
        private bool diskAccessEnabled = true;

        public static GameSession Instance => instance;
        public GameSaveData Current => current;
        public int RuntimeHealth { get; set; } = -1;
        public float RuntimeEnergy { get; set; } = -1f;
        public string PendingSpawnId { get; private set; }
        public string PendingSceneName { get; private set; }
        public event Action<string, bool> FlagChanged;

        public static bool RoomSceneExists(string roomId)
        {
            return RoomSceneRegistry.Contains(roomId);
        }

        private string SavePath => Path.Combine(Application.persistentDataPath, SaveFileName);

        private void Awake()
        {
            if (instance != null && instance != this)
            {
                Destroy(gameObject);
                return;
            }

            instance = this;
            DontDestroyOnLoad(gameObject);
            string[] arguments = Environment.GetCommandLineArgs();
            bool isolatedOpening = arguments.Contains("-clockworkSmokeTest")
                || arguments.Contains("-clockworkFreshOpening");
            diskAccessEnabled = !isolatedOpening;
            if (diskAccessEnabled)
            {
                Load();
            }
        }

        public bool HasFlag(string flagId)
        {
            return current.flags.Contains(flagId);
        }

        public void SetFlag(string flagId, bool value)
        {
            bool changed;
            if (value)
            {
                changed = !current.flags.Contains(flagId);
                if (changed) current.flags.Add(flagId);
            }
            else
            {
                changed = current.flags.Remove(flagId);
            }

            if (changed)
            {
                FlagChanged?.Invoke(flagId, value);
            }
        }

        public string ConsumePendingSpawn(string sceneName)
        {
            if (PendingSceneName != sceneName) return null;
            string spawnId = PendingSpawnId;
            PendingSpawnId = null;
            PendingSceneName = null;
            return spawnId;
        }

        public bool IsTransitioning { get; private set; }

        public bool LoadRoom(string roomId, string spawnId)
        {
            if (!RoomSceneRegistry.TryGetScene(roomId, out string sceneName)) return false;
            if (IsTransitioning) return true;
            StartCoroutine(TransitionRoutine(sceneName, spawnId));
            return true;
        }

        public bool LoadGrappleLab()
        {
            if (IsTransitioning) return false;
            StartCoroutine(TransitionRoutine("GrappleLab", "lab-start"));
            return true;
        }

        public bool LoadCombatLab()
        {
            if (IsTransitioning) return false;
            StartCoroutine(TransitionRoutine("CombatLab", "lab-start"));
            return true;
        }

        private IEnumerator TransitionRoutine(string sceneName, string spawnId)
        {
            IsTransitioning = true;
            PendingSpawnId = spawnId;
            PendingSceneName = sceneName;
            yield return ScreenFader.Instance.FadeRoutine(1f, 0.18f);
            SceneManager.LoadScene(sceneName);
            yield return null;
            yield return ScreenFader.Instance.FadeRoutine(0f, 0.25f);
            IsTransitioning = false;
        }

        public void RespawnAtLastSave()
        {
            RuntimeHealth = -1;
            if (!LoadRoom(current.roomId, current.spawnId))
            {
                LoadRoom("limbus", "start-awakening");
            }
        }

        public bool ResetToOpening()
        {
            if (IsTransitioning) return false;

            List<string> clearedFlags = new List<string>(current.flags);
            current = new GameSaveData();
            RuntimeHealth = -1;
            RuntimeEnergy = -1f;

            if (diskAccessEnabled)
            {
                try
                {
                    if (File.Exists(SavePath)) File.Delete(SavePath);
                }
                catch (Exception exception)
                {
                    Debug.LogError($"CLOCKWORK save reset failed: {exception.Message}");
                    return false;
                }
            }

            foreach (string flagId in clearedFlags)
            {
                FlagChanged?.Invoke(flagId, false);
            }

            Debug.Log("CLOCKWORK session reset to opening");
            return LoadRoom("limbus", "start-awakening");
        }

        private void Start()
        {
            // Continue from the saved room when the boot scene is a different room.
            if (!diskAccessEnabled) return;
            if (!RoomSceneRegistry.TryGetScene(current.roomId, out string savedScene)) return;
            if (SceneManager.GetActiveScene().name != savedScene)
            {
                LoadRoom(current.roomId, current.spawnId);
            }
        }

        public void SaveAt(string roomId, string spawnId)
        {
            current.roomId = roomId;
            current.spawnId = spawnId;
            if (!diskAccessEnabled) return;

            try
            {
                File.WriteAllText(SavePath, JsonUtility.ToJson(current, true));
            }
            catch (Exception exception)
            {
                Debug.LogError($"CLOCKWORK save failed: {exception.Message}");
            }
        }

        private void Load()
        {
            if (!File.Exists(SavePath)) return;
            try
            {
                GameSaveData loaded = JsonUtility.FromJson<GameSaveData>(File.ReadAllText(SavePath));
                if (loaded != null && loaded.schemaVersion == current.schemaVersion)
                {
                    current = loaded;
                }
                else if (loaded != null)
                {
                    // Preserve the incompatible save so the next SaveAt does not silently destroy it.
                    File.Copy(SavePath, $"{SavePath}.v{loaded.schemaVersion}.bak", true);
                    Debug.LogWarning(
                        $"CLOCKWORK save schema {loaded.schemaVersion} != {current.schemaVersion}; backed up and starting fresh.");
                }
            }
            catch (Exception exception)
            {
                Debug.LogWarning($"CLOCKWORK save ignored: {exception.Message}");
            }
        }
    }
}
