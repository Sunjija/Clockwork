"""Independent static WardenV8 audit; no Unity/editor/app launch.

Writes QA/audit-* only. Original/native/runtime sources are read-only. A passed
mechanical audit is not human appearance approval or a gameplay/fun test.
Original generated-cache checks are author-host evidence; preserved generated
files plus SHA baselines remain available for later portable verification.
"""
from pathlib import Path
from PIL import Image, ImageFilter
import argparse
import base64
import hashlib
import io
import json
import statistics
import subprocess
import sys
import numpy as np

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-v8-guardian'
QA = ROOT / 'QA'
V7 = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenV7'
V8 = V7.parent / 'WardenV8'
NATIVE = ROOT / 'Source/Native'
ALLOWED = {f'idle/{i:02}.png' for i in range(8)} | {f'wave-strike/{i:02}.png' for i in range(3)} | {'slam-land/00.png', 'slam-land/02.png'}
RESULT = {'scope': 'independent static source/native/export audit; no game/Unity launched',
          'humanAppearanceApproval': 'pending', 'humanFunValidation': 'pending',
          'passed': [], 'failed': [], 'observations': {}}


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixels_sha(image):
    return hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()


def rgba(path):
    return Image.open(path).convert('RGBA')


def require(condition, label, detail=''):
    RESULT['passed' if condition else 'failed'].append({'check': label, 'detail': detail})
    return condition


def resolve(path):
    path = Path(path)
    if path.is_absolute():
        return path
    for parent in (ROOT, REPO):
        if (parent / path).exists():
            return parent / path
    return ROOT / path


def rgb_palette():
    colors = load(REPO / 'art/return-v7-guardian/manifest.json')['palette']
    return {tuple(bytes.fromhex(c.lstrip('#'))) for c in colors}


def planted_bottom(image):
    bbox = image.getbbox()
    low = bbox[3] - 1
    columns = [max(y for y in range(image.height) if image.getpixel((x, y))[3])
               for x in range(image.width) if any(image.getpixel((x, y))[3] for y in range(low - 9, low + 1))]
    return statistics.median(columns)


def baseline():
    files = sorted(V7.glob('*/*.png'))
    require(len(files) == 71, 'v7-baseline-frame-count71', str(len(files)))
    rows = {p.relative_to(V7).as_posix(): sha(p) for p in files}
    path = QA / 'audit-v7-baseline.json'
    if path.exists():
        old = load(path)['frames']
        require(rows == old, 'v7-package-unchanged-from-audit-baseline')
    else:
        path.write_text(json.dumps({'note': 'Captured before WardenV8 export validation; immutable V7 reference hashes.', 'frames': rows}, indent=2))
    require(len(rgb_palette()) == 32, 'v7-palette32')
    raw_rows = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / 'Source/Generated').glob('*/*.png'))}
    if raw_rows:
        raw_baseline = QA / 'audit-raw-generation-baseline.json'
        if raw_baseline.exists():
            earlier = load(raw_baseline)['files']
            require(all(raw_rows.get(p) == digest for p, digest in earlier.items()), 'earlier-generated-candidates-preserved-byte-exact')
        else:
            raw_baseline.write_text(json.dumps({'note': 'Original candidates captured before native conversion; additional actual generated revisions may be added without overwriting these.', 'files': raw_rows}, indent=2))


def source_provenance():
    path = ROOT / 'Source/provenance.json'
    require(path.exists(), 'actual-generation-provenance-present')
    if not path.exists():
        return
    provenance = load(path)
    selected = provenance['selectedNativeSources']
    require(set(selected) == {'idle', 'jaw-impact-03', 'jaw-impact-04', 'jaw-impact-05', 'slam-land'}, 'five-selected-generated-pose-targets')
    require(provenance['successfulImageCalls'] == len(provenance['calls']) == 6, 'six-successful-calls-not-five-nativeframes')
    require(provenance.get('generatedAnchorsInspected') is True, 'generated-anchor-inspection-recorded-not-human-approval')
    caches_verified = True
    for call in provenance['calls']:
        tag = call['asset'] + '-rev' + str(call['revision'])
        original, saved = Path(call['generatedOriginal']), ROOT / call['savedFile']
        require(original.exists(), 'author-host-generated-original-present:' + tag, str(original))
        require(original.exists() and saved.exists() and sha(original) == sha(saved), 'saved-imagegen-original-byte-identical:' + tag)
        caches_verified = caches_verified and original.exists() and saved.exists() and sha(original) == sha(saved)
        prompt_file = ROOT / call['promptFile']
        require(prompt_file.exists(), 'actual-prompt-file-preserved:' + tag)
        if prompt_file.exists():
            requests = load(prompt_file)
            entries = requests.get('requests', [requests.get('request', {})])
            matching = [r for r in entries if r.get('asset') == call['asset']]
            require(len(matching) == 1 and bool(matching[0].get('prompt')), 'actual-full-prompt-identified:' + tag)
            if matching:
                require(matching[0]['referenced_image_paths'] == call['referenceImages'], 'actual-call-reference-mapping:' + tag)
    for name, saved in selected.items():
        require(len([c for c in provenance['calls'] if c['asset'] == name and c['savedFile'] == saved]) == 1,
                'selected-pose-real-call-mapping:' + name)
    RESULT['observations']['authorHostGeneratedCacheVerified'] = caches_verified
    RESULT['observations']['generatedSources'] = selected


