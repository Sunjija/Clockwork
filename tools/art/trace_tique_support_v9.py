"""Full-body support pose traces, retaining the approved identity and palette.

Every torso, shoulder, forearm and hand silhouette begins in a real complete
single-pose image. Head dimensions normalize to the approved 31x27 envelope;
the complete pre-cleanup trace is saved for comparison. Idle alone is original.
"""
from pathlib import Path
from collections import Counter, deque
import json, hashlib, math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v9-traced'
SOURCE = ART / 'SupportSource'
OLD = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'
BASE = Image.open(OLD / 'Idle/00.png').convert('RGBA')
PAL = [p for p, count in Counter(BASE.getdata()).most_common() if p[3]]
INK = PAL[0]
GOLD = (244, 203, 112, 255)
BRASS = (188, 120, 59, 255)
SHADE = (117, 64, 50, 255)
TIMES = {c['name']: c['durations'] for c in json.loads((OLD.parent / 'clips.json').read_text())['clips']}
LANDMARKS = {
    'side-brace': ((284, 164, 944, 691), 1109, (16, 8), 21),
    'side-shift': ((282, 165, 948, 700), 1109, (16, 8), 21),
    'side-contact': ((356, 179, 1069, 724), 1140, (16, 8), 21),
    'push-up': ((278, 145, 972, 711), 1139, (16, 8), 21),
    'push-down': ((293, 155, 944, 698), 1100, (16, 8), 21),
    'hurt-recoil': ((282, 161, 926, 702), 1108, (15, 9), 20),
    'hurt-settle': ((316, 155, 932, 688), 1097, (16, 8), 21),
    'push-up-high-round': ((323, 130, 927, 690), 1091, (17, 8), 21),
    'push-down-round': ((324, 237, 940, 809), 1050, (17, 13), 16),
    'side-round-contact': ((356, 179, 1069, 724), 1140, (16, 8), 21),
}


def components(im):
    left = {(x, y) for y in range(64) for x in range(64) if im.getpixel((x, y))[3]}
    groups = []
    while left:
        seed = left.pop(); group = {seed}; queue = deque([seed])
        while queue:
            x, y = queue.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = x + dx, y + dy
                    if p in left: left.remove(p); group.add(p); queue.append(p)
        groups.append(group)
    return sorted(groups, key=len, reverse=True)


def trace(name):
    path = SOURCE / (name + '.png')
    source = Image.open(path).convert('RGBA')
    box = source.getchannel('A').point(lambda x: 255 if x >= 128 else 0).getbbox()
    head, bottom, offset, body_h = LANDMARKS[name]
    left, top, right, neck = head
    x0, y0 = offset
    sx = (right - left) / 31
    im = Image.new('RGBA', (64, 64))
    def source_y(y):
        return top + (y - y0) * (neck - top) / 27 if y <= y0 + 27 else neck + (y - y0 - 27) * (bottom - neck) / body_h
    for y in range(y0, y0 + 27 + body_h):
        a, b = max(0, int(source_y(y))), min(source.height, int(source_y(y + 1)))
        for x in range(64):
            l, r = max(0, math.floor(left + (x - x0) * sx)), min(source.width, math.ceil(left + (x + 1 - x0) * sx))
            if l >= r or a >= b: continue
            region = source.crop((l, a, r, b))
            opaque = [c for c in region.getdata() if c[3] >= 128]
            if len(opaque) < region.width * region.height * .36: continue
            colors = [min(PAL, key=lambda p: sum((p[i] - c[i]) ** 2 for i in range(3))) for c in opaque]
            im.putpixel((x, y), Counter(colors).most_common(1)[0][0])
    im.save(SOURCE / (name + '-full-trace.png'))
    # Register the actual two soles, rather than assuming the source head sits
    # over the foot pivot. A leaning complete pose naturally brings its chest,
    # head and both palms forward while the support feet stay on the same root.
    sole = [(x, y) for y in range(52, 56) for x in range(64) if im.getpixel((x, y))[3]]
    dx = round(32.5 - (min(x for x, y in sole) + max(x for x, y in sole)) / 2)
    registered = Image.new('RGBA', (64, 64)); registered.alpha_composite(im, (dx, 0)); im = registered
    # Every body region, including head and both hands, remains traced from the
    # real source. Dominant color blocks avoid averaging the metallic highlights
    # into speckled intermediate colours. Head footprint stays 31 by 27.
    parts = components(im)
    for group in parts[1:]:
        assert len(group) <= 2, (name, 'detached source limb', len(group))
        for p in group: im.putpixel(p, (0, 0, 0, 0))
    assert len(components(im)) == 1, (name, 'connected full trace')
    im.save(SOURCE / (name + '-authored.png'))
    return im, {'name': name, 'source': path.relative_to(ROOT).as_posix(),
                'sourceSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'sourceCrop': box, 'headLandmarks': head, 'bodyHeight': body_h, 'offset': offset, 'footRegistrationDx': dx,
                'method': 'entire single-image silhouette traced by dominant palette blocks, head footprint normalized 31x27; all head/body/arms/feet source-derived',
                'nativeRgbaSha256': hashlib.sha256(im.tobytes()).hexdigest()}


