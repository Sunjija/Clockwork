using System;
using System.Collections;
using System.Linq;
using UnityEngine;
using static UnityEngine.Object;

namespace Clockwork
{
    public static class CaligoRouteSmokeProbe
    {
        public static IEnumerator Run(Action<bool> complete)
        {
            GameSession session = FindAnyObjectByType<GameSession>();
            bool shaftValid = false;
            if (session != null && session.LoadRoom("caligo-maintenance-shaft", "entry-bridge"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor shaftMotor = FindAnyObjectByType<TiqueMotor>();
                RepairSavePoint savePoint = FindAnyObjectByType<RepairSavePoint>();
                yield return new WaitForSecondsRealtime(1f);
                savePoint?.Activate();
                shaftValid = shaftMotor != null && shaftMotor.Grounded
                    && Mathf.Abs(shaftMotor.transform.position.x - 6f) < 1.2f
                    && session.HasFlag(GameFlagIds.TiqueRepaired);
                Debug.Log($"CLOCKWORK_SHAFT_PROBE valid={shaftValid} " +
                    $"pos={(shaftMotor == null ? Vector3.zero : shaftMotor.transform.position)} " +
                    $"repaired={session.HasFlag(GameFlagIds.TiqueRepaired)}");
            }

            bool villageValid = false;
            if (session != null && session.LoadRoom("caligo", "entry-maintenance-shaft"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor villageMotor = FindAnyObjectByType<TiqueMotor>();
                MorbiNpc morbi = FindAnyObjectByType<MorbiNpc>();
                for (int i = 0; morbi != null && i < 8; i++)
                {
                    morbi.Interact();
                }
                yield return new WaitForSecondsRealtime(0.5f);
                villageValid = villageMotor != null && villageMotor.Grounded
                    && Mathf.Abs(villageMotor.transform.position.x - 6f) < 1.2f
                    && morbi != null
                    && session.HasFlag(GameFlagIds.MysteryPartIdentified);
                Debug.Log($"CLOCKWORK_VILLAGE_PROBE valid={villageValid} " +
                    $"identified={session.HasFlag(GameFlagIds.MysteryPartIdentified)} " +
                    $"pos={(villageMotor == null ? Vector3.zero : villageMotor.transform.position)}");
            }

            bool plazaValid = false;
            if (session != null && session.LoadRoom("caligo-plaza", "entry-workshop"))
            {
                yield return new WaitForSecondsRealtime(1f);
                TiqueMotor plazaMotor = FindAnyObjectByType<TiqueMotor>();
                SpriteRenderer tiqueRenderer = plazaMotor == null
                    ? null
                    : plazaMotor.GetComponentInChildren<SpriteRenderer>();
                AmbientNpc2D[] residents = FindObjectsByType<AmbientNpc2D>(FindObjectsSortMode.None);
                ParallaxLayer2D[] plazaLayers = FindObjectsByType<ParallaxLayer2D>(FindObjectsSortMode.None);
                SpriteRenderer plazaFloor = GameObject.Find("FloorLeft")?.GetComponent<SpriteRenderer>();
                Transform plazaMidLayer = GameObject.Find("CaligoMidLayer")?.transform;
                GameObject rejectedRearWalkway = GameObject.Find("RearWalkway3");
                Camera plazaCamera = Camera.main;
                RepairSavePoint plazaCheckpoint = FindAnyObjectByType<RepairSavePoint>();
                RoomGate[] plazaGates = FindObjectsByType<RoomGate>(FindObjectsSortMode.None);
                plazaCheckpoint?.Activate();
                plazaValid = plazaMotor != null && plazaMotor.Grounded
                    && Mathf.Abs(plazaMotor.transform.position.x - 6f) < 1.2f
                    && tiqueRenderer != null
                    && Mathf.Abs(Mathf.Abs(tiqueRenderer.transform.localScale.x) - 0.21f) < 0.01f
                    && plazaCheckpoint != null && plazaCheckpoint.Activated
                    && session.Current.roomId == "caligo-plaza"
                    && residents.Length == 3
                    && residents.Count(resident => resident.IsPatrolling) == 1
                    && residents.All(resident => resident.IdleFrameCount >= 4 && resident.RoleFrameCount >= 4)
                    && residents.All(resident => Mathf.Abs(resident.transform.position.y + 1.75f) < 0.01f)
                    && plazaLayers.Length >= 2
                    && plazaMidLayer != null
                    && Mathf.Abs(plazaMidLayer.localScale.x - 0.625f) < 0.01f
                    && rejectedRearWalkway == null
                    && plazaGates.Any(gate => gate.DestinationRoomId == "caligo-drop-shaft");
                Debug.Log($"CLOCKWORK_PLAZA_PROBE valid={plazaValid} " +
                    $"pos={(plazaMotor == null ? Vector3.zero : plazaMotor.transform.position)} " +
                    $"tiqueScale={(tiqueRenderer == null ? 0f : Mathf.Abs(tiqueRenderer.transform.localScale.x))} " +
                    $"tiqueBounds={(tiqueRenderer == null ? default : tiqueRenderer.bounds)} " +
                    $"floorBounds={(plazaFloor == null ? default : plazaFloor.bounds)} " +
                    $"backgroundScale={(plazaMidLayer == null ? 0f : plazaMidLayer.localScale.x)} " +
                    $"rearWalkwayRemoved={rejectedRearWalkway == null} " +
                    $"tiqueScreen={(plazaCamera == null || plazaMotor == null ? Vector3.zero : plazaCamera.WorldToScreenPoint(plazaMotor.transform.position))} " +
                    $"checkpoint={(plazaCheckpoint != null && plazaCheckpoint.Activated)} " +
                    $"residents={residents.Length} parallax={plazaLayers.Length}");
            }

            bool dropShaftValid = false;
            if (session != null && session.LoadRoom("caligo-drop-shaft", "entry-plaza"))
            {
                yield return new WaitForSecondsRealtime(3.2f);
                TiqueMotor dropMotor = FindAnyObjectByType<TiqueMotor>();
                RoomGate[] dropGates = FindObjectsByType<RoomGate>(FindObjectsSortMode.None);
                dropShaftValid = dropMotor != null && dropMotor.Grounded
                    && dropMotor.transform.position.y < -9f
                    && !dropGates.Any(gate => gate.DestinationRoomId == "caligo-plaza")
                    && dropGates.Any(gate => gate.DestinationRoomId == "crossing-cavern"
                        && !gate.IsDestinationBuilt);
                Debug.Log($"CLOCKWORK_DROP_SHAFT_PROBE valid={dropShaftValid} " +
                    $"pos={(dropMotor == null ? Vector3.zero : dropMotor.transform.position)} " +
                    $"grounded={(dropMotor != null && dropMotor.Grounded)}");
            }

            complete(shaftValid && villageValid && plazaValid && dropShaftValid);
        }
    }
}
