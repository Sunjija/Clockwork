# CLOCKWORK Implementation Direction

Updated: 2026-07-20

This is an implementation order, not new canon. Unconfirmed mechanics stay proposals until
the designer accepts them.

## 1. Opening Readability - implemented, playtest pending

- Preserve the canon east-to-west route.
- Make the first leftward move readable through facing, blocked-arrival dressing, lighting,
  and camera lead rather than tutorial text.
- Validate with first-input hesitation and wrong-wall checks in playtests.

## 2. Critical Route Greybox

- Add `crossing-cavern` after the drop shaft.
- Continue toward the purification-plant route using map-authored room order.
- Keep hook-return details data-only until accepted.

## 3. Survival Loop - energy substrate implemented

- Prototype kill-charged, hold-to-heal recovery.
- Keep charge amount, heal cost, cast time, and interruption rules proposal values.
- Test the damaged opening separately so healing cannot erase its narrative purpose.
- Hit/defeat events and the segmented Lentium gauge are implemented with proposal tuning;
  charged weapon swaps now spend the shared gauge. Hold-to-heal timing, cost, and
  interruption remain pending.

## 4. Combat Identity - data foundation implemented

- Implement the approved fist-axis combo subset before expanding weapon-to-weapon pairs.
- Add hit feedback, enemy death response, and rat presentation alongside combo testing.
- Keep loadout changes bench-owned when a fourth weapon exists.
- Basic combo and weapon data are separated. Fist-to-greatsword and fist-to-hammer finishers
  are playable, Lentium-consuming charge attacks triggered directly by swapping with two segments;
  reverse utility transitions still require their bespoke mechanics.

## 4A. Grapple Lab - isolated prototype

- `F2` opens a non-canon room for anchor selection, staged rope travel, soft tension,
  pendulum momentum, and release.
- Keep the ability disabled in story rooms until the post-Lento acquisition and return route are approved.

## 4B. Combat Lab - isolated prototype

- `F3` opens a non-canon room with indefinitely restoring training targets.
- Use alternating punch impacts, the automatic gold third-hit pulse, and HUD combo strip to tune
  the right-left-finisher cadence without a basic-attack timing requirement.
- Keep these targets and lab-only affordances out of story-room encounter balance.

## 5. Art Vertical Integration

- Approve one plaza screen as the environment quality bar.
- Convert the approved direction into modular 32 PPU kits after collision metrics stabilize.
- Apply final character/enemy animation and environment art one room at a time.

## 6. Audio and Pacing

- Integrate SFX before final music mixing so combat and traversal timing are readable.
- Add regional music only from approved candidates; music commits remain separate.
- Finish with route pacing, checkpoint economy, UI, and accessibility passes.
