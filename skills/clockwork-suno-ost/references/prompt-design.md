# Prompt Design

## Prompt Order

Put the most identity-defining sound first, then write in this order:

1. Cue function and energy
2. Memorable motif behavior
3. Tempo, meter, or pulse behavior
4. Instruments with roles
5. Arrangement motion or boss phases
6. Production space and texture
7. Loop or ending behavior

Aim for 35-70 words for a normal regional cue and 70-120 words for a boss or unusually controlled cue. Remove any phrase that does not imply an audible result.

## Title Rule

Use exactly one documented region, boss, or event name. Do not combine names or add descriptive subtitles. For example, use `렌토`, not `중앙 정수조 — 렌토`, unless the user explicitly approves the latter.

## Role-First Instrumentation

Prefer:

- `celesta states the memory motif`
- `prepared piano carries the pulley rhythm`
- `bass clarinet shadows the player melody`
- `tuned pipe strikes mark bite openings`
- `low strings widen only during the final phase`

Avoid:

- long instrument inventories
- repeated mood adjectives
- project names used as genre labels
- `epic`, `masterpiece`, `high quality`, or `cinematic` without musical behavior
- artist imitation or direct franchise imitation

## Regional Cue Formula

```text
[signature sound and regional function], [motif treatment], [pulse behavior], [role-based palette], [A/B exploration motion], [location acoustics], [seamless or edit-friendly ending]
```

Regional cues should support repeated listening. Avoid constant climax, overly dense percussion, and melodic inactivity disguised as ambience.

## Boss Cue Formula

```text
[encounter identity], [boss motif versus player motif], [phase-one behavior], [phase-two escalation], [final-phase transformation], [attack-linked accents or silences], [instrumental palette and production], [decisive ending]
```

Translate mechanics into music instead of listing attacks literally. Examples:

- charge attack -> accumulating pulse followed by a hard silence
- shockwave sequence -> three spaced rhythmic impacts
- swarm summon -> subdivided ostinato entering under the main meter
- vulnerability window -> texture drops while the melody becomes exposed

## Memory Cue Formula

```text
[intimate exposed motif], [fragment becoming complete], [minimal pulse], [one answering instrument], [emotional turn], [unresolved or clarified cadence based on story state]
```

## Exclusions

Use the Exclude field for likely failure modes, not a second full prompt. Typical options:

```text
vocals, lyrics, choir, EDM drop, trap hats, pop backbeat, trailer braams, heroic fanfare, generic ambient wash, excessive reverb
```

Choose only relevant exclusions. Do not exclude an entire family that the positive prompt actually needs.

## Quality Checklist

- Can a listener identify a motif or hook within the first section?
- Does every named instrument have a job?
- Does the arrangement reflect gameplay progression?
- Is the cue sustainable during repeated play?
- Does the ending support looping or clean editing?
- Are story facts separate from musical proposals?
- Would the prompt still make sense with `CLOCKWORK`, `metroidvania`, and `soundtrack` removed? If yes, remove those labels.
