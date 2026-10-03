"""Offline, art-read-only packaging of eight prepared cinematic shots and two sequences.

Input: art/return-pixel-cinematics-v2-full/Clips/clip-plan.json. Each clip has
name, durationMs, durations, width, height, frames (clip-relative PNG paths),
sourceInfo (preserved verbatim). Each sequence has name, shots, durationMs.
Actual image generation/native authoring and main inspection happen upstream.
This script never generates art, invokes Unity, writes game assets or deletes.
"""
from pathlib import Path
from PIL import Image
import argparse
import base64
import hashlib
import io
import json
import re
import numpy as np

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-pixel-cinematics-v2-full'
SIZE = (640, 360)
SHOT_TIMES = {'A1': 2000, 'A2': 2000, 'A3': 2000, 'A4': 2000,
              'B1': 2000, 'B2': 2000, 'B3': 3000, 'B4': 3000}
SEQUENCES = {'awakening': (['A1', 'A2', 'A3', 'A4'], 8000),
             'homecoming': (['B1', 'B2', 'B3', 'B4'], 10000)}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def confined(root, relative):
    path = Path(relative)
    require(not path.is_absolute() and '..' not in path.parts, 'Expected confined relative path: ' + relative)
    result = (root / path).resolve()
    require(result.is_relative_to(root.resolve()), 'Input path escapes root: ' + relative)
    return result


def save(path, data):
    require(path.resolve().is_relative_to(ROOT.resolve()), 'Output must stay inside new v2 candidate root')
    if path.exists():
        require(path.read_bytes() == data, f'Preserving different existing output; use a new candidate name: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def encoded(image, **options):
    stream = io.BytesIO()
    image.save(stream, **options)
    return stream.getvalue()


def delta(first, frame):
    target = np.array(frame)
    ys, xs = np.where(np.any(np.array(first) != target, axis=2))
    return [[int(x), int(y), *map(int, target[y, x])] for y, x in zip(ys, xs)]


def preview(frames, durations, path):
    # GIF rounds cumulative boundaries to10ms; zero exposures are preview-only skips.
    # Every original frame remains in PNG/Piskel/APNG with its exact variable time.
    require(frames and len(frames) == len(durations), 'GIF frame/duration count mismatch')
    elapsed = previous = 0
    timing = []
    for ms in durations:
        elapsed += ms
        rounded = round(elapsed / 10) * 10
        timing.append(rounded - previous)
        previous = rounded
    require(all(ms >= 0 for ms in timing), 'GIF rounded boundaries must be monotonic')
    original_indexes = [i for i, ms in enumerate(timing) if ms > 0]
    skipped_indexes = [i for i, ms in enumerate(timing) if ms == 0]
    require(original_indexes, 'GIF needs at least one positive preview exposure')
    visible_frames = [frames[i] for i in original_indexes]
    visible_timing = [timing[i] for i in original_indexes]
    # One exact union palette for positive exposures, no quantization/dithering.
    palette = sorted({tuple(map(int, color)) for frame in visible_frames
                      for color in np.unique(np.array(frame.convert('RGB')).reshape(-1, 3), axis=0)})
    require(0 < len(palette) <= 256, 'GIF shared palette must contain at most256 source colors')
    packed_palette = np.array([(r << 16) | (g << 8) | b for r, g, b in palette], dtype=np.uint32)
    flat_palette = [channel for color in palette for channel in color]
    padded_palette = flat_palette + [0] * (768 - len(flat_palette))
    pictures = []
    for frame in visible_frames:
        rgb = np.array(frame.convert('RGB'), dtype=np.uint32)
        packed = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
        indexes = np.searchsorted(packed_palette, packed)
        valid = (indexes < len(palette)) & (packed_palette[np.minimum(indexes, len(palette) - 1)] == packed)
        mapped = np.zeros(packed.shape, dtype=np.uint8)  # Unmapped/padding entries are deterministically zero.
        mapped[valid] = indexes[valid].astype(np.uint8)
        require(np.all(valid), 'GIF source color is missing from the shared palette')
        indexed = Image.frombytes('P', frame.size, mapped.tobytes())
        indexed.putpalette(padded_palette)
        pictures.append(indexed.resize((1280, 720), Image.Resampling.NEAREST))
    data = encoded(pictures[0], format='GIF', save_all=True, append_images=pictures[1:],
                   duration=visible_timing, loop=0, optimize=False,
                   comment=b'10ms nearest boundary preview; PNG/APNG exact original timing authority; NOT runtime capture; human approval pending.')
    save(path, data)
    decoded = Image.open(io.BytesIO(data))
    actual_total, source_index, source_end = 0, 0, visible_timing[0]
    cached_index, expected_rgb = -1, None
    for index in range(decoded.n_frames):
        decoded.seek(index)
        duration = decoded.info.get('duration', 0)
        require(duration > 0, 'GIF decoded exposure has no positive duration')
        cursor, end = actual_total, actual_total + duration
        actual_rgb = decoded.convert('RGB').tobytes()
        # A merged GIF exposure may span several identical source exposures.
        # Compare every overlap interval, not merely the decoder's frame count.
        while cursor < end:
            require(source_index < len(visible_frames), 'GIF exposure extends beyond the rounded preview timeline')
            if cached_index != source_index:
                expected_rgb = visible_frames[source_index].convert('RGB').resize((1280, 720), Image.Resampling.NEAREST).tobytes()
                cached_index = source_index
            require(actual_rgb == expected_rgb, f'GIF decoded RGB differs from original exposure {original_indexes[source_index]}')
            cursor = min(end, source_end)
            if cursor == source_end:
                source_index += 1
                if source_index < len(visible_timing):
                    source_end += visible_timing[source_index]
        actual_total = end
    require(actual_total == sum(timing), 'GIF decoded timing total mismatch: ' + str(path))
    require(actual_total == sum(durations), 'GIF 10ms timing cannot preserve the requested total duration')
    require(source_index == len(visible_frames), 'GIF did not replay every positive rounded exposure')
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(data),
            'requestedDurationsMs': durations, 'encodedDurationsMs': timing,
            'encodedExposures': [{'originalIndex': i, 'durationMs': timing[i]} for i in original_indexes],
            'skippedOriginalIndexes': skipped_indexes,
            'requestedTotalMs': sum(durations), 'encodedTotalMs': actual_total,
            'decodedTotalMatchesSource': True, 'scale': 2, 'resampling': 'NEAREST',
            'sharedPalette': [list(color) for color in palette], 'paletteColors': len(palette),
            'dither': 'NONE: direct exact P-index assignment', 'decodedExposureRgbExact': True,
            'adjacentIdenticalExposureMergeAllowed': True, 'decodedFrameCount': decoded.n_frames,
            'description': '10ms nearest boundary preview; original variable timing is retained in PNG/APNG, not GIF.',
            'timingAuthority': 'native.apng and QA/validation.json, not GIF'}


