"""IRON MAW v6: part rig over the locked base dot.

The v0.3 base (art/return-v3-manual/Source/base-native.png) is split into trunk,
head, lower jaw and four lower legs. Every frame is one integer placement of those
native pixel parts; rotation uses RotSprite (Scale2x x3 -> nearest -> centre
sample) so outlines stay one pixel wide, and the result is snapped back to the
base's own 32-colour palette. Planted feet stay flat on the 132px baseline; a
leg that must reach further is bridged with a drawn piston rod.

Outputs:
  art/return-v6-rig/Clips/<clip>/NN.png, NN.pixels.json, sheet.png, native.apng, <clip>.piskel
  art/return-v6-rig/manifest.json, QA/contact.png
  unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenRig/<clip>/NN.png + clips.json
The v0.3 WardenAuthored frames are read only and stay in the project for comparison.
"""
from pathlib import Path
import base64, hashlib, io, json, math, shutil, uuid
import numpy as np
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[2]
SRC = R / 'art/return-v3-manual/Source/base-native.png'
ART = R / 'art/return-v6-rig'
UNITY = R / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenRig'

BASE = np.array(Image.open(SRC).convert('RGBA'))
H, W = BASE.shape[:2]
PALETTE = np.array(sorted({tuple(p) for p in BASE.reshape(-1, 4) if p[3] > 0}), dtype=np.int32)
FLOOR_ROW = 131  # last opaque row of a grounded foot (132px baseline)

# Lower legs: x band of the knee cut, knee pivot, piston row used for telescoping,
# first row of the flat foot pad.
LEGS = {
    'A': dict(x=(0, 80), cut=100, pivot=(71, 101), piston=107, foot=119),    # front far, under the jaw
    'B': dict(x=(80, 107), cut=101, pivot=(97, 102), piston=109, foot=120),  # front near
    'C': dict(x=(107, 132), cut=103, pivot=(117, 104), piston=106, foot=118),  # rear far
    'D': dict(x=(132, 192), cut=100, pivot=(148, 101), piston=104, foot=118),  # rear near
}
BODY_PIVOT = (100, 92)
NECK_PIVOT = (76, 70)
JAW_PIVOT = (72, 84)

# Piston rod ramp, left to right, from the base palette's steel ramp.
ROD = [(6, 7, 8), (36, 46, 57), (86, 93, 101), (140, 144, 147), (162, 164, 165), (86, 93, 101), (44, 49, 57), (6, 7, 8)]
COLLAR = [(6, 7, 8)] + [(26, 30, 36)] * 8 + [(6, 7, 8)]
# Power states: the mouth and back vents are the only lit colours.
LIT_RED, DIM_RED = (122, 49, 37), (85, 13, 9)
POWER = {
    0: {LIT_RED: (26, 30, 36), DIM_RED: (10, 9, 10)},
    1: {LIT_RED: DIM_RED, DIM_RED: (18, 17, 18)},
    2: {},
}


# ---------------------------------------------------------------- pixel helpers
def scale2x(img):
    h, w = img.shape[:2]
    p = np.pad(img, ((1, 1), (1, 1), (0, 0)), mode='edge')
    E = p[1:-1, 1:-1]; B = p[:-2, 1:-1]; D = p[1:-1, :-2]; F = p[1:-1, 2:]; Hh = p[2:, 1:-1]
    eq = lambda a, b: np.all(a == b, axis=-1)
    c = (~eq(B, Hh)) & (~eq(D, F))
    out = np.zeros((h * 2, w * 2, 4), img.dtype)
    out[0::2, 0::2] = np.where((c & eq(D, B))[..., None], D, E)
    out[0::2, 1::2] = np.where((c & eq(B, F))[..., None], F, E)
    out[1::2, 0::2] = np.where((c & eq(D, Hh))[..., None], D, E)
    out[1::2, 1::2] = np.where((c & eq(Hh, F))[..., None], F, E)
    return out


