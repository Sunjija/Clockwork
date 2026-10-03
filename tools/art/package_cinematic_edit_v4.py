"""Package three independent cinematic-edit candidates from inspected native PNGs.

Input: art/return-cinematic-edit-v4/Source/provenance.json and Clips/clip-plan.json.
Image generation, anchor inspection and native authoring happen upstream. This
wrapper reuses the tested v3 bounded-sheet/Piskel/APNG/GIF implementation without
modifying its source or previous packages. It neither generates new art, changes
Unity, mixes audio, encodes MP4 nor creates a combined eighteen-second sequence.
"""
from pathlib import Path
from PIL import Image
import argparse
import io
import json

import package_ending_elevator_v3 as editable_pipeline


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-cinematic-edit-v4'
SIZE = (640, 360)
CLIP_TIMES = {'awakening': 8000, 'guardian-collapse': 3000, 'elevator-ascent': 7000}

# Both helpers resolve their strict-save and relative metadata paths through
# module globals. Redirect only this process; the old scripts/packages stay
# untouched on disk, and neither previous module's main() is called.
editable_pipeline.ROOT = ROOT
editable_pipeline.pipeline.ROOT = ROOT
pipeline = editable_pipeline.pipeline
require, sha, json_bytes = pipeline.require, pipeline.sha, pipeline.json_bytes
save, editable = pipeline.save, editable_pipeline.editable


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
    require(isinstance(clips, list), 'clip-plan clips must be a list')
    names = [clip['name'] for clip in clips]
    require(len(names) == len(CLIP_TIMES) and set(names) == set(CLIP_TIMES),
            'Expected exactly awakening, guardian-collapse and elevator-ascent')
    require(not plan.get('sequences'),
            'Three independent clips must not be concatenated into a sequence')
    results, original_inputs = [], {}
    for clip in clips:
        name, durations = clip['name'], clip['durations']
        require((clip['width'], clip['height']) == SIZE, f'{name}: native canvas contract')
        require(isinstance(durations, list) and durations
                and all(type(ms) is int and ms > 0 for ms in durations),
                f'{name}: positive integer durations required')
        require(sum(durations) == clip['durationMs'] == CLIP_TIMES[name],
                f'{name}: planned independent clip duration mismatch')
        require(isinstance(clip['frames'], list)
                and len(durations) == len(clip['frames'])
                and isinstance(clip['sourceInfo'], dict), f'{name}: input schema mismatch')
        folder, export = ROOT / 'Clips' / name, ROOT / 'Exports' / name
        paths, frames, source_records = [], [], []
        for index, relative in enumerate(clip['frames']):
            require(isinstance(relative, str), f'{name}: source path must be a string')
            path = pipeline.confined(folder, relative)
            require(path.suffix.lower() == '.png' and path.is_file(),
                    f'{name}: expected source PNG: {relative}')
            data = path.read_bytes()
            with Image.open(io.BytesIO(data)) as decoded:
                require(decoded.format == 'PNG' and getattr(decoded, 'n_frames', 1) == 1,
                        f'{name}: input must really be a single-frame PNG: {relative}')
                require(decoded.size == SIZE, f'{name}/{index}: expected native640x360')
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
            'name': name, 'durations': durations, 'width': SIZE[0], 'height': SIZE[1]}]}))
        results.append(result)
    require(all(sha(path.read_bytes()) == digest for path, digest in original_inputs.items()),
            'Prepared source PNG changed during packaging')
    require(plan_path.read_bytes() == plan_bytes and provenance_path.read_bytes() == provenance_bytes,
            'Plan/provenance changed during packaging')
    script_path = Path(__file__).resolve()
    editable_helper_path = Path(editable_pipeline.__file__).resolve()
    pixel_helper_path = Path(pipeline.__file__).resolve()
    common = {'revision': 'cinematic-edit-v4', 'planSha256': sha(plan_bytes),
              'provenanceSha256': sha(provenance_bytes), 'inspectedByMain': True,
              'scriptPath': script_path.relative_to(REPO).as_posix(),
              'scriptSha256': sha(script_path.read_bytes()),
              'sharedHelperPath': editable_helper_path.relative_to(REPO).as_posix(),
              'sharedHelperSha256': sha(editable_helper_path.read_bytes()),
              'pixelHelperPath': pixel_helper_path.relative_to(REPO).as_posix(),
              'pixelHelperSha256': sha(pixel_helper_path.read_bytes()),
              'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending',
              'runtimeIntegrated': False, 'runtimeCapture': False, 'gameLaunched': False,
              'unityFilesWritten': False, 'sourcePngsModified': False,
              'independentClips': True, 'independentClipCount': len(results),
              'concatenatedSequenceCreated': False}
    save(ROOT / 'Exports/clips.json', json_bytes({'clips': [
        {key: clip[key] for key in ('name', 'durations', 'width', 'height')} for clip in results]}))
    save(ROOT / 'Exports/export-manifest.json', json_bytes({**common, 'clips': results}))
    save(ROOT / 'QA/validation.json', json_bytes({
        **common, 'passed': True,
        'scope': 'Actual offline RGBA, exact APNG timing, bounded Piskel chunks, source-byte PNG exports and exact GIF palette replay. Not runtime integration or human appearance/motion approval.',
        'clips': results}))
    print(json.dumps({'clips': len(results), 'independentClips': True,
                      'seconds': {r['name']: r['durationMs'] / 1000 for r in results},
                      'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending',
                      'runtimeIntegrated': False}))


if __name__ == '__main__':
    main()
