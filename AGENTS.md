# Clockwork game visual production rules

## Mandatory image-first workflow

The human user's standing rule is that every new or redesigned game visual must begin with an actual image-generation result. This includes characters, props, walls and floor tiles, sockets, backgrounds, HUD elements, icons, and VFX whenever their appearance is new or changed.

Use this sequence:

1. Read the applicable image-generation skill and inspect any approved reference assets. Decide which assets are unchanged reuse and which require a new visual source.
2. Generate the actual asset concept or production anchor with `image_gen`. Keep the complete prompt, reference-image paths, generated output, and generation metadata. A written prompt, an intended future generation, or a hand-painted/code-painted placeholder is not a generated source.
3. Inspect and show the generated anchor to the human user. It must directly depict the asset being produced, with its intended silhouette, material, palette, and game role. A generic or unrelated moodboard does not fulfill this step.
4. Derive the game-ready native-pixel assets from that generated anchor: crop, align, normalize scale/palette/alpha, and prepare editable sources and runtime exports. Keep a traceable source-to-export mapping. Derivation must retain the anchor's approved visual identity; do not replace it with an arbitrary new geometric design.
5. Animate through the same image-first, inspection, native-pixel cleanup, registration, editable-source, and export pipeline already established for Tique and the guardian. Reuse its proven timing, dimensions, alignment, and validation where applicable.
6. Verify the exports and game integration. Report mechanical/technical validation separately from visual approval and human playtesting. Until the user approves a new look, describe it as a preview or unapproved candidate, not an approved final asset.

Editable PNG, Piskel, APNG, pixel-delta sources, a deterministic authoring script, or the ability to paint an asset directly are **not permission to skip image generation**. Never substitute hand-painted/code-painted arbitrary shapes for the required generated anchor. Never retroactively generate an irrelevant moodboard merely to label an already-painted asset “image-first.”

## Allowed reuse and explicit exceptions

- Unchanged, previously approved art can be reused without generating it again.
- Pure gameplay, physics, input, timing, or other nonvisual changes do not require image generation when they reuse unchanged approved visuals.
- A new look requires an actual generated image source, even when the implementation is ultimately native pixel art or code-rendered.
- Only a direct, explicit human exemption may waive this workflow for a named asset or task. Record the exemption and its scope. An agent's convenience, source-format preference, or interpretation of “editable original” is not an exemption.
- Preserve prompts, generated originals, references, source/provenance records, editable derivatives, and validation evidence. Do not discard prior work or claim a process-noncompliant draft is final production art.

## Existing readability prototype: preserve direction, correct provenance

`art/return-readability-v1` and `unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/ReadabilityArt` were initially authored as native/code-painted assets without image generation. That production process did not comply with the user's image-first rule, so this package is a **readability prototype / process-noncompliant draft**, not final production art.

The user subsequently said the current distinctions are much clearer. Preserve that positively assessed design direction: connected gray walls, handled brass square weights, cyan round orbs, and recessed square/circular sockets. Do not describe the entire design or its readability improvement as rejected, and do not redesign it from zero. Preserve the working prototype and valid gameplay/model/build/capture evidence. Produce image-first refinements with genuine generated anchors that retain the current silhouettes and colors; passing technical tests alone do not complete final asset provenance or final-art approval.
