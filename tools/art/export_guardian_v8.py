"""Package five image-first guardian corrections without altering V7 motion.

Parent production generates, inspects and derives corrected full-pose anchors.
This script consumes those native inputs. It changes exactly 13 runtime frames,
copies the remaining 58 V7 PNGs byte-for-byte, and keeps names and timings.
No limb scaling, geometric breathing, procedural new poses or Unity launch.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import base64
import hashlib
import io
import json
import re
import shutil
import sys
import uuid


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-v8-guardian'
NATIVE = ROOT / 'Source/Native'
OLD = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenV7'
OUT = OLD.with_name('WardenV8')
CLIP_ROOT = ROOT / 'Clips'
V7_MANIFEST = json.loads((REPO / 'art/return-v7-guardian/manifest.json').read_text())
SPECS = json.loads((OLD / 'clips.json').read_text())['clips']
META = (OLD / 'idle/00.png.meta').read_text()
PALETTE = {tuple(bytes.fromhex(c.lstrip('#'))) + (255,) for c in V7_MANIFEST['palette']}
CANVAS = (192, 176)
BASELINE = 163
CHANGES = {('idle', i): 'idle' for i in range(8)} | {
    ('wave-strike', 0): 'jaw-impact-03',
    ('wave-strike', 1): 'jaw-impact-04',
    ('wave-strike', 2): 'jaw-impact-05',
    ('slam-land', 0): 'slam-land',
    ('slam-land', 2): 'idle',
}
NATIVE_IMAGES = {}
MAPPINGS = []


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def pixels(image):
    return image.get_flattened_data()


def blank(size=CANVAS):
    return Image.new('RGBA', size, (0, 0, 0, 0))


def pixel_delta(a, b, old_colors=False):
    result = []
    for y in range(CANVAS[1]):
        for x in range(CANVAS[0]):
            before, after = a.getpixel((x, y)), b.getpixel((x, y))
            if before != after:
                result.append([x, y, *before, *after] if old_colors else [x, y, *after])
    return result


def idle(frame):
    """Keep the corrected whole-pose perfectly rigid; pulse existing vents only.

    Warm body vent pixels (x>=80, y<140) move at most ONE step in the existing
    V7 red ramp. Mouth pixels and the steel body are unchanged. Baseline, alpha
    and all contour/limb pixels are invariant across the eight idle exposures.
    """
    source = NATIVE_IMAGES['idle']
    result = source.copy()
    level = (0, 0, 1, 1, 1, 0, -1, -1)[frame]
    if level:
        reds = sorted((p for p in PALETTE if p[0] > p[1] + 30 and p[0] > p[2] + 30), key=lambda p: sum(p[:3]))
        for y in range(140):
            for x in range(80, CANVAS[0]):
                p = source.getpixel((x, y))
                if p in reds:
                    target = reds[max(0, min(len(reds) - 1, reds.index(p) + level))]
                    result.putpixel((x, y), target)
    return result


def meta(path, kind):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-guardian-v8/' + path.relative_to(REPO).as_posix()).hex
    if kind == 'texture':
        text = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, META, count=1)
        text = text.replace('filterMode: 1', 'filterMode: 0').replace('enableMipMap: 1', 'enableMipMap: 0')
        text = text.replace('textureCompression: 1', 'textureCompression: 0')
        text = re.sub(r'(?m)^  spritePixelsToUnits:.*$', '  spritePixelsToUnits: 64', text)
    else:
        text = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder':
            text += 'folderAsset: yes\n'
        text += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    path.with_name(path.name + '.meta').write_text(text)


def export(spec):
    name, durations = spec['name'], spec['durations']
    source_folder = CLIP_ROOT / name
    runtime_folder = OUT / name
    source_folder.mkdir(parents=True, exist_ok=True)
    runtime_folder.mkdir(parents=True, exist_ok=True)
    meta(runtime_folder, 'folder')
    frames, records = [], []
    for i in range(len(durations)):
        old_path = OLD / name / f'{i:02}.png'
        new_path = runtime_folder / f'{i:02}.png'
        editable = source_folder / f'{i:02}.png'
        old_image = Image.open(old_path).convert('RGBA')
        native_name = CHANGES.get((name, i))
        if native_name:
            native_path = NATIVE / f'{native_name}.png'
            native_image = NATIVE_IMAGES[native_name]
            image = idle(i) if name == 'idle' else native_image.copy()
            image.save(editable)
            shutil.copyfile(editable, new_path)
            source_path = native_path
            source_image = native_image
            method = 'Corrected generated full-pose native source; existing vent red-ramp pulse only' if name == 'idle' else 'Corrected generated full-pose native source unchanged'
            source_kind = 'generated-correction'
        else:
            # Preserve PNG encoding AND RGBA, not merely visually identical.
            shutil.copyfile(old_path, editable)
            shutil.copyfile(old_path, new_path)
            image = old_image.copy()
            source_path = old_path
            source_image = old_image
            method = 'Unchanged V7 runtime PNG byte-for-byte reuse'
            source_kind = 'unchanged-v7-reuse'
        assert image.size == CANVAS, (name, i, image.size)
        assert set(image.getchannel('A').get_flattened_data()) <= {0, 255}
        assert set(pixels(image)) <= PALETTE | {(0, 0, 0, 0)}, (name, i, 'palette')
        meta(new_path, 'texture')
        source_delta = pixel_delta(source_image, image, True)
        v7_delta = pixel_delta(old_image, image, True)
        (source_folder / f'{i:02}.source-edits.json').write_text(json.dumps(source_delta, separators=(',', ':')))
        (source_folder / f'{i:02}.v7-edits.json').write_text(json.dumps(v7_delta, separators=(',', ':')))
        frames.append(image)
        records.append({
            'frame': i, 'sourceKind': source_kind, 'method': method,
            'sourcePath': source_path.relative_to(REPO).as_posix(), 'sourceSha256': sha(source_path),
            'v7Path': old_path.relative_to(REPO).as_posix(), 'v7Sha256': sha(old_path),
            'runtimePath': new_path.relative_to(REPO).as_posix(), 'runtimeSha256': sha(new_path),
            'rgbaSha256': rgba_sha(image), 'changedPixelsFromSource': len(source_delta),
            'changedPixelsFromV7': len(v7_delta), 'bbox': image.getbbox(),
            'sourceEditsPath': (source_folder / f'{i:02}.source-edits.json').relative_to(REPO).as_posix(),
            'v7EditsPath': (source_folder / f'{i:02}.v7-edits.json').relative_to(REPO).as_posix(),
        })
    sheet = blank((CANVAS[0] * len(frames), CANVAS[1]))
    for i, frame in enumerate(frames):
        sheet.alpha_composite(frame, (i * CANVAS[0], 0))
        delta = pixel_delta(frames[0], frame)
        (source_folder / f'{i:02}.pixels.json').write_text(json.dumps(delta, separators=(',', ':')))
    sheet.save(source_folder / 'sheet.png')
    if len(frames) > 1:
        # Disposal1 retains duplicate hold exposures instead of merging them.
        frames[0].save(source_folder / 'native.apng', format='PNG', save_all=True, append_images=frames[1:],
                       duration=durations, loop=0, disposal=1, blend=0)
    buffer = io.BytesIO()
    sheet.save(buffer, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': [
        {'layout': [[i] for i in range(len(frames))], 'base64PNG': 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode()}]}
    (source_folder / f'{name}.piskel').write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'Guardian V8 selective image-first distortion correction; exact variable durations in clips.json/APNG.',
        'fps': 20, 'width': CANVAS[0], 'height': CANVAS[1], 'layers': [json.dumps(layer)]}}))
    MAPPINGS.append({'name': name, 'durations': durations, 'frames': records})


def replay_delta(base, data, has_old=False):
    result = base.copy()
    for x, y, *p in data:
        if has_old:
            assert result.getpixel((x, y)) == tuple(p[:4])
            p = p[4:]
        result.putpixel((x, y), tuple(p))
    return result


def validate():
    changed = reused = 0
    for mapping in MAPPINGS:
        name, durations = mapping['name'], mapping['durations']
        folder = CLIP_ROOT / name
        piskel = json.loads((folder / f'{name}.piskel').read_text())['piskel']
        layer = json.loads(piskel['layers'][0])
        sheet = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        assert layer['frameCount'] == len(durations)
        assert sheet.size == (CANVAS[0] * len(durations), CANVAS[1])
        apng = Image.open(folder / 'native.apng')
        assert apng.n_frames == len(durations), (name, apng.n_frames, len(durations))
        first = Image.open(folder / '00.png').convert('RGBA')
        for record in mapping['frames']:
            i = record['frame']
            path = folder / f'{i:02}.png'
            image = Image.open(path).convert('RGBA')
            assert sha(path) == sha(REPO / record['runtimePath'])
            apng.seek(i)
            assert apng.convert('RGBA').tobytes() == image.tobytes(), (name, i, 'APNG')
            assert round(apng.info['duration']) == durations[i]
            decoded = sheet.crop((CANVAS[0] * i, 0, CANVAS[0] * (i + 1), CANVAS[1]))
            assert decoded.tobytes() == image.tobytes(), (name, i, 'Piskel')
            replay = replay_delta(first, json.loads((folder / f'{i:02}.pixels.json').read_text()))
            assert replay.tobytes() == image.tobytes(), (name, i, 'frame delta')
            source = Image.open(REPO / record['sourcePath']).convert('RGBA')
            replay = replay_delta(source, json.loads((REPO / record['sourceEditsPath']).read_text()), True)
            assert replay.tobytes() == image.tobytes(), (name, i, 'source delta')
            v7 = Image.open(REPO / record['v7Path']).convert('RGBA')
            replay = replay_delta(v7, json.loads((REPO / record['v7EditsPath']).read_text()), True)
            assert replay.tobytes() == image.tobytes(), (name, i, 'V7 delta')
            settings = (REPO / (record['runtimePath'] + '.meta')).read_text()
            assert 'filterMode: 0' in settings and 'enableMipMap: 0' in settings
            assert 'textureCompression: 1' not in settings and 'spritePixelsToUnits: 64' in settings
            if record['sourceKind'] == 'unchanged-v7-reuse':
                assert record['v7Sha256'] == record['runtimeSha256'], (name, i, 'reuse bytes')
                reused += 1
            else:
                assert record['v7Sha256'] != record['runtimeSha256'], (name, i, 'correction unchanged')
                changed += 1
    # No breathing geometry: every idle alpha, contour and steel pixel stable.
    neutral = NATIVE_IMAGES['idle']
    for frame in range(8):
        im = idle(frame)
        assert im.getchannel('A').tobytes() == neutral.getchannel('A').tobytes()
        assert im.getbbox() == neutral.getbbox()
        for y in range(CANVAS[1]):
            for x in range(CANVAS[0]):
                before, after = neutral.getpixel((x, y)), im.getpixel((x, y))
                if before != after:
                    assert x >= 80 and y < 140 and before[0] > before[1] + 30 and before[0] > before[2] + 30
    assert (changed, reused) == (13, 58), (changed, reused)
    return {'clips': len(SPECS), 'frames': changed + reused, 'correctedRuntimePngs': changed,
            'unchangedV7ByteIdenticalPngs': reused, 'paletteColors': len(PALETTE), 'canvas': CANVAS,
            'baselineRow': BASELINE, 'namesAndDurationsPreserved': True,
            'heldCoreAndCoreFlashPreserved': True, 'intendedCurlAndAirRotationsPreserved': True,
            'idleSilhouetteInvariant': True, 'idleGeometricBreathing': False,
            'binaryAlpha': True, 'point': True, 'mipmaps': False, 'compression': False, 'spritePixelsToUnits': 64,
            'apngRoundtrip': 'all frames RGBA and durations exact', 'piskelReplay': 'all frames RGBA exact',
            'pixelDeltaReplay': 'all frames RGBA exact', 'nativeSourceEditReplay': 'all frames RGBA exact',
            'v7EditReplay': 'all frames RGBA exact', 'runtimeCopies': 'all PNG SHA256 exact',
            'unityBuildPerformed': False, 'gameLaunched': False, 'runtimeCapture': False,
            'humanAppearanceApproval': 'pending'}


def qa():
    folder = ROOT / 'QA'
    folder.mkdir(parents=True, exist_ok=True)
    examples = [('idle', 0), ('wave-strike', 0), ('wave-strike', 1), ('wave-strike', 2), ('slam-land', 0)]
    sheet = Image.new('RGB', (810, 5 * 395 + 45), (16, 24, 35))
    d = ImageDraw.Draw(sheet)
    d.text((12, 12), 'GUARDIAN V8 SOURCE CORRECTION | V7 / V8 native candidate | 2x nearest | NOT runtime capture', fill=(210, 225, 236))
    for row, (name, i) in enumerate(examples):
        top = 40 + row * 395
        d.text((12, top), f'{name}/{i:02}  V7 original', fill=(165, 185, 209))
        d.text((414, top), 'V8 generated-source correction candidate', fill=(165, 185, 209))
        for col, root in enumerate((OLD, OUT)):
            image = Image.open(root / name / f'{i:02}.png').convert('RGBA').resize((384, 352), Image.Resampling.NEAREST)
            sheet.paste(image, (12 + col * 402, top + 22), image)
    sheet.save(folder / 'clip-correction-before-after.png')
    idle_frames = [idle(i) for i in range(8)]
    result = []
    for i, im in enumerate(idle_frames):
        ys = [y for y in range(CANVAS[1]) if any(im.getpixel((x, y))[3] for x in range(CANVAS[0]))]
        result.append({'frame': i, 'bbox': im.getbbox(), 'lowestOpaqueRow': max(ys),
                       'alphaSha256': hashlib.sha256(im.getchannel('A').tobytes()).hexdigest(),
                       'changedPixelsFromFixedPose': len(pixel_delta(idle_frames[0], im))})
    (folder / 'clip-idle-shape-stability.json').write_text(json.dumps(result, indent=2))
    preview = []
    for im in idle_frames:
        canvas = Image.new('RGBA', CANVAS, (16, 24, 35, 255))
        canvas.alpha_composite(im)
        preview.append(canvas.convert('RGB').resize((576, 528), Image.Resampling.NEAREST))
    preview[0].save(folder / 'clip-idle-preview.gif', save_all=True, append_images=preview[1:], duration=[110] * 8, loop=0)
    sequence_qa()


def sequence_qa():
    """Read-only offline continuity views of already exported complete clips.

    Write new QA files only: no runtime/native/provenance/manifest mutation.
    Source PNGs are composited and nearest-neighbour enlarged without altering
    their art geometry. This is NOT a game/render capture or human approval.
    """
    folder = ROOT / 'QA'
    folder.mkdir(parents=True, exist_ok=True)
    v8_specs = {c['name']: c for c in json.loads((OUT / 'clips.json').read_text())['clips']}
    report = {'method': 'Existing V7/V8 exported PNG composition only; nearest-neighbour integer enlargement',
              'runtimeCapture': False, 'gameLaunched': False, 'unityBuildPerformed': False,
              'humanAppearanceApproval': 'pending', 'geometryModified': False, 'sequences': []}
    for name in ('wave-strike', 'slam-land'):
        times = next(c['durations'] for c in SPECS if c['name'] == name)
        assert times == v8_specs[name]['durations']
        count = len(times)
        image = Image.new('RGB', (count * 400 + 16, 830), (16, 24, 35))
        draw = ImageDraw.Draw(image)
        draw.text((12, 10), f'{name} | COMPLETE FRAME CONTINUITY | native 2x NEAREST | NOT runtime capture | human approval pending', fill=(210, 225, 236))
        versions = []
        for row, (version, base) in enumerate((('V7', OLD), ('V8 candidate', OUT))):
            top = 35 + row * 392
            draw.text((12, top), version, fill=(165, 185, 209))
            gif_frames, frame_records = [], []
            for i, duration in enumerate(times):
                path = base / name / f'{i:02}.png'
                native = Image.open(path).convert('RGBA')
                large = native.resize((384, 352), Image.Resampling.NEAREST)
                image.paste(large, (12 + i * 400, top + 20), large)
                draw.text((12 + i * 400, top + 372), f'frame {i:02} / {duration}ms', fill=(165, 185, 209))
                gif = Image.new('RGBA', (576, 561), (16, 24, 35, 255))
                gif.alpha_composite(native.resize((576, 528), Image.Resampling.NEAREST), (0, 33))
                caption = ImageDraw.Draw(gif)
                caption.text((10, 7), f'{version} {name} {i:02} / {duration}ms | native3x NEAREST', fill=(210, 225, 236, 255))
                caption.text((10, 20), 'OFFLINE PREVIEW - NOT runtime capture - human approval pending', fill=(165, 185, 209, 255))
                gif_frames.append(gif.convert('RGB'))
                frame_records.append({'frame': i, 'durationMs': duration, 'sourcePath': path.relative_to(REPO).as_posix(),
                                      'sourceSha256': sha(path), 'rgbaSha256': rgba_sha(native)})
            tag = 'v7' if row == 0 else 'v8'
            gif_path = folder / f'clip-{name}-{tag}-preview.gif'
            gif_frames[0].save(gif_path, save_all=True, append_images=gif_frames[1:], duration=times, loop=0,
                               comment=b'OFFLINE PNG composition; NOT runtime capture; human appearance approval pending.')
            decoded = Image.open(gif_path)
            assert decoded.n_frames == count, (name, tag, decoded.n_frames, count)
            for i, duration in enumerate(times):
                decoded.seek(i)
                assert decoded.info['duration'] == duration
            versions.append({'version': tag, 'previewPath': gif_path.relative_to(REPO).as_posix(),
                             'previewSha256': sha(gif_path), 'frames': frame_records})
        png_path = folder / f'clip-{name}-v7-v8-full-contact.png'
        image.save(png_path)
        report['sequences'].append({'clip': name, 'durations': times, 'contactPath': png_path.relative_to(REPO).as_posix(),
                                    'contactSha256': sha(png_path), 'versions': versions})
    (folder / 'clip-sequence-preview.json').write_text(json.dumps(report, indent=2))
    return report


def main():
    expected_hashes = {p.relative_to(OLD).as_posix(): sha(p) for p in OLD.rglob('*.png')}
    for name in ('idle', 'jaw-impact-03', 'jaw-impact-04', 'jaw-impact-05', 'slam-land'):
        im = Image.open(NATIVE / f'{name}.png').convert('RGBA')
        assert im.size == CANVAS
        assert set(pixels(im)) <= PALETTE | {(0, 0, 0, 0)}, name
        assert set(im.getchannel('A').get_flattened_data()) <= {0, 255}
        NATIVE_IMAGES[name] = im
    assert len(SPECS) == 15 and sum(len(c['durations']) for c in SPECS) == 71
    OUT.mkdir(parents=True, exist_ok=True)
    CLIP_ROOT.mkdir(parents=True, exist_ok=True)
    meta(OUT, 'folder')
    for spec in SPECS:
        export(spec)
    # Preserve runtime manifest schema exactly; production selector unchanged.
    shutil.copyfile(OLD / 'clips.json', OUT / 'clips.json')
    meta(OUT / 'clips.json', 'text')
    shutil.copyfile(OLD / 'clips.json', CLIP_ROOT / 'clips.json')
    summary = validate()
    qa()
    assert expected_hashes == {p.relative_to(OLD).as_posix(): sha(p) for p in OLD.rglob('*.png')}
    manifest = {
        'revision': 'guardian-v8-selective-distortion-correction', 'date': '2026-10-02',
        'workflow': 'Actual edited generated full-pose anchors -> fixed V7 palette native derivation -> limited pulse/reuse -> editable Return exports',
        'canvas': CANVAS, 'baselineRow': BASELINE, 'palette': V7_MANIFEST['palette'],
        'footRegistrationContract': 'Grounded whole poses use planted-foot column median row163, not lowest opaque pixel. Jaw-impact03/04 retain lowest row164 with median163; no further geometric correction.',
        'nativeInputs': {name: {'path': (NATIVE / f'{name}.png').relative_to(REPO).as_posix(), 'sha256': sha(NATIVE / f'{name}.png')} for name in NATIVE_IMAGES},
        'nativeDerivationRecord': 'Source/Derivation/native-derivation.json',
        'nativeDerivationSha256': sha(ROOT / 'Source/Derivation/native-derivation.json'),
        'unchangedV7Hashes': expected_hashes, 'mappings': MAPPINGS, 'validation': summary,
        'scope': 'Selective asset correction only. No runtime build, game launch, visual approval or gameplay timing changes.',
    }
    (ROOT / 'export-manifest.json').write_text(json.dumps(manifest, indent=2))
    (ROOT / 'QA/clip-validation.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))


if __name__ == '__main__':
    if '--sequence-qa-only' in sys.argv:
        print(json.dumps(sequence_qa()))
    else:
        main()