def source_and_native():
    path = ROOT / 'Source/Derivation/native-derivation.json'
    require(path.exists(), 'native-manifest-present')
    if not path.exists():
        return
    manifest = load(path)
    require(manifest['sourceSelectionSha256'] == sha(ROOT / manifest['sourceSelection']), 'native-selection-provenance-sha')
    assets = manifest['assets']
    require(set(assets) == {'idle', 'jaw-impact-03', 'jaw-impact-04', 'jaw-impact-05', 'slam-land'}, 'five-actual-anchor-assets')
    rows = []
    palette = rgb_palette()
    ordered_palette = [list(bytes.fromhex(c.lstrip('#'))) for c in load(REPO / 'art/return-v7-guardian/manifest.json')['palette']]
    for name, record in assets.items():
        source = resolve(record['generatedSource'])
        require(source.exists(), 'generated-source-present:' + name, str(source))
        require(record['sourceSha256'] == sha(source), 'generated-source-sha:' + name)
        threshold = record.get('sourceCropAlphaThreshold', record.get('cropAlphaThreshold'))
        require(threshold == 128, 'crop-threshold128:' + name)
        raw = rgba(source)
        bounds = list(raw.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox())
        require(record['cropRect'] == bounds, 'crop128-exact:' + name, repr(bounds))
        rows.append({'asset': name, 'file': str(source.relative_to(ROOT)), 'sha256': sha(source), 'crop128': bounds})
        native_path = NATIVE / (name + '.png')
        image = rgba(native_path)
        require(image.size == (192, 176), 'native-canvas192x176:' + name, repr(image.size))
        require(set(image.getchannel('A').get_flattened_data()) <= {0, 255}, 'native-binary-alpha:' + name)
        require({p[:3] for p in image.get_flattened_data() if p[3]} <= palette, 'native-v7-palette-only:' + name)
        require(record['outputSha256'] in (sha(native_path), pixels_sha(image)), 'native-output-sha:' + name)
        require(record.get('nativeGroundRow') == 163 and planted_bottom(image) == 163, 'native-ground-baseline163:' + name)
        bbox = image.getbbox()
        fit = record['fitSize']
        width = record['targetWidth']
        require(record.get('bodyPartIndependentScaling') is False and fit == [width, round((bounds[3] - bounds[1]) * width / (bounds[2] - bounds[0]))],
                'uniform-whole-pose-scale-only:' + name)
        require(abs((bbox[0] + bbox[2]) / 2 - 96) <= .5, 'horizontal-registration-x96:' + name)
        if name == 'slam-land':
            require(bbox[2] - bbox[0] <= 149, 'landing-width-at-most149', repr(bbox))
        pixel_map = resolve(record['pixelMap'])
        require(pixel_map.exists(), 'native-source-footprints-present:' + name)
        if pixel_map.exists():
            trace = load(pixel_map)
            require(trace['sourceSha256'] == record['sourceSha256'] and trace['cropRect'] == bounds, 'pixel-map-source-crop-sha:' + name)
            require(trace['nativeCanvas'] == [192, 176] and trace['sampleSize'] == record['fitSize'] and trace['offset'] == record['offset'],
                    'pixel-map-registration:' + name)
            fit = record['fitSize']
            steps = [(bounds[2] - bounds[0]) / fit[0], (bounds[3] - bounds[1]) / fit[1]]
            require(all(abs(a - b) < 1e-8 for a, b in zip(trace['sourceStep'], steps)), 'pixel-map-source-footprint-step:' + name)
            indices = trace['samplePaletteIndices']
            require(len(indices) == fit[1] and all(len(row) == fit[0] for row in indices), 'pixel-map-full-sample-grid:' + name)
            replay = Image.new('RGBA', (192, 176))
            ox, oy = record['offset']
            in_bounds = True
            for y, row in enumerate(indices):
                for x, index in enumerate(row):
                    if index < 0:
                        continue
                    tx, ty = x + ox, y + oy
                    in_bounds = in_bounds and 0 <= tx < 192 and 0 <= ty < 176
                    if 0 <= tx < 192 and 0 <= ty < 176:
                        replay.putpixel((tx, ty), (*ordered_palette[index], 255))
            require(in_bounds and replay.tobytes() == image.tobytes(), 'pixel-map-replays-native:' + name)
            # Reconstruct the true generated-source area samples independently.
            cut = raw.crop(bounds)
            small = cut.convert('RGBa').resize(fit, Image.Resampling.BOX).convert('RGBA')
            alpha = np.where(np.array(small)[..., 3] >= 128, 255, 0).astype(np.uint8)
            sharpened = np.array(small.convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2)).convert('RGBA'))
            sharpened[..., 3] = alpha
            sharpened[alpha == 0] = 0
            sampled = rgba(ROOT / 'Source/Derivation' / (name + '-area-sampled.png'))
            require(Image.fromarray(sharpened).tobytes() == sampled.tobytes(), 'raw-source-premultiplied-area-replay:' + name)
            mapped = sharpened.copy()
            mask = mapped[..., 3] > 0
            rgb = mapped[mask, :3].astype(int)
            colors = np.array(ordered_palette).astype(int)
            distance = ((rgb[:, None] - colors[None]) ** 2).sum(-1)
            warm_pixels = (rgb[:, 0] > rgb[:, 1] + 30) & (rgb[:, 0] > rgb[:, 2] + 30)
            warm_colors = (colors[:, 0] > colors[:, 1] + 30) & (colors[:, 0] > colors[:, 2] + 30)
            distance[np.ix_(warm_pixels, ~warm_colors)] += 10 ** 7
            distance[np.ix_(~warm_pixels, warm_colors)] += 10 ** 7
            mapped[mask, :3] = colors[distance.argmin(1)]
            mapped_image = rgba(ROOT / 'Source/Derivation' / (name + '-palette-mapped.png'))
            require(Image.fromarray(mapped).tobytes() == mapped_image.tobytes(), 'raw-source-palette-replay:' + name)
            cleanup = mapped_image.copy()
            true_before, permitted = True, True
            allowed_ops = {'v7-low-contrast-single-tone-fold', 'v7-disconnected-crumb-removal', 'v7-source-silhouette-ink'}
            for edit in trace['edits']:
                xy = tuple(edit['sample'])
                true_before = true_before and cleanup.getpixel(xy) == tuple(edit['before'])
                permitted = permitted and edit['operation'] in allowed_ops
                cleanup.putpixel(xy, tuple(edit['after']))
            exact_cleanup = all(cleanup.getpixel((x, y)) == ((*ordered_palette[index], 255) if index >= 0 else (0, 0, 0, 0))
                                for y, row in enumerate(indices) for x, index in enumerate(row))
            require(true_before and permitted and exact_cleanup, 'limited-source-cleanup-replay:' + name)
        RESULT['observations'][name] = {'bounds': bbox, 'groundMedian': planted_bottom(image), 'width': bbox[2] - bbox[0]}
    base = QA / 'audit-generated-baseline.json'
    if base.exists():
        require(rows == load(base)['assets'], 'generated-baseline-unchanged')
    else:
        base.write_text(json.dumps({'note': 'Saved generated originals; portable SHA evidence. Cache-origin verification recorded separately.', 'assets': rows}, indent=2))


