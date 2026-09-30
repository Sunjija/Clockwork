"""Tique v8: independently generated single poses -> native pixel key cleanup.

The original 67 Return/Tique PNGs and old concept directories are read-only.
No generated animation sheet/video is consumed. Native exposures are deliberate
integer pixel edits of the converted keys and approved component pixels. Model
identity is preserved with the approved head, torso/heart and small leg pieces.
"""
from pathlib import Path
import argparse, base64, hashlib, io, json, re, uuid
from collections import Counter, deque
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v8-tique'
CONCEPT = ART / 'Source/Concepts'
NATIVE = ART / 'Source/Native'
QA = ART / 'QA'
OUT = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/TiqueV8'
ORIGINAL = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'
OLD_CONCEPT = ROOT / 'art/return-v5-feedback/Source/Concepts'
BASE = Image.open(ORIGINAL / 'Idle/00.png').convert('RGBA')
PAL = [c for c, _ in Counter(c for c in BASE.getdata() if c[3]).most_common()]
INK, BRASS, GOLD, SHADE, LIGHT, MID, WHITE = PAL[:7]
CLEAR = (0, 0, 0, 0)
TIMES = {c['name']: c['durations'] for c in json.loads((ORIGINAL.parent / 'clips.json').read_text())['clips']}
TIMES['Idle'] = [125] * 8
TEMPLATE = (ORIGINAL / 'Idle/00.png.meta').read_text()
SOURCES = {
    'crouch': CONCEPT / 'crouch-land.png',
    'tuck': CONCEPT / 'tuck-air.png',
    'dash': CONCEPT / 'dash-travel.png',
    'anticipate': CONCEPT / 'attack-anticipate.png',
    'impact': CONCEPT / 'attack-impact-v2.png',
    'push-side': OLD_CONCEPT / 'push-side-v3.png',
    'push-up': OLD_CONCEPT / 'push-up-v3.png',
    'push-down': OLD_CONCEPT / 'push-down-v4.png',
    'hurt': OLD_CONCEPT / 'hurt-pose-v2.png',
}
records = []
clip_records = []
pixel_audit = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(im):
    return hashlib.sha256(im.tobytes()).hexdigest()


def quantize(im):
    out = Image.new('RGBA', im.size)
    out.putdata([min(PAL, key=lambda q: sum((q[i] - c[i]) ** 2 for i in range(3)))
                 if c[3] >= 128 else CLEAR for c in im.getdata()])
    return out


