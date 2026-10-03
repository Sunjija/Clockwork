"""Image-first native derivation + unchanged game-sprite composition, offline only.

Generated backgrounds are new candidates, not byte-exact runtime-map captures.
Actual Tique/guardian/prop frame RGBA and registration are reused unmodified.
No Unity/game writes, launches, AI video or replacement character drawing.
"""
from pathlib import Path
import argparse
import io
import json
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from derive_pixel_cinematics_v1 import sample, map_rgb, native

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-pixel-cinematics-v2-full'
OLD = REPO / 'art/return-pixel-cinematics-v1'
RES = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2'
GEN = Path('/Users/daddung/.codex/generated_images/01a0a331-bd2c-78d0-996e-0b8f1f55dce7')
GENERATED = {
    'puzzle-plate': GEN / 'exec-619fe604-1040-4fa3-97e5-a5f57a3dec28.png',
    'arena-plate': GEN / 'exec-9888646f-a8b8-449d-9be9-22996a394ea3.png',
    'exit-rejected-layout': GEN / 'exec-6331da05-3b35-4e8c-83a5-8976316dc854.png',
    'exit-open-edit': GEN / 'exec-e4bfaf25-8146-4db5-806a-6089fb5a3c43.png',
}
DOOR_RECT = (578, 190, 638, 284)
USED = {}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    assert path.resolve().is_relative_to(ROOT.resolve())
    if path.exists():
        assert path.read_bytes() == data, f'Preserving different existing candidate: {path}'
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def jsave(path, data):
    save(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())


def pngsave(path, image):
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    save(path, buf.getvalue())


def archive_source(original, relative):
    data = original.read_bytes()
    target = ROOT / relative
    save(target, data)
    return {'original': str(original), 'projectCopy': relative, 'sha256': sha(data)}


def derive():
    sources = {name: archive_source(path, f'Source/Generated/{name}.png')
               for name, path in GENERATED.items()}
    previous = {}
    for name in ('relay', 'warden-core', 'workshop', 'workshop-initial'):
        previous[name] = archive_source(OLD / f'Source/Generated/{name}.png', f'Source/Generated/v1-{name}.png')
    archive_source(OLD / 'Source/provenance.json', 'Source/v1-provenance.json')
    archive_source(OLD / 'Source/requests.json', 'Source/v1-requests.json')
    palette_record = archive_source(OLD / 'Source/Native/palette.json', 'Source/Native/palette.json')
    palette = np.array(json.loads((ROOT / 'Source/Native/palette.json').read_text())['colors'], dtype=np.uint8)
    requests = []
    for name in ('requests.json', 'exit-edit-request.json'):
        data = json.loads((ROOT / 'Source' / name).read_text())
        entries = data.get('requests', [{'args': data}])
        for entry in entries:
            row = dict(entry)
            row['referenceSha256'] = {path: sha(Path(path).read_bytes()) for path in entry['args']['referenced_image_paths']}
            requests.append(row)
    jsave(ROOT / 'Source/provenance.json', {
        'revision': 'full-eight-cut-v2', 'inspectedByMain': True, 'shownToUser': True,
        'humanAppearanceApproval': 'pending', 'newImagegenOutputs': sources,
        'selectedBackgrounds': ['puzzle-plate', 'arena-plate', 'exit-open-edit'],
        'rejectedBackground': {'name': 'exit-rejected-layout', 'reason': 'Floor/door moved; preserved, never used in native frames.'},
        'reusedGeneratedOriginals': previous, 'requests': requests,
        'previousPipeline': 'Unchanged generated v1 anchors, native frames and animation are reused by source hash.',
        'runtimeCapture': False, 'unityFilesWritten': False, 'gameLaunched': False,
        'backgroundStatus': 'New generated storyboard candidates referencing game maps; not exact runtime-map replacements or integrated game captures.',
    })
    backgrounds = {}
    records = {}
    for name in ('puzzle-plate', 'arena-plate', 'exit-open-edit'):
        source = ROOT / sources[name]['projectCopy']
        sampled, record = sample(source)
        rgb, indices = map_rgb(np.array(sampled)[..., :3], palette)
        logical = native(rgb)
        full = logical.resize((640, 360), Image.Resampling.NEAREST)
        pngsave(ROOT / f'Source/Native/{name}-logical.png', logical)
        pngsave(ROOT / f'Source/Native/{name}.png', full)
        jsave(ROOT / f'Source/Derivation/{name}-pixel-map.json', {
            **record, 'sourceSha256': sources[name]['sha256'], 'paletteSha256': palette_record['sha256'],
            'sampleSize': [320, 180], 'nativeSize': [640, 360], 'integerScale': 2,
            'paletteIndices': indices.astype(int).tolist(), 'silhouettePainted': False,
        })
        backgrounds[name] = full
        records[name] = {**record, 'source': sources[name], 'rgbaSha256': sha(full.tobytes())}
    # Local generated edit ONLY: outside the doorway every native arena pixel is identical.
    opened = backgrounds['arena-plate'].copy()
    opened.paste(backgrounds['exit-open-edit'].crop(DOOR_RECT), DOOR_RECT[:2])
    pngsave(ROOT / 'Source/Native/arena-door-open.png', opened)
    a, b = np.array(opened), np.array(backgrounds['arena-plate'])
    mask = np.ones((360, 640), dtype=bool)
    x0, y0, x1, y1 = DOOR_RECT
    mask[y0:y1, x0:x1] = False
    assert np.array_equal(a[mask], b[mask])
    records['arena-door-open'] = {'base': 'arena-plate', 'generatedEdit': 'exit-open-edit',
        'nativeCropRect': list(DOOR_RECT), 'outsideCropRgbaExact': True, 'geometryWarped': False}
    jsave(ROOT / 'Source/Derivation/native-derivation.json', {
        'inspectedByMain': True, 'scriptSha256': sha(Path(__file__).read_bytes()),
        'samplerScriptSha256': sha((REPO / 'tools/art/derive_pixel_cinematics_v1.py').read_bytes()),
        'assets': records, 'bodyPartScaling': False, 'handPaintedNewBackgrounds': False,
    })
    return backgrounds['puzzle-plate'], backgrounds['arena-plate'], opened


