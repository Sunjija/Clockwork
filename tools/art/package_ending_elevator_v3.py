"""Package two independent, already-authored ending candidates without runtime writes.

Input: art/return-ending-elevator-v3/Clips/clip-plan.json and inspected provenance.
The image-first/native composition stage is upstream. This file only packages
prepared PNGs, preserving source bytes and exact APNG timing. It does not draw
new visual designs, generate images, invoke Unity, encode MP4, or concatenate
the two independent ending clips.
"""
from pathlib import Path
from PIL import Image
import argparse
import base64
import io
import json
import math
import numpy as np

import package_full_cinematics_v2 as pipeline


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-ending-elevator-v3'
SIZE = (640, 360)
CLIP_TIMES = {'guardian-collapse': 3000, 'elevator-homecoming': 7000}
SHEET_COLUMNS = 30  # At most19200px wide, below32767px image-editor limits.

# Reuse proven strict-save, exact-palette GIF, encoding and pixel-delta helpers.
# Changing a Python module variable does not modify the older package on disk.
pipeline.ROOT = ROOT
require, sha, json_bytes = pipeline.require, pipeline.sha, pipeline.json_bytes
save, encoded, delta, preview = pipeline.save, pipeline.encoded, pipeline.delta, pipeline.preview


def editable(name, folder, frames, durations, input_paths):
    """Keep editable sheets bounded; each Piskel chunk uses proven horizontal layout."""
    require(frames and len(frames) == len(durations) == len(input_paths),
            f'{name}: frame/duration/path count mismatch')
    palette = set()
    records = []
    columns = min(SHEET_COLUMNS, len(frames))
    rows = math.ceil(len(frames) / columns)
    sheet = Image.new('RGBA', (SIZE[0] * columns, SIZE[1] * rows))
    chunks = []
    restored_frames = {}
    for index, image in enumerate(frames):
        require(image.size == SIZE, f'{name}: expected640x360 native canvas')
        array = np.array(image)
        require(np.all(array[..., 3] == 255), f'{name}: expected fully opaque alpha255')
        palette.update(tuple(map(int, p)) for p in np.unique(array[..., :3].reshape(-1, 3), axis=0))
        col, row = index % columns, index // columns
        sheet.paste(image, (col * SIZE[0], row * SIZE[1]))
        edits = delta(frames[0], image)
        path = input_paths[index].with_suffix('.pixels.json')
        save(path, json_bytes(edits))
        replay = frames[0].copy()
        for x, y, r, g, b, a in json.loads(path.read_bytes()):
            replay.putpixel((x, y), (r, g, b, a))
        require(replay.tobytes() == image.tobytes(), f'{name}/{index}: first-frame delta replay failed')
        require(sheet.crop((col * 640, row * 360, (col + 1) * 640, (row + 1) * 360)).tobytes()
                == image.tobytes(), f'{name}/{index}: grid sheet RGBA replay mismatch')
        records.append({'frame': index, 'durationMs': durations[index],
                        'rgbaSha256': sha(image.tobytes()),
                        'alphaMaskSha256': sha(image.getchannel('A').tobytes()),
                        'sheetCell': [col, row],
                        'deltaPath': path.relative_to(ROOT).as_posix(),
                        'deltaSha256': sha(path.read_bytes()),
                        'changedPixelsFromFirstFrame': len(edits),
                        'deltaReplayRgbaExact': True})
    require(0 < len(palette) <= 256, f'{name}: combined visible palette exceeds256 colors')
    sheet_data = encoded(sheet, format='PNG')
    save(folder / 'sheet.png', sheet_data)
    # Multiple bounded horizontal chunks avoid introducing untested padding
    # indexes in Piskel's column-major layout. Every layout value is a global
    # animation-frame index; each populated cell has exactly one source frame.
    for start in range(0, len(frames), SHEET_COLUMNS):
        selected = frames[start:start + SHEET_COLUMNS]
        strip = Image.new('RGBA', (SIZE[0] * len(selected), SIZE[1]))
        for local, image in enumerate(selected):
            strip.paste(image, (local * SIZE[0], 0))
        chunk_data = encoded(strip, format='PNG')
        chunks.append({'layout': [[start + local] for local in range(len(selected))],
                       'base64PNG': 'data:image/png;base64,' + base64.b64encode(chunk_data).decode('ascii')})
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': chunks}
    piskel = {'modelVersion': 2, 'piskel': {
        'name': name, 'fps': 20, 'width': 640, 'height': 360,
        'description': 'Offline image-first candidate; exact variable timing in APNG/validation; human approval pending.',
        'layers': [json.dumps(layer)]}}
    piskel_path = folder / f'{name}.piskel'
    save(piskel_path, json_bytes(piskel))
    restored_layer = json.loads(json.loads(piskel_path.read_bytes())['piskel']['layers'][0])
    require(restored_layer['frameCount'] == len(frames), f'{name}: Piskel frame count mismatch')
    for chunk in restored_layer['chunks']:
        restored = Image.open(io.BytesIO(base64.b64decode(chunk['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        require(restored.width <= 32767 and restored.height == 360,
                f'{name}: Piskel bounded chunk geometry mismatch')
        require(restored.width == len(chunk['layout']) * 640, f'{name}: Piskel layout width mismatch')
        for col, frame_indexes in enumerate(chunk['layout']):
            require(len(frame_indexes) == 1, f'{name}: expected horizontal single-row Piskel chunks')
            index = frame_indexes[0]
            require(index not in restored_frames, f'{name}: duplicate Piskel frame index')
            restored_frames[index] = restored.crop((col * 640, 0, (col + 1) * 640, 360)).tobytes()
    require(set(restored_frames) == set(range(len(frames))), f'{name}: Piskel index coverage mismatch')
    apng_data = encoded(frames[0], format='PNG', save_all=True, append_images=frames[1:],
                        duration=durations, loop=0, disposal=1, blend=0)
    save(folder / 'native.apng', apng_data)
    apng = Image.open(folder / 'native.apng')
    require(apng.n_frames == len(frames), f'{name}: APNG merged hold exposures')
    for index, image in enumerate(frames):
        require(restored_frames[index] == image.tobytes(), f'{name}/{index}: Piskel RGBA replay mismatch')
        apng.seek(index)
        require(apng.convert('RGBA').tobytes() == image.tobytes(), f'{name}/{index}: APNG RGBA replay mismatch')
        require(round(apng.info['duration']) == durations[index], f'{name}/{index}: APNG variable timing mismatch')
    return {'name': name, 'width': 640, 'height': 360,
            'frameCount': len(frames), 'durations': durations, 'durationMs': sum(durations),
            'paletteColors': len(palette), 'paletteAtMost256': True, 'alpha255': True,
            'frames': records, 'gridSheetColumns': columns, 'gridSheetRows': rows,
            'piskelChunkCount': len(chunks), 'piskelMaxChunkWidth': min(len(frames), SHEET_COLUMNS) * 640,
            'piskelReplayRgbaExact': True, 'apngReplayRgbaAndDurationExact': True,
            'gridSheetReplayRgbaExact': True, 'sheetSha256': sha(sheet_data),
            'apngSha256': sha(apng_data), 'piskelSha256': sha(piskel_path.read_bytes()),
            'preview': preview(frames, durations, ROOT / 'QA' / f'{name}-preview.gif')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', action='store_true', required=True)
    args = parser.parse_args()
    require(args.inspected_anchors, 'Main-agent anchor inspection is required')
    provenance_path = ROOT / 'Source/provenance.json'
    plan_path = ROOT / 'Clips/clip-plan.json'
    provenance_bytes, plan_bytes = provenance_path.read_bytes(), plan_path.read_bytes()
    provenance = json.loads(provenance_bytes)
    require(provenance.get('inspectedByMain') is True,
            'Source/provenance.json requires inspectedByMain=true')
    plan = json.loads(plan_bytes)
    clips = plan['clips']
    names = [clip['name'] for clip in clips]
    require(len(names) == 2 and set(names) == set(CLIP_TIMES),
            'Expected exactly guardian-collapse and elevator-homecoming')
    require(not plan.get('sequences'), 'Two independent clips must not be concatenated into a sequence')
    results, original_inputs = [], {}
    for clip in clips:
        name, durations = clip['name'], clip['durations']
        require(clip['width'] == 640 and clip['height'] == 360, f'{name}: native canvas contract')
        require(durations and all(type(ms) is int and ms > 0 for ms in durations),
                f'{name}: positive integer durations required')
        require(sum(durations) == clip['durationMs'] == CLIP_TIMES[name],
                f'{name}: planned independent clip duration mismatch')
        require(len(durations) == len(clip['frames']) and isinstance(clip['sourceInfo'], dict),
                f'{name}: input schema mismatch')
        folder, export = ROOT / 'Clips' / name, ROOT / 'Exports' / name
        paths, frames, source_records = [], [], []
        for index, relative in enumerate(clip['frames']):
            path = pipeline.confined(folder, relative)
            require(path.suffix.lower() == '.png' and path.is_file(), f'{name}: expected source PNG: {relative}')
            data = path.read_bytes()
            with Image.open(io.BytesIO(data)) as decoded:
                require(decoded.format == 'PNG', f'{name}: input must really be PNG: {relative}')
                frames.append(decoded.convert('RGBA'))
            paths.append(path)
            require(original_inputs.setdefault(path, sha(data)) == sha(data),
                    f'{name}: reused source changed during read')
            target = export / f'{index:02}.png'
            save(target, data)
            require(target.read_bytes() == data, f'{name}/{index}: PNG export not byte-identical')
            source_records.append({'sourcePath': path.relative_to(REPO).as_posix(),
                                   'exportPath': target.relative_to(ROOT).as_posix(),
                                   'pngSha256': sha(data)})
        result = editable(name, folder, frames, durations, paths)
        result['sourceInfo'] = clip['sourceInfo']
        result['sourceInfoSha256'] = sha(json_bytes(clip['sourceInfo']))
        result['pngExportByteExact'] = True
        for record, source_record in zip(result['frames'], source_records):
            record.update(source_record)
        save(export / 'clips.json', json_bytes({'clips': [{
            'name': name, 'durations': durations, 'width': 640, 'height': 360}]}))
        results.append(result)
    require(all(sha(path.read_bytes()) == digest for path, digest in original_inputs.items()),
            'Prepared source PNG changed during packaging')
    require(plan_path.read_bytes() == plan_bytes and provenance_path.read_bytes() == provenance_bytes,
            'Plan/provenance changed during packaging')
    manifest = {'revision': 'ending-elevator-v3', 'planSha256': sha(plan_bytes),
                'provenanceSha256': sha(provenance_bytes), 'inspectedByMain': True,
                'sharedHelperPath': 'tools/art/package_full_cinematics_v2.py',
                'sharedHelperSha256': sha(Path(pipeline.__file__).read_bytes()),
                'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False,
                'runtimeCapture': False, 'gameLaunched': False, 'unityFilesWritten': False,
                'sourcePngsModified': False, 'independentClips': True,
                'concatenatedSequenceCreated': False, 'clips': results}
    save(ROOT / 'Exports/clips.json', json_bytes({'clips': [
        {key: clip[key] for key in ('name', 'durations', 'width', 'height')} for clip in results]}))
    save(ROOT / 'Exports/export-manifest.json', json_bytes(manifest))
    save(ROOT / 'QA/validation.json', json_bytes({
        'passed': True,
        'scope': 'Actual offline RGBA, exact APNG timing, Piskel chunks, source-byte exports, exact GIF palette replay. Not runtime integration or human approval.',
        'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False,
        'runtimeCapture': False, 'gameLaunched': False, 'unityFilesWritten': False,
        'independentClips': True, 'concatenatedSequenceCreated': False,
        'clips': results}))
    print(json.dumps({'clips': len(results), 'independentClips': True,
                      'seconds': {r['name']: r['durationMs'] / 1000 for r in results},
                      'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False}))


if __name__ == '__main__':
    main()
