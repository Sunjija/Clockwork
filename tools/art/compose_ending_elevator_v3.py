"""Image-first native derivation and two independent offline ending clips.

New lift designs come ONLY from actual inspected imagegen originals. Whole
object sampling/palette mapping is deterministic, not replacement painting.
Unchanged Tique/Warden frames are archived byte-for-byte and translated only.
No Unity writes, runtime launch, combined movie, or video codec work.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse
import hashlib
import io
import json
import math
import numpy as np

import derive_pixel_cinematics_v1 as native_pipeline

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-ending-elevator-v3'
OLD = REPO / 'art/return-pixel-cinematics-v1'
V2 = REPO / 'art/return-pixel-cinematics-v2-full'
GAME = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2'
GENERATED = {
    'shaft-workshop-plate': Path('/Users/daddung/.codex/generated_images/01a0a331-bd2c-78d0-996e-0b8f1f55dce7/exec-39db7a25-fa3e-4a3f-bafd-39c26e506ea5.png'),
    'open-lift-carriage': Path('/Users/daddung/.codex/generated_images/01a0a331-bd2c-78d0-996e-0b8f1f55dce7/exec-80470861-4bba-40c5-9f0b-632647ac1dca.png'),
}
WALK_TIMES = [60, 40, 80, 60, 40, 40, 60, 100, 40, 60, 60, 40, 40, 40]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def save(path, data):
    require(path.resolve().is_relative_to(ROOT.resolve()), 'Output escapes new candidate')
    require(not path.is_symlink(), 'Refusing symlink output')
    if path.exists():
        require(path.read_bytes() == data, 'Preserving different existing file: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def json_save(path, data):
    save(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def png_save(path, image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    save(path, buffer.getvalue())


def archive(path, relative):
    data = path.read_bytes()
    target = ROOT / relative
    save(target, data)
    return {'sourcePath': str(path), 'sourceSha256': sha(data),
            'projectCopy': relative, 'copySha256': sha(target.read_bytes())}


def derivation():
    requests = json.loads((ROOT / 'Source/requests.json').read_text())
    selected = {}
    for request in requests['requests']:
        name = request['name']
        selected[name] = archive(GENERATED[name], 'Source/Generated/' + name + '.png')
        selected[name]['args'] = request['args']
        selected[name]['references'] = []
        for index, ref in enumerate(request['args'].get('referenced_image_paths', [])):
            record = archive(Path(ref), f'Source/References/{name}-{index}.png')
            selected[name]['references'].append(record)
    provenance = {'revision': 'ending-elevator-v3', 'builtInMode': True,
                  'inspectedByMain': True, 'shownToUser': True,
                  'selectedSources': selected, 'requests': 'Source/requests.json',
                  'requestsSha256': sha((ROOT / 'Source/requests.json').read_bytes()),
                  'humanAppearanceApproval': 'pending', 'runtimeIntegrated': False,
                  'unityFilesWritten': False, 'gameLaunched': False}
    json_save(ROOT / 'Source/provenance.json', provenance)
    palette_record = archive(OLD / 'Source/Native/palette.json', 'Source/Native/palette.json')
    palette = np.array(json.loads((ROOT / palette_record['projectCopy']).read_text())['colors'], np.uint8)
    records = {}
    for name in GENERATED:
        source = ROOT / selected[name]['projectCopy']
        image = Image.open(source).convert('RGBA')
        if name == 'shaft-workshop-plate':
            sampled, geometry = native_pipeline.sample(source)
            rgb, indices = native_pipeline.map_rgb(np.array(sampled)[..., :3], palette)
            logical = native_pipeline.native(rgb)
        else:
            alpha = np.array(image)[..., 3]
            ys, xs = np.where(alpha >= 128)
            require(len(xs) > 0, 'Generated carriage has no opaque object')
            bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
            crop = image.crop(bbox)
            sample_size = (52, max(1, round(crop.height * 52 / crop.width)))
            require(sample_size[1] <= 60, 'Carriage cannot fit logical64 without distortion')
            sampled = crop.convert('RGBa').resize(sample_size, Image.Resampling.BOX).convert('RGBA')
            a = np.array(sampled)
            visible = a[..., 3] >= 128
            rgb, local_indices = native_pipeline.map_rgb(a[..., :3], palette)
            rgba = np.zeros((*visible.shape, 4), np.uint8)
            rgba[visible, :3] = rgb[visible]
            rgba[visible, 3] = 255
            offset = ((64 - sample_size[0]) // 2, (64 - sample_size[1]) // 2)
            logical = Image.new('RGBA', (64, 64))
            logical.paste(Image.fromarray(rgba, 'RGBA'), offset)
            indices = np.full((64, 64), -1, np.int32)
            ox, oy = offset
            indices[oy:oy + sample_size[1], ox:ox + sample_size[0]] = np.where(visible, local_indices, -1)
            opening = np.array(logical)[12:40, 16:48, 3]
            require(float(np.mean(opening == 0)) > .80, 'Generated lift interior is not sufficiently alpha-open')
            geometry = {'generatedDimensions': list(image.size), 'sourceRect': list(bbox),
                        'alphaBBoxThreshold': 128, 'sampleSize': list(sample_size),
                        'paddingOffsetLogical': list(offset),
                        'sourceStep': [crop.width / 52, crop.height / sample_size[1]],
                        'wholeObjectUniformScale': 52 / crop.width,
                        'heightRoundingPixels': sample_size[1] - crop.height * 52 / crop.width,
                        'binaryAlphaThreshold': 128, 'clearInteriorFraction': float(np.mean(opening == 0)),
                        'geometryWarped': False, 'bodyPartScaling': False}
        native = logical.resize((logical.width * 2, logical.height * 2), Image.Resampling.NEAREST)
        logical_path = ROOT / f'Source/Native/{name}-logical.png'
        native_path = ROOT / f'Source/Native/{name}.png'
        png_save(logical_path, logical)
        png_save(native_path, native)
        mapping = {**geometry, 'source': selected[name]['projectCopy'],
                   'sourceSha256': selected[name]['sourceSha256'], 'logicalSize': list(logical.size),
                   'nativeSize': list(native.size), 'integerScale': 2,
                   'paletteSha256': sha((ROOT / palette_record['projectCopy']).read_bytes()),
                   'paletteIndices': indices.astype(int).tolist(), 'transparentIndex': -1,
                   'cleanupEdits': [], 'silhouettePainted': False,
                   'formula': 'Premultiplied BOX whole source/object samples; fixed existing palette; binary alpha for cutout; exactly2x2 native blocks.'}
        map_path = ROOT / f'Source/Derivation/{name}-pixel-map.json'
        json_save(map_path, mapping)
        records[name] = {**geometry, 'source': selected[name]['projectCopy'],
                         'sourceSha256': selected[name]['sourceSha256'],
                         'logicalOutput': logical_path.relative_to(ROOT).as_posix(),
                         'logicalSha256': sha(logical_path.read_bytes()),
                         'output': native_path.relative_to(ROOT).as_posix(),
                         'outputSha256': sha(native_path.read_bytes()),
                         'pixelMap': map_path.relative_to(ROOT).as_posix(),
                         'pixelMapSha256': sha(map_path.read_bytes()), 'integerScale': 2}
    json_save(ROOT / 'Source/Derivation/native-derivation.json', {
        'inspectedByMain': True, 'humanAppearanceApproval': 'pending',
        'scriptSha256': sha(Path(__file__).read_bytes()),
        'readOnlyHelper': {'path': 'tools/art/derive_pixel_cinematics_v1.py',
                          'sha256': sha(Path(native_pipeline.__file__).read_bytes())},
        'reusedFixedPalette': palette_record, 'assets': records,
        'newDesignsCodePainted': False, 'unityFilesWritten': False})


def compose():
    registration_path = ROOT / 'Source/registration.json'
    registration = json.loads(registration_path.read_text())
    require(registration['nativeInspectedByMain'] is True, 'Inspect native lift floor first')
    sources = {}

    def reuse(key, path):
        if key not in sources:
            record = archive(path, 'Source/Reused/' + key + '.png')
            image = Image.open(ROOT / record['projectCopy']).convert('RGBA')
            require(set(np.unique(np.array(image)[..., 3])) <= {0, 255}, 'Reused alpha must be binary')
            sources[key] = {**record, 'size': list(image.size), 'rgbaSha256': sha(image.tobytes())}
        return Image.open(ROOT / sources[key]['projectCopy']).convert('RGBA')

    arena = reuse('arena-closed', V2 / 'Source/Native/arena-plate.png')
    lift_bg = Image.open(ROOT / 'Source/Native/shaft-workshop-plate.png').convert('RGBA')
    lift_car = Image.open(ROOT / 'Source/Native/open-lift-carriage.png').convert('RGBA')
    font_record = archive(REPO / 'art/return-v5-feedback/Source/Font/neodgm.ttf', 'Source/Reused/neodgm.ttf')
    font = ImageFont.truetype(str(ROOT / font_record['projectCopy']), 16)
    font_mode = '1'

    def actor(canvas, key, path, foot, anchor):
        image = reuse(key, path)
        xy = (int(foot[0] - anchor[0]), int(foot[1] - anchor[1]))
        require(0 <= xy[0] and xy[0] + image.width <= 640 and 0 <= xy[1] and xy[1] + image.height <= 360,
                'Actor would be clipped')
        canvas.alpha_composite(image, xy)
        return {'sourceKey': key, 'xy': list(xy), 'foot': list(foot), 'anchor': list(anchor),
                'scale': 1, 'flipped': False, 'rotated': False,
                'sourceSha256': sources[key]['sourceSha256']}

    def tique(canvas, kind, index, foot):
        return actor(canvas, f'tique/{kind}/{index:02}', GAME / f'TiqueV10/{kind}/{index:02}.png', foot, (32, 56))

    def frame_write(name, exposures):
        frames, durations, rows = [], [], []
        previous = None
        for image, start, end, description in exposures:
            require(end > start and image.size == (640, 360), 'Invalid exposure')
            rgba = image.tobytes()
            if previous == rgba:
                durations[-1] += end - start
                rows[-1]['endMs'] = end
                rows[-1]['subExposures'].append({'startMs': start, 'endMs': end, **description})
            else:
                number = len(frames)
                path = ROOT / f'Clips/{name}/{number:02}.png'
                png_save(path, image)
                frames.append(path.name)
                durations.append(end - start)
                rows.append({'index': number, 'startMs': start, 'endMs': end,
                             'pngSha256': sha(path.read_bytes()), 'rgbaSha256': sha(rgba),
                             'subExposures': [{'startMs': start, 'endMs': end, **description}]})
                previous = rgba
        json_save(ROOT / f'Source/Composition/{name}.json', {'clip': name, 'exposures': rows,
                  'durationMs': sum(durations), 'pixelTranslationOnly': True,
                  'humanMotionApproval': 'pending', 'runtimeCapture': False})
        return {'name': name, 'width': 640, 'height': 360, 'durationMs': sum(durations),
                'durations': durations, 'frames': frames, 'sourceInfo': {
                    'composition': f'Source/Composition/{name}.json',
                    'compositionSha256': sha((ROOT / f'Source/Composition/{name}.json').read_bytes()),
                    'registrationSha256': sha(registration_path.read_bytes()),
                    'actorFramesUnchanged': True, 'nativeScale': 1,
                    'newGeneratedLiftAssets': name == 'elevator-homecoming'}}

    collapse = []
    cursor = 0
    for kind, index, ms in [('idle', 0, 300)] + [('defeat', i, 110) for i in range(5)] + [('defeat', 5, 2150)]:
        image = arena.copy()
        actors = [tique(image, 'Idle', 0, (158, 282)),
                  actor(image, f'warden/{kind}/{index:02}', GAME / f'WardenV8/{kind}/{index:02}.png', (450, 282), (96, 164))]
        collapse.append((image, cursor, cursor + ms, {'phase': 'standing' if kind == 'idle' else 'collapse',
                         'backgroundKey': 'arena-closed', 'doorClosed': True, 'actors': actors}))
        cursor += ms
    clips = [frame_write('guardian-collapse', collapse)]
    require(cursor == 3000, 'Collapse duration')

    def walk_index(elapsed):
        cursor = 0
        for index, duration in enumerate(WALK_TIMES):
            cursor += duration
            if elapsed < cursor:
                return index
        return len(WALK_TIMES) - 1

    boundaries = set(range(0, 5001, 40)) | {0, 760, 1200, 2200, 2280, 2380, 2460, 3800, 4200, 4960, 5000, 6000, 7000}
    for offset in (0, 4200):
        cursor = offset
        for ms in WALK_TIMES:
            cursor += ms
            boundaries.add(cursor)
    # Existing workshop-wide last2seconds, preserving its original frame clock.
    for index in range(16):
        time = 5000 + index * 160 - 1000
        if 5000 < time < 7000:
            boundaries.add(time)
    times = sorted(t for t in boundaries if 0 <= t <= 7000)
    exposures = []
    lower, upper = registration['lowerFloorY'], registration['upperFloorY']
    center = registration['carCenterX']
    anchor = registration['carriageFloorAnchor']
    for start, end in zip(times, times[1:]):
        if start < 5000:
            progress = min(1, max(0, (start - 1200) / 2600))
            ease = progress * progress * (3 - 2 * progress)
            floor = int(round(lower + (upper - lower) * ease))
            xy = [center - anchor[0], floor - anchor[1]]
            image = lift_bg.copy()
            image.alpha_composite(lift_car, xy)
            if start < 760:
                phase, kind, index = 'boarding', 'Walk', walk_index(start)
                x = round(registration['boardingStartX'] + (center - registration['boardingStartX']) * start / 760)
            elif start < 4200:
                phase = 'boarded-hold' if start < 1200 else 'ascent' if start < 3800 else 'arrival-hold'
                kind, index, x = 'Idle', 0, center
                if 2200 <= start < 2280 or 2380 <= start < 2460:
                    kind = 'blink-half'
                elif 2280 <= start < 2380:
                    kind = 'blink-closed'
            elif start < 4960:
                phase, kind, index = 'disembarking', 'Walk', walk_index(start - 4200)
                x = round(center + (registration['landingEndX'] - center) * (start - 4200) / 760)
            else:
                phase, kind, index, x = 'workshop-landing', 'Idle', 0, registration['landingEndX']
            actor_record = tique(image, kind, index, (x, floor))
            description = {'phase': phase, 'background': 'Source/Native/shaft-workshop-plate.png',
                           'carriage': {'source': 'Source/Native/open-lift-carriage.png', 'xy': xy,
                                        'floorY': floor, 'anchor': anchor, 'scale': 1,
                                        'rigidTranslation': True}, 'actors': [actor_record]}
        else:
            workshop_elapsed = start - 5000 + 1000
            index = min(15, workshop_elapsed // 160)
            image = reuse(f'workshop-wide/{index:02}', OLD / f'Clips/workshop-wide/{index:02}.png')
            actor_record = tique(image, 'Idle', 0, registration['workshopTiqueFoot'])
            description = {'phase': 'workshop-final', 'backgroundKey': f'workshop-wide/{index:02}',
                           'workshopSourceTimeMs': workshop_elapsed, 'actors': [actor_record],
                           'captionVisible': start >= 6000}
            if start >= 6000:
                caption = '돌아갈 곳이 있어.'
                mask = Image.new('1', (640, 360))
                draw = ImageDraw.Draw(mask)
                draw.fontmode = font_mode
                x = round((640 - draw.textlength(caption, font=font)) / 2)
                draw.text((x, 326), caption, font=font, fill=1)
                image.paste((217, 228, 225, 255), mask=mask)
                description['caption'] = {'text': caption, 'fontSize': 16, 'fontSha256': font_record['sourceSha256'],
                                          'fontmode': '1', 'maskSha256': sha(mask.tobytes()), 'nativeTextNotGenerated': True}
        exposures.append((image, start, end, description))
    clips.append(frame_write('elevator-homecoming', exposures))
    require(clips[1]['durationMs'] == 7000, 'Elevator duration')
    json_save(ROOT / 'Source/reused-assets.json', {'sources': sources, 'font': font_record,
        'actorPaletteRemapped': False, 'actorScaling': False, 'humanFinalApproval': 'pending',
        'oldSourceProvenance': [archive(V2 / 'Source/provenance.json', 'Source/Reused/v2-provenance.json'),
                                archive(OLD / 'Source/provenance.json', 'Source/Reused/v1-provenance.json')]})
    json_save(ROOT / 'Clips/clip-plan.json', {'revision': 'ending-elevator-v3', 'clips': clips,
        'independentClips': True, 'sequences': [], 'runtimeIntegrated': False})
    json_save(ROOT / 'Source/Composition/authoring.json', {'scriptSha256': sha(Path(__file__).read_bytes()),
        'registrationSha256': sha(registration_path.read_bytes()), 'humanAppearanceApproval': 'pending',
        'humanMotionApproval': 'pending', 'newDesignsFromActualImagegen': True,
        'oldPackagesModified': False, 'unityFilesWritten': False, 'gameLaunched': False})
    print(json.dumps({'clips': [{ 'name': c['name'], 'frames': len(c['frames']), 'durationMs': c['durationMs']} for c in clips]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', required=True, action='store_true')
    parser.add_argument('--derive-only', action='store_true')
    args = parser.parse_args()
    require(args.inspected_anchors, 'Inspect/show actual generated sources first')
    derivation()
    if not args.derive_only:
        compose()
    else:
        print('Derived2 native image-first candidates; inspect carriage floor before registration/composition.')


if __name__ == '__main__':
    main()
