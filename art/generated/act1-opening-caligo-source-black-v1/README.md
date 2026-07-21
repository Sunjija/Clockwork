# ACT1 Opening to Caligo Black Source Sheets v1

> Status: `[proposal]` high-resolution source art. These files are not canon or final in-game assets.
> Background: opaque black `#000000FF`.

This directory contains black-background variants of the nine ACT1 opening-to-Caligo source sheets. The original green and magenta versions remain unchanged in `../act1-opening-caligo-source-v1/`.

## Intended Use

- Use these files as previews or inputs for pixel-conversion tools that work best against black.
- These files are not intended for chroma-key removal; use the original source directory when transparent extraction is required.
- Crop each module independently and align only its ground contact point to the shared baseline. Module heights may vary.

## Validation

- Every PNG is stored with a fully opaque alpha channel at the outer border.
- Near-black generation noise at the background edge was normalized to exact `#000000FF`.
