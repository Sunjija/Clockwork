"""v6 polish pass over the v5 feedback set.

Re-authors the v5 clips that did not read at 1x (HUD cells, effects, icons,
Tique contact poses). Sprites are written as explicit native pixels: small
parts as character grids with a named palette, regular shapes (cells, rings,
particle paths) as integer pixel rules. Nothing is resampled from an image.

Each re-authored clip replaces the v5 frames in place so the game and
Review-WorkOrder.py keep their paths:
  unity/.../Resources/ReturnV2/Feedback/<clip>/NN.png, clips.json
  art/return-v5-feedback/Clips/<clip>/NN.png, NN.pixels.json, sheet.png, native.apng, <clip>.piskel
and is listed in art/return-v5-feedback/polish-v6.json. Re-running the v5
author_return_feedback.py would overwrite these clips; run this tool after it.
"""
from pathlib import Path
import base64, hashlib, io, json, math, shutil
from PIL import Image

R = Path(__file__).resolve().parents[2]
ART = R / 'art/return-v5-feedback'
OUT = R / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/Feedback'
TIQUE = R / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique'

HEX = {
    '.': None,
    'k': '#0b1116', 'K': '#101921', 'n': '#1a2630', 'N': '#2a3945',       # outlines, sockets
    'g': '#56707a', 'G': '#9fb4bc', 'w': '#eaffed',                     # steel, pale, white
    'd': '#1d6f78', 'c': '#19c1d1', 'C': '#51e0df', 'l': '#a7f9f1',     # Tique cyan ramp
    'r': '#6e2410', 'o': '#d8622a', 'O': '#ffa94d', 'y': '#ffe6a0',     # core / iron ramp
    'b': '#795333', 'B': '#efb758', 'u': '#543e30', 'U': '#a46e39',     # brass
    'e': '#887d68', 'E': '#c9bca0', 'f': '#5d5446',                     # dust
}


def rgba(ch):
    h = HEX[ch]
    return (0, 0, 0, 0) if h is None else (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)


def grid(rows):
    """Character grid -> RGBA image. Every row must have the same width."""
    w = len(rows[0])
    assert all(len(r) == w for r in rows), rows
    im = Image.new('RGBA', (w, len(rows)))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            im.putpixel((x, y), rgba(ch))
    return im


def blank(w, h):
    return Image.new('RGBA', (w, h))


def put(im, x, y, ch):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), rgba(ch))


# ---------------------------------------------------------------- export
CLIPS = json.loads((OUT / 'clips.json').read_text(encoding='utf-8'))
POLISHED = []


def export(name, frames, times, note):
    assert len(frames) == len(times)
    w, h = frames[0].size
    for im in frames:
        assert im.size == (w, h) and set(im.getchannel('A').getdata()) <= {0, 255}, name
    folder, dest = ART / 'Clips' / name, OUT / name
    folder.mkdir(parents=True, exist_ok=True); dest.mkdir(parents=True, exist_ok=True)
    for old in list(folder.glob('[0-9][0-9].*')) + list(dest.glob('[0-9][0-9].png')):
        old.unlink()
    sheet = Image.new('RGBA', (w * len(frames), h))
    for i, im in enumerate(frames):
        im.save(folder / f'{i:02d}.png')
        shutil.copyfile(folder / f'{i:02d}.png', dest / f'{i:02d}.png')
        meta = dest / f'{i:02d}.png.meta'
        if not meta.exists():  # new frame index: reuse frame 00's importer settings with a new GUID
            text = (dest / '00.png.meta').read_text()
            guid = hashlib.md5(f'clockwork/{name}/{i}'.encode()).hexdigest()
            meta.write_text(text.replace(text.split('\n')[1], 'guid: ' + guid))
        px = [[x, y, *im.getpixel((x, y))] for y in range(h) for x in range(w) if im.getpixel((x, y))[3]]
        (folder / f'{i:02d}.pixels.json').write_text(json.dumps(px, separators=(',', ':')))
        sheet.alpha_composite(im, (i * w, 0))
    for extra in sorted(dest.glob('[0-9][0-9].png.meta')):
        if int(extra.name[:2]) >= len(frames):
            extra.unlink()
    sheet.save(folder / 'sheet.png')
    apng = folder / 'native.apng'
    if len(frames) > 1:
        frames[0].save(apng, save_all=True, append_images=frames[1:], duration=times, loop=0, disposal=0, blend=0)
    elif apng.exists():
        apng.unlink()
    buf = io.BytesIO(); sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames),
             'chunks': [{'layout': [[i] for i in range(len(frames))],
                         'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    (folder / f'{name}.piskel').write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'v6 native pixels; variable timing in clips.json and native.apng.',
        'fps': 20, 'width': w, 'height': h, 'layers': [json.dumps(layer)]}}))
    entry = next(c for c in CLIPS['clips'] if c['name'] == name)
    entry.update(durations=list(times), width=w, height=h)
    POLISHED.append({'clip': name, 'frames': len(frames), 'size': [w, h], 'durations': list(times), 'why': note})