def edited_replay(anchor, path):
    replay = anchor.copy()
    true_before = True
    for entry in load(path):
        x, y = entry[:2]
        before, after = tuple(entry[2:6]), tuple(entry[6:10])
        true_before = true_before and replay.getpixel((x, y)) == before
        replay.putpixel((x, y), after)
    return true_before, replay


def exports():
    manifest = load(ROOT / 'export-manifest.json')
    require(manifest['nativeDerivationSha256'] == sha(ROOT / manifest['nativeDerivationRecord']), 'export-native-derivation-record-sha')
    for name, input_record in manifest['nativeInputs'].items():
        require(input_record['sha256'] == sha(resolve(input_record['path'])), 'export-native-input-sha:' + name)
    mappings = {m['name']: m for m in manifest['mappings']}
    old = load(V7 / 'clips.json')['clips']
    new = load(V8 / 'clips.json')['clips']
    require(len(new) == 15 and sum(len(c['durations']) for c in new) == 71, '15clips71exposures')
    require(old == new and sha(V7 / 'clips.json') == sha(V8 / 'clips.json'), 'clip-manifest-byte-copy-unchanged-timings')
    require(set(mappings) == {c['name'] for c in new}, 'every-clip-export-provenance')
    changed = set()
    colors = set()
    source = ROOT / 'Clips'
    for clip in new:
        name = clip['name']
        record = mappings[name]
        require(record['durations'] == clip['durations'], 'export-mapping-timing:' + name)
        folder = source / name
        piskel = load(folder / (name + '.piskel'))['piskel']
        layer = json.loads(piskel['layers'][0])
        sheet = rgba(folder / 'sheet.png')
        embedded = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        require(embedded.tobytes() == sheet.tobytes(), 'piskel-sheet-identical:' + name)
        require(layer['frameCount'] == len(clip['durations']), 'piskel-frame-count:' + name)
        decoded = Image.open(folder / 'native.apng') if len(clip['durations']) > 1 else None
        if decoded:
            require(decoded.n_frames == len(clip['durations']), 'apng-frame-count:' + name)
        base = rgba(folder / '00.png')
        require(len(record['frames']) == len(clip['durations']), 'per-frame-provenance-count:' + name)
        for i, duration in enumerate(clip['durations']):
            tag = f'{name}/{i:02}.png'
            runtime = V8 / tag
            v7 = V7 / tag
            image = rgba(runtime)
            native_frame = folder / f'{i:02}.png'
            require(sha(runtime) == sha(native_frame), 'runtime-native-frame-copy:' + tag)
            require(image.size == (192, 176), 'runtime-canvas:' + tag)
            require(set(image.getchannel('A').get_flattened_data()) <= {0, 255}, 'runtime-binary-alpha:' + tag)
            colors |= {p[:3] for p in image.get_flattened_data() if p[3]}
            if sha(runtime) != sha(v7):
                changed.add(tag)
            if tag not in ALLOWED:
                require(sha(runtime) == sha(v7), 'intentional-v7-frame-byte-preserved:' + tag)
            info = record['frames'][i]
            require(info['runtimeSha256'] == sha(runtime) and info['rgbaSha256'] == pixels_sha(image), 'recorded-final-sha:' + tag)
            require(info['v7Sha256'] == sha(v7), 'recorded-v7-sha:' + tag)
            origin = resolve(info['sourcePath'])
            require(info['sourceSha256'] == sha(origin), 'recorded-source-sha:' + tag)
            if tag in ALLOWED and name != 'idle':
                require(image.tobytes() == rgba(origin).tobytes(), 'corrected-pose-no-additional-repainting:' + tag)
            ok, replay = edited_replay(rgba(origin), resolve(info['sourceEditsPath']))
            require(ok and replay.tobytes() == image.tobytes(), 'actual-native-source-edit-replay:' + tag)
            ok, replay = edited_replay(rgba(v7), resolve(info['v7EditsPath']))
            require(ok and replay.tobytes() == image.tobytes(), 'v7-delta-replay:' + tag)
            replay = base.copy()
            for x, y, r, g, b, a in load(folder / f'{i:02}.pixels.json'):
                replay.putpixel((x, y), (r, g, b, a))
            require(replay.tobytes() == image.tobytes(), 'editable-base-delta-replay:' + tag)
            extracted = sheet.crop((i * 192, 0, (i + 1) * 192, 176))
            require(extracted.tobytes() == image.tobytes(), 'sheet-frame-replay:' + tag)
            if decoded:
                decoded.seek(i)
                require(decoded.convert('RGBA').tobytes() == image.tobytes() and round(decoded.info['duration']) == duration,
                        'apng-pixels-timing-replay:' + tag)
            meta = runtime.with_name(runtime.name + '.meta').read_text()
            require('filterMode: 0' in meta and 'enableMipMap: 0' in meta and 'textureCompression: 1' not in meta and 'spritePixelsToUnits: 64' in meta,
                    'point-nomip-uncompressed64ppu:' + tag)
    require(changed == ALLOWED, 'exactly13-allowed-changed-58-byte-preserved', repr(sorted(changed)))
    require(colors <= rgb_palette() and len(colors) <= 32, 'runtime-original-v7-palette32', str(len(colors)))
    idle = [rgba(V8 / 'idle' / f'{i:02}.png') for i in range(8)]
    require(len({im.getchannel('A').tobytes() for im in idle}) == 1, 'idle-alpha-geometry-fixed8exposures')
    require(all(planted_bottom(im) == 163 for im in idle), 'idle-ground-fixed163')
    idle_anchor = rgba(NATIVE / 'idle.png')
    red_ramp = sorted((p for p in rgb_palette() if p[0] > p[1] + 30 and p[0] > p[2] + 30), key=sum)
    vent_only = True
    for image in idle:
        for y in range(176):
            for x in range(192):
                before, after = idle_anchor.getpixel((x, y)), image.getpixel((x, y))
                if before == after:
                    continue
                vent_only = vent_only and x >= 80 and y < 140 and before[3] == after[3] == 255 and before[:3] in red_ramp and after[:3] in red_ramp
                if before[:3] in red_ramp and after[:3] in red_ramp:
                    vent_only = vent_only and abs(red_ramp.index(before[:3]) - red_ramp.index(after[:3])) <= 1
    require(vent_only, 'idle-only-existing-back-vents-one-red-ramp-step-no-mouth-body-motion')
    landing = rgba(V8 / 'slam-land/00.png')
    bb = landing.getbbox()
    require(bb[2] - bb[0] <= 149 and planted_bottom(landing) == 163, 'landing-width149-ground163')
    RESULT['observations']['changedFrames'] = sorted(changed)
    RESULT['observations']['preservedFrames'] = 71 - len(changed)
    RESULT['observations']['runtimePaletteColors'] = len(colors)


