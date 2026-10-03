"""Re-edit traced pixel shots and generate-derived destination-free lift plates.

Original actor poses never morph: the unchanged source world is composited
first, then a single whole-frame integer NEAREST viewport supplies shot size.
All new shaft geometry comes from the inspected actual imagegen anchor.
"""
from pathlib import Path
from PIL import Image
import argparse
import hashlib
import io
import json
import numpy as np
import derive_pixel_cinematics_v1 as pixel

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-cinematic-edit-v4'
V2 = REPO / 'art/return-pixel-cinematics-v2-full'
V3 = REPO / 'art/return-ending-elevator-v3'
GAME = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2'
ORIGINAL = Path('/Users/daddung/.codex/generated_images/01a0a331-bd2c-78d0-996e-0b8f1f55dce7/exec-5d1d77ce-beff-44b0-8571-6edfee0dc528.png')
WALK_TIMES = [60, 40, 80, 60, 40, 40, 60, 100, 40, 60, 60, 40, 40, 40]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(value, label):
    if not value:
        raise ValueError(label)


def save(path, data):
    require(path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink(), 'Output escapes v4')
    if path.exists():
        require(path.read_bytes() == data, 'Preserving different existing candidate: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def json_save(path, value):
    save(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def png_save(path, image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    save(path, buffer.getvalue())


def archive(path, relative):
    data = path.read_bytes()
    save(ROOT / relative, data)
    return {'sourcePath': str(path), 'sourceSha256': sha(data), 'projectCopy': relative,
            'copySha256': sha((ROOT / relative).read_bytes())}


def derive():
    source = archive(ORIGINAL, 'Source/Generated/shaft-no-destination.png')
    requests_path = ROOT / 'Source/requests.json'
    requests = json.loads(requests_path.read_text())
    request = requests['requests'][0]
    refs = [archive(Path(path), f'Source/References/shaft-{i}.png')
            for i, path in enumerate(request['args']['referenced_image_paths'])]
    json_save(ROOT / 'Source/provenance.json', {'revision': 'cinematic-edit-v4',
        'inspectedByMain': True, 'shownToUser': True, 'builtInMode': True,
        'selectedSource': {**source, 'args': request['args'], 'references': refs},
        'requestsSha256': sha(requests_path.read_bytes()), 'humanAppearanceApproval': 'pending',
        'runtimeIntegrated': False, 'gameLaunched': False, 'unityFilesWritten': False})
    palette_copy = archive(V2 / 'Source/Native/palette.json', 'Source/Native/palette.json')
    palette = np.array(json.loads((ROOT / palette_copy['projectCopy']).read_text())['colors'], np.uint8)
    sampled, geometry = pixel.sample(ROOT / source['projectCopy'])
    rgb, indices = pixel.map_rgb(np.array(sampled)[..., :3], palette)
    logical = pixel.native(rgb)
    native = logical.resize((640, 360), Image.Resampling.NEAREST)
    png_save(ROOT / 'Source/Native/shaft-no-destination-logical.png', logical)
    png_save(ROOT / 'Source/Native/shaft-no-destination.png', native)
    json_save(ROOT / 'Source/Derivation/shaft-pixel-map.json', {
        **geometry, 'source': source['projectCopy'], 'sourceSha256': source['sourceSha256'],
        'logicalSize': [320, 180], 'nativeSize': [640, 360], 'integerScale': 2,
        'paletteSha256': palette_copy['sourceSha256'], 'paletteIndices': indices.astype(int).tolist(),
        'cleanupEdits': [], 'silhouettePainted': False, 'newObjectsCodePainted': False})
    reused_lift = {}
    for name, relative in [
        ('nativeCarriage', 'Source/Native/open-lift-carriage.png'),
        ('logicalCarriage', 'Source/Native/open-lift-carriage-logical.png'),
        ('generatedOriginal', 'Source/Generated/open-lift-carriage.png'),
        ('pixelMap', 'Source/Derivation/open-lift-carriage-pixel-map.json'),
        ('derivation', 'Source/Derivation/native-derivation.json'),
        ('provenance', 'Source/provenance.json'),
        ('requests', 'Source/requests.json')]:
        reused_lift[name] = archive(V3 / relative, 'Source/Reused/Lift/' + relative)
    json_save(ROOT / 'Source/Derivation/native-derivation.json', {
        'generatedSource': source, 'sourceGeometry': geometry, 'logicalSize': [320, 180],
        'nativeSize': [640, 360], 'integerScale': 2,
        'nativeSha256': sha((ROOT / 'Source/Native/shaft-no-destination.png').read_bytes()),
        'logicalSha256': sha((ROOT / 'Source/Native/shaft-no-destination-logical.png').read_bytes()),
        'pixelMapSha256': sha((ROOT / 'Source/Derivation/shaft-pixel-map.json').read_bytes()),
        'reusedLift': reused_lift, 'palette': palette_copy,
        'scriptSha256': sha(Path(__file__).read_bytes()),
        'nativeHelperSha256': sha(Path(pixel.__file__).read_bytes()),
        'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False,
        'newDesignsCodePainted': False})


def compose():
    reg_path = ROOT / 'Source/registration.json'
    reg = json.loads(reg_path.read_text())
    require(reg['nativeInspectedByMain'] is True, 'Inspect native anchor before composition')
    originals = {}

    def reused(key, path):
        if key not in originals:
            record = archive(path, 'Source/Reused/Frames/' + key + '.png')
            originals[key] = {**record, 'rgbaSha256': sha(Image.open(path).convert('RGBA').tobytes())}
        return Image.open(ROOT / originals[key]['projectCopy']).convert('RGBA')

    def viewport(world, rect):
        x, y, w, h = rect
        require(w * 360 == h * 640 and 640 % w == 0, 'Only fixed integer16:9 camera crops')
        require(0 <= x <= 640 - w and 0 <= y <= 360 - h, 'No camera padding/repaint outside original')
        return world.crop((x, y, x + w, y + h)).resize((640, 360), Image.Resampling.NEAREST)

    def frame_write(name, exposures):
        frames, durations, rows = [], [], []
        previous = None
        for image, start, end, metadata in exposures:
            rgba = image.tobytes()
            require(image.size == (640, 360) and end > start, 'Exposure contract')
            require(np.all(np.array(image)[..., 3] == 255), 'Opaque clip required')
            if previous == rgba:
                durations[-1] += end - start
                rows[-1]['endMs'] = end
                rows[-1]['subExposures'].append({'startMs': start, 'endMs': end, **metadata})
            else:
                index = len(frames)
                path = ROOT / f'Clips/{name}/{index:02}.png'
                png_save(path, image)
                frames.append(path.name)
                durations.append(end - start)
                rows.append({'index': index, 'startMs': start, 'endMs': end,
                             'rgbaSha256': sha(rgba), 'pngSha256': sha(path.read_bytes()),
                             'subExposures': [{'startMs': start, 'endMs': end, **metadata}]})
                previous = rgba
        metadata_path = ROOT / f'Source/Composition/{name}.json'
        json_save(metadata_path, {'name': name, 'durationMs': sum(durations), 'frames': rows,
            'sourceActorPosesUnchanged': True, 'wholeCameraIntegerScalingOnly': True,
            'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending', 'runtimeCapture': False})
        return {'name': name, 'durationMs': sum(durations), 'durations': durations,
                'width': 640, 'height': 360, 'frames': frames, 'sourceInfo': {
                    'composition': metadata_path.relative_to(ROOT).as_posix(),
                    'compositionSha256': sha(metadata_path.read_bytes()),
                    'registrationSha256': sha(reg_path.read_bytes()),
                    'wholeCameraIntegerScaleOnly': True, 'actorBodyPartsRedrawn': False,
                    'noWorkshop': name == 'elevator-ascent', 'noDestination': name == 'elevator-ascent'}}

    old_plan = json.loads((V2 / 'Clips/clip-plan.json').read_text())
    awaken = []
    cursor = 0
    for shot in old_plan['clips'][:4]:
        name = shot['name']
        rect = reg['awakeningDockCrop'] if name == 'A1' else [0, 0, 640, 360]
        for index, (filename, ms) in enumerate(zip(shot['frames'], shot['durations'])):
            key = 'awakening/' + name + '/' + filename[:-4]
            world = reused(key, V2 / 'Clips' / name / filename)
            awaken.append((viewport(world, rect), cursor, cursor + ms,
                           {'shotId': name, 'cameraRect': rect, 'cameraScale': 640 // rect[2],
                            'sourceFrameKey': key, 'originalFrameIndex': index,
                            'originalExposureMs': ms, 'sourceClockRestarted': False}))
            cursor += ms
    require(cursor == 8000, 'Awakening total8seconds')
    clips = [frame_write('awakening', awaken)]

    collapse_plan = json.loads((V3 / 'Clips/clip-plan.json').read_text())['clips'][0]
    original_collapse = []
    cursor = 0
    for filename, ms in zip(collapse_plan['frames'], collapse_plan['durations']):
        original_collapse.append((cursor, cursor + ms, filename))
        cursor += ms
    boundaries = sorted({0, 850, 1800, 3000} | {start for start, _, _ in original_collapse})
    collapse = []
    for start, end in zip(boundaries, boundaries[1:]):
        original = next(filename for first, last, filename in original_collapse if first <= start < last)
        key = 'collapse/' + original[:-4]
        world = reused(key, V3 / 'Clips/guardian-collapse' / original)
        shot = 'C1' if start < 850 else 'C2' if start < 1800 else 'C3'
        rect = reg['collapseMediumCrop'] if shot == 'C1' else reg['deadCoreCrop'] if shot == 'C2' else [0, 0, 640, 360]
        collapse.append((viewport(world, rect), start, end,
                         {'shotId': shot, 'cameraRect': rect, 'cameraScale': 640 // rect[2],
                          'sourceFrameKey': key, 'sourceClockRestarted': False, 'closedArena': True}))
    clips.append(frame_write('guardian-collapse', collapse))

    background = Image.open(ROOT / 'Source/Native/shaft-no-destination.png').convert('RGBA')
    carriage = Image.open(ROOT / 'Source/Reused/Lift/Source/Native/open-lift-carriage.png').convert('RGBA')
    car_anchor = reg['carriageFloorAnchor']
    center = reg['carCenterX']
    times = set(range(0, 7001, 40)) | {0, 760, 1200, 2200, 2800, 2880, 2980, 3060, 4600, 6600, 7000}
    cursor = 0
    for duration in WALK_TIMES:
        cursor += duration
        times.add(cursor)
    times = sorted(times)

    def pose(time):
        if time < 760:
            accumulated = 0
            for index, duration in enumerate(WALK_TIMES):
                accumulated += duration
                if time < accumulated:
                    return 'Walk', index
        if 2800 <= time < 2880 or 2980 <= time < 3060:
            return 'blink-half', 0
        if 2880 <= time < 2980:
            return 'blink-closed', 0
        return 'Idle', 0

    elevator = []
    for start, end in zip(times, times[1:]):
        u = min(1, max(0, (start - 1200) / 5400))
        floor = round(reg['lowerFloorY'] + (reg['exitFloorY'] - reg['lowerFloorY']) * u * u)
        shot = 'E1' if start < 1200 else 'E2' if start < 2200 else 'E3' if start < 4600 else 'E4'
        if start >= 6600:
            image = Image.new('RGBA', (640, 360), (0, 0, 0, 255))
            metadata = {'shotId': 'E4', 'cutToBlack': True, 'caption': None, 'destinationShown': False}
        else:
            world = background.copy()
            car_xy = [center - car_anchor[0], floor - car_anchor[1]]
            world.alpha_composite(carriage, tuple(car_xy))
            kind, index = pose(start)
            x = round(reg['boardingStartX'] + (center - reg['boardingStartX']) * min(start / 760, 1))
            actor_key = f'tique/{kind}/{index:02}'
            tique = reused(actor_key, GAME / f'TiqueV10/{kind}/{index:02}.png')
            actor_xy = [x - 32, floor - 56]
            world.alpha_composite(tique, tuple(actor_xy))
            if shot == 'E1':
                rect = reg['boardingCrop']
            elif shot == 'E2':
                rect = reg['guideInsertCrop']
            elif shot == 'E3':
                rect = [reg['riderTrackingX'], floor - reg['riderScreenFootLogical'], 160, 90]
            else:
                rect = [0, 0, 640, 360]
            image = viewport(world, rect)
            metadata = {'shotId': shot, 'cameraRect': rect, 'cameraScale': 640 // rect[2],
                        'background': 'Source/Native/shaft-no-destination.png',
                        'worldClockMs': start, 'floorY': floor, 'ascentProgress': u,
                        'carriage': {'source': 'Source/Reused/Lift/Source/Native/open-lift-carriage.png',
                                     'xy': car_xy, 'anchor': car_anchor, 'scale': 1, 'rigidTranslation': True},
                        'actor': {'sourceFrameKey': actor_key, 'xy': actor_xy, 'foot': [x, floor],
                                  'anchor': [32, 56], 'scale': 1, 'flipped': False, 'rotated': False},
                        'destinationShown': False, 'disembarking': False, 'caption': None,
                        'intentionalExitClipping': start >= 4600,
                        'sourceClockRestarted': False}
        elevator.append((image, start, end, metadata))
    clips.append(frame_write('elevator-ascent', elevator))
    for clip, ms in zip(clips, (8000, 3000, 7000)):
        require(clip['durationMs'] == ms, 'Independent clip duration')
    lineage = []
    for package, folder in ((V2, 'v2'), (V3, 'v3')):
        for relative in ('Source/provenance.json', 'Clips/clip-plan.json'):
            lineage.append(archive(package / relative, f'Source/Reused/Lineage/{folder}/' + relative))
    json_save(ROOT / 'Source/reused-assets.json', {'sources': originals, 'lineage': lineage,
        'worldActorFramesUnchanged': True, 'wholeCameraScaleNotBodyPartScale': True,
        'humanAppearanceApproval': 'pending'})
    json_save(ROOT / 'Clips/clip-plan.json', {'revision': 'cinematic-edit-v4', 'clips': clips,
        'sequences': [], 'independentClips': True, 'runtimeIntegrated': False})
    json_save(ROOT / 'Source/Composition/authoring.json', {
        'scriptSha256': sha(Path(__file__).read_bytes()), 'registrationSha256': sha(reg_path.read_bytes()),
        'integerViewportSizes': [[640, 360], [320, 180], [160, 90]],
        'noWorkshop': True, 'noArrival': True, 'noDisembark': True, 'noEndingCaption': True,
        'fallingOpeningChanged': False, 'runtimeIntegrated': False, 'unityFilesWritten': False,
        'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending'})
    print(json.dumps({'clips': [{'name': c['name'], 'frames': len(c['frames']), 'durationMs': c['durationMs']} for c in clips]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', required=True, action='store_true')
    parser.add_argument('--derive-only', action='store_true')
    args = parser.parse_args()
    require(args.inspected_anchors, 'Actual generation must be inspected and shown first')
    derive()
    if not args.derive_only:
        compose()
    else:
        print('Destination-free native source derived; inspect before camera registration.')


if __name__ == '__main__':
    main()
