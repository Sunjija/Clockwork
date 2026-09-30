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
TIMES = {c['name']: c['durations'] for c in json.loads((OLD.parent / 'clips.json').read_text())['clips']}
LANDMARKS = {
    'side-brace': ((284, 164, 944, 691), 1109, (16, 8), 21),
    'side-shift': ((282, 165, 948, 700), 1109, (16, 8), 21),
    'side-contact': ((356, 179, 1069, 724), 1140, (16, 8), 21),
    'push-up': ((278, 145, 972, 711), 1139, (16, 8), 21),
    'push-down': ((293, 155, 944, 698), 1100, (16, 8), 21),
    'hurt-recoil': ((282, 161, 926, 702), 1108, (15, 9), 20),
    'hurt-settle': ((316, 155, 932, 688), 1097, (16, 8), 21),
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
    for name in ('side-brace', 'side-shift', 'side-contact', 'push-up', 'push-down', 'hurt-recoil', 'hurt-settle'):
        keys[name], record = trace(name); provenance.append(record)
    # Native full-pose holds with a small support-foot transfer. Torso and both
    # hands keep their complete traced contours rather than being IK pieces.
    gait = [0, 0, 1, 1, 1, 0, 0, 0, 0, -1, -1, -1, 0, 0]
    for direction, key in [('side', 'side-contact'), ('up', 'push-up'), ('down', 'push-down')]:
        frames = []
        for i, step in enumerate(gait):
            frame = keys[key].copy()
            if step:
                feet = frame.crop((0, 49, 64, 56))
                for y in range(49, 56):
                    for x in range(64): frame.putpixel((x, y), (0, 0, 0, 0))
                frame.alpha_composite(feet, (step, 49))
            frames.append(frame)
        export('push-' + direction, frames, TIMES['Walk'])
        export('push-brace-' + direction, [keys[key]], [1000])
    export('hurt-pose', [keys['hurt-recoil'], keys['hurt-settle'], BASE.copy()], [40, 50, 60])
    # The user explicitly wants the comfortable original neutral form.
    idle = [BASE.copy() for _ in range(8)]
    export('Idle', idle, [125] * 8)
    (SOURCE / 'trace-provenance.json').write_text(json.dumps(provenance, indent=2))
    print('Full-body support traces: seven generated pose sources; eight clips')


if __name__ == '__main__': main()