def unrelated_assets_preserved():
    tique = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/TiqueV10'
    rel = tique.relative_to(REPO).as_posix()
    diff = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--', rel], cwd=REPO, capture_output=True)
    status = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=REPO, capture_output=True)
    require(diff.returncode == 0 and status.returncode == 0 and not status.stdout.strip(), 'tique-v10-entire-tracked-package-unchanged-from-head')
    require(len(list(tique.glob('*/*.png'))) == 139, 'tique-v10-frame-count139-preserved')
    readability = REPO / 'art/return-readability-image-first-v2/QA/audit-all-report.json'
    records = load(readability)['observations']['exportFrames']
    runtime = V7.parent / 'ReadabilityArtV2'
    require(len(records) == 77, 'readability-v2-prior-audit-77frames-present')
    for frame in records:
        path = runtime / frame['clip'] / f"{frame['index']:02}.png"
        require(sha(path) == frame['sha256'], 'readability-v2-prior-audit-byte-preserved:' + frame['clip'] + f"/{frame['index']:02}")
    v1_records = load(REPO / 'art/return-readability-v1/pixel-edit-audit.json')
    checked = 0
    for clip in v1_records:
        for frame in clip['frames']:
            path = V7.parent / 'ReadabilityArt' / clip['name'] / f"{frame['frame']:02}.png"
            require(pixels_sha(rgba(path)) == frame['sha256'], 'readability-v1-draft-pixels-preserved:' + clip['name'] + f"/{frame['frame']:02}")
            checked += 1
    require(checked == 77, 'readability-v1-draft-77frames-preserved')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('baseline', 'source', 'native', 'all'), default='all')
    args = parser.parse_args()
    QA.mkdir(parents=True, exist_ok=True)
    baseline()
    if args.phase != 'baseline':
        source_provenance()
    if args.phase in ('native', 'all'):
        source_and_native()
    if args.phase == 'all':
        exports()
        unrelated_assets_preserved()
    RESULT['phase'] = args.phase
    RESULT['mechanicalPassed'] = not RESULT['failed']
    report = QA / ('audit-' + args.phase + '-report.json')
    report.write_text(json.dumps(RESULT, indent=2))
    print(json.dumps({'phase': args.phase, 'mechanicalPassed': RESULT['mechanicalPassed'],
                      'passed': len(RESULT['passed']), 'failed': len(RESULT['failed']),
                      'findings': RESULT['failed'], 'report': str(report)}))
    return 0 if RESULT['mechanicalPassed'] else 1


if __name__ == '__main__':
    sys.exit(main())
