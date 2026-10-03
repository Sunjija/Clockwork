"""Independently read/verify cinematic candidates; only write one QA JSON report.

No packager import/call, art authoring, Unity process, game launch or file deletion.
Animation record: clips[] with name, sourceNative, allowedMaskPath and optionally
allowedMaskSha256, sourceNativeSha256, durations, frames[]. Animation paths are
repo-relative or candidate-root-relative; masks are binary black/white PNGs.
"""
from pathlib import Path
from PIL import Image
import base64
import hashlib
import io
import json
import re
import numpy as np

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-pixel-cinematics-v1'
RESULT = {'passed': False, 'checks': [], 'failures': [], 'runtimeCapture': False,
          'gameLaunched': False, 'unityFilesWritten': False,
          'geometryRigidMathematicalApproval': 'pending', 'humanAppearanceApproval': 'pending'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(value):
    path = Path(value)
    if path.is_absolute():
        return path
    if '..' in path.parts:
        raise ValueError('Unconfined input path: ' + value)
    return REPO / path if value.startswith('art/') else ROOT / path


def rgba(path):
    return Image.open(path).convert('RGBA')


def check(condition, label):
    RESULT['checks'].append({'label': label, 'passed': bool(condition)})
    if not condition:
        raise ValueError(label)


def verify():
    prov = read(ROOT / 'Source/provenance.json')
    native = read(ROOT / 'Source/Derivation/native-derivation.json')
    anim = read(ROOT / 'Source/Derivation/animation-derivation.json')
    plan = read(ROOT / 'Clips/clip-plan.json')['clips']
    manifest = read(ROOT / 'Exports/export-manifest.json')
    check(prov.get('inspectedByMain') is True and native.get('inspectedByMain') is True, 'main-anchor-inspection')
    check(manifest.get('inspectedByMain') is True and manifest.get('humanAppearanceApproval') == 'pending', 'export-candidate-not-human-approved')
    check(manifest['planSha256'] == sha(ROOT / 'Clips/clip-plan.json'), 'export-plan-sha')
    check(manifest['provenanceSha256'] == sha(ROOT / 'Source/provenance.json'), 'export-provenance-sha')
    for name, source in {**prov['selectedSources'], 'initial-workshop': prov['preservedInitialWorkshop']}.items():
        copied, original = ROOT / source['projectCopy'], Path(source['original'])
        check(sha(copied) == source['sha256'] == sha(original), 'generated-source-copy-sha:' + name)
        check(copied.read_bytes() == original.read_bytes(), 'generated-original-byte-preserved:' + name)
        for reference in source.get('references', []):
            check(sha(Path(reference['path'])) == reference['sha256'], 'generation-reference-sha:' + reference['path'])
    for field in ('requestSet', 'editRequest'):
        check(sha(Path(prov[field]['path'])) == prov[field]['sha256'], 'generation-request-sha:' + field)
    palette_path = ROOT / 'Source/Native/palette.json'
    palette = read(palette_path)['colors']
    check(len(palette) <= 64 and sha(palette_path) == native['paletteSha256'], 'native-palette64-sha')
    palette_set = {tuple(p[:3]) for p in palette}
    for name, record in native['assets'].items():
        path, source = resolve(record['output']), resolve(record['source'])
        image = rgba(path)
        array = np.array(image)
        check(sha(path) == record['outputSha256'] and sha(source) == record['sourceSha256'], 'native-source-output-sha:' + name)
        check(image.size == (640, 360) and np.all(array[..., 3] == 255), 'native640x360-alpha255:' + name)
        colors = {p[:3] for p in image.get_flattened_data()}
        check(len(colors) <= 64 and colors <= palette_set, 'native-fixed-palette:' + name)
        if name == 'workshop-close':
            check(record['sourceSha256'] == native['assets']['workshop']['sourceSha256'], 'workshop-close-shares-generated-source')
            base = rgba(resolve(native['assets']['workshop']['logicalOutput']))
            crop = base.crop(record['logicalCropRect'])
            expected = crop.resize((640, 360), Image.Resampling.NEAREST)
            check(record['integerScale'] == 4 and image.tobytes() == expected.tobytes(), 'same-workshop-logical-crop4x-exact')
            close_logical = rgba(ROOT / 'Source/Native/workshop-close-logical.png')
            check(close_logical.size == (320, 180) and close_logical.tobytes() == crop.resize((320, 180), Image.Resampling.NEAREST).tobytes(),
                  'workshop-close-logical-crop2x-exact')
        else:
            logical = rgba(resolve(record['logicalOutput']))
            check(sha(resolve(record['logicalOutput'])) == record['logicalSha256'], 'logical-source-sha:' + name)
            check(logical.size == (320, 180) and record['integerScale'] == 2 and
                  image.tobytes() == logical.resize((640, 360), Image.Resampling.NEAREST).tobytes(), 'logical-native2x-exact:' + name)
            mapping_path = resolve(record['pixelMap'])
            mapping = read(mapping_path)
            check(sha(mapping_path) == record['pixelMapSha256'], 'native-pixelmap-sha:' + name)
            indices = np.array(mapping['paletteIndices'])
            reconstructed = np.array(palette, dtype=np.uint8)[indices][..., :3]
            check(indices.shape == (180, 320) and np.all(indices >= 0) and
                  np.array_equal(reconstructed, np.array(logical)[..., :3]), 'native-palette-map-replay:' + name)
    animations = anim['clips']
    animations = animations if isinstance(animations, dict) else {c['name']: c for c in animations}
    exports = {c['name']: c for c in manifest['clips']}
    expected_times = {'relay-power': 2000, 'warden-boot': 2000, 'workshop-wide': 3000, 'workshop-close': 3000}
    check(set(exports) == set(animations) == {c['name'] for c in plan} == set(expected_times), 'four-clip-names-exact')
    all_exports = read(ROOT / 'Exports/clips.json')['clips']
    for clip in plan:
        name, times, files = clip['name'], clip['durations'], clip['frames']
        folder, exported, animation = ROOT / 'Clips' / name, exports[name], animations[name]
        check(sum(times) == expected_times[name] and times == exported['durations'], 'clip-duration2-2-3-3s:' + name)
        source_path = resolve(clip['sourceNative'])
        anchor = rgba(source_path)
        check(clip['sourceNative'] == exported['sourceNative'] == animation['sourceNative'] and
              sha(source_path) == exported['sourceNativeSha256'], 'clip-native-source-record:' + name)
        mask_path = resolve(animation['allowedMaskPath'])
        mask_image = Image.open(mask_path).convert('L')
        check(mask_image.size == (640, 360) and set(mask_image.get_flattened_data()) <= {0, 255}, 'binary-animation-mask:' + name)
        check(sha(mask_path) == animation['allowedMaskSha256'], 'animation-mask-sha:' + name)
        check(sha(source_path) == animation['sourceNativeSha256'], 'animation-native-sha:' + name)
        layer = json.loads(read(folder / f'{name}.piskel')['piskel']['layers'][0])
        embedded = rgba(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1])))
        sheet, apng, first = rgba(folder / 'sheet.png'), Image.open(folder / 'native.apng'), rgba(folder / files[0])
        check(layer['frameCount'] == len(files) == len(times) == apng.n_frames and
              embedded.size == sheet.size == (640 * len(files), 360) and embedded.tobytes() == sheet.tobytes(), 'editable-count-and-sheet:' + name)
        check(sha(folder / 'sheet.png') == exported['sheetSha256'] and sha(folder / 'native.apng') == exported['apngSha256'] and
              sha(folder / f'{name}.piskel') == exported['piskelSha256'], 'editable-package-shas:' + name)
        rows = np.array(mask_image) == 0
        for index, filename in enumerate(files):
            path, record = folder / filename, exported['frames'][index]
            animated = animation['frames'][index]
            image, export_path = rgba(path), ROOT / 'Exports' / name / f'{index:02}.png'
            check(image.size == (640, 360) and np.all(np.array(image)[..., 3] == 255), f'frame-alpha-size:{name}/{index}')
            check({p[:3] for p in image.get_flattened_data()} <= palette_set, f'frame-palette:{name}/{index}')
            check(path.read_bytes() == export_path.read_bytes() and sha(path) == record['pngSha256'] and
                  hashlib.sha256(image.tobytes()).hexdigest() == record['rgbaSha256'], f'export-byte-sha:{name}/{index}')
            check(record['frame'] == index and record['durationMs'] == times[index] and resolve(record['sourcePath']) == path,
                  f'export-frame-source-record:{name}/{index}')
            check(animated['frame'] == index and animated['durationMs'] == times[index] and
                  resolve(animated['output']) == path and animated['pngSha256'] == sha(path) and
                  animated['rgbaSha256'] == record['rgbaSha256'], f'animation-frame-record:{name}/{index}')
            native_replay = anchor.copy()
            edits = read(resolve(animated['localEditsPath']))
            before_exact = True
            for x, y, *colors in edits:
                before_exact = before_exact and native_replay.getpixel((x, y)) == tuple(colors[:4])
                native_replay.putpixel((x, y), tuple(colors[4:]))
            check(before_exact and native_replay.tobytes() == image.tobytes() and len(edits) == animated['changedPixelsFromNative'], f'native-delta-replay:{name}/{index}')
            check(np.array_equal(np.array(image)[rows], np.array(anchor)[rows]), f'nonanimated-pixels-invariant:{name}/{index}')
            replay = first.copy()
            for x, y, r, g, b, a in read(path.with_suffix('.pixels.json')):
                replay.putpixel((x, y), (r, g, b, a))
            check(replay.tobytes() == image.tobytes(), f'delta-replay:{name}/{index}')
            check(embedded.crop((index * 640, 0, (index + 1) * 640, 360)).tobytes() == image.tobytes(), f'piskel-replay:{name}/{index}')
            apng.seek(index)
            check(apng.convert('RGBA').tobytes() == image.tobytes() and round(apng.info['duration']) == times[index], f'apng-rgba-duration:{name}/{index}')
        expected_clip = {'name': name, 'durations': times, 'width': 640, 'height': 360}
        check(expected_clip in all_exports and read(ROOT / 'Exports' / name / 'clips.json')['clips'] == [expected_clip], 'export-clip-manifest:' + name)
    links = re.findall(r'\]\((/[^)\n]+)\)', (ROOT / 'README.md').read_text(encoding='utf-8'))
    check(bool(links) and all(Path(path).exists() for path in links), 'readme-absolute-links-exist')
    RESULT['passed'] = True


if __name__ == '__main__':
    try:
        verify()
    except Exception as error:
        RESULT['failures'].append(str(error))
    output = ROOT / 'QA/independent-validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(RESULT, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': RESULT['passed'], 'checks': len(RESULT['checks']), 'failures': RESULT['failures']}))
    raise SystemExit(0 if RESULT['passed'] else 1)