def sprite(group, clip, frame):
    path = RES / group / clip / f'{frame:02}.png'
    key = path.relative_to(RES).as_posix()
    if key not in USED:
        USED[key] = archive_source(path, 'Source/Reused/' + key)
    image = Image.open(ROOT / USED[key]['projectCopy']).convert('RGBA')
    assert set(image.getchannel('A').getdata()) <= {0, 255}, key
    return image, key


def place(canvas, group, clip, frame, position, anchor):
    image, key = sprite(group, clip, frame)
    xy = (int(position[0] - anchor[0]), int(position[1] - anchor[1]))
    canvas.alpha_composite(image, xy)
    return {'source': key, 'sourceSha256': USED[key]['sha256'], 'xy': list(xy),
            'size': list(image.size), 'anchor': list(anchor), 'scale': 1, 'flip': False,
            'rgbaSha256': sha(image.tobytes()), 'bodyPartsRedrawn': False}


def prop(canvas, clip, frame, center):
    image, key = sprite('ReadabilityArtV2', clip, frame)
    return place(canvas, 'ReadabilityArtV2', clip, frame, center, (image.width // 2, image.height // 2))


def timings(group, clip):
    path = RES / group / 'clips.json'
    return next(c['durations'] for c in json.loads(path.read_text())['clips'] if c['name'] == clip)


def pose_at(ms, durations, loop=True):
    if loop:
        ms %= sum(durations)
    for index, duration in enumerate(durations):
        if ms < duration:
            return index
        ms -= duration
    return len(durations) - 1


def boundaries(durations, start=0):
    result = [start]
    for ms in durations:
        start += ms
        result.append(start)
    return result


FONT_PATH = REPO / 'art/return-v5-feedback/Source/Font/neodgm.ttf'
FONT = ImageFont.truetype(str(FONT_PATH), 16)


def caption(image, text):
    draw = ImageDraw.Draw(image)
    draw.fontmode = '1'
    box = draw.textbbox((0, 0), text, font=FONT)
    width = box[2] - box[0]
    x, y = (640 - width) // 2, 326
    # Existing pixel-font UI layer, not generated lettering or a new prop.
    draw.rectangle((x - 10, 322, x + width + 10, 346), fill=(12, 18, 28, 255))
    draw.text((x, y - box[1]), text, font=FONT, fill=(231, 207, 146, 255))
    return {'text': text, 'font': str(FONT_PATH), 'fontSha256': sha(FONT_PATH.read_bytes()),
            'sizeNative': 16, 'fontmode': '1', 'generatedLettering': False}


def compose_shot(name, duration, cuts, render, source_info):
    cuts = sorted(set(cuts + [0, duration]))
    cuts = [t for t in cuts if 0 <= t <= duration]
    frames, durations, metadata = [], [], []
    for begin, end in zip(cuts, cuts[1:]):
        image, record = render(begin)
        assert image.size == (640, 360)
        assert set(image.getchannel('A').getdata()) == {255}
        # Hold exposures merge only if exact RGBA is identical.
        if frames and frames[-1].tobytes() == image.tobytes():
            durations[-1] += end - begin
            metadata[-1]['durationMs'] += end - begin
            metadata[-1]['subexposures'].append({'timeMs': begin, 'durationMs': end - begin, **record})
        else:
            frames.append(image)
            durations.append(end - begin)
            metadata.append({'timeMs': begin, 'durationMs': end - begin, 'subexposures': [record]})
    for index, image in enumerate(frames):
        pngsave(ROOT / f'Clips/{name}/{index:02}.png', image)
        metadata[index]['rgbaSha256'] = sha(image.tobytes())
    jsave(ROOT / f'Clips/{name}/composition.json', {'shot': name, 'frames': metadata, 'sourceInfo': source_info})
    return {'name': name, 'durationMs': duration, 'durations': durations,
            'width': 640, 'height': 360, 'frames': [f'{i:02}.png' for i in range(len(frames))],
            'sourceInfo': source_info}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inspected-anchors', action='store_true', required=True)
    assert parser.parse_args().inspected_anchors
    puzzle, arena, opened = derive()
    clips = []
    push = timings('TiqueV10', 'push-side')
    moving = timings('ReadabilityArtV2', 'battery-moving')
    connect = timings('ReadabilityArtV2', 'amber-slot-connect')
    walk = timings('TiqueV10', 'Walk')
    boot = timings('WardenV8', 'boot')
    defeat = timings('WardenV8', 'defeat')
    assert sum(push) == 760 and sum(walk) == 760 and sum(connect) == 460
    assert sum(boot) == 2400 and sum(defeat) == 1550

    def a1(t):
        out = puzzle.copy()
        layers = [prop(out, 'cyan-slot-filled', 0, (249, 155)), prop(out, 'orb-docked', 0, (249, 155)),
                  prop(out, 'amber-slot-filled', 0, (249, 227)), prop(out, 'battery-docked', 0, (249, 227))]
        socket_clip = 'amber-slot-empty' if t < 760 else ('amber-slot-connect' if t < 1220 else 'amber-slot-filled')
        sf = pose_at(t - 760, connect, False) if 760 <= t < 1220 else 0
        layers.append(prop(out, socket_clip, sf, (393, 263)))
        x = 357 + round(36 * min(t, 760) / 760)
        layers.append(prop(out, 'battery-moving' if t < 760 else 'battery-docked', pose_at(t, moving) if t < 760 else 0, (x, 263)))
        layers.append(place(out, 'TiqueV10', 'push-side' if t < 760 else 'Idle', pose_at(t, push) if t < 760 else 0, (x - 37, 279), (32, 56)))
        return out, {'background': 'puzzle-plate', 'layers': layers}
    # Keep the original battery-moving exposure boundaries as well as Tique and
    # socket timing. Some intersections are5ms; native APNG is authoritative.
    moving_cuts = [time for cycle in (0, sum(moving))
                   for time in boundaries(moving, cycle) if time <= 760]
    a1_cuts = list(range(0, 760, 40)) + boundaries(push) + moving_cuts + boundaries(connect, 760) + [1220]
    clips.append(compose_shot('A1', 2000, a1_cuts, a1, {
        'action': 'Last brass handled weight docks; cyan round orb and gray connected grid remain readable.',
        'background': 'Generated game-referenced fixed-grid candidate, not exact runtime map.',
        'motion': 'Rigid36-native-pixel translation over760ms; original push, moving and connect exposures.',
        'spriteScaling': False, 'timingIsRuntimeCapture': False}))

    old_plan = json.loads((OLD / 'Exports/clips.json').read_text())['clips']
    for name, original in [('A2', 'relay-power'), ('A3', 'warden-boot'), ('B3', 'workshop-wide'), ('B4', 'workshop-close')]:
        spec = next(c for c in old_plan if c['name'] == original)
        times = spec['durations']
        start = 0
        records = []
        for i, duration in enumerate(times):
            path = OLD / f'Clips/{original}/{i:02}.png'
            image = Image.open(path).convert('RGBA')
            meta = {'source': str(path), 'sourcePngSha256': sha(path.read_bytes()), 'timeMs': start, 'durationMs': duration}
            if name == 'B4' and start >= 1600:
                meta['caption'] = caption(image, '돌아갈 곳이 있어.')
                pngsave(ROOT / f'Clips/{name}/{i:02}.png', image)
                meta['reusedRgbaUnchangedOutsideCaption'] = True
            else:
                save(ROOT / f'Clips/{name}/{i:02}.png', path.read_bytes())
                meta['reusedPngByteExact'] = True
            meta['rgbaSha256'] = sha(image.tobytes())
            records.append(meta)
            start += duration
        info = {'priorClip': original, 'priorGeneratedSource': 'Source/v1-provenance.json',
                'originalFrameTimingPreserved': True, 'newPropsAuthored': False,
                'captionOnsetMs': 1600 if name == 'B4' else None}
        jsave(ROOT / f'Clips/{name}/composition.json', {'frames': records, 'sourceInfo': info})
        clips.append({'name': name, 'durationMs': sum(times), 'durations': times, 'width': 640, 'height': 360,
                      'frames': [f'{i:02}.png' for i in range(len(times))], 'sourceInfo': info})

    def a4(t):
        out = arena.copy()
        layers = [place(out, 'WardenV8', 'boot', pose_at(t + 400, boot, False), (450, 282), (96, 164)),
                  place(out, 'TiqueV10', 'Idle', 0, (158, 282), (32, 56))]
        record = {'background': 'arena-plate', 'layers': layers}
        if t >= 600:
            record['caption'] = caption(out, '폐기 대상 감지')
        return out, record
    clips.append(compose_shot('A4', 2000, [x - 400 for x in boundaries(boot)] + [600], a4, {
        'action': 'Current guardian boot t400..2400; current Tique left/guardian right; threat subtitle.',
        'bootDeadHoldOmittedMs': 400, 'originalPoseTimingAfterOmission': True,
        'registration': {'Tique': [32, 56], 'Warden': [96, 164], 'floorY': 282},
        'background': 'arena-plate', 'runtimeCapture': False, 'spriteScaling': False}))

    def b1(t):
        out = (arena if t < 550 else opened).copy()
        layers = [place(out, 'WardenV8', 'defeat', pose_at(t, defeat, False), (450, 282), (96, 164)),
                  place(out, 'TiqueV10', 'Idle', 0, (158, 282), (32, 56))]
        return out, {'background': 'arena-plate' if t < 550 else 'arena-door-open', 'layers': layers}
    clips.append(compose_shot('B1', 2000, boundaries(defeat) + [550], b1, {
        'action': 'Current defeat once; final crouch/core-off held1450ms; door opens.',
        'loop': False, 'finalPose': 'WardenV8/defeat/05.png', 'floorY': 282, 'spriteScaling': False}))

    def b2(t):
        out = opened.copy()
        x = 158 + round(438 * min(t, 1520) / 1520)
        layers = [place(out, 'WardenV8', 'defeat', 5, (450, 282), (96, 164)),
                  place(out, 'TiqueV10', 'Walk' if t < 1520 else 'Idle', pose_at(t, walk) if t < 1520 else 0, (x, 282), (32, 56))]
        return out, {'background': 'arena-door-open', 'layers': layers}
    b2_cuts = list(range(0, 1520, 40)) + boundaries(walk) + boundaries(walk, 760) + [1520]
    clips.append(compose_shot('B2', 2000, b2_cuts, b2, {
        'action': 'Current Walk two760ms cycles to warm door; idle last480ms.',
        'previewAutoMoveOnly': True, 'runtimeMustWaitForPlayerDoorInteraction': True,
        'floorY': 282, 'spriteScaling': False, 'originalWalkPoseTiming': True}))
    clips.sort(key=lambda c: c['name'])
    jsave(ROOT / 'Source/reused-sprites.json', {'assets': USED, 'spriteFrameRgbaUnchanged': True,
                                              'posesGeneratedAgain': False, 'unityFilesWritten': False})
    jsave(ROOT / 'Clips/clip-plan.json', {'clips': clips, 'sequences': [
        {'name': 'awakening', 'shots': ['A1', 'A2', 'A3', 'A4'], 'durationMs': 8000},
        {'name': 'homecoming', 'shots': ['B1', 'B2', 'B3', 'B4'], 'durationMs': 10000}],
        'notContinuous18s': True, 'bossFightBetweenSequences': True, 'openingUnchanged': True})
    contact = Image.new('RGB', (1280, 1568), (12, 18, 28))
    draw = ImageDraw.Draw(contact)
    draw.fontmode = '1'
    labels = {'A1': '추·소켓 도킹', 'A2': '릴레이 연결', 'A3': '문지기 노심 기동', 'A4': '전투 대치',
              'B1': '문지기 정지', 'B2': '열린 출구로 이동', 'B3': '공방 와이드', 'B4': '공방 근접·귀환 자막'}
    for i, clip in enumerate(clips):
        x, y = (i % 2) * 640, (i // 2) * 392
        draw.text((x + 12, y + 8), f"{clip['name']}  {labels[clip['name']]}  {clip['durationMs']//1000}초", font=FONT, fill=(231, 207, 146))
        contact.paste(Image.open(ROOT / f"Clips/{clip['name']}/{clip['frames'][-1]}").convert('RGB'), (x, y + 30))
    pngsave(ROOT / 'QA/full-eight-cut-contact.png', contact)
    print(json.dumps({'cuts': 8, 'newGeneratedAnchors': 4, 'selectedNewAnchors': 3,
                      'frameCounts': {c['name']: len(c['frames']) for c in clips},
                      'runtimeIntegrated': False, 'humanAppearanceApproval': 'pending'}))


if __name__ == '__main__':
    main()
