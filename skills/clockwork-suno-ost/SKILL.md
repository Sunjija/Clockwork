---
name: clockwork-suno-ost
description: Design and iterate original instrumental Suno prompts for CLOCKWORK game music. Use for regional exploration themes, boss themes, memory-recovery cues, transitions, leitmotif planning, soundtrack variation, Suno generation setup, or evaluation of generated CLOCKWORK OST variants. Prioritize audible musical instructions, narrative continuity, loop behavior, and role-based instrumentation; do not use for lyric-first or vocal-song requests unless the user explicitly expands the scope.
---

# CLOCKWORK Suno OST

Create cohesive, original instrumental game music prompts whose musical changes follow CLOCKWORK's exploration, memory recovery, bosses, and progression. Treat generated music as a candidate until the user selects it as canon.

## Core Rules

- Preserve documented story and map facts. Label new musical choices as proposals; never turn an unapproved prompt detail into game canon.
- Default to instrumental. Add vocals, choir, spoken words, or lyrics only when explicitly requested.
- Use concrete audible directions. Do not rely on labels such as `CLOCKWORK soundtrack`, `metroidvania music`, `masterpiece`, or an artist name.
- Use `clockwork` only when it describes an audible mechanism such as ticking pulse, escapement rhythm, wound-spring acceleration, or tuned metal percussion.
- Keep a focused palette and assign each important sound a role.
- Preserve one recognizable motif relationship across related tracks, but do not invent canonical pitches unless an approved reference establishes them.
- Avoid redundant clarification. Infer low-risk production details from project context and proceed; ask only when a missing decision would materially change the requested track.
- When the user already authorized Suno generation, proceed without an additional approval checkpoint.

## Workflow

1. Identify the cue type: region, boss, memory, transition, safe zone, pursuit, or ending.
2. Extract the cue's narrative job, player state, gameplay intensity, location acoustics, and progression point from available project documents.
3. Define the relationship to existing motifs or selected reference audio: fragmented, warm, hidden, corrupted, compressed, clarified, or fully stated.
4. Choose a compact sound palette with roles for pulse, groove, harmony, hook, counterline, texture, and impact.
5. Define arrangement motion and game behavior: exploration loop, danger layer, checkpoint breath, boss phases, victory release, or memory reveal.
6. Write the Suno style prompt and exclusions using [prompt-design.md](references/prompt-design.md).
7. If operating Suno, follow [suno-workflow.md](references/suno-workflow.md).
8. Evaluate results against the cue's function. Do not claim audio quality from titles, durations, or metadata alone when the audio has not been heard.

## CLOCKWORK Continuity

Read [clockwork-music-bible.md](references/clockwork-music-bible.md) whenever a cue must connect to another region, memory event, boss, act, or established motif.

When working inside the CLOCKWORK repository, also read `docs/music/01_region_music_direction.md` for the current proposed genre family, adjacent-cue relationship, and directions to avoid. Treat that document's genre assignments as proposals until the user approves them.

Use these continuity transformations:

- Before memory recovery: incomplete phrases, missing resolution, thin orchestration.
- During memory recovery: expose the motif clearly and reduce competing texture.
- Safe settlements: retain the motif contour but soften rhythm, register, and harmony.
- Threatened regions: hide the motif in bass, counterline, or environmental rhythm.
- Bosses: oppose, compress, distort, or interrupt the motif; restore it only when the encounter's narrative supports that turn.
- Ascents and act finales: add register and layers instead of replacing the musical identity with generic grandeur.

## Output Contract

For a prompt-writing request, return only the useful production fields:

```markdown
### Title
Exact region, encounter, or event title

### Function
Where it plays and what the player should feel or understand

### Style Prompt
Ready-to-paste Suno style prompt

### Exclude
Only concrete unwanted outputs

### Continuity Notes
Motif relationship, loop or phase plan, and any explicitly labeled proposals
```

Omit sections the user does not need. For batch work, use a compact table plus one prompt block per cue. When directly operating Suno, report created titles and completion state rather than repeating every prompt unless requested.

## Iteration Rules

- Generate two variants per prompt unless the user requests another count.
- Change one major variable per iteration: melody behavior, rhythm, palette, arrangement, or production space.
- Keep the title equal to one exact canonical region, boss, or event name. Do not join a location and boss with punctuation, add a subtitle, translate it, or make it poetic unless the user approves that exact title.
- Use a selected result as inspiration only after the user identifies it or explicitly delegates selection.
- Never publish, share, like, delete, or overwrite Suno results unless explicitly requested.
