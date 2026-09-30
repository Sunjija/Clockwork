"""Independent preservation and native packaging checks for traced Tique V9.

This checks real files and constraints. It cannot certify natural movement.
"""
from pathlib import Path
from collections import Counter, deque
import hashlib, json
from PIL import Image

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
ART = R / 'art/return-v9-traced'
OLD = P / 'Assets/Resources/Return/Tique'
NEW = P / 'Assets/Resources/ReturnV2/TiqueV9'


def connected(im):
    pixels = {(x, y) for y in range(64) for x in range(64) if im.getpixel((x, y))[3]}
    groups = 0
    while pixels:
        groups += 1; todo = deque([pixels.pop()])
        while todo:
            x, y = todo.popleft()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in pixels: pixels.remove(n); todo.append(n)
    return groups


def main():
    count = 0
    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1
    preserved = json.loads((P / 'QA/WorkOrderV01/original-sha256.json').read_text(encoding='utf-8-sig'))
    for rel, digest in preserved.items():
        data = (R / rel).read_bytes()
        check(digest in (hashlib.sha256(data).hexdigest(), hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()), 'original ' + rel)
    base = Image.open(OLD / 'Idle/00.png').convert('RGBA')
    palette = {p for p in base.getdata() if p[3]}
    clips = json.loads((NEW / 'clips.json').read_text())['clips']
    original_times = {c['name']: c['durations'] for c in json.loads((OLD.parent / 'clips.json').read_text())['clips']}
    frames, total = {}, 0
    for clip in clips:
        name, times = clip['name'], clip['durations']
        if name in original_times and name != 'Idle': check(times == original_times[name], name + ' authored times')
        frames[name] = []
        for index, duration in enumerate(times):
            path = NEW / name / f'{index:02d}.png'
            image = Image.open(path).convert('RGBA'); frames[name].append(image)
            pixels = set(image.getdata())
            check(image.size == (64, 64), str(path) + ' canvas')
            check({c[3] for c in pixels} <= {0, 255}, str(path) + ' alpha')
            check({c for c in pixels if c[3]} <= palette, str(path) + ' original palette')
            check(connected(image) == 1, str(path) + ' attached silhouette')
            source = OLD / name if name == 'Walk' else ART / name
            check(path.read_bytes() == (source / path.name).read_bytes(), str(path) + ' reviewed/native runtime equality')
            total += 1
        check((ART / 'Editable' / name / (name + '.piskel')).is_file(), name + ' editable source')
    check(total == 134 and len(clips) == 14, 'complete fourteen clips')
    for i in range(14):
        check((NEW / 'Walk' / f'{i:02d}.png').read_bytes() == (OLD / 'Walk' / f'{i:02d}.png').read_bytes(), 'approved Walk exact ' + str(i))
    for name, index in [('Attack', 0), ('Attack', 11), ('Jump', 14), ('DoubleJump', 12), ('Dash', 11), ('hurt-pose', 2)]:
        check(frames[name][index].tobytes() == base.tobytes(), name + ' neutral endpoint')
    check(len({f.tobytes() for f in frames['Jump'][4:10]}) >= 3, 'ascent/apex/descent distinct whole poses')
    check(frames['Jump'][9].tobytes() != frames['Jump'][10].tobytes(), 'ground impact differs from air descent')
    check(frames['DoubleJump'][8].tobytes() != frames['DoubleJump'][9].tobytes(), 'double ground impact differs from air descent')
    for i in range(12):
        check(frames['Dash'][i].getchannel('A').tobytes() == frames['dash-ghost'][i].getchannel('A').tobytes(), 'ghost matches full Dash ' + str(i))
    result = {'passed': True, 'originalAssetsPreserved': len(preserved), 'nativeFrames': total,
              'clips': len(clips), 'checks': count,
              'scope': 'Real native files, palette, alpha, silhouette connectivity, phase distinction, Walk preservation and packaging; natural motion and physical inputs excluded'}
    out = P / 'QA/V9'; out.mkdir(parents=True, exist_ok=True)
    (out / 'native-checks.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == '__main__': main()
