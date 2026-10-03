"""Derive inspected real imagegen cutscene anchors; never draw replacement designs.

Uniform premultiplied BOX sampling, a fixed 64-color palette (the existing
guardian's 32 plus generated amber/cyan/navy ramps), recorded native indices,
integer NEAREST exports, and one shared workshop source for both camera cuts.
Output is confined to a new unapproved offline art package. No Unity writes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-pixel-cinematics-v1'
LOGICAL = (320, 180)
CANVAS = (640, 360)
NAMES = ('relay', 'warden-core', 'workshop')
CLOSE_RECT = (70, 25, 230, 115)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def sample(path):
    image = Image.open(path).convert('RGBA')
    w, h = image.size
    # A single uniform scale; the tiny aspect excess is cropped, never squashed.
    cw, ch = min(w, h * 16 / 9), min(h, w * 9 / 16)
    box = ((w-cw)/2, (h-ch)/2, (w+cw)/2, (h+ch)/2)
    result = image.convert('RGBa').resize(LOGICAL, Image.Resampling.BOX, box=box).convert('RGBA')
    if set(result.getchannel('A').get_flattened_data()) != {255}:
        raise ValueError('These scene anchors must be fully opaque; no background synthesis.')
    return result, {'generatedDimensions': [w, h], 'sourceRect': list(box),
                    'sourceStep': [cw/320, ch/180], 'wholeImageUniformScale': 320/cw,
                    'geometryWarped': False, 'bodyPartScaling': False}


def ramp(points, count):
    if not len(points):
        raise ValueError('Generated source is missing a requested color ramp')
    pixels = Image.fromarray(points.astype(np.uint8).reshape(-1, 1, 3), 'RGB')
    indexed = pixels.quantize(colors=count, method=Image.Quantize.MEDIANCUT,
                             dither=Image.Dither.NONE)
    colors = np.array(indexed.getpalette(), np.uint8).reshape(-1, 3)
    indices = sorted(set(indexed.get_flattened_data()))
    return [tuple(map(int, colors[i])) for i in indices]


def palette_from_sources(samples):
    original = REPO / 'art/return-v7-guardian/manifest.json'
    guardian = [tuple(bytes.fromhex(c[1:])) for c in json.loads(original.read_text())['palette']]
    all_rgb = np.concatenate([np.array(im)[..., :3].reshape(-1, 3) for im in samples.values()]).astype(np.int32)
    r, g, b = all_rgb.T
    amber = (r > g+15) & (g > b+10) & (g*100 > r*42)
    cyan = (g > r+25) & (b > r+20) & (g > 70)
    navy = (b >= r+4) & (g >= r) & (g < 80)
    colors = list(dict.fromkeys(guardian + ramp(all_rgb[amber], 16) +
                               ramp(all_rgb[cyan], 8) + ramp(all_rgb[navy], 8)))
    if len(colors) > 64:
        raise ValueError('Fixed cinematic palette exceeds64 colors')
    return np.array(colors, np.uint8), original


def map_rgb(rgb, palette):
    points = rgb.reshape(-1, 3).astype(np.int32)
    p = palette.astype(np.int32)
    # Match the established guardian pipeline's warm/cool separation.
    def groups(a):
        r, g, b = a.T
        red = (r > g+30) & (r > b+30) & ((g-b)*100 < r*20)
        amber = (r > g+15) & (g > b+10) & ~red
        cyan = (g > r+25) & (b > r+20) & (g > 70)
        return red, amber, cyan
    sg, tg = groups(points), groups(p)
    results = []
    for start in range(0, len(points), 4096):
        pts = points[start:start+4096]
        d = ((pts[:, None] - p[None])**2).sum(-1)
        for source_group, target_group in zip(sg, tg):
            if target_group.any():
                d[np.ix_(source_group[start:start+4096], ~target_group)] += 10**7
        results.append(d.argmin(1))
    indices = np.concatenate(results).reshape(rgb.shape[:2])
    return palette[indices], indices


def native(rgb):
    alpha = np.full((*rgb.shape[:2], 1), 255, np.uint8)
    return Image.fromarray(np.concatenate([rgb, alpha], -1), 'RGBA')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', action='store_true', required=True)
    args = parser.parse_args()
    provenance_path = ROOT / 'Source/provenance.json'
    provenance = json.loads(provenance_path.read_text())
    if not args.inspected_anchors or provenance.get('inspectedByMain') is not True:
        raise SystemExit('Inspect and show every actual generated anchor first.')
    samples, records = {}, {}
    for name in NAMES:
        record = provenance['selectedSources'][name]
        source = ROOT / record['projectCopy']
        if sha(source) != record['sha256']:
            raise ValueError(f'{name}: source/provenance mismatch')
        samples[name], records[name] = sample(source)
        records[name].update({'source': source.relative_to(REPO).as_posix(),
                              'sourceSha256': sha(source)})
    palette, guardian_manifest = palette_from_sources(samples)
    palette_path = ROOT / 'Source/Native/palette.json'
    write_json(palette_path, {'colors': palette.astype(int).tolist(), 'count': len(palette),
              'existingGuardianPalette': guardian_manifest.relative_to(REPO).as_posix(),
              'existingGuardianPaletteSha256': sha(guardian_manifest),
              'additionalRamps': '16 amber +8 cyan +8 navy sampled from actual generated scenes',
              'colorsInventedForNewGeometry': False})
    selected = {}
    for name in NAMES:
        rgb, indices = map_rgb(np.array(samples[name])[..., :3], palette)
        logical = native(rgb)
        selected[name] = logical
        folder = ROOT / 'Source/Native'
        folder.mkdir(parents=True, exist_ok=True)
        logical_path, output = folder/f'{name}-logical.png', folder/f'{name}.png'
        logical.save(logical_path)
        full = logical.resize(CANVAS, Image.Resampling.NEAREST)
        full.save(output)
        index_path = ROOT/'Source/Derivation'/f'{name}-pixel-map.json'
        write_json(index_path, {'source': records[name]['source'],
                   'sourceSha256': records[name]['sourceSha256'],
                   'sourceRect': records[name]['sourceRect'],
                   'sourceStep': records[name]['sourceStep'], 'sampleSize': list(LOGICAL),
                   'nativeCanvas': list(CANVAS), 'integerScale': 2,
                   'formula': 'Each logical sample is premultiplied BOX over its source rectangle; fixed palette index; each sample expands to exactly2x2 native pixels.',
                   'palette': palette_path.relative_to(REPO).as_posix(),
                   'paletteSha256': sha(palette_path), 'paletteIndices': indices.astype(int).tolist(),
                   'cleanupEdits': [], 'silhouettePainted': False})
        records[name].update({'logicalOutput': logical_path.relative_to(REPO).as_posix(),
                              'logicalSha256': sha(logical_path),
                              'output': output.relative_to(REPO).as_posix(), 'outputSha256': sha(output),
                              'pixelMap': index_path.relative_to(REPO).as_posix(),
                              'pixelMapSha256': sha(index_path), 'nativeCanvas': list(CANVAS),
                              'logicalGrid': list(LOGICAL), 'integerScale': 2,
                              'uniqueColors': len(set(logical.get_flattened_data()))})
    close = selected['workshop'].crop(CLOSE_RECT)
    close.resize(LOGICAL, Image.Resampling.NEAREST).save(ROOT/'Source/Native/workshop-close-logical.png')
    close.resize(CANVAS, Image.Resampling.NEAREST).save(ROOT/'Source/Native/workshop-close.png')
    records['workshop-close'] = {'sameSourceAs': 'workshop', 'source': records['workshop']['source'],
         'sourceSha256': records['workshop']['sourceSha256'], 'logicalCropRect': list(CLOSE_RECT),
         'cropSize': list(close.size), 'nativeCanvas': list(CANVAS), 'integerScale': 4,
         'output': (ROOT/'Source/Native/workshop-close.png').relative_to(REPO).as_posix(),
         'outputSha256': sha(ROOT/'Source/Native/workshop-close.png'),
         'newObjectsAuthored': False, 'geometryWarped': False}
    write_json(ROOT/'Source/Derivation/native-derivation.json', {
        'revision': 'pixel-cinematics-native-v1', 'inspectedByMain': True,
        'humanAppearanceApproval': 'pending', 'scriptSha256': sha(Path(__file__)),
        'method': 'Generated individual scene -> uniform premultiplied BOX logical320x180 -> fixed64palette -> integer2x native640x360; close shot is the same workshop crop4x.',
        'paletteSha256': sha(palette_path), 'assets': records, 'unityFilesWritten': False})
    qa = ROOT/'QA'
    qa.mkdir(parents=True, exist_ok=True)
    contact = Image.new('RGB', (1280, 780), (12, 18, 28))
    draw = ImageDraw.Draw(contact)
    for i, (name, label) in enumerate([('relay', 'A2 RELAY'), ('warden-core', 'A3 GUARDIAN CORE'),
                                     ('workshop', 'B3 WORKSHOP WIDE'), ('workshop-close', 'B4 SAME WORKSHOP CROP')]):
        x, y = (i%2)*640, (i//2)*390
        draw.text((x+10, y+8), label+' | UNAPPROVED / OFFLINE', fill=(211, 227, 231))
        contact.paste(Image.open(ROOT/'Source/Native'/f'{name}.png').convert('RGB'), (x, y+26))
    contact.save(qa/'contact-2x.png')
    print(json.dumps({'nativeAssets': 4, 'logicalGrid': LOGICAL, 'nativeCanvas': CANVAS,
                      'paletteColors': len(palette), 'humanAppearanceApproval': 'pending'}))


if __name__ == '__main__':
    main()
