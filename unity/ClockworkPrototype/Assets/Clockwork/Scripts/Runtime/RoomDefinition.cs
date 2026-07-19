using UnityEngine;

namespace Clockwork
{
    [CreateAssetMenu(menuName = "Clockwork/Room Definition")]
    public sealed class RoomDefinition : ScriptableObject
    {
        [SerializeField] private string roomId;
        [SerializeField] private string displayName;
        [SerializeField] private Rect cameraBounds;
        [SerializeField] private string musicCueId;

        public string RoomId => roomId;
        public string DisplayName => displayName;
        public Rect CameraBounds => cameraBounds;
        public string MusicCueId => musicCueId;

#if UNITY_EDITOR
        public void Configure(string id, string label, Rect bounds, string cueId)
        {
            roomId = id;
            displayName = label;
            cameraBounds = bounds;
            musicCueId = cueId;
        }
#endif
    }
}