def editable(name, folder, frames, durations, gif_path, input_paths=None):
    require(frames and len(frames) == len(durations), f'{name}: frame/duration count mismatch')
    palette = set()
    for image in frames:
        require(image.size == SIZE, f'{name}: expected640x360 native canvas')
        array = np.array(image)
        require(np.all(array[..., 3] == 255), f'{name}: expected fully opaque alpha255')
        palette.update(tuple(p) for p in np.unique(array[..., :3].reshape(-1, 3), axis=0))
    require(len(palette) <= 256, f'{name}: combined visible palette exceeds256 colors')
    sheet = Image.new('RGBA', (SIZE[0] * len(frames), SIZE[1]))
    records = []
    for index, image in enumerate(frames):
        sheet.paste(image, (index * SIZE[0], 0))
        row = {'frame': index, 'durationMs': durations[index],
               'rgbaSha256': sha(image.tobytes()), 'alphaMaskSha256': sha(image.getchannel('A').tobytes())}
        if input_paths is not None:
            edits = delta(frames[0], image)
            path = input_paths[index].with_suffix('.pixels.json')
            save(path, json_bytes(edits))
            replay = frames[0].copy()
            for x, y, r, g, b, a in json.loads(path.read_bytes()):
                replay.putpixel((x, y), (r, g, b, a))
            require(replay.tobytes() == image.tobytes(), f'{name}/{index}: first-frame delta replay failed')
            row.update({'deltaPath': path.relative_to(ROOT).as_posix(), 'deltaSha256': sha(path.read_bytes()),
                        'changedPixelsFromFirstFrame': len(edits), 'deltaReplayRgbaExact': True})
        records.append(row)
    sheet_data = encoded(sheet, format='PNG')
    save(folder / 'sheet.png', sheet_data)
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': [
        {'layout': [[i] for i in range(len(frames))],
         'base64PNG': 'data:image/png;base64,' + base64.b64encode(sheet_data).decode('ascii')}]}
    piskel = {'modelVersion': 2, 'piskel': {'name': name, 'fps': 20, 'width': 640, 'height': 360,
        'description': 'Offline image-first candidate; exact variable timing in APNG/validation; human approval pending.',
        'layers': [json.dumps(layer)]}}
    save(folder / f'{name}.piskel', json_bytes(piskel))
    restored_layer = json.loads(json.loads((folder / f'{name}.piskel').read_bytes())['piskel']['layers'][0])
    restored = Image.open(io.BytesIO(base64.b64decode(restored_layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
    require(restored_layer['frameCount'] == len(frames) and restored.size == sheet.size, f'{name}: Piskel frame geometry mismatch')
    apng_data = encoded(frames[0], format='PNG', save_all=True, append_images=frames[1:],
                        duration=durations, loop=0, disposal=1, blend=0)
    save(folder / 'native.apng', apng_data)
    apng = Image.open(folder / 'native.apng')
    require(apng.n_frames == len(frames), f'{name}: APNG merged hold exposures')
    for index, image in enumerate(frames):
        require(restored.crop((index * 640, 0, (index + 1) * 640, 360)).tobytes() == image.tobytes(),
                f'{name}/{index}: Piskel RGBA replay mismatch')
        apng.seek(index)
        require(apng.convert('RGBA').tobytes() == image.tobytes(), f'{name}/{index}: APNG RGBA replay mismatch')
        require(round(apng.info['duration']) == durations[index], f'{name}/{index}: APNG variable timing mismatch')
    return {'name': name, 'width': 640, 'height': 360, 'frameCount': len(frames),
            'durations': durations, 'durationMs': sum(durations), 'paletteColors': len(palette),
            'paletteAtMost256': True, 'alpha255': True, 'frames': records,
            'piskelReplayRgbaExact': True, 'apngReplayRgbaAndDurationExact': True,
            'sheetSha256': sha(sheet_data), 'apngSha256': sha(apng_data),
            'piskelSha256': sha((folder / f'{name}.piskel').read_bytes()),
            'preview': preview(frames, durations, gif_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', action='store_true', required=True)
    args = parser.parse_args()
    require(args.inspected_anchors, 'Main-agent anchor inspection is required')
    provenance_path, plan_path = ROOT / 'Source/provenance.json', ROOT / 'Clips/clip-plan.json'
    provenance_bytes, plan_bytes = provenance_path.read_bytes(), plan_path.read_bytes()
    require(json.loads(provenance_bytes).get('inspectedByMain') is True, 'Source/provenance.json requires inspectedByMain=true')
    plan = json.loads(plan_bytes)
    names = [clip['name'] for clip in plan['clips']]
    require(len(names) == 8 and set(names) == set(SHOT_TIMES), 'Expected exactly8 A1..A4/B1..B4 shots')
    sequence_names = [sequence['name'] for sequence in plan['sequences']]
    require(len(sequence_names) == 2 and set(sequence_names) == set(SEQUENCES), 'Expected awakening and homecoming sequences')
    cached, results, original_inputs = {}, [], {}
    for clip in plan['clips']:
        name, durations = clip['name'], clip['durations']
        require(re.fullmatch(r'[AB][1-4]', name) and clip['width'] == 640 and clip['height'] == 360, f'{name}: shot contract')
        require(durations and all(type(ms) is int and ms > 0 for ms in durations), f'{name}: positive integer durations required')
        require(sum(durations) == clip['durationMs'] == SHOT_TIMES[name], f'{name}: planned shot duration mismatch')
        require(len(durations) == len(clip['frames']) and isinstance(clip['sourceInfo'], dict), f'{name}: input schema mismatch')
        folder, export = ROOT / 'Clips' / name, ROOT / 'Exports' / name
        paths, frames, source_records = [], [], []
        for index, relative in enumerate(clip['frames']):
            path = confined(folder, relative)
            require(path.suffix.lower() == '.png' and path.is_file(), f'{name}: expected source PNG: {relative}')
            data = path.read_bytes()
            with Image.open(io.BytesIO(data)) as decoded:
                require(decoded.format == 'PNG', f'{name}: input must really be PNG: {relative}')
                frames.append(decoded.convert('RGBA'))
            paths.append(path)
            require(original_inputs.setdefault(path, sha(data)) == sha(data), f'{name}: reused source changed during read')
            target = export / f'{index:02}.png'
            save(target, data)
            require(target.read_bytes() == data, f'{name}/{index}: PNG export not byte-identical')
            source_records.append({'sourcePath': path.relative_to(REPO).as_posix(),
                                   'exportPath': target.relative_to(ROOT).as_posix(), 'pngSha256': sha(data)})
        result = editable(name, folder, frames, durations, ROOT / 'QA' / f'{name}-preview.gif', paths)
        result['sourceInfo'] = clip['sourceInfo']
        result['sourceInfoSha256'] = sha(json_bytes(clip['sourceInfo']))
        result['pngExportByteExact'] = True
        for record, source_record in zip(result['frames'], source_records):
            record.update(source_record)
        save(export / 'clips.json', json_bytes({'clips': [{'name': name, 'durations': durations, 'width': 640, 'height': 360}]}))
        cached[name] = (frames, durations)
        results.append(result)
    sequence_results = []
    for sequence in plan['sequences']:
        name, shots = sequence['name'], sequence['shots']
        require(shots == SEQUENCES[name][0] and sequence['durationMs'] == SEQUENCES[name][1], f'{name}: sequence shot order/duration contract')
        frames, durations, locations = [], [], []
        for shot in shots:
            shot_frames, shot_durations = cached[shot]
            frames.extend(shot_frames)
            durations.extend(shot_durations)
            locations.extend({'shot': shot, 'shotFrame': i} for i in range(len(shot_frames)))
        require(sum(durations) == sequence['durationMs'], f'{name}: concatenated duration mismatch')
        folder = ROOT / 'Sequences' / name
        result = editable(name, folder, frames, durations, folder / 'preview.gif')
        result['shots'] = shots
        for row, location in zip(result['frames'], locations):
            row.update(location)
        sequence_results.append(result)
    require(all(sha(path.read_bytes()) == digest for path, digest in original_inputs.items()), 'Prepared source PNG changed during packaging')
    require(plan_path.read_bytes() == plan_bytes and provenance_path.read_bytes() == provenance_bytes, 'Plan/provenance changed during packaging')
    export_manifest = {'revision': 'pixel-cinematics-v2-full', 'planSha256': sha(plan_bytes),
        'provenanceSha256': sha(provenance_bytes), 'inspectedByMain': True,
        'humanAppearanceApproval': 'pending', 'runtimeCapture': False, 'gameLaunched': False,
        'unityFilesWritten': False, 'sourcePngsModified': False, 'clips': results, 'sequences': sequence_results}
    save(ROOT / 'Exports/clips.json', json_bytes({'clips': [{key: clip[key] for key in ('name', 'durations', 'width', 'height')} for clip in results]}))
    save(ROOT / 'Exports/export-manifest.json', json_bytes(export_manifest))
    save(ROOT / 'QA/validation.json', json_bytes({'passed': True, 'scope': 'Actual offline artifact RGBA/timing/byte checks; not runtime capture or human motion approval.',
        'humanAppearanceApproval': 'pending', 'geometryRigidMathematicalApproval': 'pending',
        'runtimeCapture': False, 'gameLaunched': False, 'unityFilesWritten': False,
        'clips': results, 'sequences': sequence_results}))
    print(json.dumps({'clips': len(results), 'sequences': len(sequence_results), 'shotSeconds': [r['durationMs'] / 1000 for r in results],
                      'sequenceSeconds': [r['durationMs'] / 1000 for r in sequence_results], 'humanAppearanceApproval': 'pending'}))


if __name__ == '__main__':
    main()