def save_index():
    text = json.dumps(CLIPS, indent=2, ensure_ascii=False)
    (OUT / 'clips.json').write_text(text, encoding='utf-8')
    (ART / 'clips.json').write_text(text, encoding='utf-8')
    (ART / 'polish-v6.json').write_text(json.dumps({
        'tool': 'tools/art/author_return_polish.py',
        'method': 'explicit native pixels (character grids / integer pixel rules); no resampling of generated images',
        'clips': POLISHED}, indent=2, ensure_ascii=False), encoding='utf-8')


# ---------------------------------------------------------------- HUD cells
def cell(w, h, outline, rim, fill, hi, lo, chamfer):
    """A power cell that fills its whole slot: outline, rim, lit fill, top-left
    highlight and a darker bottom edge. chamfer cuts the corners (iron plates)."""
    im = blank(w, h)
    for y in range(h):
        for x in range(w):
            edge = min(x, y, w - 1 - x, h - 1 - y)
            corner = min(x, w - 1 - x) + min(y, h - 1 - y)
            if corner < chamfer:
                continue
            if edge == 0 or corner == chamfer:
                ch = outline
            elif edge == 1:
                ch = rim
            elif y >= h - 3:
                ch = lo
            elif (x <= 3 and y <= 3) or y == 2:
                ch = hi
            else:
                ch = fill
            if ch:
                put(im, x, y, ch)
    return im


def hud_cells():
    tique = dict(chamfer=1)
    iron = dict(chamfer=2)
    export('tique-cell-full', [cell(10, 12, 'k', 'd', 'C', 'l', 'c', **tique)], [1000],
           'v5 cell was a 4px capsule inside an 8x10 slot; reads as a tick at 1x')
    export('tique-cell-empty', [cell(10, 12, 'k', 'N', 'n', 'n', 'K', **tique)], [1000], 'matching empty socket')
    export('tique-cell-ghost', [cell(10, 12, 'k', 'g', 'G', 'w', 'g', **tique)], [1000],
           'pale steel afterimage, never brighter than a live cell')
    export('iron-full', [cell(10, 12, 'k', 'r', 'o', 'O', 'r', **iron)], [1000], 'iron cell fills its slot; chamfered plate vs round Tique cell')
    export('iron-empty', [cell(10, 12, 'k', 'N', 'n', 'n', 'K', **iron)], [1000], 'matching empty socket')
    export('iron-ghost', [cell(10, 12, 'k', 'u', 'E', 'y', 'e', **iron)], [1000], 'dim afterimage')


# ---------------------------------------------------------------- effect primitives
def disc(im, cx, cy, r, ch, floor=None):
    """Integer pixel disc; floor clips anything below that row (ground effects).
    Tiny radii become a 2x2 or 1x1 block instead of a plus sign."""
    if r < 1.3:
        n = 2 if r >= .8 else 1
        for y in range(round(cy), round(cy) + n):
            for x in range(round(cx), round(cx) + n):
                if floor is None or y <= floor:
                    put(im, x, y, ch)
        return
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * .8 and (floor is None or y <= floor):
                put(im, x, y, ch)


def puff(im, cx, cy, r, light='E', mid='e', dark='f', floor=None):
    """Shaded dust puff: dark base, mid body, light cap offset up-left."""
    disc(im, cx, cy, r, dark, floor)
    if r >= 1.5:
        disc(im, cx - .5, cy - .6, r - .8, mid, floor)
    if r >= 2.5:
        disc(im, cx - 1, cy - 1.2, r - 1.9, light, floor)