def rotsprite(layer, pivot, deg):
    """Rotate a full-canvas RGBA layer about pivot; + is screen clockwise."""
    if abs(deg) < 1e-6:
        return layer.copy()
    big = layer
    for _ in range(3):
        big = scale2x(big)
    s = 8
    rot = Image.fromarray(big.astype(np.uint8)).rotate(
        -deg, resample=Image.NEAREST, center=(pivot[0] * s + s / 2, pivot[1] * s + s / 2))
    return np.array(rot)[s // 2::s, s // 2::s][:layer.shape[0], :layer.shape[1]].copy()


def shift(layer, dx, dy):
    out = np.zeros_like(layer)
    h, w = layer.shape[:2]
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = layer[ys0:ys1, xs0:xs1]
    return out


def rot_point(p, pivot, deg):
    a = math.radians(deg)
    x, y = p[0] - pivot[0], p[1] - pivot[1]
    return (pivot[0] + x * math.cos(a) - y * math.sin(a), pivot[1] + x * math.sin(a) + y * math.cos(a))


def body_point(p, pose):
    x, y = rot_point(p, BODY_PIVOT, pose.get('body_rot', 0))
    return (x + pose.get('body_dx', 0), y + pose.get('body_dy', 0))


def place(layer, pivot, deg, target):
    """One resample: rotate about pivot, then move the pivot onto target."""
    return shift(rotsprite(layer, pivot, deg), round(target[0] - pivot[0]), round(target[1] - pivot[1]))


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]
    return dst


def bottom(img):
    ys = np.where((img[..., 3] > 0).any(axis=1))[0]
    return int(ys[-1]) if len(ys) else None


