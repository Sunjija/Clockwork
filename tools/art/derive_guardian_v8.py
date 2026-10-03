"""Minor whole-pose guardian repairs from five real imagegen edit anchors.

The existing V7 sources and exports are read-only. This converter never paints
or independently scales body parts. It uses the established V7 premultiplied
BOX, fixed palette, modest source cleanup and ground registration, with source
hashes, source area sampling maps and every cleanup pixel recorded separately.
Run only after the five actual anchors have been inspected by the parent agent.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parents[2]
ART = REPO / 'art/return-v8-guardian'
NATIVE = ART / 'Source/Native'
DERIVATION = ART / 'Source/Derivation'
QA = ART / 'QA'
V7 = REPO / 'art/return-v7-guardian'
CANVAS = (192, 176)
BASELINE = 163
CENTER_X = 96
SPECS = {
    'idle': ('idle/00.png', 136),
    'jaw-impact-03': ('jaw_shockwave/03.png', 136),
    'jaw-impact-04': ('jaw_shockwave/04.png', 136),
    'jaw-impact-05': ('jaw_shockwave/05.png', 136),
    'slam-land': ('drop_slam/06.png', 149),
}
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value, compact=False):
    path.write_text(json.dumps(value, ensure_ascii=False,
                               indent=None if compact else 2,
                               separators=(',', ':') if compact else None,
                               default=lambda v: v.item() if isinstance(v, np.generic) else list(v)) + '\n', encoding='utf-8')


def bounds(a):
    yy, xx = np.where(a[..., 3] > 0)
    return [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]


def warm(p):
    return (p[..., 0] > p[..., 1] + 30) & (p[..., 0] > p[..., 2] + 30)


def source_samples(source, target_width):
    im = Image.open(source).convert('RGBA')
    raw = np.array(im)
    yy, xx = np.where(raw[..., 3] >= 128)
    if not len(xx):
        raise ValueError(f'No opaque source object: {source}')
    crop = [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]
    cropped = im.crop(crop)
    factor = target_width / cropped.width
    fit = [target_width, max(1, round(cropped.height * factor))]
    raw_mask = raw[..., 3] >= 128
    source_low = int(yy.max())
    source_band = max(1, round(10 / factor))
    source_supports = []
    for x in np.where(raw_mask[max(0, source_low - source_band + 1):source_low + 1].any(0))[0]:
        source_supports.append([int(x), int(np.where(raw_mask[:, x])[0][-1])])
    if fit[1] > BASELINE + 1:
        raise ValueError(f'{source}: whole-pose height {fit[1]} would exceed registration; inspect anchor, never squash a body part')
    small = cropped.convert('RGBa').resize(fit, Image.Resampling.BOX).convert('RGBA')
    alpha = np.where(np.array(small)[..., 3] >= 128, 255, 0).astype(np.uint8)
    rgb = small.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    a = np.array(rgb.convert('RGBA'))
    a[..., 3] = alpha
    a[alpha == 0] = 0
    return a, {'generatedDimensions': list(im.size), 'sourceCropAlphaThreshold': 128,
               'cropRect': crop, 'wholePoseScale': factor, 'fitSize': fit,
               'targetWidth': target_width, 'bodyPartIndependentScaling': False,
               'sourceLowestOpaqueRow': source_low,
               'sourceFootMedianRowAlpha128': int(np.median([p[1] for p in source_supports])),
               'sourceFootSupportBandHeight': source_band,
               'sourceFootSupportAlpha128': source_supports}


def map_palette(a, palette):
    out = a.copy()
    m = a[..., 3] > 0
    px = a[m, :3].astype(int)
    distances = ((px[:, None] - palette[None].astype(int)) ** 2).sum(-1)
    # Same warm/cool separation as V7; tiny red vents must not turn blue-gray.
    pw, cw = warm(palette.astype(int)), warm(px)
    distances[np.ix_(cw, ~pw)] += 10 ** 7
    distances[np.ix_(~cw, pw)] += 10 ** 7
    out[m, :3] = palette[distances.argmin(1)]
    return out


def source_cleanup(a, palette):
    out, edits = a.copy(), []
    h, w = a.shape[:2]
    for y in range(h):
        for x in range(w):
            me = tuple(a[y, x])
            if not me[3]:
                continue
            neighbors = [(x + dx, y + dy) for dx, dy in N4 if 0 <= x + dx < w and 0 <= y + dy < h]
            colors = [tuple(a[ny, nx]) for nx, ny in neighbors]
            if len(colors) != 4 or any(c[3] == 0 for c in colors) or me in colors:
                continue
            majority, count = Counter(colors).most_common(1)[0]
            if count >= 2 and abs(sum(map(int, majority[:3])) - sum(map(int, me[:3]))) < 38 * 3:
                donor = next([nx, ny] for nx, ny in neighbors if tuple(a[ny, nx]) == majority)
                out[y, x] = majority
                edits.append({'sample': [x, y], 'operation': 'v7-low-contrast-single-tone-fold', 'donorSample': donor,
                              'before': list(me), 'after': list(majority)})
    mask = out[..., 3] > 0
    p = np.pad(mask.astype(int), 1)
    count = sum(p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] for dx, dy in N8)
    for y, x in np.argwhere(mask & (count < 2)):
        edits.append({'sample': [int(x), int(y)], 'operation': 'v7-disconnected-crumb-removal',
                      'before': out[y, x].astype(int).tolist(), 'after': [0, 0, 0, 0]})
        out[y, x] = 0
    mask = out[..., 3] > 0
    p = np.pad(mask, 1)
    edge = mask & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    ink = palette[np.argmin(palette.astype(int).sum(1))]
    for y, x in np.argwhere(edge):
        before = out[y, x].astype(int).tolist()
        if not (out[y, x, :3] == ink).all():
            out[y, x, :3] = ink
            edits.append({'sample': [int(x), int(y)], 'operation': 'v7-source-silhouette-ink', 'before': before,
                          'after': out[y, x].astype(int).tolist()})
    return out, edits


def ground_row(a):
    mask = a[..., 3] > 0
    low = int(np.where(mask.any(1))[0][-1])
    supports = []
    for x in np.where(mask[max(0, low - 9):low + 1].any(0))[0]:
        supports.append([int(x), int(np.where(mask[:, x])[0][-1])])
    return int(np.median([row[1] for row in supports])), supports


def register(a):
    bb = bounds(a)
    ground, supports = ground_row(a)
    offset = [round(CENTER_X - (bb[0] + bb[2]) / 2), BASELINE - ground]
    canvas = np.zeros((CANVAS[1], CANVAS[0], 4), np.uint8)
    yy, xx = np.where(a[..., 3] > 0)
    ty, tx = yy + offset[1], xx + offset[0]
    if not ((tx >= 0) & (tx < CANVAS[0]) & (ty >= 0) & (ty < CANVAS[1])).all():
        raise ValueError('Whole-pose registration leaves native canvas; inspect source, never region-rescale')
    canvas[ty, tx] = a[yy, xx]
    final_ground, final_supports = ground_row(canvas)
    assert final_ground == BASELINE
    return canvas, {'offset': offset, 'sampleOpaqueBounds': bb, 'opaqueBounds': bounds(canvas),
                    'groundRowBeforeRegistration': ground, 'groundSupportBeforeRegistration': supports,
                    'nativeGroundRow': final_ground, 'nativeGroundSupport': final_supports,
                    'nativeLowestOpaqueRow': int(np.where((canvas[..., 3] > 0).any(1))[0][-1]),
                    'bboxCenterX': (bounds(canvas)[0] + bounds(canvas)[2]) / 2}


def pixel_map(name, a, palette, meta, edits):
    lookup = {tuple(c): i for i, c in enumerate(palette.astype(int).tolist())}
    indices = [[lookup.get(tuple(map(int, a[y, x, :3])), -1) if a[y, x, 3] else -1 for x in range(a.shape[1])] for y in range(a.shape[0])]
    crop, fit = meta['cropRect'], meta['fitSize']
    sx, sy = (crop[2] - crop[0]) / fit[0], (crop[3] - crop[1]) / fit[1]
    path = DERIVATION / f'{name}-pixel-map.json'
    write_json(path, {'asset': name, 'source': meta['generatedSource'], 'sourceSha256': meta['sourceSha256'],
                      'interpretation': 'Each entry at [sampleY][sampleX] is its fixed V7 palette index, or -1 for transparent. TargetXY=sampleXY+offset. Exact BOX source rect=[cropLeft+x*stepX,cropTop+y*stepY,cropLeft+(x+1)*stepX,cropTop+(y+1)*stepY]. Mild unsharp reads neighboring samples. Any changed alpha/color has a separately recorded source cleanup edit. Registration padding is transparent. No new silhouette or body-part geometry is authored.',
                      'sourceStep': [sx, sy], 'cropRect': crop, 'sampleSize': fit, 'offset': meta['offset'],
                      'nativeCanvas': list(CANVAS), 'samplePaletteIndices': indices,
                      'unsharp': {'radius': 1.2, 'percent': 60, 'threshold': 2}, 'edits': edits}, compact=True)
    return path.relative_to(ART).as_posix()


def sheets(frames, records):
    names = list(SPECS)
    # At 2x every native pixel remains crisp; all five before/after pairs share
    # the exact 192x176 frame registration rather than individually fitted art.
    before_after = Image.new('RGB', (1980, 820), (16, 22, 31))
    source_native = Image.new('RGB', (1980, 780), (16, 22, 31))
    b, s = ImageDraw.Draw(before_after), ImageDraw.Draw(source_native)
    b.text((16, 12), 'V7 ORIGINAL / WHOLE-POSE V8 CANDIDATE - NATIVE 2X (appearance approval pending)', fill=(225, 235, 238))
    s.text((16, 12), 'ACTUAL GENERATED EDIT SOURCE -> FIXED V7 PALETTE / NATIVE PIXELS', fill=(225, 235, 238))
    for i, name in enumerate(names):
        x = 12 + i * 394
        b.text((x, 42), name + ' / original V7', fill=(195, 210, 220))
        old = Image.open(V7 / 'Frames' / SPECS[name][0]).convert('RGBA')
        old2 = old.resize((384, 352), Image.Resampling.NEAREST)
        before_after.paste(old2, (x, 64), old2)
        b.text((x, 432), 'corrected source -> native V8', fill=(195, 210, 220))
        corrected = Image.fromarray(frames[name]).resize((384, 352), Image.Resampling.NEAREST)
        before_after.paste(corrected, (x, 454), corrected)
        s.text((x, 42), name + ' / imagegen whole pose', fill=(195, 210, 220))
        raw = Image.open(ART / records[name]['generatedSource']).convert('RGBA').crop(records[name]['cropRect'])
        raw.thumbnail((360, 275), Image.Resampling.LANCZOS)
        source_native.paste(raw, (x + (384 - raw.width) // 2, 95 + (275 - raw.height) // 2), raw)
        s.text((x, 392), 'native 192x176 / 2x', fill=(195, 210, 220))
        source_native.paste(corrected, (x, 414), corrected)
    before_after.save(QA / 'native-v7-v8-comparison-2x.png')
    source_native.save(QA / 'native-source-comparison-2x.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inspected-anchors', action='store_true', help='Explicit gate: parent has inspected and selected the actual five generated edits')
    args = parser.parse_args()
    if not args.inspected_anchors:
        raise SystemExit('STOP: inspect/show actual imagegen anchors first; then pass --inspected-anchors. No native assets derived.')
    provenance_path = ART / 'Source/provenance.json'
    provenance = json.loads(provenance_path.read_text())
    selected = provenance.get('selectedNativeSources', provenance.get('selectedPreviewFiles', {}))
    if any(name not in selected for name in SPECS):
        raise SystemExit('STOP: provenance must explicitly select all five actual generated sources.')
    for name in SPECS:
        if not (ART / selected[name]).is_file():
            raise SystemExit(f'STOP: actual generated image missing for {name}. No substitutes allowed.')
    for path in (NATIVE, DERIVATION, QA):
        path.mkdir(parents=True, exist_ok=True)
    v7_manifest = V7 / 'manifest.json'
    hex_colors = json.loads(v7_manifest.read_text())['palette']
    palette = np.array([[int(color[i:i + 2], 16) for i in (1, 3, 5)] for color in hex_colors], np.uint8)
    assert len(palette) == 32
    write_json(NATIVE / 'palette.json', {'kind': 'unchanged-v7-fixed-palette', 'colors': palette.astype(int).tolist(),
                                       'hexColors': hex_colors, 'source': v7_manifest.relative_to(REPO).as_posix(), 'sourceSha256': sha(v7_manifest)})
    frames, records = {}, {}
    for name, (old_frame, width) in SPECS.items():
        source = ART / selected[name]
        a, meta = source_samples(source, width)
        meta.update({'generatedSource': selected[name], 'sourceSha256': sha(source),
                     'originalV7Native': (V7 / 'Frames' / old_frame).relative_to(REPO).as_posix(),
                     'originalV7Sha256': sha(V7 / 'Frames' / old_frame)})
        Image.fromarray(a).save(DERIVATION / f'{name}-area-sampled.png')
        mapped = map_palette(a, palette)
        Image.fromarray(mapped).save(DERIVATION / f'{name}-palette-mapped.png')
        cleaned, edits = source_cleanup(mapped, palette)
        frames[name], registration = register(cleaned)
        meta.update(registration)
        output = NATIVE / f'{name}.png'
        Image.fromarray(frames[name]).save(output)
        meta.update({'output': output.relative_to(ART).as_posix(), 'outputSha256': sha(output),
                     'cleanupCount': len(edits), 'cleanupOperations': dict(Counter(e['operation'] for e in edits)),
                     'opaquePixelCount': int((frames[name][..., 3] > 0).sum()),
                     'uniqueOpaqueColors': len(np.unique(frames[name][frames[name][..., 3] > 0, :3], axis=0))})
        meta['pixelMap'] = pixel_map(name, cleaned, palette, meta, edits)
        assert set(np.unique(frames[name][..., 3])) <= {0, 255}
        assert meta['opaqueBounds'][2] - meta['opaqueBounds'][0] <= width
        records[name] = meta
    write_json(DERIVATION / 'native-derivation.json', {
        'version': 8, 'approval': 'Inspected generated-anchor derivatives; human final appearance approval pending',
        'method': 'Whole-pose uniform alpha128 crop / premultiplied BOX / mild unsharp / exact V7 32-color palette / V7 limited native cleanup / bbox x96 + planted median row163',
        'script': 'tools/art/derive_guardian_v8.py', 'scriptSha256': sha(Path(__file__)),
        'sourceSelection': 'Source/provenance.json', 'sourceSelectionSha256': sha(provenance_path),
        'canvas': list(CANVAS), 'baselineRow': BASELINE, 'palette': 'Source/Native/palette.json',
        'paletteSha256': sha(NATIVE / 'palette.json'), 'assets': records,
        'unchanged': 'All V7 generated originals and native outputs are preserved. No Tique, gameplay, combat timing or runtime code is edited here.',
        'technicalVersusAppearance': 'Dimensions, palette, registration and reproducible source mapping are technical checks, not final visual approval or animation/playtest certification.'})
    sheets(frames, records)
    print(json.dumps({'nativeAssets': len(frames), 'paletteColors': len(palette),
                      'assets': {name: {'bounds': m['opaqueBounds'], 'footRow': m['nativeGroundRow'], 'crop': m['cropRect']} for name, m in records.items()}}, indent=2))


if __name__ == '__main__':
    main()