def line(im, x0, y0, x1, y1, ch):
    x0, y0, x1, y1 = map(round, (x0, y0, x1, y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        put(im, x0, y0, ch)
        if (x0, y0) == (x1, y1):
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy


def ray(im, cx, cy, angle, r0, r1, ch):
    a = math.radians(angle)
    line(im, cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * r1, cy + math.sin(a) * r1, ch)


def ellipse(im, cx, cy, rx, ry, ch, keep=lambda a: True):
    seen = set()
    for step in range(0, 360, 3):
        a = math.radians(step)
        p = (round(cx + math.cos(a) * rx), round(cy + math.sin(a) * ry))
        if p not in seen and keep(step):
            seen.add(p); put(im, *p, ch)


def bolt(im, x0, y0, x1, y1, ch, jag, seed):
    """Zig-zag electric arc between two points with a fixed jitter pattern."""
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) // 3))
    pts = [(x0, y0)]
    nx, ny = -(y1 - y0), (x1 - x0)
    ln = math.hypot(nx, ny) or 1
    for i in range(1, n):
        t = i / n
        off = jag * (1 if (i + seed) % 2 else -1)
        pts.append((x0 + (x1 - x0) * t + nx / ln * off, y0 + (y1 - y0) * t + ny / ln * off))
    pts.append((x1, y1))
    for a, b in zip(pts, pts[1:]):
        line(im, *a, *b, ch)


def particles(w, h, specs, t, floor=None, g=60.0):
    """Debris pixels on ballistic paths. spec = (x, y, vx, vy, [(until, ch, size), ...])."""
    im = blank(w, h)
    for x, y, vx, vy, stages in specs:
        px, py = x + vx * t, y + vy * t + .5 * g * t * t
        if floor is not None and py > floor:
            py = floor
        for until, ch, size in stages:
            if t < until:
                if ch:
                    for dy in range(size):
                        for dx in range(size):
                            put(im, round(px) + dx, round(py) + dy, ch)
                break
    return im


def layer(*ims):
    out = ims[0].copy()
    for im in ims[1:]:
        out.alpha_composite(im)
    return out


def times_at(durations):
    """Start time (s) of each exposure, used to place particles on real time."""
    t, out = 0, []
    for d in durations:
        out.append(t / 1000); t += d
    return out


# ---------------------------------------------------------------- effects
def fx_core_hit():
    # Fist meets the open core: white contact core, warm star, breaking streaks,
    # falling embers. Centre (12,12) is the stored contact point.
    d = [25, 30, 35, 40, 40]
    f0 = blank(24, 24); disc(f0, 12, 12, 2.2, 'w'); ray(f0, 12, 12, 0, 3, 4, 'y'); ray(f0, 12, 12, 180, 3, 4, 'y')
    ray(f0, 12, 12, 90, 3, 4, 'y'); ray(f0, 12, 12, 270, 3, 4, 'y')
    f1 = blank(24, 24)
    for a in (0, 90, 180, 270):
        ray(f1, 12, 12, a, 2, 9, 'O'); ray(f1, 12, 12, a, 1, 6, 'y')
    for a in (45, 135, 225, 315):
        ray(f1, 12, 12, a, 3, 5, 'o')
    disc(f1, 12, 12, 1.5, 'w')
    f2 = blank(24, 24)
    for a in range(0, 360, 45):
        r0, r1 = (6, 10) if a % 90 == 0 else (5, 8)
        ray(f2, 12, 12, a, r0, r1, 'O' if a % 90 == 0 else 'o'); ray(f2, 12, 12, a, r0, r0 + 1, 'y')
    # Uneven speeds so the embers scatter instead of forming a ring.
    embers = [(12 + 6 * math.cos(math.radians(a)), 12 + 6 * math.sin(math.radians(a)),
               (20 + k % 3 * 8) * math.cos(math.radians(a)), (20 + k % 3 * 8) * math.sin(math.radians(a)) - 15,
               [(.1, 'O', 2), (.2, 'o', 1)]) for k, a in enumerate(range(10, 360, 50))]
    t = times_at(d)
    f3 = particles(24, 24, embers, t[3] - t[2] + .02, g=110)
    f4 = particles(24, 24, embers[::2], t[4] - t[2] + .02, g=110)
    return [f0, f1, f2, f3, f4], d


def fx_hurt():
    # Tique takes damage: cold, jagged break (cyan/white), clearly not the warm core hit.
    d = [30, 40, 45, 55]
    f0 = blank(24, 24)
    for a in (20, 110, 200, 290):
        ray(f0, 12, 12, a, 0, 4, 'w')
    disc(f0, 12, 12, 1, 'w')
    f1 = blank(24, 24)
    for i, a in enumerate(range(0, 360, 60)):
        r1 = 9 if i % 2 else 7
        ray(f1, 12, 12, a + 15, 3, r1, 'C'); ray(f1, 12, 12, a + 15, 3, 4, 'w')
    ellipse(f1, 12, 12, 3, 3, 'l')
    shards = [(12 + 6 * math.cos(math.radians(a)), 12 + 6 * math.sin(math.radians(a)),
               55 * math.cos(math.radians(a)), 55 * math.sin(math.radians(a)) - 10,
               [(.07, 'l', 2), (.14, 'C', 1), (.2, 'd', 1)]) for a in range(15, 375, 60)]
    t = times_at(d)
    f2 = particles(24, 24, shards, .03, g=120)
    f3 = particles(24, 24, shards, t[3] - t[2] + .05, g=120)
    return [f0, f1, f2, f3], d


def fx_armor():
    # Punch on closed armour: dull tick and grey/brass chips bouncing back (faces +x;
    # the game flips it with the punch direction). No hit spark, no core colours.
    d = [40, 50, 50]
    f0 = blank(20, 16)
    line(f0, 13, 5, 15, 7, 'G'); line(f0, 15, 7, 13, 9, 'G'); put(f0, 16, 7, 'w'); put(f0, 12, 7, 'g')
    chips = [(13, 7, -45, -35, [(.1, 'G', 2), (.2, 'g', 1)]), (13, 8, -55, -5, [(.1, 'B', 2), (.2, 'b', 1)]),
             (14, 6, -30, -55, [(.12, 'G', 1)]), (14, 9, -35, 15, [(.1, 'g', 2), (.2, 'g', 1)])]
    f1 = layer(particles(20, 16, chips, .035, g=150)); put(f1, 15, 7, 'G')
    f2 = particles(20, 16, chips, .09, g=150)
    return [f0, f1, f2], d


def fx_air():
    # Whiff: a short pale arc that ends at the fist's real reach, nothing else.
    d = [30, 40, 40]
    frames = []
    for i, (a0, a1, ch) in enumerate([(-60, 10, 'w'), (-40, 35, 'l'), (-10, 45, 'd')]):
        im = blank(20, 16)
        for k, a in enumerate(range(a0, a1, 4)):
            r = math.radians(a)
            if i < 2 or k % 2 == 0:  # the last exposure breaks into dots
                put(im, round(8 + 7 * math.cos(r)), round(8 + 6 * math.sin(r)), ch)
        frames.append(im)
    return frames, d


def fx_boost():
    # Second jump in the air: flat cyan ring pushed down from the feet.
    d = [30, 40, 45, 55]
    frames = []
    for rx, ry, cy, ch, hi, gap in [(4, 1, 12, 'w', 'w', 0), (7, 2, 14, 'C', 'w', 0), (9, 3, 16, 'c', 'C', 40), (10, 3, 18, 'd', 'd', 60)]:
        im = blank(24, 24)
        ellipse(im, 12, cy, rx, ry, ch, keep=lambda a, g=gap: g == 0 or (a // g) % 2 == 0)
        if hi != ch:
            ellipse(im, 12, cy, rx, ry, hi, keep=lambda a: 200 < a < 340)
        frames.append(im)
    return frames, d


def fx_pylon_impact():
    # Charged pylon struck by the charge: electric discharge (cyan arcs, gold sparks).
    d = [25, 30, 30, 30, 35]
    f0 = blank(24, 24); disc(f0, 12, 12, 1.5, 'w')
    for a in (45, 135, 225, 315):
        ray(f0, 12, 12, a, 2, 4, 'l')
    f1 = blank(24, 24)
    for i, a in enumerate((20, 100, 170, 250, 320)):
        r = math.radians(a)
        bolt(f1, 12, 12, 12 + math.cos(r) * 10, 12 + math.sin(r) * 10, 'C', 1.2, i)
    disc(f1, 12, 12, 1.5, 'w')
    f2 = blank(24, 24)
    for i, a in enumerate((40, 130, 210, 290)):
        r = math.radians(a)
        bolt(f2, 12 + math.cos(r) * 4, 12 + math.sin(r) * 4, 12 + math.cos(r) * 11, 12 + math.sin(r) * 11, 'c', 1, i)
    sparks = [(12 + 5 * math.cos(math.radians(a)), 12 + 5 * math.sin(math.radians(a)),
               (60 + k % 3 * 25) * math.cos(math.radians(a)), (60 + k % 3 * 25) * math.sin(math.radians(a)) - 25,
               [(.07, 'B', 2), (.14, 'b', 1)]) for k, a in enumerate(range(0, 360, 40))]
    t = times_at(d)
    f2.alpha_composite(particles(24, 24, sparks, t[2] - t[1], g=160))
    f3 = particles(24, 24, sparks, t[3] - t[1], g=160)
    f4 = particles(24, 24, sparks[::2], t[4] - t[1], g=160)
    return [f0, f1, f2, f3, f4], d


def fx_dust():
    # Shared jump/land/dash dust (32x16, ground row 15): a full cloud of overlapping
    # shaded puffs on the contact beat, rolling outward and thinning, with specks.
    d = [30, 40, 40, 45, 45]
    specks = [(16 + s * 3, 13, s * v, -35 - v // 3, [(.1, 'e', 1), (.2, 'f', 1)]) for s in (-1, 1) for v in (40, 70)]
    t = times_at(d)
    frames = []
    for i, (spread, r, lift, n) in enumerate([(3, 2.4, 0, 2), (6, 3.4, 0, 3), (9, 3.2, 1, 3), (12, 2.4, 2, 2), (13, 1.4, 3, 1)]):
        im = blank(32, 16)
        for side in (-1, 1):
            for k in reversed(range(n)):
                cx = 16 + side * (spread - k * 3)
                puff(im, cx, 14 - lift - k * .7 - r * .3, r - k * .45, floor=15)
        if i:
            im.alpha_composite(particles(32, 16, specks, t[i] + .02, floor=15, g=200))
        frames.append(im)
    line(frames[0], 11, 15, 21, 15, 'e'); line(frames[1], 8, 15, 24, 15, 'f')
    return frames, d


def fx_slam_dust():
    # Warden landing (96x24): thin shock line, two low dust walls, debris arcs.
    d = [35, 35, 40, 40, 45, 45]
    debris = [(48 + s * 8, 20, s * v, -60 - (v % 20), [(.14, 'g', 2), (.22, 'g', 1)]) for s in (-1, 1) for v in (40, 70, 95)]
    t = times_at(d)
    frames = []
    # Overlapping puffs make one low dust wall per side that rolls outward and thins.
    for i, (reach, puffs, r) in enumerate([(22, 0, 0), (34, 4, 4.4), (40, 5, 5.0), (44, 5, 4.4), (46, 4, 3.2), (47, 3, 1.8)]):
        im = blank(96, 24)
        if i < 2:
            line(im, 48 - reach, 23, 48 + reach, 23, 'E' if i == 0 else 'e'); line(im, 44, 22, 52, 22, 'w' if i == 0 else 'E')
        for s in (-1, 1):
            for k in reversed(range(puffs)):
                # Alternate big/small puffs and heights so the wall reads as one cloud.
                rk = r - k * .45 + (.8 if k % 2 == 0 else -.4)
                cx = 48 + s * (9 + k * 6 + i * 4)
                puff(im, cx, 22 - rk * .6 - (k % 2) * 1.5 - i * .3, rk, floor=23)
        if i:
            im.alpha_composite(particles(96, 24, debris, t[i] + .02, floor=23, g=260))
        frames.append(im)
    return frames, d


def fx_friction():
    # Weight dragged one tile (faces +x): low scrape puffs trailing behind the base.
    d = [40, 40, 40, 40]
    frames = []
    for i in range(4):
        im = blank(32, 16)
        for k in range(3 - i // 2):
            x = 12 - k * 5 - i * 2
            puff(im, x, 14 - k * .5, 1.8 - k * .4 - i * .2, floor=15)
        if i < 2:
            line(im, 14, 15, 22 - i * 3, 15, 'f')
        frames.append(im)
    return frames, d


def fx_wall_brake():
    # Charge hits a plain wall (faces +x toward the wall): heavy grey chips and a
    # dust burst at the foot, no cyan discharge.
    d = [40, 40, 40, 40]
    chips = [(24, 10, -60, -50, [(.1, 'G', 2), (.16, 'g', 1)]), (24, 12, -80, -20, [(.1, 'G', 2), (.16, 'g', 1)]),
             (25, 8, -40, -70, [(.12, 'B', 1)]), (23, 13, -50, 5, [(.1, 'g', 2)])]
    frames = []
    for i in range(4):
        im = blank(32, 16)
        puff(im, 22 - i * 2, 13 - i * .4, 2.4 + i * .3 - (i == 3) * 1.2, floor=15)
        puff(im, 17 - i * 3, 14 - i * .3, 1.6 + (i == 1) * .6 - (i >= 2) * .6, floor=15)
        if i == 0:
            line(im, 26, 6, 26, 14, 'G'); put(im, 27, 10, 'w')
        im.alpha_composite(particles(32, 16, chips, .02 + i * .04, floor=15, g=200))
        frames.append(im)
    return frames, d


def fx_weight_settle():
    # Weight stops on its tile: two tiny puffs pinched out at both base corners.
    d = [45, 45, 50]
    frames = []
    for off, r in [(12, 1.6), (14, 1.9), (15, 1.2)]:
        im = blank(32, 16)
        for s in (-1, 1):
            puff(im, 16 + s * off, 14, r, floor=15)
        frames.append(im)
    line(frames[0], 5, 15, 27, 15, 'f')
    return frames, d


def fx_orb_release():
    # Orb pushed (faces +x, orb ahead): three short cyan push lines behind it.
    d = [40, 50, 50]
    frames = []
    for i in range(3):
        im = blank(24, 16)
        for k, y in enumerate((5, 8, 11)):
            x1 = 12 - i * 3 - (k == 1) * 2
            ln = 5 - i - (k != 1)
            if ln > 0:
                line(im, x1 - ln, y, x1, y, 'l' if i == 0 else 'C' if i == 1 else 'd')
        frames.append(im)
    return frames, d


def fx_orb_stop():
    # Orb meets a wall/object. Emitted on the orb's front edge for any of the four
    # push directions, so the mark is symmetric: a cyan contact ring that breaks up.
    d = [40, 50, 50]
    frames = []
    for i, (r, ch, gap) in enumerate([(2, 'w', 0), (4, 'C', 45), (6, 'd', 30)]):
        im = blank(24, 16)
        ellipse(im, 12, 8, r, r * .75, ch, keep=lambda a, g=gap: g == 0 or (a // g) % 2 == 0)
        if i == 0:
            put(im, 12, 8, 'l')
        frames.append(im)
    return frames, d


def fx_bridge():
    # Pylon end of the charge wire: a small electric star at the coil.
    d = [30, 30, 40]
    f0 = blank(32, 32); disc(f0, 16, 16, 2, 'w')
    for a in (0, 90, 180, 270):
        ray(f0, 16, 16, a, 2, 5, 'l')
    f1 = blank(32, 32)
    for i, a in enumerate((30, 120, 210, 300)):
        r = math.radians(a)
        bolt(f1, 16, 16, 16 + math.cos(r) * 8, 16 + math.sin(r) * 8, 'C', 1, i)
    disc(f1, 16, 16, 1, 'w')
    f2 = blank(32, 32)
    for a in (60, 150, 240, 330):
        r = math.radians(a)
        put(f2, round(16 + math.cos(r) * 9), round(16 + math.sin(r) * 9), 'c')
        put(f2, round(16 + math.cos(r) * 6), round(16 + math.sin(r) * 6), 'd')
    return [f0, f1, f2], d


def fx_dash_ghost():
    # Afterimages from Tique's own Dash frames: cyan outline, sparse dark fill, so
    # two trailing copies read as echoes and never as a second solid body.
    frames = []
    for i in range(12):
        src = Image.open(TIQUE / 'Dash' / f'{i:02d}.png').convert('RGBA')
        a = src.getchannel('A')
        im = blank(64, 64)
        for y in range(64):
            for x in range(64):
                if not a.getpixel((x, y)):
                    continue
                edge = any(not (0 <= x + dx < 64 and 0 <= y + dy < 64) or not a.getpixel((x + dx, y + dy))
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge:
                    put(im, x, y, 'C')
                elif (x + y) % 2 == 0:
                    put(im, x, y, 'd')
        frames.append(im)
    d = json.loads((R / 'unity/TiqueReturnPrototype/Assets/Resources/Return/clips.json').read_text())
    return frames, next(c['durations'] for c in d['clips'] if c['name'] == 'Dash')


def fx_chute():
    # Ceiling hatch Tique drops out of in the opening (48x40): riveted frame, dark
    # shaft, one flap hanging open. Drawn over the workshop background.
    im = blank(48, 40)
    for y in range(0, 12):
        for x in range(4, 44):
            edge = x in (4, 43) or y in (0, 11)
            put(im, x, y, 'k' if edge else ('N' if y <= 2 else 'K'))
    for x in range(6, 42):  # brass lip under the frame
        put(im, x, 12, 'b'); put(im, x, 13, 'k')
    for x in range(8, 40, 8):
        put(im, x, 1, 'B'); put(im, x + 1, 1, 'U')
    for x in (5, 42):
        for y in range(3, 11):
            put(im, x, y, 'g')
    # flap hinged on the right lip, hanging down at an angle
    for k in range(18):
        x, y = 40 - k // 3, 14 + k
        for t in range(4):
            put(im, x - t, y, 'k' if t in (0, 3) else ('G' if t == 1 else 'g'))
    for y in range(14, 32, 5):
        put(im, 39 - (y - 14) // 3 - 1, y, 'B')
    return [im], [1000]


def effects():
    for name, fn, note in [
        ('hit', fx_core_hit, 'white contact core -> warm star -> streaks -> falling embers; no grid dissolve'),
        ('hurt', fx_hurt, 'cold jagged break, distinct from the warm core hit'),
        ('armor', fx_armor, 'v5 chips were dark brown and vanished on the dark arena'),
        ('air', fx_air, 'short arc limited to the fist reach'),
        ('boost', fx_boost, 'flat ring pushed down from the feet'),
        ('pylon-impact', fx_pylon_impact, 'electric arcs + gold sparks; v5 reused the hit star in orange'),
        ('dust', fx_dust, 'shaded puffs spreading and shrinking; v5 ended in vertical bars'),
        ('slam-dust', fx_slam_dust, 'low shock line, dust walls, debris arcs; v5 ended in a dotted grid'),
        ('friction', fx_friction, 'low scrape trail; v5 was identical to wall-brake'),
        ('wall-brake', fx_wall_brake, 'heavy chips + dust; separate from puzzle friction'),
        ('weight-settle', fx_weight_settle, 'two small corner puffs'),
        ('orb-release', fx_orb_release, 'push lines behind the orb; v5 was identical to orb-stop'),
        ('orb-stop', fx_orb_stop, 'symmetric contact ring; v5 was identical to orb-release'),
        ('bridge', fx_bridge, 'electric star at the pylon coil'),
        ('dash-ghost', fx_dash_ghost, 'outline echo instead of a solid teal body'),
        ('chute', fx_chute, 'v5 chute was a faint brown outline; now a riveted hatch with a hanging flap'),
    ]:
        frames, d = fn()
        export(name, frames, d, note)


# ---------------------------------------------------------------- icons
def icon(rows, main, second='g', size=12):
    """10x10 mask ('#' main colour, '+' second colour) centred in a 12x12 cell with
    a dark one-pixel outline, so every icon reads on panels and on the world."""
    im = blank(size, size)
    pad = (size - len(rows[0])) // 2
    filled = set()
    for y, row in enumerate(rows):
        assert len(row) == len(rows[0]), rows
        for x, ch in enumerate(row):
            if ch != '.':
                put(im, x + pad, y + pad, main if ch == '#' else second if ch == '+' else ch)
                filled.add((x + pad, y + pad))
    for x, y in filled:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
            p = (x + dx, y + dy)
            if p not in filled and 0 <= p[0] < size and 0 <= p[1] < size:
                put(im, *p, 'k')
    return im


ICONS = {
    'icon-jump': ('C', 'g', 'up arrow leaving the floor line', [
        '....##....',
        '...####...',
        '..######..',
        '.###..###.',
        '....##....',
        '....##....',
        '....##....',
        '..........',
        '++++++++++',
        '..........']),
    'icon-dash': ('C', 'd', 'forward arrow with speed lines', [
        '..........',
        '.....#....',
        '.....##...',
        '++.######.',
        '....######',
        '++.######.',
        '.....##...',
        '.....#....',
        '..........',
        '..........']),
    'icon-attack': ('B', 'w', 'punch impact burst (a 10px fist read as a mushroom)', [
        '....#.....',
        '.#..#..#..',
        '..#.#.#...',
        '...###....',
        '####+####.',
        '...###....',
        '..#.#.#...',
        '.#..#..#..',
        '....#.....',
        '..........']),
    'icon-interact': ('C', 'l', 'charge bolt', [
        '.....###..',
        '....###...',
        '...###....',
        '..#######.',
        '....###...',
        '...###....',
        '..###.....',
        '.##.......',
        '..........',
        '..........']),
    'icon-undo': ('G', 'g', 'arrow curling back to the left', [
        '..........',
        '..#.......',
        '.##+++++..',
        '#########.',
        '.##.....##',
        '..#......#',
        '.........#',
        '........##',
        '...######.',
        '..........']),
    'icon-reset': ('G', 'g', 'closed loop with arrowhead', [
        '...####...',
        '..#....#..',
        '.#......##',
        '.#.....###',
        '.#......#.',
        '.#........',
        '.#......#.',
        '..#....#..',
        '...####...',
        '..........']),
    'icon-hint': ('B', 'g', 'light bulb', [
        '...####...',
        '..##++##..',
        '.##+####..',
        '.#+#####..',
        '.#######..',
        '..#####...',
        '...###....',
        '...+++....',
        '...+++....',
        '....+.....']),
    'icon-locked': ('B', 'k', 'padlock', [
        '...####...',
        '..#....#..',
        '..#....#..',
        '.########.',
        '.########.',
        '.###++###.',
        '.####+###.',
        '.####+###.',
        '.########.',
        '..........']),
    'icon-pause': ('G', 'g', 'two bars', [
        '..........',
        '..##..##..',
        '..##..##..',
        '..##..##..',
        '..##..##..',
        '..##..##..',
        '..##..##..',
        '..##..##..',
        '..........',
        '..........']),
}


def protect_ring():
    # Invulnerability mark: broken cyan ring around the heart (world, centred on the
    # chest) and beside the HUD meter. Four arcs with gaps, never a solid shield.
    im = blank(24, 24)
    ellipse(im, 11.5, 11.5, 9, 9, 'k', keep=lambda a: (a + 20) % 90 < 60)
    ellipse(im, 11.5, 11.5, 8, 8, 'C', keep=lambda a: (a + 20) % 90 < 60)
    ellipse(im, 11.5, 11.5, 7, 7, 'd', keep=lambda a: (a + 20) % 90 < 60)
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        put(im, round(11.5 + math.cos(r) * 8), round(11.5 + math.sin(r) * 8), 'l')
    return im


def icons():
    for name, (main, second, why, rows) in ICONS.items():
        export(name, [icon(rows, main, second)], [1000], why + '; v5 12px icons were muddy brown/cyan blobs')
    export('protect', [protect_ring()], [1000], 'broken ring; v5 was four faint corner ticks')


# ---------------------------------------------------------------- Tique contact poses
# Built only from approved Tique pixels: Walk/Idle bodies with their swinging arms
# removed, plus the forward arm of Attack/05 so the fist stops on the pushed
# object's face. Up/down pushes rotate that same arm
# with RotSprite about the shoulder. The far arm is the same arm one shade darker.
import numpy as np

OUTLINE = (0x2b, 0x1b, 0x24, 255)
DARKER = {(0xf4, 0xcb, 0x70): (0xdd, 0xa1, 0x4b), (0xff, 0xe7, 0xa3): (0xf4, 0xcb, 0x70),
          (0xdd, 0xa1, 0x4b): (0xbc, 0x78, 0x3b), (0xbc, 0x78, 0x3b): (0x9c, 0x59, 0x38),
          (0x9c, 0x59, 0x38): (0x75, 0x40, 0x32), (0x75, 0x40, 0x32): (0x52, 0x30, 0x28),
          (0x52, 0x30, 0x28): (0x2b, 0x1b, 0x24)}
TORSO = (24, 40)          # idle torso columns; arms live outside them
ARM_ROWS = (34, 48)       # rows where the idle arms hang
SHOULDER = (40, 39)       # idle-space shoulder the arm attaches to


def load_np(path):
    return np.array(Image.open(path).convert('RGBA'))


IDLE = load_np(TIQUE / 'Idle/00.png')
TIQUE_PALETTE = np.array(sorted({tuple(p) for p in IDLE.reshape(-1, 4) if p[3]}), dtype=np.int32)


def body_offset(frame):
    """Integer (dx, dy) of this frame's head relative to Idle (Walk bobs by 0-1px)."""
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if (np.roll(np.roll(IDLE, dy, 0), dx, 1)[4:30, 8:56] == frame[4:30, 8:56]).all():
                return dx, dy
    raise ValueError('head does not match Idle')


def armless(frame, offset=None):
    dx, dy = offset or body_offset(frame)
    out = frame.copy()
    y0, y1 = ARM_ROWS[0] + dy, ARM_ROWS[1] + dy
    x0, x1 = TORSO[0] + dx, TORSO[1] + dx
    out[y0:y1, :x0] = 0
    out[y0:y1, x1 + 1:] = 0
    a = out[..., 3] > 0
    for y in range(y0, y1):          # close the torso sides where the arms were
        for x in (x0, x1):
            if a[y, x] and (not a[y, x - 1] or not a[y, x + 1]):
                out[y, x] = OUTLINE
    return out, (dx, dy)


def forward_arm(cut=3):
    """Attack/05 arm (x>=46), with `cut` forearm columns removed."""
    atk = load_np(TIQUE / 'Attack/05.png')
    arm = np.zeros_like(atk)
    arm[38:47, 46:] = atk[38:47, 46:]
    short = np.zeros_like(arm)
    short[:, :48] = arm[:, :48]
    short[:, 48:64 - cut] = arm[:, 48 + cut:64]
    # Attack/05's body sits 3 rows lower than Idle and its shoulder at x 46.
    return np.roll(np.roll(short, -3, 0), SHOULDER[0] - 46, 1)


def darker(img):
    out = img.copy()
    for src, dst in DARKER.items():
        m = np.all(img[..., :3] == src, axis=-1) & (img[..., 3] > 0)
        out[m, :3] = dst
    return out


def rot_arm(arm, deg):
    if not deg:
        return arm.copy()
    big = arm
    for _ in range(3):
        big = np.array(scale2x_img(Image.fromarray(big)))
    s = 8
    r = np.array(Image.fromarray(big).rotate(-deg, resample=Image.NEAREST,
                                               center=(SHOULDER[0] * s + s / 2, SHOULDER[1] * s + s / 2)))
    r = r[s // 2::s, s // 2::s][:64, :64].copy()
    a = r[..., 3] > 127
    flat = r[a][:, :3].astype(np.int32)
    d = ((flat[:, None, :] - TIQUE_PALETTE[None, :, :3]) ** 2).sum(-1)
    out = np.zeros_like(r)
    out[a] = TIQUE_PALETTE[d.argmin(1)].astype(np.uint8)
    return out


def scale2x_img(im):
    a = np.array(im.convert('RGBA'))
    h, w = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode='edge')
    E, B, D, F, Hh = p[1:-1, 1:-1], p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 2:], p[2:, 1:-1]
    eq = lambda x, y: np.all(x == y, axis=-1)
    c = (~eq(B, Hh)) & (~eq(D, F))
    out = np.zeros((h * 2, w * 2, 4), a.dtype)
    out[0::2, 0::2] = np.where((c & eq(D, B))[..., None], D, E)
    out[0::2, 1::2] = np.where((c & eq(B, F))[..., None], F, E)
    out[1::2, 0::2] = np.where((c & eq(D, Hh))[..., None], D, E)
    out[1::2, 1::2] = np.where((c & eq(Hh, F))[..., None], F, E)
    return Image.fromarray(out)


# Full-length arm: with the shoulder on the torso edge the fist ends at x 52, one
# pixel short of the pushed weight's face (tile centre + 21).
ARM = forward_arm(0)
ARM_LONG = ARM
ARM_ANGLE = {'side': 0, 'up': -45, 'down': 55}


def shifted(img, dx, dy):
    return np.roll(np.roll(img, dy, 0), dx, 1)


def push_frame(body_src, direction, offset=None):
    """Both hands on the pushed object: the near arm plus the far arm one shade darker
    and a little lower so both fists show. Up/down tilt the same arms up-forward or
    down-forward, the approved stand-in for back/front views Tique does not have."""
    body, (dx, dy) = armless(body_src, offset)
    arm = ARM_LONG if direction == 'up' else ARM
    near = shifted(rot_arm(arm, ARM_ANGLE[direction]), dx, dy)
    if direction == 'up':
        # Both hands raised up-forward to the block above; far arm lower, one shade darker.
        far = darker(shifted(rot_arm(arm, ARM_ANGLE[direction] + 10), dx, dy + 3))
    else:
        far = darker(shifted(rot_arm(ARM, ARM_ANGLE[direction] + (4 if direction == 'down' else 0)), dx, dy + 4))
    out = np.zeros_like(body)
    for part in (far, body, near):
        m = part[..., 3] > 0
        out[m] = part[m]
    # Pixels the pose may change: new arms plus the swinging arms that were erased.
    changed = (near[..., 3] > 0) | (far[..., 3] > 0) | np.any(out != body_src, axis=-1)
    return Image.fromarray(out), sorted((int(x), int(y)) for y, x in zip(*np.where(changed)))


def hurt_frames():
    # Flinch away from the hit (faces +x): whole approved body steps back 1-2px, the
    # eyes squeeze using the approved blink frames, the front arm rises to the face.
    blink_half = load_np(OUT / 'blink-half/00.png'); blink_closed = load_np(OUT / 'blink-closed/00.png')
    frames = []
    for eyes, back, up, arm in [(blink_half, 1, 0, -70), (blink_closed, 2, 1, -80), (blink_half, 1, 0, -45)]:
        base = IDLE.copy(); base[10:30] = eyes[10:30]
        body, _ = armless(base, (0, 0))
        near = rot_arm(ARM, arm)
        out = np.zeros_like(body)
        for part in (body, near):
            m = part[..., 3] > 0
            out[m] = part[m]
        out = np.roll(np.roll(out, -up, 0), -back, 1)
        out[64 - up:] = 0
        frames.append(Image.fromarray(out))
    return frames


def tique_poses():
    walk = [load_np(TIQUE / 'Walk' / f'{i:02d}.png') for i in range(14)]
    walk_times = json.loads((R / 'unity/TiqueReturnPrototype/Assets/Resources/Return/clips.json').read_text())
    walk_times = next(c['durations'] for c in walk_times['clips'] if c['name'] == 'Walk')
    masks = {}
    for direction in ('side', 'up', 'down'):
        frames, arm = zip(*(push_frame(w, direction) for w in walk))
        masks['push-' + direction] = list(arm)
        export('push-' + direction, list(frames), walk_times,
               'approved Attack/05 arm on armless Walk frames' +
               ('' if direction == 'side' else f', arm rotated {ARM_ANGLE[direction]} deg with RotSprite') +
               '; v5 arms were flat double bars')
        brace, arm = push_frame(IDLE, direction)
        masks['push-brace-' + direction] = [arm]
        export('push-brace-' + direction, [brace], [1000], 'blocked push: same arms on the planted Idle body')
    export('hurt-pose', hurt_frames(), [40, 50, 60], 'flinch: step back, squeezed eyes, arm up; v5 matched Idle')
    (ART / 'polish-v6-arm-masks.json').write_text(json.dumps(masks, separators=(',', ':')))


STAGES = [hud_cells, effects, icons, tique_poses]

if __name__ == '__main__':
    for stage in STAGES:
        stage()
    save_index()
    print('polished', len(POLISHED), 'clips')
