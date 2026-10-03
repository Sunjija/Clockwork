"""Independently replay v4 sources, native derivation and every camera exposure.

Only QA/composition-validation.json and QA/shot-board.png are written. The
generator/compositor is never imported or executed. PNG sources, old packages,
runtime assets and exports remain read-only; technical checks are not approval.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import io
import json
import numpy as np

import derive_pixel_cinematics_v1 as pixel


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-cinematic-edit-v4'
SIZE = (640, 360)
TIMES = {'awakening': 8000, 'guardian-collapse': 3000, 'elevator-ascent': 7000}
WALK = [60, 40, 80, 60, 40, 40, 60, 100, 40, 60, 60, 40, 40, 40]
FONT = REPO / 'art/return-v5-feedback/Source/Font/neodgm.ttf'
OUTPUTS = {ROOT / 'QA/composition-validation.json', ROOT / 'QA/shot-board.png'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(relative):
    return json.loads((ROOT / relative).read_bytes())


def confined(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT.resolve()), 'Path escapes v4: ' + str(relative))
    return path


def save(path, data):
    require(path in OUTPUTS and not path.is_symlink(), 'QA checker output is not authorized')
    if path.exists():
        require(path.read_bytes() == data, 'Preserving different existing QA: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def image(path):
    with Image.open(path) as decoded:
        return decoded.convert('RGBA')


def archive(record):
    original, copy = Path(record['sourcePath']), confined(record['projectCopy'])
    source_bytes, copy_bytes = original.read_bytes(), copy.read_bytes()
    require(source_bytes == copy_bytes, 'Archive changed source bytes: ' + str(copy))
    require(sha(source_bytes) == record['sourceSha256'] == record['copySha256'],
            'Archive SHA mismatch: ' + str(copy))
    if 'rgbaSha256' in record:
        require(sha(image(copy).tobytes()) == record['rgbaSha256'], 'Archive RGBA SHA mismatch')


def native_check(palette):
    derivation = load('Source/Derivation/native-derivation.json')
    for record in [derivation['generatedSource'], derivation['palette'],
                   *derivation['reusedLift'].values()]:
        archive(record)
    logical = image(ROOT / 'Source/Native/shaft-no-destination-logical.png')
    native = image(ROOT / 'Source/Native/shaft-no-destination.png')
    mapping = load('Source/Derivation/shaft-pixel-map.json')
    require(logical.size == (320, 180) and native.size == SIZE, 'Shaft dimensions changed')
    sampled, geometry = pixel.sample(confined(mapping['source']))
    rgb, indexes = pixel.map_rgb(np.array(sampled)[..., :3], palette)
    require(geometry == derivation['sourceGeometry'], 'Source BOX geometry changed')
    require(np.array_equal(indexes, mapping['paletteIndices']), 'Generated shaft palette-index replay failed')
    require(pixel.native(rgb).tobytes() == logical.tobytes(), 'Generated shaft BOX/palette replay failed')
    require(logical.resize(SIZE, Image.Resampling.NEAREST).tobytes() == native.tobytes(),
            'Shaft exact2x native replay failed')
    for field, relative in [('logicalSha256', 'Source/Native/shaft-no-destination-logical.png'),
                            ('nativeSha256', 'Source/Native/shaft-no-destination.png'),
                            ('pixelMapSha256', 'Source/Derivation/shaft-pixel-map.json')]:
        require(sha(confined(relative).read_bytes()) == derivation[field], 'Shaft recorded SHA mismatch')
    lift_root = ROOT / 'Source/Reused/Lift'
    lift_map = load('Source/Reused/Lift/Source/Derivation/open-lift-carriage-pixel-map.json')
    lift_derivation = load('Source/Reused/Lift/Source/Derivation/native-derivation.json')
    lift_record = lift_derivation['assets']['open-lift-carriage']
    source = image(lift_root / lift_map['source'])
    require(sha((lift_root / lift_map['source']).read_bytes()) == lift_map['sourceSha256'],
            'Generated lift original SHA mismatch')
    alpha = np.array(source)[..., 3]
    ys, xs = np.where(alpha >= 128)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]
    require(bbox == lift_map['sourceRect'], 'Lift whole-object alpha bounds changed')
    crop = source.crop(tuple(bbox))
    sample_size = (52, max(1, round(crop.height * 52 / crop.width)))
    require(list(sample_size) == lift_map['sampleSize'], 'Lift sample geometry changed')
    sampled = np.array(crop.convert('RGBa').resize(sample_size, Image.Resampling.BOX).convert('RGBA'))
    rgb, indexes = pixel.map_rgb(sampled[..., :3], palette)
    visible = sampled[..., 3] >= 128
    rgba = np.zeros((*visible.shape, 4), np.uint8)
    rgba[visible, :3], rgba[visible, 3] = rgb[visible], 255
    reconstructed = Image.new('RGBA', (64, 64))
    offset = ((64 - sample_size[0]) // 2, (64 - sample_size[1]) // 2)
    reconstructed.paste(Image.fromarray(rgba), offset)
    full_indexes = np.full((64, 64), -1, np.int32)
    x, y = offset
    full_indexes[y:y + sample_size[1], x:x + sample_size[0]] = np.where(visible, indexes, -1)
    require(np.array_equal(full_indexes, lift_map['paletteIndices']), 'Lift palette/alpha map replay failed')
    lift_logical = image(lift_root / lift_record['logicalOutput'])
    lift_native = image(lift_root / lift_record['output'])
    require(reconstructed.tobytes() == lift_logical.tobytes(), 'Lift premultiplied BOX replay failed')
    require(lift_logical.resize((128, 128), Image.Resampling.NEAREST).tobytes() == lift_native.tobytes(),
            'Lift exact2x native replay failed')
    require(set(np.unique(np.array(lift_native)[..., 3])) == {0, 255}, 'Lift alpha must be binary')
    require(np.mean(np.array(lift_logical)[12:40, 16:48, 3] == 0) > .8, 'Lift interior lost transparency')
    require(derivation['nativeHelperSha256'] == sha(Path(pixel.__file__).read_bytes()),
            'Recorded native helper SHA changed')
    require(derivation['scriptSha256'] == sha((REPO / 'tools/art/compose_cinematic_edit_v4.py').read_bytes()),
            'Recorded v4 authoring script SHA changed')
    return {'shaftGeneratedBoxPaletteReplayExact': True, 'shaftNative2xReplayExact': True,
            'liftGeneratedBoxPaletteAlphaReplayExact': True, 'liftNative2xReplayExact': True,
            'liftInteriorAlphaOpen': True, 'fixedPaletteColors': len(palette)}


def floor_at(time, reg):
    progress = min(1, max(0, (time - 1200) / 5400))
    return reg['lowerFloorY'] + (reg['exitFloorY'] - reg['lowerFloorY']) * progress ** 2


def pose_at(time):
    if time < 760:
        end = 0
        for index, duration in enumerate(WALK):
            end += duration
            if time < end:
                return f'tique/Walk/{index:02}'
    if 2800 <= time < 2880 or 2980 <= time < 3060:
        return 'tique/blink-half/00'
    if 2880 <= time < 2980:
        return 'tique/blink-closed/00'
    return 'tique/Idle/00'


def camera(world, metadata):
    x, y, width, height = metadata['cameraRect']
    require(all(type(v) is int for v in (x, y, width, height)), 'Camera is not integer registered')
    require((width, height) in {(640, 360), (320, 180), (160, 90)}, 'Unsupported camera size')
    require(0 <= x <= 640 - width and 0 <= y <= 360 - height, 'Camera requires padding')
    require(metadata['cameraScale'] == 640 // width, 'Camera scale differs from whole-frame crop')
    return world.crop((x, y, x + width, y + height)).resize(SIZE, Image.Resampling.NEAREST)


def main():
    protected = {p: sha(p.read_bytes()) for folder in ('Source', 'Clips')
                 for p in (ROOT / folder).rglob('*') if p.is_file() and p.suffix != '.pixels.json'}
    provenance, reg = load('Source/provenance.json'), load('Source/registration.json')
    require(provenance['inspectedByMain'] is True and provenance['shownToUser'] is True
            and reg['nativeInspectedByMain'] is True, 'Main source/native inspection missing')
    archive(provenance['selectedSource'])
    for record in provenance['selectedSource']['references']:
        archive(record)
    require(sha((ROOT / 'Source/requests.json').read_bytes()) == provenance['requestsSha256'],
            'Actual image-generation request SHA changed')
    palette = np.array(load('Source/Native/palette.json')['colors'], np.uint8)
    native_result = native_check(palette)
    reused = load('Source/reused-assets.json')
    for record in [*reused['sources'].values(), *reused['lineage']]:
        archive(record)
    cached = {key: image(confined(record['projectCopy'])) for key, record in reused['sources'].items()}
    plan = load('Clips/clip-plan.json')
    require(len(plan['clips']) == 3 and {c['name'] for c in plan['clips']} == set(TIMES)
            and not plan['sequences'] and plan['independentClips'] is True, 'Independent three-clip contract')
    authoring = load('Source/Composition/authoring.json')
    require(all(authoring[k] is True for k in ('noWorkshop', 'noArrival', 'noDisembark', 'noEndingCaption'))
            and authoring['fallingOpeningChanged'] is False, 'Scope changed from requested re-edit')
    require(authoring['registrationSha256'] == sha((ROOT / 'Source/registration.json').read_bytes()),
            'Camera registration SHA mismatch')
    background = image(ROOT / 'Source/Native/shaft-no-destination.png')
    carriage = image(ROOT / 'Source/Reused/Lift/Source/Native/open-lift-carriage.png')
    results, compositions, all_subs = [], {}, []
    for clip in plan['clips']:
        name = clip['name']
        composition = load(clip['sourceInfo']['composition'])
        compositions[name] = composition
        require(sha(confined(clip['sourceInfo']['composition']).read_bytes())
                == clip['sourceInfo']['compositionSha256'], f'{name}: composition SHA changed')
        require(sum(clip['durations']) == clip['durationMs'] == composition['durationMs'] == TIMES[name],
                f'{name}: timeline length changed')
        require(len(clip['frames']) == len(clip['durations']) == len(composition['frames']),
                f'{name}: frame count mismatch')
        cursor, exposures, scales = 0, 0, set()
        for index, row in enumerate(composition['frames']):
            require(row['index'] == index and row['startMs'] == cursor
                    and row['endMs'] - row['startMs'] == clip['durations'][index], f'{name}: PNG timeline gap')
            path = ROOT / 'Clips' / name / clip['frames'][index]
            actual = image(path)
            require(actual.size == SIZE and set(np.unique(np.array(actual)[..., 3])) == {255},
                    f'{name}: non-native or non-opaque PNG')
            require(sha(path.read_bytes()) == row['pngSha256'] and sha(actual.tobytes()) == row['rgbaSha256'],
                    f'{name}: prepared PNG SHA mismatch')
            sub_cursor = row['startMs']
            for sub in row['subExposures']:
                require(sub['startMs'] == sub_cursor and sub['endMs'] > sub_cursor, f'{name}: subexposure gap')
                time = sub['startMs']
                if name != 'elevator-ascent':
                    world = cached[sub['sourceFrameKey']]
                    expected = camera(world, sub)
                    require(sub['sourceClockRestarted'] is False, 'Source animation clock restarted at cut')
                    if name == 'awakening':
                        shot = f'A{min(4, time // 2000 + 1)}'
                        require(sub['shotId'] == shot and sub['sourceFrameKey'].startswith('awakening/' + shot + '/'),
                                'Awakening shot/source order changed')
                        require(sub['cameraRect'] == (reg['awakeningDockCrop'] if shot == 'A1' else [0, 0, 640, 360]),
                                'Awakening camera contract changed')
                    else:
                        shot = 'C1' if time < 850 else 'C2' if time < 1800 else 'C3'
                        rect = reg['collapseMediumCrop'] if shot == 'C1' else reg['deadCoreCrop'] if shot == 'C2' else [0, 0, 640, 360]
                        require(sub['shotId'] == shot and sub['cameraRect'] == rect and sub['closedArena'] is True,
                                'Closed-arena collapse shot contract changed')
                elif time >= 6600:
                    require(sub['cutToBlack'] is True and sub['caption'] is None
                            and sub['destinationShown'] is False, 'Final black cut gained a destination/caption')
                    expected = Image.new('RGBA', SIZE, (0, 0, 0, 255))
                else:
                    shot = 'E1' if time < 1200 else 'E2' if time < 2200 else 'E3' if time < 4600 else 'E4'
                    require(sub['shotId'] == shot and sub['worldClockMs'] == time, 'Elevator shot/world-clock contract')
                    floor = round(floor_at(time, reg))
                    require(sub['floorY'] == floor and sub['sourceClockRestarted'] is False,
                            'Elevator quadratic world clock restarted or changed')
                    require(sub['destinationShown'] is False and sub['disembarking'] is False
                            and sub['caption'] is None, 'Elevator gained destination/disembarking/caption')
                    require(sub['background'] == 'Source/Native/shaft-no-destination.png', 'Wrong destination-free plate')
                    car, actor = sub['carriage'], sub['actor']
                    car_xy = [reg['carCenterX'] - reg['carriageFloorAnchor'][0], floor - reg['carriageFloorAnchor'][1]]
                    x = round(reg['boardingStartX'] + (reg['carCenterX'] - reg['boardingStartX']) * min(time / 760, 1))
                    require(car['xy'] == car_xy and car['anchor'] == reg['carriageFloorAnchor']
                            and car['scale'] == 1 and car['rigidTranslation'] is True, 'Carriage body transformed')
                    require(car['source'] == 'Source/Reused/Lift/Source/Native/open-lift-carriage.png', 'Carriage source changed')
                    require(actor['xy'] == [x - 32, floor - 56] and actor['foot'] == [x, floor]
                            and actor['anchor'] == [32, 56] and actor['scale'] == 1
                            and actor['flipped'] is False and actor['rotated'] is False, 'Tique body or floor contact changed')
                    require(actor['sourceFrameKey'] == pose_at(time), 'Tique walk/blink source clock changed')
                    require(time < 760 or x == reg['carCenterX'], 'Seated rider slid relative to carriage')
                    rect = (reg['boardingCrop'] if shot == 'E1' else reg['guideInsertCrop'] if shot == 'E2'
                            else [reg['riderTrackingX'], floor - reg['riderScreenFootLogical'], 160, 90] if shot == 'E3'
                            else [0, 0, 640, 360])
                    require(sub['cameraRect'] == rect and sub['intentionalExitClipping'] == (time >= 4600),
                            'Elevator camera or intentional wide exit clipping changed')
                    world = background.copy()
                    world.alpha_composite(carriage, tuple(car_xy))
                    world.alpha_composite(cached[actor['sourceFrameKey']], tuple(actor['xy']))
                    expected = camera(world, sub)
                require(actual.tobytes() == expected.tobytes(), f'{name}/{index}@{time}: whole-world camera RGBA replay failed')
                if 'cameraScale' in sub:
                    scales.add(sub['cameraScale'])
                exposures += 1
                all_subs.append((name, sub))
                sub_cursor = sub['endMs']
            require(sub_cursor == row['endMs'], f'{name}: merged subexposures do not cover PNG duration')
            cursor = row['endMs']
        require(cursor == TIMES[name], f'{name}: final timeline gap')
        results.append({'name': name, 'frameCount': len(clip['frames']), 'subExposureCount': exposures,
                        'durationMs': cursor, 'wholeWorldCameraReplayRgbaExact': True,
                        'cameraIntegerScales': sorted(scales), 'pngHashesExact': True, 'alpha255': True})
    cuts = []
    for time in (1200, 2200, 4600):
        require(abs(floor_at(time - 1e-7, reg) - floor_at(time + 1e-7, reg)) < 1e-6,
                'Quadratic world floor is discontinuous across camera cut')
        require(any(name == 'elevator-ascent' and sub['startMs'] == time for name, sub in all_subs),
                'Camera boundary omitted from source exposures')
        cuts.append({'timeMs': time, 'continuousFloorY': floor_at(time, reg), 'roundedFloorY': round(floor_at(time, reg))})
    selections = [('awakening', 1060, 'A1 / 도킹 전신'), ('awakening', 3000, 'A2 / 릴레이 인서트'),
                  ('awakening', 5000, 'A3 / 문지기 노심'), ('awakening', 7200, 'A4 / 전투 공간'),
                  ('guardian-collapse', 520, 'C1 / 붕괴 미디엄'), ('guardian-collapse', 1200, 'C2 / 꺼진 노심'),
                  ('guardian-collapse', 2400, 'C3 / 정적 와이드'), ('elevator-ascent', 760, 'E1 / 탑승 미디엄'),
                  ('elevator-ascent', 1800, 'E2 / 레일 인서트'), ('elevator-ascent', 3400, 'E3 / 티크 트래킹'),
                  ('elevator-ascent', 5000, 'E4 / 상승 와이드'), ('elevator-ascent', 6600, 'E4 / 암전')]
    board = Image.new('RGB', (640 * 3, (360 + 26) * 4), (12, 17, 24))
    draw = ImageDraw.Draw(board)
    draw.fontmode = '1'
    font = ImageFont.truetype(str(FONT), 16)
    board_records = []
    clips_by_name = {clip['name']: clip for clip in plan['clips']}
    for cell, (name, time, label) in enumerate(selections):
        row = next(row for row in compositions[name]['frames'] if row['startMs'] <= time < row['endMs'])
        frame_path = ROOT / 'Clips' / name / clips_by_name[name]['frames'][row['index']]
        col, grid_row = cell % 3, cell // 3
        x, y = col * 640, grid_row * 386
        board.paste(image(frame_path).convert('RGB'), (x, y))
        draw.text((x + 8, y + 365), f'{label} · {time / 1000:.3f}s', font=font, fill=(231, 224, 207))
        board_records.append({'cell': [col, grid_row], 'clip': name, 'timeMs': time,
                              'frameIndex': row['index'], 'pngSha256': sha(frame_path.read_bytes()), 'label': label})
    buffer = io.BytesIO()
    board.save(buffer, format='PNG')
    board_bytes = buffer.getvalue()
    require(all(sha(path.read_bytes()) == digest for path, digest in protected.items()), 'Source/Clips changed during check')
    save(ROOT / 'QA/shot-board.png', board_bytes)
    validation = {'passed': True, 'revision': 'cinematic-edit-v4',
        'scope': 'Independent source/archive hashes, generated-to-native replay, all prepared PNGs and every merged subexposure whole-world/camera replay. Semantic room absence follows main visual inspection; this is not human art/motion approval or runtime capture.',
        'scriptPath': Path(__file__).relative_to(REPO).as_posix(), 'scriptSha256': sha(Path(__file__).read_bytes()),
        'readOnlyNativeHelperSha256': sha(Path(pixel.__file__).read_bytes()),
        'sourceFileHashes': {path.relative_to(ROOT).as_posix(): digest for path, digest in protected.items() if path.is_relative_to(ROOT / 'Source')},
        'native': native_result, 'reusedOriginalBytesExact': True,
        'clips': results, 'quadraticWorldFloorContinuousAcrossCuts': cuts,
        'carriageAndRiderRigidWorldTranslation': True, 'noDestinationDisembarkCaptionLayers': True,
        'intentionalWideExitClippingFromMs': 4600, 'cutToBlackMs': 6600,
        'sourceAndPreparedPngsUnchanged': True, 'independentClips': True, 'concatenatedSequenceCreated': False,
        'shotBoard': {'path': 'QA/shot-board.png', 'sha256': sha(board_bytes), 'size': list(board.size),
                      'fontPath': FONT.relative_to(REPO).as_posix(), 'fontSha256': sha(FONT.read_bytes()),
                      'fontSize': 16, 'fontMode': '1', 'cells': board_records},
        'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending', 'runtimeIntegrated': False,
        'runtimeCapture': False, 'gameLaunched': False, 'unityFilesWritten': False}
    save(ROOT / 'QA/composition-validation.json', (json.dumps(validation, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps({'passed': True, 'clips': results, 'shotBoard': 'QA/shot-board.png',
                      'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False}))


if __name__ == '__main__':
    main()