def draw_rod(out, cx, y, rows, collar_at):
    for k in range(rows):
        ramp = COLLAR if k == collar_at else ROD
        for i, c in enumerate(ramp):
            out[y + k, cx - len(ramp) // 2 + i] = (*c, 255)


def stretch(layer, row, n):
    """Telescope out: push everything below row down n rows, bridge with a rod."""
    if n <= 0:
        return layer.copy()
    out = np.zeros_like(layer)
    out[:row + 1] = layer[:row + 1]
    out[row + 1 + n:] = layer[row + 1:layer.shape[0] - n]
    xs = np.where(layer[row, :, 3] > 0)[0]
    if len(xs):
        draw_rod(out, int(round(xs.mean())), row + 1, n, 0)
    return out


def retract(layer, row, n):
    """Telescope in: drop n rows below row, pulling the foot up."""
    if n <= 0:
        return layer.copy()
    out = np.zeros_like(layer)
    out[:row + 1] = layer[:row + 1]
    out[row + 1:layer.shape[0] - n] = layer[row + 1 + n:]
    return out


def snap_palette(img):
    a = img[..., 3] > 127
    flat = img[a][:, :3].astype(np.int32)
    d = ((flat[:, None, :] - PALETTE[None, :, :3]) ** 2).sum(-1)
    out = np.zeros_like(img)
    out[a] = PALETTE[d.argmin(1)].astype(np.uint8)
    return out


def despeckle(img):
    """Drop opaque pixels with fewer than two opaque neighbours (rotation crumbs)."""
    a = (img[..., 3] > 0).astype(np.int32)
    p = np.pad(a, 1)
    n = sum(p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx)
    out = img.copy()
    out[(a == 1) & (n < 2)] = 0
    return out


def power(img, level):
    out = img.copy()
    for src, dst in POWER[level].items():
        m = np.all(img[..., :3] == src, axis=-1) & (img[..., 3] > 0)
        out[m, :3] = dst
    return out


# ---------------------------------------------------------------- the rig
def masks():
    alpha = BASE[..., 3] > 0
    ys, xs = np.mgrid[0:H, 0:W]
    legs = {k: alpha & (ys >= L['cut']) & (xs >= L['x'][0]) & (xs < L['x'][1]) for k, L in LEGS.items()}
    # The near front foot's toe and heel spill across the x bands.
    spill = alpha & (((ys >= 128) & (xs >= 107) & (xs <= 115)) | ((ys >= 129) & (xs == 79)))
    legs['A'] &= ~spill; legs['C'] &= ~spill; legs['B'] |= spill
    body = alpha.copy()
    for m in legs.values():
        body &= ~m
    jaw = body & (((xs <= 75) & (ys >= 80)) | ((xs <= 44) & (ys >= 74)))
    head = body & (xs <= 75) & ~jaw
    # Mouth/neck shadow carried by the head: shows where the jaw or neck parts open.
    cavity = alpha & (xs >= 44) & (xs <= 80) & (ys >= 60) & (ys <= 86)
    return body & ~head & ~jaw, head, jaw, cavity, legs


TRUNK, HEAD, JAW, CAVITY, LEG_MASKS = masks()
SHADOW = np.array((*DIM_RED, 255), dtype=np.uint8)


def planted_leg(layer, L, lp, dx, dy):
    """Shin swings about the knee; the foot pad stays flat on the baseline."""
    fr = L['foot']
    shin = layer.copy(); shin[fr:] = 0
    foot = layer.copy(); foot[:fr] = 0
    xs = np.where(layer[fr - 1, :, 3] > 0)[0]
    ankle = (xs.mean(), fr - 1)
    rot = lp.get('rot', 0)
    shin = shift(rotsprite(shin, L['pivot'], rot), dx, dy)
    ax, ay = rot_point(ankle, L['pivot'], rot)
    ax, ay = ax + dx, ay + dy
    foot = shift(foot, round(ax - ankle[0]) + lp.get('foot_dx', 0), FLOOR_ROW - bottom(foot))
    top = fr + FLOOR_ROW - bottom(layer)
    gap = top - round(ay) - 1
    if gap > 0:
        draw_rod(shin, round(ax), round(ay) + 1, gap, gap - 1)
    else:
        shin[top + 3:] = 0  # the shin sinks into the pad, never below the floor
    return over(shin, foot)


def free_leg(layer, L, lp, dx, dy):
    layer = stretch(layer, L['piston'], lp.get('extend', 0))
    layer = retract(layer, L['piston'], lp.get('shorten', 0))
    return shift(rotsprite(layer, L['pivot'], lp.get('rot', 0)), dx, dy)


def pose_frame(pose, level=2):
    if not pose:
        return power(BASE.copy(), level)
    b, h, j = pose.get('body_rot', 0), pose.get('head', 0), pose.get('jaw', 0)
    neck = body_point(NECK_PIVOT, pose)
    hinge = body_point(rot_point(JAW_PIVOT, NECK_PIVOT, h), pose)
    trunk = place(BASE * TRUNK[..., None], BODY_PIVOT, b, body_point(BODY_PIVOT, pose))
    head = place(BASE * HEAD[..., None], NECK_PIVOT, b + h, neck)
    jaw = place(BASE * JAW[..., None], JAW_PIVOT, b + h + j, hinge)
    back = np.zeros_like(BASE); back[CAVITY] = SHADOW
    back = place(back, NECK_PIVOT, b + h, neck)
    canvas = np.zeros_like(BASE)
    for k in ('A', 'C', 'B', 'D'):  # far legs first; every leg sits behind the chassis
        L, lp = LEGS[k], pose.get(k, {})
        nx, ny = body_point(L['pivot'], pose)
        dx = round(nx - L['pivot'][0]) + lp.get('dx', 0)
        dy = round(ny - L['pivot'][1]) + lp.get('dy', 0)
        layer = BASE * LEG_MASKS[k][..., None]
        over(canvas, planted_leg(layer, L, lp, dx, dy) if lp.get('floor') else free_leg(layer, L, lp, dx, dy))
    for part in (back, trunk, head, jaw):
        over(canvas, part)
    img = despeckle(snap_palette(canvas))
    low = bottom(img)
    if low > FLOOR_ROW:  # an airborne reach never draws below the grounded baseline
        img = shift(img, 0, FLOOR_ROW - low)
    return power(img, level)


# ---------------------------------------------------------------- poses
# Degrees are screen clockwise: body/head + lift the nose, jaw + closes the mouth.
# The head faces -x, so "forward" is left.
def planted(body, **legs):
    p = dict(body)
    for k in 'ABCD':
        p[k] = {'floor': True, **legs.get(k, {})}
    return p


def tuck(t, **body):
    p = dict(A=dict(shorten=round(10 * t), dy=round(-8 * t), dx=round(10 * t), rot=-22 * t),
             B=dict(shorten=round(9 * t), dy=round(-7 * t), dx=round(4 * t), rot=-12 * t),
             C=dict(shorten=round(9 * t), dy=round(-7 * t), dx=round(-3 * t), rot=12 * t),
             D=dict(shorten=round(10 * t), dy=round(-7 * t), dx=round(-10 * t), rot=22 * t))
    p.update(body)
    return p


def reach(r, **body):
    p = dict(A=dict(extend=round(6 * r), rot=16 * r, dx=round(-4 * r)),
             B=dict(extend=round(6 * r), rot=8 * r, dx=round(-2 * r)),
             C=dict(extend=round(5 * r), rot=-8 * r, dx=round(2 * r)),
             D=dict(extend=round(6 * r), rot=-16 * r, dx=round(4 * r)))
    p.update(body)
    return p


LIFTED = dict(floor=False)
SLUMP = planted(dict(body_dy=11, body_rot=-10, head=-11, jaw=-16),
                A=dict(rot=10, foot_dx=-3), B=dict(rot=6, foot_dx=-2), C=dict(rot=-4, foot_dx=1), D=dict(rot=-8, foot_dx=2))
GALLOP_A = planted(dict(body_dx=-4, body_dy=5, body_rot=-7, head=-6, jaw=8),
                   A=dict(rot=16), B=dict(LIFTED, shorten=6, dy=-4, rot=-14),
                   C=dict(LIFTED, shorten=6, dy=-4, rot=16), D=dict(rot=-18))
GALLOP_B = planted(dict(body_dx=-4, body_dy=3, body_rot=-5, head=-5, jaw=8),
                   A=dict(LIFTED, shorten=6, dy=-4, rot=-12), B=dict(rot=14),
                   C=dict(rot=-16), D=dict(LIFTED, shorten=6, dy=-4, rot=18))
REAR = dict(LIFTED, shorten=5, dy=-5, rot=-12)

CLIPS = {
    # Tique Idle: one fixed base frame.
    'idle': ('Idle', [('base', {})]),
    # Tique Attack timing. Rears back with the mouth wide (held through the wave
    # telegraph), snaps the head into the floor on frame 4 when the waves spawn.
    'attack': ('Attack', [
        ('base', {}),
        ('coil', planted(dict(body_dx=3, body_dy=-2, body_rot=6, head=8, jaw=-10), A=dict(rot=-6), B=dict(rot=-4))),
        ('brace', planted(dict(body_dx=5, body_dy=-4, body_rot=12, head=12, jaw=-15), A=REAR, B=dict(REAR, rot=-8), D=dict(rot=-8))),
        ('snap', planted(dict(body_dx=-2, body_dy=2, body_rot=-4, head=-6, jaw=6), A=dict(rot=12), B=dict(rot=8))),
        ('impact', planted(dict(body_dx=-4, body_dy=8, body_rot=-10, head=-10, jaw=10), A=dict(rot=16, foot_dx=-3), B=dict(rot=10, foot_dx=-2), D=dict(rot=-6))),
        ('hold', planted(dict(body_dx=-4, body_dy=7, body_rot=-9, head=-9, jaw=10), A=dict(rot=16, foot_dx=-3), B=dict(rot=10, foot_dx=-2), D=dict(rot=-6))),
        ('release', planted(dict(body_dx=-3, body_dy=5, body_rot=-6, head=-5, jaw=4), A=dict(rot=12, foot_dx=-2), B=dict(rot=6, foot_dx=-1))),
        ('return', planted(dict(body_dx=-1, body_dy=3, body_rot=-3, head=-1, jaw=0), A=dict(rot=6), B=dict(rot=3))),
        ('recoil', planted(dict(body_dx=1, body_dy=1, body_rot=1, head=2, jaw=-3))),
        ('settle', planted(dict(body_dy=1, head=1, jaw=-1))),
        ('jaw rest', planted(dict(jaw=-1))),
        ('base', {}),
    ]),
    # Tique Dash timing. Frame 2 is held for the whole charge telegraph.
    'charge': ('Dash', [
        ('base', {}),
        ('lower', planted(dict(body_dx=3, body_dy=4, body_rot=-6, head=-4, jaw=5),
                          A=dict(rot=8), B=dict(rot=6), C=dict(rot=-4), D=dict(rot=-6))),
        ('brace', planted(dict(body_dx=7, body_dy=8, body_rot=-11, head=-9, jaw=9),
                          A=dict(rot=18, dx=-2), B=dict(rot=14, dx=-2), C=dict(rot=-6), D=dict(rot=-10, dx=2))),
        ('launch', planted(dict(body_dx=-7, body_dy=2, body_rot=-6, head=-6, jaw=8),
                           A=dict(LIFTED, shorten=4, dy=-3, rot=22), B=dict(LIFTED, shorten=3, dy=-2, rot=18),
                           C=dict(rot=-22), D=dict(rot=-26))),
        ('drive A', GALLOP_A),
        ('drive B', GALLOP_B),
        ('drive A', GALLOP_A),
        ('brake', planted(dict(body_dx=-3, body_dy=6, body_rot=-13, head=-3, jaw=6),
                          A=dict(rot=22, dx=-2), B=dict(rot=18, dx=-1),
                          C=dict(LIFTED, shorten=4, dy=-3, rot=8), D=dict(LIFTED, shorten=4, dy=-3, rot=10))),
        ('absorb', planted(dict(body_dx=2, body_dy=5, body_rot=-3, head=4, jaw=-7), A=dict(rot=6), B=dict(rot=4))),
        ('settle', planted(dict(body_dx=1, body_dy=3, body_rot=-1, head=1, jaw=-4))),
        ('jaw rest', planted(dict(body_dy=1, jaw=-1))),
        ('base', {}),
    ]),
    # Tique Jump timing: crouch, rear-leg push, tuck, nose-down reach, squash.
    'slam': ('Jump', [
        ('base', {}),
        ('compress', planted(dict(body_dy=5, body_rot=-5, head=-3, jaw=3))),
        ('brace', planted(dict(body_dy=9, body_rot=-8, head=-5, jaw=6))),
        ('lift', dict(body_dy=-10, body_rot=12, head=6, jaw=-9,
                      A=dict(shorten=3, dy=-3, rot=-8), B=dict(shorten=2, dy=-2, rot=-5),
                      C=dict(floor=True), D=dict(floor=True, rot=-6))),
        ('tuck', tuck(.6, body_dy=-9, body_rot=9, head=4, jaw=-7)),
        ('apex in', tuck(.9, body_dy=-8, body_rot=4, head=2, jaw=-3)),
        ('apex', tuck(1.0, body_dy=-8)),
        ('unfold', tuck(.45, body_dy=-6, body_rot=-7, head=-3, jaw=4)),
        ('fall', reach(.6, body_dy=-4, body_rot=-12, head=-5, jaw=7)),
        ('reach', reach(1.0, body_dy=-3, body_rot=-10, head=-4, jaw=7)),
        ('contact', planted(dict(body_dy=12, body_rot=-7, head=-4, jaw=7),
                            A=dict(foot_dx=-3), B=dict(foot_dx=-2), C=dict(foot_dx=2), D=dict(foot_dx=3))),
        ('absorb', planted(dict(body_dy=10, body_rot=-5, head=-2, jaw=-4), A=dict(foot_dx=-2), D=dict(foot_dx=2))),
        ('head follows', planted(dict(body_dy=6, body_rot=-3, head=-7, jaw=-6))),
        ('recover', planted(dict(body_dy=2, body_rot=-1, head=-2, jaw=-2))),
        ('base', {}),
    ]),
    # Attack timing borrowed as before. Pylon impact throws the head back, then the
    # overloaded chassis slumps with the jaw hanging open; frame 6 is held while the
    # core is exposed, 7-11 close back up.
    'stagger': ('Attack', [
        ('base', {}),
        ('collision', planted(dict(body_dx=4, body_rot=4, head=8, jaw=-4))),
        ('recoil', planted(dict(body_dx=6, body_dy=2, body_rot=7, head=10, jaw=-10),
                           A=dict(LIFTED, shorten=3, dy=-3, rot=-8), B=dict(LIFTED, shorten=2, dy=-2, rot=-6))),
        ('rise', planted(dict(body_dx=4, body_rot=5, head=6, jaw=-8), A=dict(LIFTED, shorten=2, dy=-2, rot=-4))),
        ('overload', planted(dict(body_dx=2, body_dy=6, body_rot=-6, head=-8, jaw=-12),
                             A=dict(rot=8, foot_dx=-2), B=dict(rot=4, foot_dx=-1))),
        ('hold', planted(dict(body_dx=1, body_dy=9, body_rot=-9, head=-10, jaw=-14),
                         A=dict(rot=10, foot_dx=-3), B=dict(rot=6, foot_dx=-2), C=dict(rot=-4, foot_dx=1), D=dict(rot=-6, foot_dx=2))),
        ('open', SLUMP),
        ('settle', planted(dict(body_dy=9, body_rot=-8, head=-8, jaw=-10),
                           A=dict(rot=8, foot_dx=-2), B=dict(rot=4, foot_dx=-1), D=dict(rot=-4, foot_dx=1))),
        ('release', planted(dict(body_dy=6, body_rot=-5, head=-4, jaw=-6), A=dict(rot=4, foot_dx=-1))),
        ('return', planted(dict(body_dy=3, body_rot=-2, head=-1, jaw=-3))),
        ('rest', planted(dict(body_dy=1))),
        ('base', {}),
    ]),
}
# Power-up (2.4s arrival) and shutdown (after the last core hit). Same rig,
# with the lit reds switched off in steps. The last shutdown frame is held.
POWERED = {
    'boot': ([600, 600, 600, 600], [
        ('dark slump', SLUMP, 0),
        ('head lifts', planted(dict(body_dy=8, body_rot=-7, head=-6, jaw=-8),
                               A=dict(rot=6, foot_dx=-2), B=dict(rot=4, foot_dx=-1), D=dict(rot=-4, foot_dx=1)), 1),
        ('rising', planted(dict(body_dy=4, body_rot=-3, head=0, jaw=-4)), 2),
        ('awake', planted(dict(body_dy=-2, body_rot=3, head=4, jaw=-8)), 2),
    ]),
    'shutdown': ([60, 60, 60, 60], [
        ('power drop', planted(dict(body_dy=3, body_rot=-4, head=-4, jaw=-6)), 2),
        ('buckle', planted(dict(body_dy=7, body_rot=-7, head=-8, jaw=-10),
                           A=dict(rot=6, foot_dx=-2), B=dict(rot=4, foot_dx=-1)), 1),
        ('fall', planted(dict(body_dy=10, body_rot=-9, head=-11, jaw=-13),
                         A=dict(rot=9, foot_dx=-3), B=dict(rot=5, foot_dx=-2), D=dict(rot=-6, foot_dx=2)), 0),
        ('off', SLUMP, 0),
    ]),
}
TIQUE = json.loads((R / 'unity/TiqueReturnPrototype/Assets/Resources/Return/clips.json').read_text())
TIQUE = {c['name']: c['durations'] for c in TIQUE['clips']}


# ---------------------------------------------------------------- export
META_TEXTURE = (R / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenAuthored/idle/00.png.meta').read_text()
META_FOLDER = 'fileFormatVersion: 2\nguid: {}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
META_TEXT = 'fileFormatVersion: 2\nguid: {}\nTextScriptImporter:\n  externalObjects: {{}}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'


def guid(path):
    """Stable GUID per asset path, so re-running the tool never churns metas."""
    return uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork/' + str(path.relative_to(R))).hex


def meta(path, template):
    if template is META_TEXTURE:
        text = template.replace(template.split('\n')[1], 'guid: ' + guid(path))
    else:
        text = template.format(guid(path))
    path.with_name(path.name + '.meta').write_text(text)


def export(name, frames, times, names, manifest):
    folder = ART / 'Clips' / name
    dest = UNITY / name
    for d in (folder, dest):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    meta(dest, META_FOLDER)
    base = Image.fromarray(BASE)
    ims = [Image.fromarray(f) for f in frames]
    sheet = Image.new('RGBA', (W * len(ims), H))
    rows = []
    for i, im in enumerate(ims):
        assert set(np.unique(frames[i][..., 3])) <= {0, 255}
        im.save(folder / f'{i:02d}.png')
        shutil.copyfile(folder / f'{i:02d}.png', dest / f'{i:02d}.png')
        meta(dest / f'{i:02d}.png', META_TEXTURE)
        sheet.alpha_composite(im, (i * W, 0))
        a, b = frames[i], BASE
        ys, xs = np.where(np.any(a != b, axis=-1))
        (folder / f'{i:02d}.pixels.json').write_text(
            json.dumps([[int(x), int(y), *map(int, a[y, x])] for y, x in zip(ys, xs)], separators=(',', ':')))
        rows.append({'frame': i, 'name': names[i], 'changedPixels': int(len(xs)),
                     'bottom': bottom(a), 'sha256': hashlib.sha256(a.tobytes()).hexdigest()})
    sheet.save(folder / 'sheet.png')
    if len(ims) > 1:
        ims[0].save(folder / 'native.apng', save_all=True, append_images=ims[1:], duration=times, loop=0, disposal=0, blend=0)
    buf = io.BytesIO(); sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(ims),
             'chunks': [{'layout': [[i] for i in range(len(ims))],
                         'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    (folder / f'{name}.piskel').write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'IRON MAW rig frames; variable timing lives in clips.json and native.apng.',
        'fps': 20, 'width': W, 'height': H, 'layers': [json.dumps(layer)]}}))
    manifest.append({'name': name, 'durations': times, 'names': names, 'frames': len(ims),
                     'durationMs': sum(times), 'loop': name == 'idle', 'audit': rows})


