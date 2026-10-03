"""Package prepared image-first cinematic PNGs offline; never author art or run Unity.

Input: art/return-pixel-cinematics-v1/Clips/clip-plan.json, with clips containing
name, durations (integer milliseconds), width, height, sourceNative (repo-relative
PNG), and frames (paths relative to Clips/<name>/). Main-agent anchor inspection
must be recorded as Source/provenance.json inspectedByMain=true.
"""
from pathlib import Path
from PIL import Image
import argparse
import base64
import hashlib
import io
import json
import re

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-pixel-cinematics-v1'
PLAN = ROOT / 'Clips/clip-plan.json'
PROVENANCE = ROOT / 'Source/provenance.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def resolve(root, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f'Only confined relative paths are allowed: {relative}')
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes its declared root: {relative}')
    return resolved


def save_bytes(path, data):
    """Reruns may reproduce identical artifacts, never replace different files."""
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError(f'Output must stay inside the cinematic candidate directory: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise FileExistsError(f'Preserving existing file; use a new candidate path: {path}')
        return
    path.write_bytes(data)


def save_json(path, data):
    save_bytes(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def image_bytes(image, **options):
    output = io.BytesIO()
    image.save(output, **options)
    return output.getvalue()


def rgba_hash(image):
    return sha(image.tobytes())


def delta(base, image):
    return [[x, y, *image.getpixel((x, y))]
            for y in range(image.height) for x in range(image.width)
            if image.getpixel((x, y)) != base.getpixel((x, y))]


def require(condition, description):
    if not condition:
        raise ValueError(description)


def gif_preview(images, durations, path):
    """Offline 2x NEAREST preview; GIF's 10ms clock is not the timing authority."""
    elapsed = previous = 0
    rounded = []
    previews = []
    for image, duration in zip(images, durations):
        elapsed += duration
        current = round(elapsed / 10) * 10
        rounded.append(max(10, current - previous))
        previous = current
        background = Image.new('RGBA', image.size, (14, 20, 29, 255))
        background.alpha_composite(image)
        previews.append(background.convert('RGB').resize(
            (image.width * 2, image.height * 2), Image.Resampling.NEAREST))
    data = image_bytes(previews[0], format='GIF', save_all=True,
                       append_images=previews[1:], duration=rounded, loop=0,
                       comment=b'Offline PNG preview; NOT runtime capture; human approval pending.')
    save_bytes(path, data)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(data),
            'encodedDurationsMs': rounded, 'encodedTotalMs': sum(rounded),
            'scale': 2, 'resampling': 'NEAREST', 'runtimeCapture': False,
            'timingAuthority': 'native.apng and clips.json, not GIF'}


def package(clip):
    name = clip['name']
    require(isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', name), 'Invalid clip name')
    folder, export = ROOT / 'Clips' / name, ROOT / 'Exports' / name
    times, paths = clip['durations'], clip['frames']
    size = (clip['width'], clip['height'])
    require(all(type(v) is int and v > 0 for v in size), f'{name}: invalid native dimensions')
    require(isinstance(times, list) and isinstance(paths, list) and times and len(times) == len(paths),
            f'{name}: frame/timing count')
    require(all(type(t) is int and t > 0 for t in times), f'{name}: durations must be positive integer ms')
    anchor = resolve(REPO, clip['sourceNative'])
    require(anchor.is_file() and anchor.suffix.lower() == '.png', f'{name}: missing sourceNative PNG')
    frames, sources = [], []
    for relative in paths:
        source = resolve(folder, relative)
        require(source.is_file() and source.suffix.lower() == '.png', f'{name}: missing frame {relative}')
        image = Image.open(source).convert('RGBA')
        require(image.size == size, f'{name}/{relative}: frame dimensions differ from plan')
        colors = set(image.get_flattened_data())
        require({p[3] for p in colors} <= {0, 255}, f'{name}/{relative}: expected binary alpha0/255')
        require(all(p == (0, 0, 0, 0) for p in colors if not p[3]),
                f'{name}/{relative}: transparent RGB must be zero for exact editable replay')
        sources.append((source, source.read_bytes()))
        frames.append(image)
    palette = {p[:3] for image in frames for p in image.get_flattened_data() if p[3]}
    require(len(palette) <= 64, f'{name}: native clip exceeds64 visible RGB colors')
    sheet = Image.new('RGBA', (size[0] * len(frames), size[1]), (0, 0, 0, 0))
    records = []
    for index, (image, (source, original_bytes)) in enumerate(zip(frames, sources)):
        sheet.alpha_composite(image, (index * size[0], 0))
        output = export / f'{index:02}.png'
        save_bytes(output, original_bytes)
        edits = delta(frames[0], image)
        edits_path = resolve(folder, paths[index]).with_suffix('.pixels.json')
        save_json(edits_path, edits)
        replay = frames[0].copy()
        for x, y, r, g, b, a in json.loads(edits_path.read_text()):
            replay.putpixel((x, y), (r, g, b, a))
        require(replay.tobytes() == image.tobytes(), f'{name}/{index}: pixel delta replay failed')
        require(output.read_bytes() == original_bytes, f'{name}/{index}: PNG export changed source bytes')
        records.append({'frame': index, 'durationMs': times[index],
                        'sourcePath': source.relative_to(REPO).as_posix(), 'pngSha256': sha(original_bytes),
                        'exportPath': output.relative_to(ROOT).as_posix(), 'rgbaSha256': rgba_hash(image),
                        'alphaMaskSha256': sha(image.getchannel('A').tobytes()), 'bounds': image.getbbox(),
                        'changedPixelsFromFirstFrame': len(edits), 'pixelDeltaReplay': True})
    sheet_data = image_bytes(sheet, format='PNG')
    save_bytes(folder / 'sheet.png', sheet_data)
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': [
        {'layout': [[i] for i in range(len(frames))],
         'base64PNG': 'data:image/png;base64,' + base64.b64encode(sheet_data).decode('ascii')}]}
    piskel = {'modelVersion': 2, 'piskel': {'name': name, 'fps': 20,
        'description': 'Image-first native candidate; variable durations in APNG/clips.json; human approval pending.',
        'width': size[0], 'height': size[1], 'layers': [json.dumps(layer)]}}
    save_json(folder / f'{name}.piskel', piskel)
    parsed = json.loads((folder / f'{name}.piskel').read_text())['piskel']
    parsed_layer = json.loads(parsed['layers'][0])
    decoded_sheet = Image.open(io.BytesIO(base64.b64decode(
        parsed_layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
    require(parsed_layer['frameCount'] == len(frames), f'{name}: Piskel frame count')
    apng_data = image_bytes(frames[0], format='PNG', save_all=True, append_images=frames[1:],
                            duration=times, loop=0, disposal=1, blend=0)
    save_bytes(folder / 'native.apng', apng_data)
    apng = Image.open(folder / 'native.apng')
    require(getattr(apng, 'n_frames', 1) == len(frames), f'{name}: APNG merged hold exposures')
    for index, image in enumerate(frames):
        recovered = decoded_sheet.crop((index * size[0], 0, (index + 1) * size[0], size[1]))
        require(recovered.tobytes() == image.tobytes(), f'{name}/{index}: Piskel replay failed')
        apng.seek(index)
        require(apng.convert('RGBA').tobytes() == image.tobytes(), f'{name}/{index}: APNG RGBA replay failed')
        require(round(apng.info.get('duration', 0)) == times[index], f'{name}/{index}: APNG timing mismatch')
    require(all(source.read_bytes() == original for source, original in sources), f'{name}: source PNG mutated')
    alpha_values = sorted({p[3] for image in frames for p in image.get_flattened_data()})
    return {'name': name, 'width': size[0], 'height': size[1], 'durations': times,
            'sourceNative': clip['sourceNative'], 'sourceNativeSha256': sha(anchor.read_bytes()),
            'frames': records, 'palette': [list(p) for p in sorted(palette)], 'paletteColors': len(palette),
            'paletteAtMost64': True, 'alphaValues': alpha_values, 'binaryAlpha': True,
            'alpha255': alpha_values == [255], 'shapeStable': len({r['alphaMaskSha256'] for r in records}) == 1,
            'shapeMetric': 'Alpha mask only; this does not assert rigid body geometry in opaque scenes.',
            'shapeCheck': 'Alpha masks recorded, not forced invariant for intentionally changing poses.',
            'piskelReplayRgbaExact': True, 'apngReplayRgbaAndDurationExact': True,
            'pixelDeltaReplayRgbaExact': True, 'pngExportByteExact': True,
            'sheetSha256': sha(sheet_data), 'apngSha256': sha(apng_data),
            'piskelSha256': sha((folder / f'{name}.piskel').read_bytes()),
            'preview': gif_preview(frames, times, ROOT / 'QA' / f'{name}-preview.gif')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', action='store_true', required=True)
    args = parser.parse_args()
    require(args.inspected_anchors, 'Main-agent anchor inspection is required')
    provenance_bytes, plan_bytes = PROVENANCE.read_bytes(), PLAN.read_bytes()
    require(json.loads(provenance_bytes).get('inspectedByMain') is True,
            'Source/provenance.json must record inspectedByMain=true')
    plan = json.loads(plan_bytes)
    require(isinstance(plan.get('clips'), list) and plan['clips'], 'clip-plan.json requires nonempty clips')
    names = [clip['name'] for clip in plan['clips']]
    require(len(names) == len(set(names)), 'Clip names must be unique')
    result = [package(clip) for clip in plan['clips']]
    runtime_manifest = {'clips': [{'name': c['name'], 'durations': c['durations'],
                                  'width': c['width'], 'height': c['height']} for c in result]}
    save_json(ROOT / 'Exports/clips.json', runtime_manifest)
    for clip in result:
        save_json(ROOT / 'Exports' / clip['name'] / 'clips.json', {'clips': [
            c for c in runtime_manifest['clips'] if c['name'] == clip['name']]})
    save_json(ROOT / 'Exports/export-manifest.json', {'revision': 'pixel-cinematics-v1',
        'method': 'Offline packaging of prepared native PNGs only; no generated video or geometry authoring.',
        'planSha256': sha(plan_bytes), 'provenanceSha256': sha(provenance_bytes), 'inspectedByMain': True,
        'humanAppearanceApproval': 'pending', 'runtimeCapture': False, 'gameLaunched': False,
        'unityFilesWritten': False, 'sourcePngsModified': False, 'clips': result})
    require(PLAN.read_bytes() == plan_bytes and PROVENANCE.read_bytes() == provenance_bytes,
            'Plan/provenance must remain unchanged')
    print(json.dumps({'clips': len(result), 'frames': sum(len(c['frames']) for c in result),
                      'manifest': str(ROOT / 'Exports/export-manifest.json'), 'humanAppearanceApproval': 'pending'}))


if __name__ == '__main__':
    main()
