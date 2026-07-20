using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Clockwork
{
    [Serializable]
    public sealed class GameSaveData
    {
        public int schemaVersion = 1;
        public string roomId = "caligo-maintenance-shaft";
        public string spawnId = "entry-limbus";
        public List<string> flags = new List<string>();
        public List<string> abilities = new List<string>();
    }

    public static class GameFlagIds
    {
        public const string TiqueRepaired = "TIQUE_REPAIRED";
    }

    public sealed class GameSession : MonoBehaviour
    {
        private const string SaveFileName = "clockwork-save-01.json";
        private static GameSession instance;

        [SerializeField] private GameSaveData current = new GameSaveData();
        private bool diskAccessEnabled = true;

        public static GameSession Instance => instance;
        public GameSaveData Current => current;
        public event Action<string, bool> FlagChanged;

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
            diskAccessEnabled = !Environment.GetCommandLineArgs().Contains("-clockworkSmokeTest");
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