def main():
    ART.mkdir(parents=True, exist_ok=True)
    UNITY.mkdir(parents=True, exist_ok=True)
    meta(UNITY, META_FOLDER)
    manifest = []
    for name, (tique, poses) in CLIPS.items():
        times = TIQUE[tique]
        assert len(times) == len(poses), (name, len(times), len(poses))
        export(name, [pose_frame(p) for _, p in poses], times, [n for n, _ in poses], manifest)
    for name, (times, poses) in POWERED.items():
        export(name, [pose_frame(p, lvl) for _, p, lvl in poses], times, [n for n, _, _ in poses], manifest)
    clips = [{k: c[k] for k in ('name', 'durations', 'names', 'frames', 'durationMs', 'loop')} for c in manifest]
    (UNITY / 'clips.json').write_text(json.dumps({'clips': clips}, indent=2, ensure_ascii=False))
    meta(UNITY / 'clips.json', META_TEXT)
    (ART / 'manifest.json').write_text(json.dumps({
        'source': str(SRC.relative_to(R)), 'palette': len(PALETTE), 'baselineRow': FLOOR_ROW + 1,
        'method': 'part rig: trunk/head/jaw/4 legs, integer placement + RotSprite, base palette snap, planted feet flat',
        'clips': manifest}, indent=2, ensure_ascii=False))
    contact(manifest)
    print('wrote', sum(c['frames'] for c in manifest), 'frames in', len(manifest), 'clips')


