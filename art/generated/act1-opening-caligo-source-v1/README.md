# ACT1 Opening to Caligo Source Asset Sheets v1

> Status: `[proposal]` high-resolution source art. These files are not canon and are not final in-game assets.
> Scope: ACT1 opening in Limbus through Caligo and the entrance to the descending maintenance shaft.

## Sheets

| File | Contents | Nominal key color |
|---|---|---|
| `01-limbus-fall-site-green.png` | Fall-site chute, landing frame, discharge port, intake pipe, scrap piles | `#00ff00` |
| `02-limbus-scrap-plain-part-room-green.png` | Scrap plain, conveyor, sorter, grabber, salvage cabinet, maintenance shelf | `#00ff00` |
| `03-limbus-bridge-transition-green.png` | Limbus exit, retaining plate, railings, Caligo-side repair language | `#00ff00` |
| `04a-limbus-caligo-bridge-structure-green.png` | Bridge piers, arch support, drainage pipe, railings, maintenance lamp | `#00ff00` |
| `04b-limbus-caligo-bridge-sewage-magenta.png` | Toxic sewage fall, pool surface, mist, runoff | `#ff00ff` |
| `05-caligo-entrance-watch-green.png` | Entrance, watch post, hand gate, pipes, storage, lamp | `#00ff00` |
| `06-morbi-workshop-green.png` | Workshop, bench, hoist, shelves, repair cradle, MOD apparatus | `#00ff00` |
| `07-caligo-village-plaza-green.png` | Residences, checkpoint, clean-water rack, parts depot, workbench, pipes | `#00ff00` |
| `08-caligo-water-storage-shaft-green.png` | Water tanks, distribution stand, ration shelf, downpipes, shaft and ladder | `#00ff00` |

## Alignment Rule

- Crop each module independently after removing the key color.
- Normalize the bottom of each opaque module to one shared ground baseline.
- Keep module heights and widths varied according to function; only the ground contact line is shared.
- Water, mist, and runoff effects use their own effect anchors instead of the structural ground baseline.

## Processing Order

1. Remove the chroma key at source resolution and remove color spill. Sample the border or use a color-range selection because generated key colors vary slightly around the nominal value.
2. Crop modules independently while preserving a small transparent margin.
3. Convert to the approved pixel-art resolution, palette, and dithering preset.
4. Clean one-pixel noise and verify that supports, pipes, and feet remain connected.
5. Align the final transparent bounds to the common ground baseline in Unity.

The Limbus and bridge directions follow first-pass approved concepts, but the generated sheets remain proposals until reviewed. Caligo visual modules are proposals based on the canon settlement character and the ACT1 environment art bible.
