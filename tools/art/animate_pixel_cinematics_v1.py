"""Small traceable animations of inspected image-first native scenes.

No fresh art is drawn: lighting affects existing emitted-color pixels only,
one sampled piston insert translates rigidly by integer pixels, and a handful
of generated dust flecks drift against recorded source-neighbor underlays.
All other pixels remain byte-exact. No Unity writes, AI video, or game launch.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from derive_pixel_cinematics_v1 import map_rgb, CLOSE_RECT, sha, write_json

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO/'art/return-pixel-cinematics-v1'
NATIVE = ROOT/'Source/Native'
DERIVATION = ROOT/'Source/Derivation'
DURATIONS_SHORT = [200, 120, 100, 100, 100, 100, 100, 100, 100, 100, 280, 600]
DURATIONS_LONG = [160]*15 + [600]


def rgba(a):
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def light(a, mask, levels, palette):
    result = a.copy()
    colors = a[mask, :3].astype(float)
    level = np.asarray(levels)
    if level.ndim:
        level = level[:, None]
    target = np.rint(colors*level).clip(0, 255).astype(np.uint8).reshape(-1, 1, 3)
    mapped, _ = map_rgb(target, palette)
    result[mask, :3] = mapped[:, 0]
    return result


def relays(a, palette):
    p = a[..., :3].astype(int)
    yy, xx = np.indices(a.shape[:2])
    mask = (p[..., 1] > p[..., 0]+25) & (p[..., 2] > p[..., 0]+20) & (p[..., 1] > 70)
    mask &= (yy > 70) & (yy < 145)
    frames, states = [], []
    for i in range(12):
        aperture = (.03, .25, .6, 1.)[min(3, i)]
        progress = max(0., min(1., (i-3)/5))
        threshold = 165 + progress*135
        levels = np.where(xx[mask] < 150, aperture,
                          np.where(xx[mask] <= threshold, 1., .035))
        frames.append(light(a, mask, levels, palette))
        states.append({'apertureLevel': aperture, 'rightwardCableProgress': progress})
    assert np.array_equal(frames[-1], a), 'Relay final state must exactly match native anchor'
    return frames, mask, states, ['Existing cyan aperture pixels power on, then cable segments illuminate left-to-right. All brass and steel geometry is invariant.']


def underlay(a, mask, radius=5):
    """Source-neighbor donors only; every exact source coordinate is retained."""
    result, donors = a.copy(), []
    for y, x in np.argwhere(mask):
        candidates = []
        for dx, dy in ((-radius, 0), (radius, 0), (-radius, 1), (radius, 1), (0, radius), (0, -radius)):
            nx, ny = int(x+dx), int(y+dy)
            if 0 <= nx < a.shape[1] and 0 <= ny < a.shape[0] and not mask[ny, nx]:
                candidates.append((int(a[ny, nx, :3].sum()), nx, ny))
        if not candidates:
            raise ValueError('No recorded donor available for a moving source pixel')
        _, nx, ny = min(candidates)
        result[y, x] = a[ny, nx]
        donors.append({'at': [int(x), int(y)], 'sourceDonor': [nx, ny], 'rgba': a[ny, nx].astype(int).tolist()})
    return result, donors


def shifted_mask(mask, offset):
    result = np.zeros_like(mask)
    ys, xs = np.where(mask)
    dx, dy = offset
    if not ((xs+dx >= 0) & (xs+dx < mask.shape[1]) & (ys+dy >= 0) & (ys+dy < mask.shape[0])).all():
        raise ValueError('Native layer leaves scene bounds')
    result[ys+dy, xs+dx] = True
    return result


def move_layer(back, original, mask, offset):
    image = back.copy()
    ys, xs = np.where(mask)
    dx, dy = offset
    image[ys+dy, xs+dx] = original[ys, xs]
    # A strict sampled-pixel rigid-translation test; no region resize/warp.
    assert np.array_equal(image[ys+dy, xs+dx], original[ys, xs])
    return image


def warden(a, palette):
    p = a[..., :3].astype(int)
    yy, xx = np.indices(a.shape[:2])
    core = (p[..., 0] > p[..., 1]+25) & (p[..., 0] > p[..., 2]+25)
    inside = ((xx > 88) & (xx < 195) & (yy > 35) & (yy < 131))
    vents = ((xx > 239) & (xx < 280) & (yy > 29) & (yy < 57))
    core &= inside | vents
    part = Image.new('L', (320, 180), 0)
    # This is the already-generated exposed rod, not newly authored anatomy.
    polygon = [(243, 113), (248, 112), (260, 139), (256, 145), (247, 124)]
    ImageDraw.Draw(part).polygon(polygon, fill=255)
    rod = np.array(part) > 0
    backing, donors = underlay(a, rod, 6)
    layer = np.zeros_like(a); layer[rod] = a[rod]
    rgba(layer).save(DERIVATION/'warden-rod-source-layer.png')
    rgba(backing).save(DERIVATION/'warden-rod-recorded-underlay.png')
    offsets = [(0, 0)]*3 + [(1, 1)]*5 + [(0, 1)] + [(0, 0)]*3
    levels = [.03, .06, .12, .3, .55, .8, 1., .84, 1., .9, 1., 1.]
    frames, states, allowed = [], [], core.copy()
    for i, (offset, level) in enumerate(zip(offsets, levels)):
        allowed |= rod | shifted_mask(rod, offset)
        moved = move_layer(backing, a, rod, offset)
        frame = light(moved, core, level, palette)
        frames.append(frame)
        states.append({'mouthAndVentLevel': level, 'pistonLogicalOffset': list(offset)})
    assert np.array_equal(frames[-1], a), 'Final guardian geometry and light must exactly match source'
    write_json(DERIVATION/'warden-rod-registration.json', {'sourceNative': 'Source/Native/warden-core-logical.png',
        'sourceSha256': sha(NATIVE/'warden-core-logical.png'), 'polygon': polygon,
        'method': 'Rigid whole sampled insert integer translation; no limb scaling or interpolation',
        'integerOffsets': [list(x) for x in offsets], 'underlaySourceDonors': donors,
        'humanAppearanceApproval': 'pending'})
    return frames, allowed, states, ['Only existing mouth/core and vent colors power on. A sampled exposed rod makes a one-logical-pixel rigid activation stroke and returns. Jaw plates and all other body/background pixels stay fixed.']


def workshops(a):
    p = a[..., :3].astype(int)
    candidates = []
    # Air inside the generated lamp cone only, above all workbench/gear solids.
    for y in range(82, 92):
        for x in range(114, 138):
            r, g, b = p[y, x]
            neighbors = p[y-1:y+2, x-1:x+2, 0]
            contrast = float(r-neighbors.mean())
            if r > g+15 and g > b+8 and r > 70 and contrast > 3:
                candidates.append((contrast, x, y))
    chosen = []
    for _, x, y in sorted(candidates, reverse=True):
        if all(abs(x-cx)+abs(y-cy) >= 4 for cx, cy in chosen):
            chosen.append((x, y))
        if len(chosen) == 5:
            break
    if len(chosen) < 3:
        raise ValueError('Generated source has too few distinct lamp-cone flecks; do not paint replacements')
    mask = np.zeros(a.shape[:2], bool)
    for x, y in chosen:
        mask[y, x] = True
    backing, donors = underlay(a, mask, 1)
    layer = np.zeros_like(a); layer[mask] = a[mask]
    rgba(layer).save(DERIVATION/'workshop-dust-source-layer.png')
    rgba(backing).save(DERIVATION/'workshop-dust-recorded-underlay.png')
    offsets = [(0, 0), (0, 0), (0, -1), (0, -1), (1, -1), (1, -1), (1, -2), (1, -2),
               (1, -2), (0, -2), (0, -2), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0)]
    frames, allowed = [], mask.copy()
    for offset in offsets:
        allowed |= shifted_mask(mask, offset)
        frames.append(move_layer(backing, a, mask, offset))
    assert np.array_equal(frames[0], a) and np.array_equal(frames[-1], a)
    write_json(DERIVATION/'workshop-dust-registration.json', {
        'sourceNative': 'Source/Native/workshop-logical.png', 'sourceSha256': sha(NATIVE/'workshop-logical.png'),
        'sourceFleckCoordinates': [list(x) for x in chosen], 'sourceFleckRgba': [a[y, x].astype(int).tolist() for x, y in chosen],
        'underlaySourceDonors': donors, 'integerOffsets': [list(x) for x in offsets],
        'newParticleDesignPainted': False, 'method': 'Five actual generated air-fleck samples move by integer pixels; lamp and all props remain fixed.'})
    return frames, allowed, [{'dustLogicalOffset': list(x)} for x in offsets], ['Five sparse generated lamp-cone flecks drift slowly. Lamp intensity, clock, bench, stool and all other props are invariant.']


def edit_records(before, after):
    ys, xs = np.where((before != after).any(-1))
    return [[int(x), int(y), *before[y, x].astype(int).tolist(), *after[y, x].astype(int).tolist()] for y, x in zip(ys, xs)]


def save_clip(name, source_name, arrays, allowed, states, durations, mechanics):
    folder = ROOT/'Clips'/name
    folder.mkdir(parents=True, exist_ok=True)
    source_path = NATIVE/f'{source_name}.png'
    source = np.array(Image.open(source_path).convert('RGBA'))
    if name == 'workshop-close':
        frames = [rgba(a).crop(CLOSE_RECT).resize((640, 360), Image.Resampling.NEAREST) for a in arrays]
        mask = Image.fromarray(allowed.astype(np.uint8)*255).crop(CLOSE_RECT).resize((640, 360), Image.Resampling.NEAREST)
    else:
        frames = [rgba(a).resize((640, 360), Image.Resampling.NEAREST) for a in arrays]
        mask = Image.fromarray(allowed.astype(np.uint8)*255).resize((640, 360), Image.Resampling.NEAREST)
    mask_path = DERIVATION/f'{name}-allowed-mask.png'
    mask.save(mask_path)
    mask_array = np.array(mask) > 0
    frame_records = []
    for i, (image, duration, state) in enumerate(zip(frames, durations, states)):
        a = np.array(image)
        assert np.array_equal(a[~mask_array], source[~mask_array]), name+' altered static geometry'
        edits = edit_records(source, a)
        path = folder/f'{i:02}.png'
        image.save(path)
        edits_path = folder/f'{i:02}.source-edits.json'
        write_json(edits_path, edits)
        frame_records.append({'frame': i, 'durationMs': duration, 'state': state,
            'output': path.relative_to(REPO).as_posix(), 'pngSha256': sha(path),
            'rgbaSha256': hashlib.sha256(image.tobytes()).hexdigest(),
            'changedPixelsFromNative': len(edits), 'localEditsPath': edits_path.relative_to(REPO).as_posix()})
    return {'name': name, 'sourceNative': source_path.relative_to(REPO).as_posix(),
        'sourceNativeSha256': sha(source_path), 'allowedMaskPath': mask_path.relative_to(REPO).as_posix(),
        'allowedMaskSha256': sha(mask_path), 'staticOutsideMask': True, 'mechanics': mechanics,
        'frames': frame_records}, {'name': name, 'width': 640, 'height': 360,
            'sourceNative': source_path.relative_to(REPO).as_posix(), 'durations': durations,
            'frames': [f'{i:02}.png' for i in range(len(frames))]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-native', action='store_true', required=True)
    args = parser.parse_args()
    provenance = json.loads((ROOT/'Source/provenance.json').read_text())
    if not args.inspected_native or not provenance.get('inspectedNativeByMain'):
        raise SystemExit('Main must inspect native derivatives before animation')
    palette = np.array(json.loads((NATIVE/'palette.json').read_text())['colors'], np.uint8)
    raw = {n: np.array(Image.open(NATIVE/f'{n}-logical.png').convert('RGBA')) for n in ('relay', 'warden-core', 'workshop')}
    relay, guardian, workshop = relays(raw['relay'], palette), warden(raw['warden-core'], palette), workshops(raw['workshop'])
    records, clips = [], []
    for name, source, data, times in [('relay-power', 'relay', relay, DURATIONS_SHORT),
            ('warden-boot', 'warden-core', guardian, DURATIONS_SHORT),
            ('workshop-wide', 'workshop', workshop, DURATIONS_LONG),
            ('workshop-close', 'workshop-close', workshop, DURATIONS_LONG)]:
        frames, mask, states, mechanics = data
        record, plan = save_clip(name, source, frames, mask, states, times, mechanics)
        records.append(record); clips.append(plan)
    write_json(DERIVATION/'animation-derivation.json', {'revision': 'pixel-cinematics-animation-v1',
        'scriptSha256': sha(Path(__file__)), 'nativeDerivationSha256': sha(DERIVATION/'native-derivation.json'),
        'inspectedNativeByMain': True, 'humanAppearanceApproval': 'pending', 'geometryWarped': False,
        'interpolatedLimbScaling': False, 'unityFilesWritten': False, 'clips': records})
    write_json(ROOT/'Clips/clip-plan.json', {'clips': clips})
    print(json.dumps({'clips': len(clips), 'frames': sum(len(c['frames']) for c in clips),
                      'durationMs': [sum(c['durations']) for c in clips], 'humanAppearanceApproval': 'pending'}))


if __name__ == '__main__':
    main()