def contact(manifest, s=2):
    crop = (8, 26, 184, 140)
    cw, ch = (crop[2] - crop[0]) * s, (crop[3] - crop[1]) * s
    cols = max(c['frames'] for c in manifest)
    sheet = Image.new('RGBA', (cols * (cw + 4) + 70, len(manifest) * (ch + 4)), (24, 26, 30, 255))
    d = ImageDraw.Draw(sheet)
    for r, c in enumerate(manifest):
        d.text((4, r * (ch + 4) + ch // 2), c['name'], fill=(235, 235, 235, 255))
        for i in range(c['frames']):
            im = Image.open(ART / 'Clips' / c['name'] / f'{i:02d}.png').crop(crop)
            t = Image.new('RGBA', im.size, (46, 50, 58, 255))
            ImageDraw.Draw(t).line([(0, FLOOR_ROW + 1 - crop[1]), (im.width, FLOOR_ROW + 1 - crop[1])], fill=(90, 98, 108, 255))
            t.alpha_composite(im)
            sheet.alpha_composite(t.resize((cw, ch), Image.NEAREST), (70 + i * (cw + 4), r * (ch + 4)))
    (ART / 'QA').mkdir(exist_ok=True)
    sheet.save(ART / 'QA/contact.png')


if __name__ == '__main__':
    main()
