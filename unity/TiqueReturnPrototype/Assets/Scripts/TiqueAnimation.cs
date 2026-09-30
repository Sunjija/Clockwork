using System;
using System.Collections.Generic;

namespace TiqueReturn
{
    // Presentation only. Physics, action timers, input priority and contact windows
    // stay in ReworkModel; the legacy ReturnModel.Pose remains unchanged.
    public static class TiqueAnimation
    {
        // Jump force starts immediately. Show release at lift-off, rather than
        // playing grounded preload drawings after the character is airborne.
        const float Takeoff = .045f, Landing = .12f, DashPreparation = .06f;
        public const float HurtExposure = .15f;

        // Expose each authored pose inside an existing gameplay window. This maps
        // visual time, never extends a movement lock or waits before applying force.
        static int Window(int[] times, float age, float window, int first, int last)
        {
            int sum = 0;
            for (int i = first; i <= last; i++) sum += times[i];
            return WardenAnimation.FrameAt(times, Math.Max(0, age) * sum / (window * 1000), first, last);
        }

        public static int Select(ReturnModel hero, IDictionary<string, int[]> clips, out string clip)
        {
            if (hero.Dashing)
            {
                clip = "Dash";
                return hero.dashAge < DashPreparation
                    ? Window(clips[clip], hero.dashAge, DashPreparation, 0, 2)
                    : Window(clips[clip], hero.dashAge - DashPreparation, ReturnModel.DashTime - DashPreparation, 3, 6);
            }
            if (hero.Attacking)
            {
                clip = "Attack";
                return WardenAnimation.FrameAt(clips[clip], hero.attackAge);
            }
            if (!hero.grounded)
            {
                clip = hero.doublePose ? "DoubleJump" : "Jump";
                if (hero.airAge < Takeoff) return 3;
                if (hero.doublePose)
                    return hero.vy < -35 ? 4 : hero.vy < 0 ? 5 : hero.vy < 35 ? 6 : hero.vy < 140 ? 7 : 8;
                return hero.vy < -140 ? 4 : hero.vy < -40 ? 5 : hero.vy < 0 ? 6 : hero.vy < 40 ? 7 : hero.vy < 140 ? 8 : 9;
            }
            // Ground contact takes precedence even while a direction is held.
            if (hero.landAge < Landing)
            {
                clip = hero.doublePose ? "DoubleJump" : "Jump";
                return Window(clips[clip], hero.landAge, Landing, hero.doublePose ? 9 : 10, clips[clip].Length - 1);
            }
            // Recovery poses cannot disguise resumed walking or an airborne fall.
            if (hero.axis == 0 && hero.dashAge < .34f)
            {
                clip = "Dash";
                return WardenAnimation.FrameAt(clips[clip], hero.dashAge - ReturnModel.DashTime, 7, 11);
            }
            if (hero.axis != 0 && hero.CanMove)
            {
                clip = "Walk";
                return WardenAnimation.FrameAt(clips[clip], hero.walkAge, loop: true);
            }
            clip = "Idle";
            return WardenAnimation.FrameAt(clips[clip], hero.clock, loop: true);
        }

        public static bool InitialHurtVisible(ReworkModel model)
        {
            float age = model.clock - model.hurtAt;
            return model.phase == Journey.Combat && age >= 0 && age < HurtExposure
                && !model.hero.Dashing && !model.hero.Attacking;
        }

        public static bool ShouldBlinkBody(ReworkModel model)
        {
            return model.phase == Journey.Combat && model.hero.invincible > 0 && !model.reducedEffects
                && !InitialHurtVisible(model) && (int)(model.clock * 14) % 2 == 1;
        }
    }
}
