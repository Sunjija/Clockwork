"""Independent read-only audit of image-first readability V2.

Only QA/audit-* evidence is written. Raw/generated/native/export files are never
modified. Mechanical checks are separate from subjective appearance approval
and human playtesting; neither is granted by this audit.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import argparse
import base64
import hashlib
import io
import json
import statistics
import sys

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-readability-image-first-v2'
QA = ROOT / 'QA'
NATIVE = ROOT / 'Source/Native'
RUNTIME = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/ReadabilityArtV2'
OLD = REPO / 'art/return-readability-v1/manifest.json'
EXPECTED_SIZE = {'wall': (36, 36), 'floor': (36, 36), 'weight': (30, 32),
                 'orb': (26, 26), 'weight_socket': (36, 36), 'orb_socket': (36, 36)}
RESULT = {'scope': 'independent source/native/export mechanical audit, not user approval or gameplay',
          'userAppearanceApproval': 'pending', 'humanFunValidation': 'pending',
          'passed': [], 'failed': [], 'observations': {}}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels_sha(im):
    return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()


def require(condition, label, detail=''):
    RESULT['passed' if condition else 'failed'].append({'check': label, 'detail': detail})
    return condition


def load(path):
    return json.loads(path.read_text())


def resolve(path):
    path = Path(path)
    if path.is_absolute():
        return path
    if (ROOT / path).exists():
        return ROOT / path
    return REPO / path


def source_audit():
    provenance = load(ROOT / 'Source/provenance.json')
    selected = provenance['selectedPreviewFiles']
    rows = []
    for name, rel in selected.items():
        saved = ROOT / rel
        matching = [c for c in provenance['calls'] if c['savedFile'] == rel]
        require(len(matching) == 1, 'generated-call-mapping:' + name, rel)
        if not matching:
            continue
        call = matching[0]
        original = Path(call['generatedOriginal'])
        require(original.exists(), 'generated-original-present:' + name, str(original))
        require(original.exists() and sha(original) == sha(saved), 'generated-original-unchanged:' + name)
        require((ROOT / call['promptFile']).exists(), 'prompt-preserved:' + name, call['promptFile'])
        image = Image.open(saved).convert('RGBA')
        mask = image.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        rows.append({'asset': name, 'file': rel, 'sha256': sha(saved), 'size': list(image.size),
                     'crop128': list(mask.getbbox()), 'unsafeNonzeroAlphaBbox': list(image.getbbox())})
    prior = QA / 'audit-source-baseline.json'
    if prior.exists():
        baseline = {r['asset']: r for r in load(prior)['assets']}
        for row in rows:
            require(row['asset'] in baseline and row['sha256'] == baseline[row['asset']]['sha256'],
                    'selected-raw-baseline-unchanged:' + row['asset'])
    else:
        prior.write_text(json.dumps({'note': 'Captured before native/export review; raw image SHA only.', 'assets': rows}, indent=2))
    RESULT['observations']['sources'] = rows


def rgba(path):
    return Image.open(path).convert('RGBA')


def visible_palette(image):
    return {p[:3] for p in image.getdata() if p[3]}


def luma(pixel):
    return .2126 * pixel[0] + .7152 * pixel[1] + .0722 * pixel[2] if pixel[3] else 0


def transparent_holes(image):
    w, h = image.size
    cells = {(x, y) for y in range(h) for x in range(w) if image.getpixel((x, y))[3] == 0}
    holes = []
    while cells:
        start = cells.pop()
        visited, todo = {start}, [start]
        while todo:
            x, y = todo.pop()
            for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if p in cells:
                    cells.remove(p)
                    visited.add(p)
                    todo.append(p)
        if not any(x in (0, w - 1) or y in (0, h - 1) for x, y in visited):
            xs, ys = zip(*visited)
            holes.append({'pixels': len(visited), 'bounds': [min(xs), min(ys), max(xs) + 1, max(ys) + 1]})
    return sorted(holes, key=lambda x: -x['pixels'])


def native_audit():
    manifest = ROOT / 'Source/Derivation/native-derivation.json'
    require(manifest.exists(), 'native-derivation-manifest-present', str(manifest))
    if not manifest.exists():
        return
    mapping = load(manifest)['assets']
    if isinstance(mapping, list):
        mapping = {r['asset']: r for r in mapping}
    all_palette = set()
    recorded_palette = load(NATIVE / 'palette.json')['colors']
    images = {}
    for name, size in EXPECTED_SIZE.items():
        path = NATIVE / (name + '.png')
        require(path.exists(), 'native-present:' + name)
        if not path.exists():
            continue
        image = rgba(path)
        images[name] = image
        require(image.size == size, 'native-dimensions:' + name, repr(image.size))
        require(set(image.getchannel('A').getdata()) <= {0, 255}, 'native-binary-alpha:' + name)
        all_palette |= visible_palette(image)
        record = mapping.get(name, {})
        require(record.get('cropAlphaThreshold') == 128, 'crop-threshold-128:' + name)
        source = resolve(record.get('generatedSource', 'missing'))
        require(source.exists(), 'native-source-present:' + name, str(source))
        if source.exists():
            require(record.get('sourceSha256') == sha(source), 'native-source-sha:' + name)
            bounds = list(rgba(source).getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox())
            require(record.get('cropRect') == bounds, 'crop128-exact:' + name, f"record={record.get('cropRect')} expected={bounds}")
        require(record.get('outputSha256') in (sha(path), pixels_sha(image)), 'native-output-sha:' + name)
        pixel_map = resolve(record.get('pixelMap', 'missing'))
        require(pixel_map.exists(), 'native-pixel-source-map:' + name, str(pixel_map))
        if pixel_map.exists():
            trace = load(pixel_map)
            require(trace['sourceSha256'] == record.get('sourceSha256'), 'pixel-map-source-sha:' + name)
            entries = trace['pixels']
            covered = {tuple(p['target']) for p in entries}
            require(len(entries) == size[0] * size[1] and len(covered) == len(entries), 'pixel-map-complete-unique:' + name)
            exact = all(tuple(p['rgba']) == image.getpixel(tuple(p['target'])) for p in entries)
            require(exact, 'pixel-map-replays-native:' + name)
            entries_match = all(p['paletteEntry'] is None and p['rgba'][3] == 0 or
                                p['paletteEntry'] is not None and tuple(recorded_palette[p['paletteEntry']]) == tuple(p['rgba'][:3]) for p in entries)
            require(entries_match, 'pixel-map-palette-exact:' + name)
            crop = record['cropRect']
            within = all(p.get('sourceRect') is None and p['rgba'][3] == 0 or
                         p.get('sourceRect') is not None and crop[0] - .001 <= p['sourceRect'][0] <= p['sourceRect'][2] <= crop[2] + .001 and
                         crop[1] - .001 <= p['sourceRect'][1] <= p['sourceRect'][3] <= crop[3] + .001 for p in entries)
            require(within, 'source-footprints-inside-128-crop:' + name)
        # V1 is layout reference only; a byte-identical native copy would require explanation.
        v1_clip = {'weight': 'battery-idle', 'orb': 'orb-idle', 'weight_socket': 'amber-slot-empty',
                   'orb_socket': 'cyan-slot-empty', 'wall': 'wall-00', 'floor': 'floor'}[name]
        v1 = REPO / 'art/return-readability-v1/Clips' / v1_clip / '00.png'
        require(rgba(v1).tobytes() != image.tobytes(), 'not-v1-native-copy:' + name)
    require(len(all_palette) <= 48, 'native-shared-palette-cap48', str(len(all_palette)))
    RESULT['observations']['nativePaletteColors'] = len(all_palette)
    if 'weight' in images:
        holes = transparent_holes(images['weight'])
        require(any(h['pixels'] >= 6 and h['bounds'][2] - h['bounds'][0] >= 3 and h['bounds'][3] - h['bounds'][1] >= 2 for h in holes),
                'weight-handle-hole-readable', repr(holes))
        RESULT['observations']['weightTransparentHoles'] = holes
    if 'orb' in images:
        im = images['orb']
        require(all(im.getpixel(p)[3] == 0 for p in ((0, 0), (25, 0), (0, 25), (25, 25))), 'orb-empty-corners')
    for name in ('weight_socket', 'orb_socket'):
        if name not in images:
            continue
        im = images[name]
        centre = [luma(im.getpixel((x, y))) for y in range(9, 27) for x in range(9, 27)]
        dark_ratio = sum(v < 65 for v in centre) / len(centre)
        require(dark_ratio >= .6, 'socket-dark-negative-space:' + name, f'{dark_ratio:.3f} interior below luma65; heuristic, not aesthetic approval')
    if all(k in images for k in ('wall', 'floor')):
        means = {k: statistics.mean(luma(p) for p in v.getdata() if p[3]) for k, v in images.items()}
        require(means['floor'] < means['wall'], 'floor-darker-than-wall', repr(means))
        RESULT['observations']['visibleMeanLuminance'] = means


def export_audit():
    source = ROOT / 'Clips'
    manifest = RUNTIME / 'clips.json'
    require(manifest.exists(), 'runtime-clips-present', str(manifest))
    if not manifest.exists():
        return
    expected = {c['name']: c for c in load(OLD)['clips']}
    actual_list = load(manifest)['clips']
    actual = {c['name']: c for c in actual_list}
    require(len(actual) == len(actual_list) == 31 and set(actual) == set(expected), 'clip-name-set31')
    require(sum(len(c['durations']) for c in actual.values()) == 77, 'native-frame-count77')
    require(load(source / 'clips.json')['clips'] == actual_list, 'source-runtime-manifest-identical')
    require((source / 'export-manifest.json').exists(), 'frame-source-mapping-manifest-present')
    provenance = load(source / 'export-manifest.json')
    mapped = {m['name']: m for m in provenance['mappings']}
    require(set(mapped) == set(actual), 'all-clips-have-native-source-mapping')
    palette = set()
    frames = []
    for name, spec in actual.items():
        prior = expected[name]
        record = mapped.get(name, {})
        anchor = resolve(record.get('nativeSource', 'missing'))
        require(anchor.exists() and record.get('nativeSha256') == sha(anchor), 'export-native-sha:' + name, str(anchor))
        require(len(record.get('frames', [])) == len(spec['durations']), 'frame-provenance-count:' + name)
        require(spec['durations'] == prior['durations'], 'unchanged-timing:' + name)
        clip = source / name
        piskel_path = clip / (name + '.piskel')
        require(piskel_path.exists(), 'piskel-present:' + name)
        piskel = load(piskel_path)['piskel']
        layer = json.loads(piskel['layers'][0])
        sheet = rgba(clip / 'sheet.png')
        embedded = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        require(embedded.tobytes() == sheet.tobytes(), 'piskel-sheet-identical:' + name)
        require(layer['frameCount'] == len(spec['durations']), 'piskel-frame-count:' + name)
        base = rgba(clip / '00.png')
        runtime_files = sorted((RUNTIME / name).glob('[0-9][0-9].png'))
        require(len(runtime_files) == len(spec['durations']), 'runtime-png-count:' + name)
        decoded = Image.open(clip / 'native.apng') if len(spec['durations']) > 1 else None
        if decoded:
            require(decoded.n_frames == len(spec['durations']), 'apng-frame-count:' + name)
        for i, duration in enumerate(spec['durations']):
            tag = name + f'/{i:02}'
            path = clip / f'{i:02}.png'
            image = rgba(path)
            palette |= visible_palette(image)
            require(image.size == (prior['width'], prior['height']), 'export-dimensions:' + tag)
            require(set(image.getchannel('A').getdata()) <= {0, 255}, 'export-binary-alpha:' + tag)
            runtime = RUNTIME / name / f'{i:02}.png'
            require(sha(path) == sha(runtime), 'runtime-copy-identical:' + tag)
            if i < len(record.get('frames', [])):
                frame_record = record['frames'][i]
                require(frame_record.get('pngSha256') == sha(path) and frame_record.get('rgbaSha256') == pixels_sha(image),
                        'recorded-frame-sha:' + tag)
            settings = runtime.with_name(runtime.name + '.meta').read_text()
            require('filterMode: 0' in settings and 'enableMipMap: 0' in settings and 'textureCompression: 1' not in settings and 'spritePixelsToUnits: 64' in settings,
                    'point-nomip-uncompressed:' + tag)
            replay = base.copy()
            for x, y, r, g, b, a in load(clip / f'{i:02}.pixels.json'):
                replay.putpixel((x, y), (r, g, b, a))
            require(replay.tobytes() == image.tobytes(), 'pixel-delta-replay-identical:' + tag)
            anchor_replay = rgba(anchor)
            true_before = True
            source_edits = load(clip / f'{i:02}.source-edits.json')
            for entry in source_edits:
                x, y = entry[:2]
                before, after = tuple(entry[2:6]), tuple(entry[6:10])
                true_before = true_before and anchor_replay.getpixel((x, y)) == before
                anchor_replay.putpixel((x, y), after)
            require(true_before and anchor_replay.tobytes() == image.tobytes(), 'native-source-edit-replay-identical:' + tag)
            extracted = sheet.crop((i * image.width, 0, (i + 1) * image.width, image.height))
            require(extracted.tobytes() == image.tobytes(), 'sheet-frame-identical:' + tag)
            if decoded:
                decoded.seek(i)
                require(decoded.convert('RGBA').tobytes() == image.tobytes() and round(decoded.info['duration']) == duration,
                        'apng-frame-timing-identical:' + tag)
            frames.append({'clip': name, 'index': i, 'sha256': sha(path), 'pixelsSha256': pixels_sha(image)})
    require(len(palette) <= 48, 'export-shared-palette-cap48', str(len(palette)))
    RESULT['observations']['exportPaletteColors'] = len(palette)
    RESULT['observations']['exportFrames'] = frames
    # Assert base identity is genuinely the derived anchor, before state edits.
    for asset, clip_name in (('weight', 'battery-idle'), ('orb', 'orb-idle'), ('weight_socket', 'amber-slot-empty'),
                             ('orb_socket', 'cyan-slot-empty'), ('floor', 'floor'), ('wall', 'wall-00')):
        require(rgba(NATIVE / (asset + '.png')).tobytes() == rgba(source / clip_name / '00.png').tobytes(),
                'idle-is-generated-derived-native:' + asset)
    for mask in range(16):
        image = rgba(source / f'wall-{mask:02}' / '00.png')
        require(all(p[3] == 255 for p in image.getdata()), 'wall-full-cell-alpha:' + str(mask))
        native_wall = rgba(NATIVE / 'wall.png')
        unchanged_centre = all(image.getpixel((x, y)) == native_wall.getpixel((x, y)) for y in range(4, 32) for x in range(4, 32))
        require(unchanged_centre, 'wall-architecture-centre-not-repainted:' + str(mask))
        if mask & 2:
            adjacent = rgba(source / f'wall-{((mask & (1 | 4)) | 8):02}' / '00.png')
            require([image.getpixel((35, y)) for y in range(36)] == [adjacent.getpixel((0, y)) for y in range(36)],
                    'wall-east-west-connected-continuity:' + str(mask))
        if mask & 4:
            adjacent = rgba(source / f'wall-{((mask & (2 | 8)) | 1):02}' / '00.png')
            require([image.getpixel((x, 35)) for x in range(36)] == [adjacent.getpixel((x, 0)) for x in range(36)],
                    'wall-south-north-connected-continuity:' + str(mask))


def visual_sheet():
    # Reviewer convenience only, and explicitly not a screenshot or user approval.
    if not all((NATIVE / (n + '.png')).exists() for n in EXPECTED_SIZE):
        return
    canvas = Image.new('RGB', (1140, 510), (17, 27, 36))
    d = ImageDraw.Draw(canvas)
    d.text((12, 9), 'INDEPENDENT V2 NATIVE AUDIT | 5x nearest | technical review, appearance approval pending', fill=(225, 240, 240))
    for i, name in enumerate(EXPECTED_SIZE):
        x = i * 190 + 12
        im = rgba(NATIVE / (name + '.png'))
        scale = im.resize((im.width * 5, im.height * 5), Image.Resampling.NEAREST)
        canvas.paste(scale, (x, 42 + 180 - scale.height), scale)
        gray = ImageOps.grayscale(scale).convert('RGBA')
        gray.putalpha(scale.getchannel('A'))
        canvas.paste(gray, (x, 270 + 180 - scale.height), gray)
        d.text((x, 230), name, fill=(190, 215, 223))
        d.text((x, 460), 'grayscale / ' + str(im.size), fill=(150, 175, 190))
    canvas.save(QA / 'audit-native-review.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('source', 'native', 'export', 'all'), default='all')
    args = parser.parse_args()
    QA.mkdir(parents=True, exist_ok=True)
    source_audit()
    if args.phase in ('native', 'all'):
        native_audit()
        visual_sheet()
    if args.phase in ('export', 'all'):
        export_audit()
    RESULT['mechanicalPassed'] = not RESULT['failed']
    RESULT['phase'] = args.phase
    out = QA / ('audit-' + args.phase + '-report.json')
    out.write_text(json.dumps(RESULT, indent=2))
    print(json.dumps({'phase': args.phase, 'mechanicalPassed': RESULT['mechanicalPassed'],
                      'checksPassed': len(RESULT['passed']), 'checksFailed': len(RESULT['failed']),
                      'failed': RESULT['failed'], 'report': str(out)}))
    return 0 if RESULT['mechanicalPassed'] else 1


if __name__ == '__main__':
    sys.exit(main())