def canonicalize(name, im, record):
    """Explicit native contour corrections on a complete-image trace.

    The source establishes pose and contact. The one approved model establishes
    the character's face, shell and heart pixels; independent image variations
    never become a new face or a compressed chest. No limb is taken from Walk.
    """
    before = im.copy()
    dx = record['footRegistrationDx']
    if name == 'side-round-contact':
        head = (22, 8); torso = (29, 34)
        hands = [(53, 35), (52, 43)]
    elif name == 'push-down-round':
        head = (16, 13); torso = (23, 39)
        # The moving battery's right bevel begins one native row lower.
        hands = [(23, 56), (40, 57)]
    elif name == 'hurt-recoil':
        head = (15 + dx, 9); torso = (22 + dx, 35)
        hands = [(18 + dx, 37), (43 + dx, 37)]
    elif name == 'hurt-settle':
        head = (16 + dx, 8); torso = (23 + dx, 34)
        hands = [(17 + dx, 42), (44 + dx, 42)]
    else:
        # Rear view is one stable whole-image key. Its ear-cap/back-shell art is
        # retained, without inventing frontal eyes or a heart on the back.
        head = None; torso = (23, 34); hands = [(14, 22), (48, 22)]
    cleanup = {
        'side-round-contact': [(52, 33, 60, 41), (51, 41, 59, 49)],
        'hurt-recoil': [(17 + dx, 36, 22 + dx, 43), (43 + dx, 36, 49 + dx, 43)],
        'hurt-settle': [(16 + dx, 41, 22 + dx, 48), (44 + dx, 41, 49 + dx, 48)],
    }
    for x1, y1, x2, y2 in cleanup.get(name, []):
        for y in range(y1, y2):
            for x in range(x1, x2): im.putpixel((x, y), (0, 0, 0, 0))
    if head:
        oldx, oldy = record['offset']; oldx += dx
        for y in range(oldy, oldy + 27):
            for x in range(max(0, oldx - 3), min(64, oldx + 35)):
                im.putpixel((x, y), (0, 0, 0, 0))
        if name == 'push-down-round':
            for y in range(40, 56):
                for x in range(24, 41): im.putpixel((x, y), (0, 0, 0, 0))
        for y in range(27):
            for x in range(31): im.putpixel((head[0] + x, head[1] + y), BASE.getpixel((16 + x, 8 + y)))
        # Canonical chest dimensions do not shrink with the pose image.
        for y in range(16):
            for x in range(21):
                im.putpixel((torso[0] + x, torso[1] + y), BASE.getpixel((23 + x, 34 + y)))
        # Head is the last authority at the shared neck row.
        for y in range(27):
            for x in range(31): im.putpixel((head[0] + x, head[1] + y), BASE.getpixel((16 + x, 8 + y)))
    if name == 'push-down-round':
        # Keep the two actual source boots visible beside the crouched shell.
        for y in range(52, 56):
            for x in list(range(18, 23)) + list(range(44, 48)):
                if before.getpixel((x, y))[3]: im.putpixel((x, y), before.getpixel((x, y)))
        # Trace the bent downward arm contours from the crouched source beside
        # the standard shell, with the feet staying at the registered root.
        d = ImageDraw.Draw(im)
        d.line([(22, 42), (20, 47), (21, 52), (24, 56)], fill=INK, width=4)
        d.line([(22, 42), (20, 47), (21, 52), (24, 56)], fill=BRASS, width=2)
        d.line([(44, 42), (46, 47), (45, 52), (42, 56)], fill=INK, width=4)
        d.line([(44, 42), (46, 47), (45, 52), (42, 56)], fill=BRASS, width=2)
    if name == 'side-round-contact':
        d = ImageDraw.Draw(im)
        # Correct the source elbow/wrist contours where the standard chest
        # occludes a source-specific shoulder. Two bent arms, no straight rail.
        for points in [[(48, 37), (51, 39), (54, 37)], [(48, 41), (50, 43), (54, 45)]]:
            d.line(points, fill=INK, width=4)
            d.line(points, fill=BRASS, width=2)
    if torso and head:
        # Limbs are behind the one standard chest plate; its heart and shell
        # never change size or acquire an arm-coloured stripe between frames.
        for y in range(16):
            for x in range(21): im.putpixel((torso[0] + x, torso[1] + y), BASE.getpixel((23 + x, 34 + y)))
        for y in range(27):
            for x in range(31): im.putpixel((head[0] + x, head[1] + y), BASE.getpixel((16 + x, 8 + y)))
    if name == 'push-up-high-round':
        # Segment the actual back head and ear caps before shortening the
        # source's overlong U-shaped arms. No old hand fringe is retained.
        back_head = Image.new('RGBA', (64, 64))
        head_mask = Image.new('L', (64, 64)); md = ImageDraw.Draw(head_mask)
        md.ellipse((17, 8, 47, 34), fill=255)
        md.rectangle((15, 19, 20, 26), fill=255); md.rectangle((46, 19, 51, 26), fill=255)
        for y in range(8, 35):
            for x in range(64):
                if head_mask.getpixel((x, y)): back_head.putpixel((x, y), before.getpixel((x, y)))
                im.putpixel((x, y), (0, 0, 0, 0))
        for y in range(35, 45):
            for x in list(range(8, 23)) + list(range(44, 59)): im.putpixel((x, y), (0, 0, 0, 0))
        im.alpha_composite(back_head)
        # The rear shell uses the standard 21x16 footprint and the actual
        # generated bronze back colours. It has no invented heart on the back.
        rear = im.copy()
        for y in range(16):
            for x in range(21):
                mask = BASE.getpixel((23 + x, 34 + y))[3]
                c = rear.getpixel((23 + x, 34 + y))
                im.putpixel((23 + x, 34 + y), (c if c[3] else BRASS) if mask else (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for points in [[(23, 35), (19, 31), (16, 26)], [(42, 35), (46, 31), (49, 26)]]:
            d.line(points, fill=INK, width=3); d.line(points, fill=BRASS, width=1)
    if name == 'push-down-round':
        for y in range(52, 56):
            for x in list(range(18, 27)) + list(range(40, 48)):
                if before.getpixel((x, y))[3]: im.putpixel((x, y), before.getpixel((x, y)))
    if name == 'hurt-settle':
        im.putpixel((21 + dx, 43), INK); im.putpixel((22 + dx, 43), INK)
    # Every new hand uses the same 4x4 round ball: 2/4/4/2, two colours.
    for x0, y0 in hands:
        for y in range(4):
            for x in range(4):
                c = (0, 0, 0, 0) if (x, y) in ((0, 0), (3, 0), (0, 3), (3, 3)) else INK
                if x in (1, 2) and y in (1, 2): c = GOLD
                im.putpixel((x0 + x, y0 + y), c)
    # Remove only isolated quantization specks. Any detached limb is an error.
    for group in components(im)[1:]:
        if len(group) > 2:
            im.resize((512, 512), Image.Resampling.NEAREST).save(SOURCE / (name + '-cleanup-rejected.png'))
        assert len(group) <= 2, (name, 'cleanup detached limb', sorted(group))
        for p in group: im.putpixel(p, (0, 0, 0, 0))
    edits = [{'x': x, 'y': y, 'from': list(before.getpixel((x, y))), 'to': list(im.getpixel((x, y)))}
             for y in range(64) for x in range(64) if before.getpixel((x, y)) != im.getpixel((x, y))]
    (SOURCE / (name + '-native-edits.json')).write_text(json.dumps({'model': 'original Idle00 canonical head31x27/chest21x16/heart13x10; new hands4x4 round two-colour balls', 'head': head, 'torso': torso, 'hands': hands, 'edits': edits}, indent=2))
    im.save(SOURCE / (name + '-authored.png'))
    record['nativeCorrections'] = {'head': head, 'torso': torso, 'roundHands': hands, 'changedPixels': len(edits)}
    record['traceMethod'] = record['method']
    record['method'] = 'complete generated single-pose trace followed by explicit original-model head/chest/heart pixel corrections, connected limb contour cleanup and shared fingerless round hands; back-facing shell retains generated rear colours'
    record['nativeRgbaSha256'] = hashlib.sha256(im.tobytes()).hexdigest()
    return im


def export(name, frames, times):
    folder = ART / name; folder.mkdir(parents=True, exist_ok=True)
    contact = Image.new('RGBA', (7 * 208, ((len(frames) + 6) // 7) * 220), '#142330')
    draw = ImageDraw.Draw(contact)
    for i, frame in enumerate(frames):
        assert frame.size == (64, 64)
        assert len(components(frame)) == 1, (name, i, 'detached')
        assert {p for p in frame.getdata() if p[3]} <= set(PAL)
        frame.save(folder / f'{i:02d}.png')
        x, y = i % 7 * 208, i // 7 * 220
        draw.text((x + 4, y + 3), f'{name} {i:02d} {times[i]}ms', fill='white')
        contact.alpha_composite(frame.resize((192, 192), Image.Resampling.NEAREST), (x + 8, y + 23))
    contact.save(folder / 'contact-3x.png')
    (folder / 'clip.json').write_text(json.dumps({'name': name, 'durations': times}, indent=2))


def main():
    SOURCE.mkdir(parents=True, exist_ok=True)
    keys = {}; provenance = []
    for name in LANDMARKS:
        keys[name], record = trace(name); provenance.append(record)
        if name in ('side-round-contact', 'push-up-high-round', 'push-down-round', 'hurt-recoil', 'hurt-settle'):
            keys[name] = canonicalize(name, keys[name], record)
    # Native full-pose holds with a small support-foot transfer. Torso and both
    # hands keep their complete traced contours rather than being IK pieces.
    gait = [0, 0, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, 0, 0]
    for direction, key in [('side', 'side-round-contact'), ('up', 'push-up-high-round'), ('down', 'push-down-round')]:
        frames = []
        for i, step in enumerate(gait):
            frame = keys[key].copy()
            if step and direction != 'down':
                feet = frame.crop((0, 52, 64, 56))
                for y in range(52, 56):
                    for x in range(64): frame.putpixel((x, y), (0, 0, 0, 0))
                frame.alpha_composite(feet, (step, 52))
            frames.append(frame)
        export('push-' + direction, frames, TIMES['Walk'])
        export('push-brace-' + direction, [keys[key]], [1000])
    export('hurt-pose', [keys['hurt-recoil'], keys['hurt-settle'], BASE.copy()], [40, 50, 60])
    # The user explicitly wants the comfortable original neutral form.
    idle = [BASE.copy() for _ in range(8)]
    export('Idle', idle, [125] * 8)
    (SOURCE / 'trace-provenance.json').write_text(json.dumps(provenance, indent=2))
    print('Full-body support traces: ten generated pose sources; eight clips')


if __name__ == '__main__': main()
