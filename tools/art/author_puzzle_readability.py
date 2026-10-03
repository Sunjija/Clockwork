"""Native pixel-authoring pass for puzzle props, using the Return state pipeline.

No generated strips, runtime tint substitution, smooth scaling, or altered puzzle
rules. Every final frame is an editable integer-pixel drawing, exported as PNG,
Piskel, per-pixel replay deltas, and variable-timing APNG. Existing StateArt timing
is copied exactly. Old assets are read for comparison and never overwritten.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import base64
import hashlib
import io
import json
import re
import shutil
import uuid

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-readability-v1'
RESOURCE = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2'
OUT = RESOURCE / 'ReadabilityArt'
TIMING = {c['name']: c for c in json.loads((RESOURCE / 'StateArt/clips.json').read_text())['clips']}
META = (RESOURCE / 'StateArt/battery-idle/00.png.meta').read_text()

# Fixed, modest palette; roles also differ in silhouette and lightness.
INK = (9, 17, 24, 255)
VOID = (13, 23, 31, 255)
FLOOR = (25, 36, 44, 255)
FLOOR_EDGE = (31, 43, 51, 255)
WALL_DARK = (41, 55, 68, 255)
WALL = (64, 82, 97, 255)
WALL_LIGHT = (89, 109, 122, 255)
WALL_RIVET = (114, 130, 138, 255)
BRASS_DARK = (93, 55, 30, 255)
BRASS = (168, 100, 39, 255)
AMBER = (236, 157, 53, 255)
AMBER_LIGHT = (255, 211, 104, 255)
AMBER_WHITE = (255, 239, 163, 255)
CYAN_DARK = (22, 78, 92, 255)
CYAN_MID = (28, 139, 160, 255)
CYAN = (65, 210, 220, 255)
CYAN_LIGHT = (157, 244, 235, 255)
WHITE = (225, 250, 241, 255)
RED = (244, 87, 69, 255)
PALETTE = {v for k, v in list(globals().items()) if k.isupper() and isinstance(v, tuple) and len(v) == 4}
CLIPS = []
AUDIT = []


def blank(size):
    return Image.new('RGBA', size, (0, 0, 0, 0))


def floor():
    im = Image.new('RGBA', (36, 36), FLOOR)
    d = ImageDraw.Draw(im)
    d.line((0, 0, 35, 0), fill=FLOOR_EDGE)
    d.line((0, 0, 0, 35), fill=FLOOR_EDGE)
    d.line((35, 1, 35, 35), fill=VOID)
    d.line((1, 35, 35, 35), fill=VOID)
    d.point((8, 26), fill=FLOOR_EDGE)
    d.point((26, 9), fill=FLOOR_EDGE)
    return im


def wall(mask):
    """Connected edges: top/N=1, right/E=2, bottom/S=4, left/W=8."""
    im = Image.new('RGBA', (36, 36), WALL)
    d = ImageDraw.Draw(im)
    # A continuous horizontal structural seam, never an isolated machine hub.
    d.rectangle((0, 18, 35, 19), fill=WALL_DARK)
    d.line((0, 20, 35, 20), fill=WALL_LIGHT)
    d.line((10, 8, 16, 8), fill=WALL_LIGHT)
    d.line((22, 27, 28, 27), fill=WALL_DARK)
    # Rivets sit away from the centre and are deliberately much duller than props.
    for x, y in ((7, 7), (28, 28)):
        d.rectangle((x, y, x + 2, y + 2), fill=WALL_DARK)
        d.point((x, y), fill=WALL_RIVET)
    if not mask & 1:
        d.rectangle((0, 0, 35, 1), fill=INK)
        d.rectangle((2, 2, 33, 3), fill=WALL_LIGHT)
    if not mask & 2:
        d.rectangle((34, 0, 35, 35), fill=INK)
        d.line((33, 2, 33, 33), fill=WALL_DARK)
    if not mask & 4:
        d.rectangle((0, 33, 35, 35), fill=INK)
        d.line((2, 32, 33, 32), fill=WALL_DARK)
    if not mask & 8:
        d.rectangle((0, 0, 1, 35), fill=INK)
        d.line((2, 4, 2, 32), fill=WALL_LIGHT)
    return im


def battery(mode='idle', frame=0):
    im = blank((30, 32))
    d = ImageDraw.Draw(im)
    # Separate, small ground shadow; not a full cell, unlike the wall.
    d.rectangle((5, 29, 25, 30), fill=VOID)
    # Large open rectangular carrying handle -- the defining silhouette.
    shift = [0, 0, 1, 1, 1, 0, -1, -1, 0, 0, 0, 0][frame] if mode == 'moving' else 0
    d.rectangle((8 + shift, 0, 21 + shift, 10), fill=INK)
    d.rectangle((10 + shift, 1, 19 + shift, 3), fill=AMBER_LIGHT)
    d.rectangle((9 + shift, 3, 11 + shift, 9), fill=BRASS)
    d.rectangle((18 + shift, 3, 20 + shift, 9), fill=BRASS)
    d.rectangle((12 + shift, 4, 17 + shift, 8), fill=(0, 0, 0, 0))
    # Chamfered mass with broad light top edge and heavy dark underside.
    d.polygon([(5, 10), (24, 10), (27, 13), (27, 27), (24, 29), (5, 29), (2, 26), (2, 13)], fill=INK)
    d.polygon([(6, 11), (23, 11), (25, 13), (25, 25), (23, 27), (6, 27), (4, 25), (4, 13)], fill=AMBER)
    d.rectangle((4, 14, 6, 24), fill=AMBER_LIGHT)
    d.line((7, 12, 22, 12), fill=AMBER_WHITE)
    d.rectangle((7, 24, 24, 26), fill=BRASS)
    d.line((7, 27, 22, 27), fill=BRASS_DARK)
    # Rectangular inset and vertical strokes, never a round hub.
    d.rectangle((10, 15, 21, 23), fill=BRASS_DARK)
    d.rectangle((11, 16, 20, 21), fill=BRASS)
    for x in (12, 15, 18):
        d.line((x, 17, x, 20), fill=AMBER_LIGHT)
    d.rectangle((4, 28, 8, 30), fill=INK)
    d.rectangle((22, 28, 26, 30), fill=INK)
    d.line((5, 28, 7, 28), fill=WALL_RIVET)
    d.line((23, 28, 25, 28), fill=WALL_RIVET)
    if mode == 'moving':
        # Native contact-foot exposures, no shape scaling or whole-image wobble.
        if frame in (2, 3, 4, 7, 8):
            d.point((2 + frame % 2, 30), fill=BRASS)
            d.point((28 - frame % 2, 30), fill=AMBER)
    if mode == 'docked':
        d.line((5, 26, 8, 26), fill=AMBER_WHITE)
        d.line((21, 26, 24, 26), fill=AMBER_WHITE)
    return im


def orb(mode='idle', frame=0):
    im = blank((26, 26))
    d = ImageDraw.Draw(im)
    d.line((7, 25, 19, 25), fill=VOID)
    # Chunky circular silhouette with empty corners, not a square machine casing.
    d.ellipse((1, 1, 24, 24), fill=INK)
    d.ellipse((3, 3, 22, 22), fill=CYAN_DARK)
    d.ellipse((4, 3, 21, 20), fill=CYAN_MID)
    d.ellipse((4, 3, 19, 18), fill=CYAN)
    d.line([(5, 8), (7, 5), (11, 4), (15, 4)], fill=CYAN_LIGHT, width=2)
    d.line([(17, 20), (20, 18), (22, 14)], fill=CYAN_DARK)
    # Revolving meridian: integer-pixel paths clipped to the unchanged sphere.
    centre = [6, 7, 9, 11, 13, 15, 18, 20, 18, 15, 13, 11, 9, 7][frame] if mode == 'moving' else 12
    curve = [3, 2, 1, 0, -1, -2, -2, -2, -1, 0, 1, 2, 3]
    previous = None
    for y, bend in zip(range(6, 19), curve):
        x = max(4, min(21, centre + bend))
        if previous is not None:
            seam = blank(im.size)
            sd = ImageDraw.Draw(seam)
            sd.line([previous, (x, y)], fill=CYAN_DARK, width=2)
            for sy in range(5, 21):
                for sx in range(3, 23):
                    if seam.getpixel((sx, sy))[3] and im.getpixel((sx, sy)) in (CYAN, CYAN_MID, CYAN_LIGHT):
                        im.putpixel((sx, sy), CYAN_DARK)
        previous = (x, y)
    d = ImageDraw.Draw(im)
    d.rectangle((7, 5, 9, 6), fill=WHITE)
    d.point((6, 7), fill=CYAN_LIGHT)
    if mode == 'docked':
        d.line((10, 22, 15, 22), fill=CYAN_LIGHT)
    return im


def socket(kind, level=0, wrong=False):
    im = blank((36, 36))
    d = ImageDraw.Draw(im)
    amber = kind == 'amber'
    dim = BRASS if amber else CYAN_MID
    lit = AMBER_LIGHT if amber else CYAN_LIGHT
    # Flat dark cavities: light on the lower lip, dark on the upper inside edge.
    if amber:
        d.rectangle((2, 2, 33, 33), fill=VOID)
        d.rectangle((3, 3, 32, 32), outline=BRASS_DARK, width=2)
        d.rectangle((6, 6, 29, 29), fill=INK)
        d.line((6, 6, 29, 6), fill=VOID, width=2)
        d.line((6, 28, 29, 28), fill=dim)
        d.line((28, 7, 28, 28), fill=dim)
        # Negative-space matching shape in the cavity; not a protruding object.
        d.rectangle((13, 12, 22, 23), outline=BRASS_DARK)
        corners = [(2, 7, 2, 2, 7, 2), (28, 2, 33, 2, 33, 7), (33, 28, 33, 33, 28, 33), (7, 33, 2, 33, 2, 28)]
    else:
        d.ellipse((1, 1, 34, 34), fill=VOID)
        d.ellipse((3, 3, 32, 32), outline=CYAN_DARK, width=2)
        d.ellipse((6, 6, 29, 29), fill=INK)
        d.arc((6, 6, 29, 29), 15, 155, fill=dim)
        d.ellipse((13, 13, 22, 22), outline=CYAN_DARK)
        corners = [(2, 8, 2, 2, 8, 2), (27, 2, 33, 2, 33, 8), (33, 27, 33, 33, 27, 33), (8, 33, 2, 33, 2, 27)]
    # Outside contact segments remain visible with 30x32 / 26x26 objects seated.
    for i, points in enumerate(corners):
        d.line(list(zip(points[::2], points[1::2])), fill=lit if i < level else dim, width=2)
    if level == 4:
        for x, y in ((0, 17), (34, 17), (17, 0), (17, 34)):
            d.rectangle((x, y, min(x + 1, 35), min(y + 1, 35)), fill=WHITE)
    if wrong:
        # Unmatched ports, not a locked/unmovable X in the middle of the object.
        for x, y in ((0, 0), (29, 0), (0, 29), (29, 29)):
            d.line((x, y, x + 6, y + 6), fill=RED)
            d.line((x + 6, y, x, y + 6), fill=RED)
    return im


def meta(path, kind):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-readability-v1/' + path.relative_to(REPO).as_posix()).hex
    if kind == 'texture':
        body = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, META, count=1)
        body = body.replace('textureCompression: 1', 'textureCompression: 0')
        body = body.replace('filterMode: 1', 'filterMode: 0').replace('enableMipMap: 1', 'enableMipMap: 0')
    else:
        body = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder':
            body += 'folderAsset: yes\n'
        body += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    path.with_name(path.name + '.meta').write_text(body)


def export(name, images, timing=None, loop=False):
    source = ROOT / 'Clips' / name
    runtime = OUT / name
    source.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    meta(runtime, 'folder')
    times = TIMING[timing]['durations'] if timing else [1000]
    assert len(images) == len(times), (name, len(images), len(times))
    w, h = images[0].size
    sheet = blank((w * len(images), h))
    edits = []
    for i, image in enumerate(images):
        assert image.size == (w, h)
        assert set(image.getchannel('A').getdata()) <= {0, 255}
        assert set(image.getdata()) <= PALETTE | {(0, 0, 0, 0)}
        image.save(source / f'{i:02}.png')
        shutil.copyfile(source / f'{i:02}.png', runtime / f'{i:02}.png')
        meta(runtime / f'{i:02}.png', 'texture')
        sheet.alpha_composite(image, (i * w, 0))
        delta = [[x, y, *image.getpixel((x, y))] for y in range(h) for x in range(w)
                 if image.getpixel((x, y)) != images[0].getpixel((x, y))]
        (source / f'{i:02}.pixels.json').write_text(json.dumps(delta, separators=(',', ':')))
        edits.append({'frame': i, 'changedPixels': len(delta), 'bounds': image.getbbox(),
                      'sha256': hashlib.sha256(image.tobytes()).hexdigest()})
    sheet.save(source / 'sheet.png')
    if len(images) > 1:
        images[0].save(source / 'native.apng', format='PNG', save_all=True, append_images=images[1:],
                       duration=times, loop=0, disposal=1, blend=0)
        decoded = Image.open(source / 'native.apng')
        assert decoded.n_frames == len(images), (name, decoded.n_frames, len(images))
        for i, image in enumerate(images):
            decoded.seek(i)
            assert decoded.convert('RGBA').tobytes() == image.tobytes(), (name, i)
            assert round(decoded.info['duration']) == times[i], (name, i, decoded.info)
    buf = io.BytesIO()
    sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(images), 'chunks': [
        {'layout': [[i] for i in range(len(images))], 'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    (source / (name + '.piskel')).write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'Native pixel-authored prop. Exact variable timing in clips.json / APNG.',
        'fps': 20, 'width': w, 'height': h, 'layers': [json.dumps(layer)]}}))
    c = {'name': name, 'durations': times, 'width': w, 'height': h, 'loop': loop,
         'tiqueTiming': TIMING[timing].get('tiqueTiming') if timing else None,
         'source': 'native integer-pixel authoring; editable Piskel and pixel-delta replay'}
    CLIPS.append(c)
    AUDIT.append({'name': name, 'frames': edits})


def enlarged(image, scale=5):
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def comparison():
    entries = [('wall', 'Art/wall.png', 'wall-00'),
               ('weight', 'StateArt/battery-idle/00.png', 'battery-idle'),
               ('orb', 'StateArt/orb-idle/00.png', 'orb-idle'),
               ('square socket', 'StateArt/amber-slot-empty/00.png', 'amber-slot-empty'),
               ('round socket', 'StateArt/cyan-slot-empty/00.png', 'cyan-slot-empty')]
    contact = Image.new('RGB', (1100, 490), (17, 27, 36))
    d = ImageDraw.Draw(contact)
    d.text((18, 12), 'PUZZLE READABILITY V1 | native 36px grid | 5x nearest-neighbour comparison', fill=(225, 240, 240))
    for col, (label, old, new) in enumerate(entries):
        x = 20 + col * 216
        d.text((x, 38), label, fill=(225, 240, 240))
        for row, path in enumerate((RESOURCE / old, OUT / new / '00.png')):
            image = enlarged(Image.open(path).convert('RGBA'))
            y = 64 + row * 210
            contact.paste(image, (x + (180 - image.width) // 2, y + 180 - image.height), image)
            d.text((x, y + 187), 'old' if row == 0 else 'new editable pixels', fill=(143, 170, 184))
    contact.save(ROOT / 'QA/before-after.png')
    gray = ImageOps.grayscale(contact).convert('RGB')
    gray.save(ROOT / 'QA/before-after-grayscale.png')


def board(room, old=False):
    im = Image.new('RGBA', (252, 252), FLOOR)
    objects = []
    for pos in range(49):
        x, y = pos % 7, pos // 7
        wall_here = room['rows'][y][x] == '#'
        if old:
            tile = Image.open(RESOURCE / 'Art' / ('wall.png' if wall_here else 'floor.png')).convert('RGBA')
        else:
            mask = 0
            for dx, dy, bit in ((0, -1, 1), (1, 0, 2), (0, 1, 4), (-1, 0, 8)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 7 and 0 <= ny < 7 and room['rows'][ny][nx] == '#':
                    mask |= bit
            tile = wall(mask) if wall_here else floor()
        im.alpha_composite(tile, (x * 36, y * 36))
    for i, pos in enumerate(room['goals']):
        kind = 'amber' if room['types'][i] == 0 else 'cyan'
        s = Image.open(RESOURCE / 'StateArt' / (kind + '-slot-empty') / '00.png').convert('RGBA') if old else socket(kind)
        im.alpha_composite(s, (pos % 7 * 36, pos // 7 * 36))
    for i, pos in enumerate(room['boxes']):
        weight = room['types'][i] == 0
        path = RESOURCE / 'StateArt' / ('battery-idle' if weight else 'orb-idle') / '00.png'
        b = Image.open(path).convert('RGBA') if old else battery() if weight else orb()
        objects.append((pos // 7, b, (pos % 7 * 36 + (3 if weight else 5), pos // 7 * 36 + (0 if weight else 6))))
    player = room['start']
    tique = Image.open(RESOURCE / 'TiqueV10/Idle/00.png').convert('RGBA')
    objects.append((player // 7, tique, (player % 7 * 36 + 18 - 32, player // 7 * 36 + 32 - 56)))
    for _, sprite, xy in sorted(objects, key=lambda it: it[0]):
        im.alpha_composite(sprite, xy)
    return im


def qa():
    dest = ROOT / 'QA'
    dest.mkdir(parents=True, exist_ok=True)
    comparison()
    levels = json.loads((RESOURCE / 'puzzles.json').read_text())['levels']
    # Static composition only, not a claim of runtime capture or play validation.
    pages = Image.new('RGB', (1060, 1730), (17, 27, 36))
    d = ImageDraw.Draw(pages)
    d.text((18, 14), 'STATIC NATIVE ART COMPOSITION | exact room layouts | not a runtime screenshot', fill=(225, 240, 240))
    for i, room in enumerate(levels):
        top = 38 + i * 560
        d.text((18, top), f'Room {i + 1}: new color / grayscale', fill=(190, 215, 223))
        b = enlarged(board(room), 2)
        pages.paste(b, (18, top + 22), b)
        gray = ImageOps.grayscale(b).convert('RGBA')
        pages.paste(gray, (546, top + 22), gray)
    pages.save(dest / 'room-layouts-color-and-gray.png')
    for i, room in enumerate(levels):
        board(room).save(dest / f'room-{i + 1}-native.png')
    sheet = Image.new('RGB', (1120, ((len(CLIPS) + 6) // 7) * 190), (17, 27, 36))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(CLIPS):
        image = Image.open(OUT / c['name'] / f"{len(c['durations']) // 2:02}.png").convert('RGBA')
        image = enlarged(image, 4)
        x, y = (i % 7) * 160, (i // 7) * 190
        sheet.paste(image, (x + (144 - image.width) // 2, y + 144 - image.height), image)
        d.text((x + 3, y + 151), c['name'], fill=(190, 215, 223))
        d.text((x + 3, y + 168), f"{c['width']}x{c['height']} / {len(c['durations'])}f", fill=(130, 158, 173))
    sheet.save(dest / 'all-state-contact.png')
    occupied = Image.new('RGB', (520, 180), (17, 27, 36))
    for n, (kind, obj) in enumerate((('amber', battery('docked')), ('cyan', orb('docked')))):
        sample = floor()
        sample.alpha_composite(socket(kind, 4))
        sample.alpha_composite(obj, (3, 0) if kind == 'amber' else (5, 6))
        large = enlarged(sample, 4)
        occupied.paste(large, (20 + n * 250, 8), large)
    ImageDraw.Draw(occupied).text((20, 158), 'Powered outer rim stays visible; no lock/latch', fill=(190, 215, 223))
    occupied.save(dest / 'occupied-socket-rims.png')


def validate_editable():
    for clip in CLIPS:
        name = clip['name']
        source = ROOT / 'Clips' / name
        piskel = json.loads((source / (name + '.piskel')).read_text())['piskel']
        layer = json.loads(piskel['layers'][0])
        sheet = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        assert sheet.size == (clip['width'] * len(clip['durations']), clip['height'])
        assert layer['frameCount'] == len(clip['durations'])
        base = Image.open(source / '00.png').convert('RGBA')
        for i in range(layer['frameCount']):
            final = Image.open(source / f'{i:02}.png').convert('RGBA')
            replay = base.copy()
            for x, y, r, g, b, a in json.loads((source / f'{i:02}.pixels.json').read_text()):
                replay.putpixel((x, y), (r, g, b, a))
            assert replay.tobytes() == final.tobytes(), (name, i, 'delta-replay')
            frame = sheet.crop((i * final.width, 0, (i + 1) * final.width, final.height))
            assert frame.tobytes() == final.tobytes(), (name, i, 'piskel-replay')
            settings = (OUT / name / f'{i:02}.png.meta').read_text()
            assert 'filterMode: 0' in settings and 'enableMipMap: 0' in settings
            assert 'textureCompression: 1' not in settings
        if name in TIMING:
            assert clip['durations'] == TIMING[name]['durations'], name
    # Connected horizontal/vertical edges have identical material continuity.
    for mask in range(16):
        a = wall(mask)
        if mask & 2:
            # Same vertical exposure on the adjacent tile; reciprocal W.
            b = wall((mask & (1 | 4)) | 8)
            assert [a.getpixel((35, y)) for y in range(36)] == [b.getpixel((0, y)) for y in range(36)]
        if mask & 4:
            b = wall((mask & (2 | 8)) | 1)
            assert [a.getpixel((x, 35)) for x in range(36)] == [b.getpixel((x, 0)) for x in range(36)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    meta(OUT, 'folder')
    export('floor', [floor()])
    for mask in range(16):
        export(f'wall-{mask:02}', [wall(mask)])
    for mode in ('idle', 'moving', 'docked'):
        name = 'battery-' + mode
        export(name, [battery(mode, i) for i in range(len(TIMING[name]['durations']))], name, mode == 'moving')
        name = 'orb-' + mode
        export(name, [orb(mode, i) for i in range(len(TIMING[name]['durations']))], name, mode == 'moving')
    for kind in ('amber', 'cyan'):
        export(kind + '-slot-empty', [socket(kind)], kind + '-slot-empty')
        export(kind + '-slot-filled', [socket(kind, 4)], kind + '-slot-filled')
        export(kind + '-slot-wrong', [socket(kind, 0, True)], kind + '-slot-wrong')
        export(kind + '-slot-connect', [socket(kind, n) for n in (0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4)], kind + '-slot-connect')
    data = {'clips': CLIPS}
    (OUT / 'clips.json').write_text(json.dumps(data, indent=2))
    meta(OUT / 'clips.json', 'text')
    (ROOT / 'clips.json').write_text(json.dumps(data, indent=2))
    (ROOT / 'manifest.json').write_text(json.dumps({
        'revision': 'readability-v1', 'method': 'native pixel authorship, existing Return export/timing pattern',
        'generatedAnimationStripsUsed': False, 'oldAssetsModified': False,
        'wallMask': {'N': 1, 'E': 2, 'S': 4, 'W': 8}, 'wallClipName': 'wall-{mask:02d}',
        'palette': sorted([list(p) for p in PALETTE]), 'clips': CLIPS,
        'runtimePath': OUT.relative_to(REPO).as_posix(),
        'validationScope': 'native asset / APNG / Piskel / palette validation; gameplay verification is separate'
    }, indent=2))
    (ROOT / 'pixel-edit-audit.json').write_text(json.dumps(AUDIT, indent=2))
    validate_editable()
    qa()
    frame_count = sum(len(c['durations']) for c in CLIPS)
    validation = {'clips': len(CLIPS), 'frames': frame_count, 'paletteColors': len(PALETTE),
                  'alpha': [0, 255], 'point': True, 'mipmaps': False, 'compression': False,
                  'apngRoundtrip': 'all multi-frame clips byte-identical, timings identical',
                  'piskelReplay': 'all frames byte-identical', 'pixelDeltaReplay': 'all frames byte-identical',
                  'timingSource': 'ReturnV2/StateArt/clips.json', 'wallMasks': list(range(16)),
                  'rulesChanged': False, 'runtimeCapture': False}
    (ROOT / 'QA/validation.json').write_text(json.dumps(validation, indent=2))
    print(json.dumps(validation))


if __name__ == '__main__':
    main()
