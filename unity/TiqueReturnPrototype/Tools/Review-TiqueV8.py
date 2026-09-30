"""Check native Tique V8 assets independently of the authoring tool.

This verifies preservation/packaging and measurable pixel constraints. A PASS
does not certify natural motion; contact sheets and actual playback still need
visual review.
"""
from pathlib import Path
from collections import deque
import hashlib
import json
from PIL import Image

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
OLD = P / 'Assets/Resources/Return/Tique'
NEW = P / 'Assets/Resources/ReturnV2/TiqueV8'
ART = R / 'art/return-v8-tique'
QA = P / 'QA/V8'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def components(image):
    alive = {(x, y) for y in range(64) for x in range(64)
             if image.getpixel((x, y))[3]}
    sizes = []
    while alive:
        seed = alive.pop()
        work = deque([seed])
        count = 0
        while work:
            x, y = work.popleft()
            count += 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    pos = (x + dx, y + dy)
                    if pos in alive:
                        alive.remove(pos)
                        work.append(pos)
        sizes.append(count)
    return sorted(sizes, reverse=True)


def run():
    checks = []
    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        checks.append(message)

    # Previous work-order baseline already locks the original 309 assets.
    baseline = json.loads((P / 'QA/WorkOrderV01/original-sha256.json').read_text(encoding='utf-8-sig'))
    preserved = 0
    for rel, digest in baseline.items():
        path = R / rel
        raw = path.read_bytes()
        normalized = raw.replace(b'\r\n', b'\n')
        check(hashlib.sha256(raw).hexdigest() == digest or
              hashlib.sha256(normalized).hexdigest() == digest,
              'preserved ' + rel)
        preserved += 1

    old_clips = json.loads((P / 'Assets/Resources/Return/clips.json').read_text(encoding='utf-8-sig'))
    clips = json.loads((NEW / 'clips.json').read_text(encoding='utf-8-sig'))['clips']
    by_name = {c['name']: c for c in clips}
    base = Image.open(OLD / 'Idle/00.png').convert('RGBA')
    palette = {p for p in base.getdata() if p[3]}
    head_pixels = [(x, y, base.getpixel((x, y))) for y in range(8, 33) for x in range(16, 47)
                   if base.getpixel((x, y))[3]]
    def approved_head(image):
        return any(all(image.getpixel((x + dx, y + dy)) == colour for x, y, colour in head_pixels)
                   for dx in range(-3, 4) for dy in range(-2, 4))
    check(len(palette) == 13, 'approved palette has thirteen opaque colours')
    check(by_name['Idle']['durations'] == [125] * 8, 'calm idle loop keeps one second')
    for old in old_clips['clips']:
        if old['name'] != 'Idle':
            check(by_name[old['name']]['durations'] == old['durations'],
                  old['name'] + ' retains authored durations and frame count')

    frames = {}
    total = 0
    for clip in clips:
        name = clip['name']
        frames[name] = []
        for i in range(len(clip['durations'])):
            path = NEW / name / f'{i:02d}.png'
            image = Image.open(path).convert('RGBA')
            check(image.size == (64, 64), f'{name}/{i:02d} native canvas')
            check(set(image.getchannel('A').getdata()) <= {0, 255}, f'{name}/{i:02d} binary alpha')
            check(image.getbbox() is not None, f'{name}/{i:02d} nonempty')
            if name != 'dash-ghost':
                check({p for p in image.getdata() if p[3]} <= palette, f'{name}/{i:02d} locked palette')
                check(len(components(image)) == 1, f'{name}/{i:02d} connected character')
            if name in {'Idle','Attack','Jump','DoubleJump','Dash','hurt-pose'}:
                check(approved_head(image), f'{name}/{i:02d} exact approved head and eyes, translation only')
            check(path.read_bytes() == (ART / 'Clips' / name / f'{i:02d}.png').read_bytes(),
                  f'{name}/{i:02d} actual runtime matches reviewed frame')
            frames[name].append(image)
            total += 1
        check((ART / 'Clips' / name / f'{name}.piskel').exists(), name + ' editable source packaged')

    for i in range(14):
        check(frames['Walk'][i].tobytes() == Image.open(OLD / 'Walk' / f'{i:02d}.png').convert('RGBA').tobytes(),
              f'approved Walk/{i:02d} unchanged')
    for name, index in [('Attack', 0), ('Attack', 11), ('Jump', 14), ('DoubleJump', 12), ('Dash', 11), ('hurt-pose', 2)]:
        check(frames[name][index].tobytes() == base.tobytes(), f'{name}/{index:02d} connects to neutral idle')
    for name, indices in [('Dash', range(3, 7)), ('Jump', range(4, 7)), ('DoubleJump', range(0, 4))]:
        check(len({frames[name][i].tobytes() for i in indices}) == len(indices), name + ' selected active exposures differ')
    check(len(frames['dash-ghost']) == len(frames['Dash']), 'dash ghosts cover every selected index')

    result = {'passed': True, 'preservedOriginalAssets': preserved, 'nativeFrames': total,
              'clips': len(clips), 'checks': len(checks),
              'scope': 'Native constraints and preservation; subjective motion needs playback inspection.'}
    QA.mkdir(parents=True, exist_ok=True)
    (QA / 'native-checks.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    run()
