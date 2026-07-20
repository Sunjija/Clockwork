using System;
using System.Collections;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
using static UnityEngine.Object;

namespace Clockwork
{
    public static class GrappleSmokeProbe
    {
        public static IEnumerator Run(Action<bool> complete)
        {
            GameSession session = GameSession.Instance;
            bool loaded = session != null && session.LoadGrappleLab();
            float deadline = Time.realtimeSinceStartup + 4f;
            while (loaded && SceneManager.GetActiveScene().name != "GrappleLab"
                && Time.realtimeSinceStartup < deadline)
            {
                yield return null;
            }
            yield return null;
            yield return null;

            TiqueGrapple grapple = FindAnyObjectByType<TiqueGrapple>();
            TiqueMotor motor = FindAnyObjectByType<TiqueMotor>();
            Rigidbody2D body = motor == null ? null : motor.GetComponent<Rigidbody2D>();
            GrappleAnchor anchor = FindObjectsByType<GrappleAnchor>(FindObjectsSortMode.None)
                .FirstOrDefault(candidate => candidate.name == "AnchorCenter");

            bool valid = loaded && grapple != null && grapple.isActiveAndEnabled
                && body != null && anchor != null;
            if (valid)
            {
                body.position = (Vector2)anchor.transform.position + new Vector2(3f, -3f);
                body.linearVelocity = new Vector2(4f, 0f);
                valid = grapple.TryAttach(anchor);
                float ropeLength = grapple.RopeLength;
                yield return new WaitForSecondsRealtime(0.65f);
                float constrainedDistance = Vector2.Distance(body.position, anchor.transform.position);
                valid &= grapple.IsAttached
                    && grapple.IsTensioned
                    && constrainedDistance <= ropeLength + 0.2f
                    && float.IsFinite(body.linearVelocity.x)
                    && float.IsFinite(body.linearVelocity.y);
                Vector2 releaseVelocity = body.linearVelocity;
                grapple.Release();
                yield return new WaitForFixedUpdate();
                valid &= !grapple.IsAttached
                    && releaseVelocity.sqrMagnitude > 0.01f
                    && body.linearVelocity.sqrMagnitude > 0.01f;
                Debug.Log($"CLOCKWORK_GRAPPLE_PROBE valid={valid} rope={ropeLength:F2} "
                    + $"distance={constrainedDistance:F2} release={releaseVelocity}");
            }
            else
            {
                Debug.Log("CLOCKWORK_GRAPPLE_PROBE valid=False setup-missing");
            }

            complete(valid);
        }
    }
}
