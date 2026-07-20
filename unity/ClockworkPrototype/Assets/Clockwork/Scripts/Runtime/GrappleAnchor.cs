using UnityEngine;

namespace Clockwork
{
    public sealed class GrappleAnchor : MonoBehaviour
    {
        [SerializeField] private float selectionPriority;

        public float SelectionPriority => selectionPriority;

#if UNITY_EDITOR
        public void Configure(float priority)
        {
            selectionPriority = priority;
        }
#endif
    }
}