def convert(name, path):
    src = Image.open(path).convert('RGBA')
    # Strict alpha content bounds; sources are single transparent pose images.
    bb = src.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox()
    assert bb, path
    crop = src.crop(bb)
    scale = 48 / crop.height
    size = (round(crop.width * scale), 48)
    sampled = crop.convert('RGBa').resize(size, Image.Resampling.BOX).convert('RGBA')
    small = quantize(sampled)
    im = Image.new('RGBA', (64, 64))
    offset = ((64 - small.width) // 2, 56 - small.height)
    im.alpha_composite(small, offset)
    im.save(NATIVE / (name + '-converted.png'))
    records.append({'name': name, 'source': path.relative_to(ROOT).as_posix(),
                    'sourceSha256': digest(path), 'sourceSize': src.size,
                    'cropPixels': bb, 'sampleSize': size, 'sampleOffset': offset,
                    'method': 'single static pose -> alpha content crop -> premultiplied BOX -> binary alpha -> approved 13-color palette',
                    'convertedRgbaSha256': rgba_sha(im)})
    return im


def shift(im, dx=0, dy=0):
    out = Image.new('RGBA', (64, 64))
    out.alpha_composite(im, (dx, dy))
    return out


def put(im, x, y, c):
    if 0 <= x < 64 and 0 <= y < 64:
        im.putpixel((x, y), c)


def pattern(im, x, y, rows, colors):
    """Explicit native pixel exposure patch; no smooth transforms or tweening."""
    for yy, row in enumerate(rows):
        for xx, symbol in enumerate(row):
            if symbol != '.':
                put(im, x + xx, y + yy, colors[symbol])


def connect(im, points, ink=INK, metal=BRASS, lit=GOLD):
    """Hand-authored 3px articulated connection, native grid only."""
    # The path coordinates are specific to a reviewed key/exposure, not IK.
    d = ImageDraw.Draw(im)
    d.line(points, fill=ink, width=5)
    d.line(points, fill=metal, width=3)
    d.line([(x, y - 1) for x, y in points], fill=lit, width=1)
    # One articulated elbow, not a row of repeated square beads.
    for x, y in points[1:2] if len(points) > 2 else []:
        pattern(im, x - 2, y - 2, ['.000.', '01110', '01210', '03330', '.000.'],
                {'0': ink, '1': lit, '2': LIGHT, '3': SHADE})


def components(im):
    mask = {(x, y) for y in range(64) for x in range(64) if im.getpixel((x, y))[3]}
    groups = []
    while mask:
        p = next(iter(mask)); mask.remove(p); q = deque([p]); group = [p]
        while q:
            x, y = q.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in mask:
                        mask.remove(n); q.append(n); group.append(n)
        groups.append(group)
    return groups


def head(dx=0, dy=0):
    im = Image.new('RGBA', (64, 64))
    im.alpha_composite(BASE.crop((16, 8, 47, 35)), (16 + dx, 8 + dy))
    return im


def torso(dx=0, dy=0, turn=0):
    im = Image.new('RGBA', (64, 64))
    # Exact original torso/heart pixels, without dangling arm pieces.
    for y in range(34, 50):
        for x in range(23, 44):
            c = BASE.getpixel((x, y))
            if c[3]: put(im, x + dx, y + dy, c)
    if turn:
        # Waist rotation is a native changing rear-side occlusion/shading, not
        # a translated full body. Cyan heart pixels remain exactly the original
        # local pattern. Turn sign affects bronze-only side contours.
        for yy, xs in [(37, range(24, 28)), (38, range(24, 27)), (39, range(24, 26)),
                       (45, range(25, 29)), (46, range(26, 31)), (47, range(28, 33))]:
            for xx in xs:
                c = im.getpixel((xx + dx, yy + dy))
                if c[3] and not is_cyan(c):
                    put(im, xx + dx, yy + dy, SHADE if turn > 0 else MID)
        # Diagonal hip seam changes direction while the chest remains round.
        for x, y in ([(26, 48), (28, 48), (30, 49), (32, 49)] if turn > 0
                      else [(26, 49), (28, 49), (30, 48), (32, 48)]):
            put(im, x + dx, y + dy, INK)
        # The core/front plate moves one native pixel with the turning chest,
        # while the outer torso stays planted. Core shape is copied exactly;
        # this is surface rotation/occlusion, not sliding the full body as one.
        hx = 1 if turn > 0 else -1
        for y in range(37, 47):
            for x in range(30, 43):
                put(im, x + dx, y + dy, BRASS if y < 45 else MID)
        im.alpha_composite(BASE.crop((30, 37, 43, 47)), (30 + dx + hx, 37 + dy))
    return im


def is_cyan(c):
    return c[3] and c[1] > c[0] * 1.4 and c[2] > c[0] * 1.4


def leg(im, side, dx=0, dy=0, angle='neutral'):
    box = (24, 49, 31, 56) if side == 'far' else (33, 49, 41, 56)
    patch = BASE.crop(box)
    im.alpha_composite(patch, (box[0] + dx, box[1] + dy))
    return im


def pose(headxy=(0, 0), bodyxy=(0, 0), legs=((0, 0), (0, 0)), turn=0):
    im = Image.new('RGBA', (64, 64))
    leg(im, 'far', *legs[0]); leg(im, 'near', *legs[1])
    # Hips occlude the tops of short leg pieces when compressing. Soles stay
    # planted; upper legs must not paint over the lowered round body.
    im.alpha_composite(torso(*bodyxy, turn))
    im.alpha_composite(head(*headxy))
    # Fill the small original neck gap only when the head leads the compact body.
    bx, by = bodyxy; hx, hy = headxy
    for y in range(33 + hy, 36 + by):
        for x in range(28 + bx, 39 + bx):
            if not im.getpixel((x, y))[3]:put(im, x, y, SHADE)
    im.info['headxy'] = headxy
    im.info['bodyxy'] = bodyxy
    im.info['heartshift'] = 1 if turn > 0 else -1 if turn < 0 else 0
    return im


def mitten(im, x, y, donor, box, flip=False):
    patch = donor.crop(box)
    # A compact 4x5 native hand, sampled once from the SINGLE converted pose.
    patch = quantize(patch.convert('RGBa').resize((4, 5), Image.Resampling.BOX).convert('RGBA'))
    if flip: patch = patch.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    # Clean the sampled hand with a closed mitten contour, without fingers.
    # Color chips originate in the source; silhouette repairs use its palette.
    pattern(patch, 0, 0, ['.00.', '0..0', '0..0', '0..0', '.00.'], {'0': INK})
    for yy in (1, 2, 3):
        for xx in (1, 2):
            if not patch.getpixel((xx, yy))[3]:patch.putpixel((xx, yy), GOLD if yy == 1 else BRASS)
    # Preserve two sampled center pixels, repair only a missing highlight on the
    # tiny closed fist so it cannot collapse into an unreadable black speck.
    patch.putpixel((1, 1), LIGHT); patch.putpixel((2, 1), GOLD)
    im.alpha_composite(patch, (x, y))


def rest_arms(im, bx=0, by=0):
    # Original arm pixels maintain neutral hanging shape.
    for box in [(16, 35, 24, 48), (43, 37, 48, 48)]:
        im.alpha_composite(BASE.crop(box), (box[0] + bx, box[1] + by))
    return im


def sample_review(keys):
    font = ImageFont.load_default()
    contact = Image.new('RGBA', (5 * 256, ((len(keys) + 4) // 5) * 224), (18, 26, 31, 255))
    d = ImageDraw.Draw(contact)
    for i, (name, key) in enumerate(keys.items()):
        x, y = i % 5 * 256, i // 5 * 224
        d.text((x + 4, y + 2), name, fill=(245, 210, 130), font=font)
        contact.alpha_composite(key.resize((192, 192), Image.Resampling.NEAREST), (x + 24, y + 20))
        d.line((x + 24, y + 20 + 56 * 3, x + 215, y + 20 + 56 * 3), fill=(64, 92, 101))
    contact.save(QA / 'converted-keys-3x.png')


def meta(path, kind):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-tique-v8/' + path.relative_to(ROOT).as_posix()).hex
    if kind == 'texture':
        txt = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, TEMPLATE, count=1)
        txt = re.sub(r'[ \t]+$', '', txt, flags=re.M)
    else:
        txt = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder': txt += 'folderAsset: yes\n'
        txt += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    target = path.with_name(path.name + '.meta')
    if not target.exists(): target.write_text(txt, encoding='utf-8')


def export(name, frames, times, sources, note):
    assert len(frames) == len(times)
    folder = ART / 'Clips' / name; folder.mkdir(parents=True, exist_ok=True)
    game = OUT / name; game.mkdir(parents=True, exist_ok=True); meta(game, 'folder')
    sheet = Image.new('RGBA', (64 * len(frames), 64))
    contact = Image.new('RGBA', (7 * 204, ((len(frames) + 6) // 7) * 224), (18, 26, 31, 255))
    d = ImageDraw.Draw(contact)
    for i, frame in enumerate(frames):
        # Canonical head/eyes and cyan heart stay intact, with physically
        # appropriate occlusion: the big head is in front of shoulder/arm tips.
        if 'headxy' in frame.info and name != 'dash-ghost':
            frame.alpha_composite(head(*frame.info['headxy']))
            bx, by = frame.info['bodyxy']
            for y in range(34, 48):
                for x in range(27, 43):
                    c = BASE.getpixel((x, y))
                    if is_cyan(c):put(frame, x + bx + frame.info.get('heartshift', 0), y + by, c)
        pixels = set(frame.getdata()); assert {c[3] for c in pixels} <= {0, 255}, (name, i)
        assert {c for c in pixels if c[3]} <= set(PAL), (name, i, 'palette')
        groups = components(frame)
        assert len(groups) == 1, (name, i, [(len(g), g[:3]) for g in groups])
        target = folder / f'{i:02}.png'; frame.save(target)
        frame.save(game / target.name); meta(game / target.name, 'texture')
        if name == 'Walk':
            original_bytes = (ORIGINAL / 'Walk' / target.name).read_bytes()
            target.write_bytes(original_bytes); (game / target.name).write_bytes(original_bytes)
        sheet.alpha_composite(frame, (i * 64, 0))
        x, y = i % 7 * 204, i // 7 * 224
        d.text((x + 4, y + 2), f'{name} {i:02} {times[i]}ms', fill=(245, 210, 130))
        contact.alpha_composite(frame.resize((192, 192), Image.Resampling.NEAREST), (x + 6, y + 20))
        d.line((x + 6, y + 188, x + 197, y + 188), fill=(72, 102, 112))
        deltas = [[x, y, *frame.getpixel((x, y))] for y in range(64) for x in range(64)
                  if frame.getpixel((x, y)) != BASE.getpixel((x, y))]
        (folder / f'{i:02}.pixels.json').write_text(json.dumps(deltas, separators=(',', ':')))
        pixel_audit.append({'clip': name, 'frame': i, 'rgbaSha256': rgba_sha(frame),
                            'changedFromIdle': len(deltas), 'components8': len(groups), 'bbox': frame.getbbox()})
    sheet.save(folder / 'sheet.png'); contact.save(QA / (name + '-contact-3x.png'))
    if len(frames) > 1:
        # Background disposal forces even identical hold exposures to remain
        # separate APNG frames, keeping PNG/APNG duration indexing identical.
        frames[0].save(folder / 'native.apng', save_all=True, append_images=frames[1:], duration=times, loop=0, disposal=1, blend=0)
        decoded = Image.open(folder / 'native.apng')
        assert decoded.n_frames == len(frames), (name, 'APNG merged holds')
        for n in range(len(frames)):
            decoded.seek(n)
            assert decoded.convert('RGBA').tobytes() == frames[n].tobytes(), (name, n, 'APNG pixels')
            assert round(decoded.info['duration']) == times[n], (name, n, 'APNG timing')
    b = io.BytesIO(); sheet.save(b, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': [
        {'layout': [[i] for i in range(len(frames))], 'base64PNG': 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()}]}
    (folder / (name + '.piskel')).write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'Single-image keys with native pixel exposures. Variable times in clips.json/APNG.',
        'fps': 20, 'width': 64, 'height': 64, 'layers': [json.dumps(layer)]}}))
    clip_records.append({'name': name, 'durations': times, 'width': 64, 'height': 64,
                         'sources': sources, 'note': note, 'uniqueFrames': len({f.tobytes() for f in frames})})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--sources-only', action='store_true')
    args = parser.parse_args()
    for folder in (NATIVE, QA, OUT): folder.mkdir(parents=True, exist_ok=True)
    keys = {name: convert(name, path) for name, path in SOURCES.items() if path.exists()}
    sample_review(keys)
    (NATIVE / 'conversion-provenance.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    if args.sources_only:
        print('Converted single keys:', ', '.join(keys)); return
    missing = set(SOURCES) - set(keys); assert not missing, ('single poses not ready', missing)
    build_clips(keys)
    package_key_evidence()
    (NATIVE / 'conversion-provenance.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    meta(OUT, 'folder')
    runtime = OUT / 'clips.json'
    runtime.write_text(json.dumps({'clips': [{'name': c['name'], 'durations': c['durations']} for c in clip_records]}, indent=2))
    meta(runtime, 'text')
    (ART / 'manifest.json').write_text(json.dumps({'status': 'implemented candidate, visual review required',
        'method': 'independent static pose concepts -> native conversion -> explicit native exposure edits; no generated animation sheets/videos',
        'canvas': [64, 64], 'footPivot': [32, 56], 'approvedPalette': [list(c) for c in PAL],
        'revision': 'iteration6', 'review': 'First draft rejected; iteration2..5 actual archived comparisons. Iteration6 pulls both boost boots one pixel up/inward after independent review; actual runtime review and human acceptance recorded separately.',
        'contributionDisclosure': 'Generated sources guide pose topology and provide sampled palm center pixels; tuck also provides actual knee/boot image patches. Head, torso, heart and neutral feet are preserved from approved native images. Connecting joints, contour cleanup, occlusion, waist seam and timing are explicitly native authored, not generated animation frames.',
        'originalIdleRgbaSha256': rgba_sha(BASE), 'singleImageConversions': records,
        'clips': clip_records, 'nativeFrames': pixel_audit}, indent=2), encoding='utf-8')
    (QA / 'native-checks.json').write_text(json.dumps({'passed': True, 'clips': len(clip_records),
        'frames': len(pixel_audit), 'binaryAlpha': True, 'approved13Palette': True,
        'connectedComponents8': True, 'activeDashDistinct': True, 'walkByteExact': True,
        'humanQualityApproval': False}, indent=2))
    print('Produced', len(clip_records), 'clips;', len(pixel_audit), 'native exposures')


def package_key_evidence():
    selected = {'crouch': ('Jump', 11), 'tuck': ('Jump', 4), 'dash': ('Dash', 4),
                'anticipate': ('Attack', 2), 'impact': ('Attack', 4),
                'push-side': ('push-side', 0), 'push-up': ('push-up', 0),
                'push-down': ('push-down', 0), 'hurt': ('hurt-pose', 0)}
    for record in records:
        name = record['name']; clip, frame = selected[name]
        im = Image.open(ART / 'Clips' / clip / f'{frame:02}.png').convert('RGBA')
        im.save(NATIVE / (name + '-authored.png'))
        old = Image.open(NATIVE / (name + '-converted.png')).convert('RGBA')
        delta = [[x, y, *im.getpixel((x, y))] for y in range(64) for x in range(64)
                 if im.getpixel((x, y)) != old.getpixel((x, y))]
        (NATIVE / (name + '-cleanup.pixels.json')).write_text(json.dumps(delta, separators=(',', ':')))
        record['cleanedKey'] = {'clip': clip, 'frame': frame, 'file': name + '-authored.png',
                                'rgbaSha256': rgba_sha(im), 'pixelCleanupCount': len(delta)}
        if name == 'tuck':
            record['nativeContribution']['kneeAndBootCrops'] = [[25, 48, 32, 54], [32, 49, 40, 56]]
    # Compare equivalent state poses against the actual old runtime PNGs. This
    # is QA composition only; gameplay frames are not changed here.
    rows = [('Attack', [2, 4, 6]), ('Jump', [4, 8, 11]),
            ('DoubleJump', [2, 3, 7]), ('Dash', [3, 4, 7])]
    sheet = Image.new('RGBA', (6 * 204, len(rows) * 224), (18, 26, 31, 255)); d = ImageDraw.Draw(sheet)
    for ri, (clip, indices) in enumerate(rows):
        for ci, index in enumerate(indices):
            for version, folder in enumerate([ORIGINAL / clip, ART / 'Clips' / clip]):
                im = Image.open(folder / f'{index:02}.png').convert('RGBA')
                x, y = (ci * 2 + version) * 204, ri * 224
                d.text((x + 4, y + 2), f'{clip} {index:02} ' + ('old' if version == 0 else 'v8'), fill=(245, 210, 130))
                sheet.alpha_composite(im.resize((192, 192), Image.Resampling.NEAREST), (x + 6, y + 20))
                d.line((x + 6, y + 188, x + 197, y + 188), fill=(72, 102, 112))
    sheet.save(QA / 'baseline-compare-3x.png')


def build_clips(keys):
    # Single-image contribution boxes on the converted64px images. The four
    # mitten center pixels survive sampling; contours/connecting arms are native
    # cleanup. Full generated heads/torso are never pasted over canonical parts.
    hand_boxes = {
        'crouch': (42, 42, 47, 47), 'tuck': (44, 39, 49, 44),
        'dash': (15, 41, 20, 46), 'anticipate': (18, 37, 23, 42),
        'impact': (48, 37, 53, 42), 'push-side': (48, 33, 53, 38),
        'push-up': (44, 33, 49, 38), 'push-down': (41, 43, 46, 48),
        'hurt': (41, 39, 46, 44),
    }
    for r in records:
        r['nativeContribution'] = {'part': 'compact mitten center color pixels / action silhouette guide',
            'convertedCrop': hand_boxes[r['name']],
                                   'canonicalParts': 'original head/torso/heart/feet pixel pieces',
                                   'manualEdits': 'integer arm connections, closed mitten contour, force transfer, waist bronze occlusion, hip seam'}

    def hands(im, key, a, b, path_a, path_b):
        connect(im, path_a); connect(im, path_b)
        mitten(im, *a, keys[key], hand_boxes[key])
        mitten(im, *b, keys[key], hand_boxes[key])
        return im

    def preload(h=(-1, 1), body=(0, 1), turn=-1):
        im = pose(h, body, turn=turn); bx, by = body
        return hands(im, 'anticipate', (19 + bx, 39 + by), (41 + bx, 39 + by),
                     [(24 + bx, 36 + by), (21 + bx, 38 + by), (21 + bx, 41 + by)],
                     [(43 + bx, 38 + by), (43 + bx, 40 + by)])

    def punch(reach, headxy, bodyxy, elbow_y, legs):
        im = pose(headxy, bodyxy, legs, turn=1); bx, by = bodyxy
        # Rear shoulder travels across the UPPER chest above the heart. The
        # elbow opens and short forearm follows; no huge hand or straight stick.
        rear = Image.new('RGBA', (64, 64))
        # Rear shoulder is behind the turning torso. Only the short bent
        # forearm/fist emerges past its right side; no straight cross-chest bar.
        connect(rear, [(35 + bx, 36 + by), (42 + bx, elbow_y - 2), (reach - 2, elbow_y), (reach + 1, elbow_y + 1)])
        mitten(rear, reach, elbow_y - 1, keys['impact'], hand_boxes['impact'])
        rear.alpha_composite(torso(*bodyxy, 1)); rear.alpha_composite(im)
        connect(rear, [(43 + bx, 39 + by), (43 + bx, 42 + by)])
        mitten(rear, 41 + bx, 42 + by, keys['impact'], hand_boxes['impact'])
        rear.info.update(im.info)
        return rear

    def rise(bodydy=-1, legs=((-1, -3), (0, -4)), armheight=0, headxy=(0, 0)):
        im = pose(headxy, (0, bodydy), legs)
        # Actual new tucked-knee/boot pixels from the converted SINGLE air pose;
        # original feet are removed, not stretched into longer legs.
        for y in range(50, 58):
            for x in range(20, 44):put(im, x, y, CLEAR)
        for box, dest in [((25, 48, 32, 54), (25 + legs[0][0], 48 + max(-5, legs[0][1]))),
                          ((32, 49, 40, 56), (32 + legs[1][0], 48 + max(-5, legs[1][1])))]:
            im.alpha_composite(keys['tuck'].crop(box), dest)
        return hands(im, 'tuck', (17, 39 + armheight), (45, 39 + armheight),
                     [(24, 36 + bodydy), (21, 38 + armheight), (19, 41 + armheight)],
                     [(43, 38 + bodydy), (46, 40 + armheight)])

    def fall(step=0):
        im = pose((0, 0), (0, 0 if step == 0 else 1))
        return hands(im, 'tuck', (17, 34 + step * 2), (46, 34 + step * 2),
                     [(24, 36), (21, 35 + step), (19, 36 + step * 2)],
                     [(43, 38), (46, 36 + step), (48, 36 + step * 2)])

    def land(stage):
        hd, bd = [(2, 1), (2, 2), (2, 1), (1, 0), (0, 0)][stage]
        im = pose((0, hd), (0, bd))
        if stage < 3:
            # Small bent knee hinges sample the crouch reference's bronze ramp.
            # Boot/sole pixels y52..55 remain exactly in the neutral positions.
            for x, y, c in [(25, 50, GOLD), (26, 51, SHADE), (35, 50, GOLD), (36, 51, SHADE)]:
                put(im, x, y, c)
        return rest_arms(im, 0, bd) if stage < 4 else BASE.copy()

    def travel(stage):
        hs = [(2, 2), (2, 2), (2, 1), (1, 1)][stage]
        feet = [((-2, -2), (-1, -1)), ((-1, -1), (-2, -3)),
                ((-2, -2), (0, -2)), ((-1, 0), (0, -1))][stage]
        im = pose(hs, (1, 1), feet)
        return hands(im, 'dash', (16 + (stage == 3), 43 + (stage == 3)), (41, 43 + stage % 2),
                     [(25, 37), (21, 40), (18 + (stage == 3), 45 + (stage == 3))],
                     [(44, 39), (45, 42), (43, 45 + stage % 2)])

    # Comfortable original stance: no crouched readiness or spread feet.
    # Slow head settle1px while feet/chest remain unchanged; one-second cycle.
    idle = [BASE.copy() for _ in range(8)]
    for i in (3, 4):
        idle[i] = BASE.copy()
        # Only a sparse bronze shoulder relaxation, not changing feet or shape.
        for x, y in [(22, 39), (44, 42)]:
            old = idle[i].getpixel((x, y))
            if old[3] and not is_cyan(old):idle[i].putpixel((x, y), MID)
    export('Idle', idle, TIMES['Idle'], ['approved Idle; shoulder palette relaxation only'],
           'Neutral original pose, planted feet and exact head/heart identity; tiny shoulder settling')

    walk = [Image.open(ORIGINAL / 'Walk' / f'{i:02}.png').convert('RGBA') for i in range(14)]
    export('Walk', walk, TIMES['Walk'], ['approved Walk14 byte-exact native pixels'],
           'User-approved head position and heart-bottom seam retained unchanged')

    attack = [BASE.copy(), preload(), preload((-1, 1), (-1, 1)),
              punch(40, (0, 1), (0, 1), 40, ((-1, 0), (0, 0))),
              punch(51, (1, 1), (0, 1), 41, ((-2, 0), (1, 0))),
              punch(52, (1, 2), (1, 1), 42, ((-1, 0), (1, 0))),
              punch(44, (1, 1), (0, 1), 41, ((-1, 0), (1, 0))),
              punch(36, (0, 1), (0, 0), 40, ((0, 0), (0, 0))),
              preload((0, 1), (0, 0)), rest_arms(pose((0, 1), (0, 0), turn=-1)),
              rest_arms(pose()), BASE.copy()]
    export('Attack', attack, TIMES['Attack'], ['anticipate', 'impact'],
           'Rear-arm punch: hip seam/side occlusion turn, foot drive, elbow opens, short hand, recoils. Reach peaks in04/05 at120..220ms')

    jump = [BASE.copy(), land(3), land(0), rise(0, ((0, -1), (0, -2)), 0, (0, 1)),
            rise(-1), rise(0, ((0, -3), (1, -4)), -1),
            rise(0, ((-1, -2), (1, -3)), -3), rise(0, ((0, -2), (1, -2)), -2),
            fall(0), fall(1), land(0), land(1), land(2), land(3), BASE.copy()]
    export('Jump', jump, TIMES['Jump'], ['crouch', 'tuck'],
           'Planted preload, short tucked ascent, arms loosen at apex, open falling silhouette, foot contact then head-lag recovery')

    double = [rise(-1), preload((0, 0), (0, -1)),
              rise(-2, ((-2, -3), (1, -2)), -1), rise(-2, ((0, -5), (-1, -5)), -2, (0, -1)),
              rise(-1, ((0, -4), (-1, -5)), -1), rise(0, ((-1, -2), (1, -3)), -3),
              rise(0, ((0, -2), (1, -2)), -2), fall(0), fall(1), land(0), land(1), land(3), BASE.copy()]
    export('DoubleJump', double, TIMES['DoubleJump'], ['tuck', 'crouch'],
           'Asymmetric short kick distinct from first jump, feet recollect, apex release, fall and grounded recovery')

    dash = [BASE.copy(), land(3), preload((1, 1), (0, 1)),
            *[travel(i) for i in range(4)],
            rest_arms(pose((1, 1), (0, 1), ((-1, 0), (1, 0))), 0, 1),
            preload((0, 2), (-1, 1)), rest_arms(pose((-1, 1), (0, 0))),
            rest_arms(pose((0, 1), (0, 0))), BASE.copy()]
    assert len({f.tobytes() for f in dash[3:7]}) == 4
    export('Dash', dash, TIMES['Dash'], ['dash', 'crouch'],
           'Compact leading head/chest, tiny trailing hands, distinct active03..06 feet/arm follow-through, front-foot brake')

    hurt = [preload((-1, 1), (0, 1)), preload((0, 1), (0, 0)), BASE.copy()]
    # Replace the compact hands with samples from the hurt image itself.
    for i in range(2):
        mitten(hurt[i], 19, 40, keys['hurt'], hand_boxes['hurt'])
        mitten(hurt[i], 42, 40, keys['hurt'], hand_boxes['hurt'])
    export('hurt-pose', hurt, [40, 50, 60], ['hurt'],
           'Short back recoil, arms tuck, head follows back to exact neutral Idle')

    def heart_center(im):
        pts = [(x, y) for y in range(34, 48) for x in range(27, 43) if is_cyan(im.getpixel((x, y)))]
        return round(sum(x for x, y in pts) / len(pts)), round(sum(y for x, y in pts) / len(pts))
    cx, cy = heart_center(BASE)

    def push(source, direction):
        im = source.copy(); px, py = heart_center(source); dx, dy = px - cx, py - cy
        # Remove only original dangling arm pixel regions. Keep heart/torso,
        # approved head seam, walk feet and full silhouette height unchanged.
        for box in [(16, 35, 24, 48), (43, 37, 50, 48)]:
            for y in range(box[1] + dy, box[3] + dy):
                for x in range(box[0] + dx, box[2] + dx):
                    if not is_cyan(im.getpixel((x, y))):put(im, x, y, CLEAR)
        if direction == 'side':
            a, b = (51 + dx, 38 + dy), (51 + dx, 44 + dy)
            pa = [(39 + dx, 37 + dy), (44 + dx, 39 + dy), (49 + dx, 39 + dy), (53 + dx, 40 + dy)]
            pb = [(43 + dx, 40 + dy), (46 + dx, 45 + dy), (53 + dx, 46 + dy)]
        elif direction == 'up':
            a, b = (20 + dx, 33 + dy), (44 + dx, 33 + dy)
            pa = [(24 + dx, 38 + dy), (21 + dx, 36 + dy), (22 + dx, 35 + dy)]
            pb = [(43 + dx, 39 + dy), (46 + dx, 35 + dy)]
        else:
            a, b = (24 + dx, 44 + dy), (42 + dx, 44 + dy)
            pa = [(24 + dx, 37 + dy), (21 + dx, 41 + dy), (26 + dx, 46 + dy)]
            pb = [(43 + dx, 38 + dy), (46 + dx, 42 + dy), (44 + dx, 46 + dy)]
        if direction == 'side':
            # Rear upper arm is occluded by the round chest, emerging only past
            # its right contour. Two bent forearms/palms remain separately seen.
            rear = Image.new('RGBA', (64, 64))
            connect(rear, pa); mitten(rear, *a, keys['push-side'], hand_boxes['push-side'])
            rear.alpha_composite(im); rear.info.update(im.info); im = rear
            connect(im, pb); mitten(im, *b, keys['push-side'], hand_boxes['push-side'])
        else:
            hands(im, 'push-' + direction, a, b, pa, pb)
        # Restore original cyan core exactly after bronze arm overlap. Hand
        # silhouettes remain outside the core instead of covering its identity.
        for y in range(34, 48):
            for x in range(27, 43):
                c = source.getpixel((x, y))
                if is_cyan(c):put(im, x, y, c)
        return im

    for direction in ['side', 'up', 'down']:
        frames = [push(im, direction) for im in walk]
        export('push-' + direction, frames, TIMES['Walk'], ['push-' + direction, 'approved Walk head/torso/feet'],
               'Two closed small connected palms; Walk support/heart/head retained; shoulders brace and follow chest per native exposure')
        export('push-brace-' + direction, [push(BASE, direction)], [1000], ['push-' + direction, 'approved Idle feet'],
               'Two-palm stationary brace with neutral planted feet')

    ghosts = []
    for frame in dash:
        im = frame.copy(); im.putdata([PAL[11] if c[3] else CLEAR for c in im.getdata()]); ghosts.append(im)
    export('dash-ghost', ghosts, TIMES['Dash'], ['new Dash full-image silhouette'],
           'Exact new Dash silhouettes, binary alpha and approved original cyan-shadow palette')


if __name__ == '__main__': main()
