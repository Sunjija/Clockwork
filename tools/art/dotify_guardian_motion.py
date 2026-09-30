"""IRON MAW v7: dotify the guardian motion images into game-scale pixel art.

Source: art/generated/guardian-motion-images/<motion>/frame-0..7.png (192x192,
soft generated "pixel" style, ~157px wide, 40+ tones per frame, frame-to-frame
foot jitter, drop_slam drawn ~25% smaller than the other motions).

Per frame:
  1. premultiplied area-average downscale to the game size (idle 136px wide, the
     locked v0.3 body width) + mild unsharp mask; drop_slam gets its own factor
     so its body matches the other motions
  2. binary alpha at 50%
  3. one shared 32-colour palette for all 64 frames (median cut + k-means refine),
     nearest-colour mapping without dithering
  4. low-contrast single-pixel noise folded into its neighbours (rivets and other
     high-contrast single pixels are kept), crumbs removed, 1px darkest outline
  5. registration on a 192x176 canvas: grounded frames put the planted feet on the
     row-163 baseline (median of each foot column's lowest pixel, so one low pad
     does not bob the body); airborne/rolled frames rest their lowest pixel there;
     each motion keeps its own horizontal motion around the canvas centre (x 96)

Game clips are then assembled from these frames (tools reuse; transitions that
the eight source frames do not cover are bridged with existing frames).

Outputs:
  art/return-v7-guardian/Frames/<motion>/NN.png          dotified source frames
  art/return-v7-guardian/Clips/<clip>/...                game clips (PNG, sheet, APNG, Piskel)
  art/return-v7-guardian/manifest.json, QA/*.png|gif
  unity/.../Resources/ReturnV2/WardenV7/<clip>/NN.png + clips.json (+ .meta)
"""
from pathlib import Path
import base64, io, json, shutil, uuid
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

R = Path(__file__).resolve().parents[2]
SRC = R / 'art/generated/guardian-motion-images'
ART = R / 'art/return-v7-guardian'
UNITY = R / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenV7'
META_TEXTURE = (R / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/WardenAuthored/idle/00.png.meta').read_text()

MOTIONS = ['idle', 'walk', 'rolling_charge', 'jaw_shockwave', 'drop_slam', 'stagger_recover', 'hit_reaction', 'defeat']
CANVAS = (192, 176)
BASELINE = 163          # last opaque row of a planted foot; the game draws at bossY - 164
BODY_WIDTH = 136        # locked v0.3 body width
DROP_SLAM_SIZE = 1.33   # drop_slam's recover pose is 117x82 vs idle 157x108 in the source
PALETTE_SIZE = 32
# Frames that are off the ground or rolled: rest the lowest pixel on the baseline
# instead of the planted-foot median.
LOOSE = {('rolling_charge', i) for i in range(1, 6)} | {('drop_slam', i) for i in range(1, 6)}


# ---------------------------------------------------------------- source -> native
def source(motion, i):
    return Image.open(SRC / motion / f'frame-{i}.png').convert('RGBA')


def idle_width():
    widths = []
    for i in range(8):
        bb = source('idle', i).getbbox()
        widths.append(bb[2] - bb[0])
    return float(np.median(widths))


SCALE = BODY_WIDTH / idle_width()


def downscale(im, factor):
    """Area average, then a mild unsharp mask to win back the edge contrast the
    averaging softens (60% chosen against 0% and 110% on idle)."""
    w, h = im.size
    small = im.convert('RGBa').resize((round(w * factor), round(h * factor)), Image.BOX).convert('RGBA')
    a = np.array(small)
    alpha = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
    rgb = Image.fromarray(a).convert('RGB').filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    a = np.array(rgb.convert('RGBA'))
    a[..., 3] = alpha
    a[alpha == 0] = 0
    return a


def planted_bottom(a):
    """Median of each foot column's lowest opaque row (within the bottom 10 rows)."""
    alpha = a[..., 3] > 0
    ys = np.where(alpha.any(1))[0]
    low = ys[-1]
    cols = []
    for x in np.where(alpha[low - 9:low + 1].any(0))[0]:
        cols.append(np.where(alpha[:, x])[0][-1])
    return int(np.median(cols))


def place(a, motion, i, factor):
    """Put a downscaled frame on the canvas: the source centre column (96) maps to
    x 96, and the frame's ground contact to the baseline."""
    canvas = np.zeros((CANVAS[1], CANVAS[0], 4), np.uint8)
    h, w = a.shape[:2]
    ox = round(96 - 96 * factor)
    ground = int(np.where((a[..., 3] > 0).any(1))[0][-1]) if (motion, i) in LOOSE else planted_bottom(a)
    oy = BASELINE - ground
    ys, xs = np.where(a[..., 3] > 0)
    ty, tx = ys + oy, xs + ox
    ok = (ty >= 0) & (ty < CANVAS[1]) & (tx >= 0) & (tx < CANVAS[0])
    assert ok.all(), (motion, i, 'frame leaves the canvas')
    canvas[ty, tx] = a[ys, xs]
    return canvas


# ---------------------------------------------------------------- palette
WARM_SLOTS = 7  # mouth, core and vents keep their own ramp


def kmeans(px, k, seed_img_colors):
    strip = Image.fromarray(px.astype(np.uint8).reshape(1, -1, 3), 'RGB')
    seed = strip.quantize(colors=k, method=Image.Quantize.MEDIANCUT).getpalette()[:k * 3]
    centers = np.array(seed, np.float64).reshape(-1, 3)[:k]
    rng = np.random.default_rng(7)
    sample = px[rng.choice(len(px), min(len(px), 60000), replace=False)]
    for _ in range(12):
        lab = ((sample[:, None, :] - centers[None]) ** 2).sum(-1).argmin(1)
        for c in range(len(centers)):
            m = lab == c
            if m.any():
                centers[c] = sample[m].mean(0)
    return centers


def warm(px):
    return (px[:, 0] > px[:, 1] + 30) & (px[:, 0] > px[:, 2] + 30)


def build_palette(frames):
    """32 colours: the steel/navy body and the warm mouth/core/vent pixels are
    quantized separately, so the small red areas keep a light-to-dark ramp instead
    of collapsing into one red."""
    px = np.concatenate([f[f[..., 3] > 0][:, :3] for f in frames]).astype(np.float64)
    hot = warm(px)
    centers = np.concatenate([kmeans(px[~hot], PALETTE_SIZE - WARM_SLOTS, None), kmeans(px[hot], WARM_SLOTS, None)])
    return np.unique(np.round(centers).astype(np.uint8), axis=0)


def map_palette(a, pal):
    """Nearest colour, but warm pixels only map to warm entries and cool to cool,
    so a dark red never turns navy and vice versa."""
    out = a.copy()
    m = a[..., 3] > 0
    c = a[m][:, :3].astype(np.int32)
    pw = warm(pal.astype(np.float64))
    d = ((c[:, None, :] - pal[None].astype(np.int32)) ** 2).sum(-1)
    cw = warm(c.astype(np.float64))
    d[np.ix_(cw, ~pw)] += 10 ** 7
    d[np.ix_(~cw, pw)] += 10 ** 7
    out[m, :3] = pal[d.argmin(1)]
    return out


# ---------------------------------------------------------------- cleanup
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def neighbours(a, y, x, offsets):
    h, w = a.shape[:2]
    for dx, dy in offsets:
        yy, xx = y + dy, x + dx
        if 0 <= yy < h and 0 <= xx < w:
            yield a[yy, xx]


def fold_noise(a, limit=38):
    """A single pixel unlike all four neighbours, and close in tone to their
    majority, is generator noise: take the majority colour. Distinct single pixels
    (rivet highlights, dark seams) are kept."""
    out = a.copy()
    h, w = a.shape[:2]
    ys, xs = np.where(a[..., 3] > 0)
    for y, x in zip(ys, xs):
        me = tuple(a[y, x])
        nb = [tuple(n) for n in neighbours(a, y, x, N4)]
        if len(nb) < 4 or any(n[3] == 0 for n in nb) or me in nb:
            continue
        counts = {}
        for n in nb:
            counts[n] = counts.get(n, 0) + 1
        major, k = max(counts.items(), key=lambda kv: kv[1])
        if k >= 2 and abs(sum(map(int, major[:3])) - sum(map(int, me[:3]))) < limit * 3:
            out[y, x] = major
    return out


def drop_crumbs(a):
    """Remove opaque pixels with fewer than two opaque neighbours."""
    out = a.copy()
    alpha = a[..., 3] > 0
    p = np.pad(alpha.astype(np.int32), 1)
    h, w = alpha.shape
    n = sum(p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w] for dx, dy in N8)
    out[alpha & (n < 2)] = 0
    return out


def outline(a, ink):
    """Every silhouette pixel (touching transparency) becomes the darkest colour."""
    out = a.copy()
    alpha = a[..., 3] > 0
    p = np.pad(alpha, 1)
    h, w = alpha.shape
    edge = alpha & ~(p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:])
    out[edge, :3] = ink
    return out


# ---------------------------------------------------------------- frames
def dotify_all():
    native = {}
    for motion in MOTIONS:
        factor = SCALE * (DROP_SLAM_SIZE if motion == 'drop_slam' else 1)
        native[motion] = [place(downscale(source(motion, i), factor), motion, i, factor) for i in range(8)]
    pal = build_palette([f for fs in native.values() for f in fs])
    ink = pal[np.argmin(pal.astype(int).sum(1))]
    for motion, fs in native.items():
        native[motion] = [outline(drop_crumbs(fold_noise(map_palette(f, pal))), ink) for f in fs]
    return native, pal


# ---------------------------------------------------------------- game clips
# (clip, [(motion, frame, ms), ...], loop, note). The game picks ranges out of these
# by state; see Assets/Scripts/WardenAnimation.cs.
def clips_from(native):
    """Idle stands ~16px taller than the neutral pose every attack starts and ends
    in, so each clip is bridged through an existing mid-height frame instead of
    dropping the head in one exposure:
      hit_reaction/1  mouth shut, head half down   -> before the charge brace
      stagger_recover/0  mouth open, mid height    -> before the wave and slam dips
    The wave's last source frame dips below idle again and is dropped; defeat
    starts from its already-slumping frame 2 because it follows the head-down
    core-exposed pose."""
    idle = [('idle', i, 110) for i in range(8)]
    return [
        ('idle', idle, True, 'Rest: breathing loop'),
        ('walk', [('walk', i, 90) for i in range(8)], True, 'spare: walk cycle (no walking state yet)'),
        ('charge-aim', [('hit_reaction', 1, 90), ('rolling_charge', 0, 170), ('rolling_charge', 1, 1000)], False,
         'ChargeAim: shut the jaw, brace, curl up and hold the ball'),
        ('charge-roll', [('rolling_charge', 2, 80), ('rolling_charge', 3, 80), ('rolling_charge', 4, 80)], True,
         'Charge: rolling loop'),
        ('charge-crash', [('rolling_charge', 5, 90), ('hit_reaction', 2, 120), ('hit_reaction', 3, 120),
                          ('hit_reaction', 4, 110), ('hit_reaction', 5, 110), ('hit_reaction', 6, 100),
                          ('hit_reaction', 7, 100)], False, 'Recover after a plain wall: unroll, head thrown back, settle'),
        ('stagger-open', [('rolling_charge', 5, 70), ('stagger_recover', 1, 90), ('stagger_recover', 2, 110),
                          ('stagger_recover', 3, 1000)], False, 'Open: unroll into the pylon, reel, core bared (held)'),
        ('stagger-close', [('stagger_recover', i, 120) for i in (4, 5, 6, 7)], False, 'Recover after Open'),
        ('wave-aim', [('stagger_recover', 0, 60), ('jaw_shockwave', 0, 110), ('jaw_shockwave', 1, 1000),
                      ('jaw_shockwave', 2, 30)], False, 'WaveAim: dip, rear up (held), swing down in the last 30ms'),
        ('wave-strike', [('jaw_shockwave', 3, 120), ('jaw_shockwave', 4, 120), ('jaw_shockwave', 5, 200),
                         ('jaw_shockwave', 6, 310)], False, 'Wave: jaw hits the floor as the waves spawn, pinned, lift'),
        ('slam-rise', [('stagger_recover', 0, 50), ('drop_slam', 0, 80), ('drop_slam', 1, 170), ('drop_slam', 2, 150),
                       ('drop_slam', 3, 1000)], False, 'SlamAim: dip + crouch inside the 130ms grounded brace, leap, curl (held)'),
        ('slam-fall', [('drop_slam', 4, 90), ('drop_slam', 5, 1000)], False, 'Slam: flip, dive (held)'),
        ('slam-land', [('drop_slam', 6, 220), ('drop_slam', 7, 250), ('idle', 0, 110)], False, 'Recover after slam: sprawl, stand'),
        ('defeat', [('defeat', i, 110) for i in range(2, 7)] + [('defeat', 7, 1000)], False, 'Down: collapse from the slumped core pose, hold'),
        ('boot', [('defeat', i, t) for i, t in zip(range(7, -1, -1), (500, 300, 250, 250, 250, 250, 300, 300))], False,
         'Arrival 2.4s: the collapse played back while the lights come on'),
    ]


# Lit colours (mouth/vents) dim for the power-down/boot frames.
def lit_mask(pal):
    red = [tuple(c) for c in pal if int(c[0]) > int(c[2]) + 40 and int(c[0]) > 70]  # noqa: lit reds
    return red


def dim(frame, pal, level):
    """level 0 = dark, 1 = dim, 2 = lit. Reds map to the nearest dark steel / dark red."""
    if level >= 2:
        return frame
    reds = lit_mask(pal)
    darks = sorted((tuple(c) for c in pal if tuple(c) not in reds), key=lambda c: sum(map(int, c)))
    out = frame.copy()
    for c in reds:
        m = np.all(frame[..., :3] == c, axis=-1) & (frame[..., 3] > 0)
        target = darks[1] if level == 0 else min(reds, key=lambda r: sum(map(int, r)))
        if level == 1 and c == target:
            target = darks[2]
        out[m, :3] = target
    return out


def core_flash(frame, pal, step):
    """Keep only the core's warm pixels (x < 96 on the held frame) and push them to
    white (step 0) or the hottest reds (step 1)."""
    reds = sorted(lit_mask(pal), key=lambda c: sum(map(int, c)))
    out = np.zeros_like(frame)
    ys, xs = np.where(frame[..., 3] > 0)
    for y, x in zip(ys, xs):
        c = tuple(frame[y, x, :3])
        if x < 96 and c in reds:
            rank = reds.index(c) / max(1, len(reds) - 1)
            out[y, x, :3] = (248, 248, 248) if step == 0 and rank > .3 else reds[-1] if rank > .3 else reds[-2]
            out[y, x, 3] = 255
    return out


POWER = {  # clip -> per-frame level
    'boot': [0, 0, 1, 1, 1, 2, 2, 2],
    'defeat': [2, 2, 1, 1, 0, 0],
}


# ---------------------------------------------------------------- export
def guid(path):
    return uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork/' + str(path.relative_to(R))).hex


def meta(path, kind):
    if kind == 'texture':
        text = META_TEXTURE.replace(META_TEXTURE.split('\n')[1], 'guid: ' + guid(path))
    elif kind == 'folder':
        text = f'fileFormatVersion: 2\nguid: {guid(path)}\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {{}}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    else:
        text = f'fileFormatVersion: 2\nguid: {guid(path)}\nTextScriptImporter:\n  externalObjects: {{}}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    path.with_name(path.name + '.meta').write_text(text)


def fresh(folder):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def write_sequence(folder, frames, times, name, unity=None):
    ims = [Image.fromarray(f) for f in frames]
    for i, im in enumerate(ims):
        im.save(folder / f'{i:02d}.png')
        if unity is not None:
            shutil.copyfile(folder / f'{i:02d}.png', unity / f'{i:02d}.png')
            meta(unity / f'{i:02d}.png', 'texture')
    sheet = Image.new('RGBA', (CANVAS[0] * len(ims), CANVAS[1]))
    for i, im in enumerate(ims):
        sheet.alpha_composite(im, (i * CANVAS[0], 0))
    sheet.save(folder / 'sheet.png')
    if len(ims) > 1:
        ims[0].save(folder / 'native.apng', save_all=True, append_images=ims[1:], duration=times, loop=0, disposal=0, blend=0)
    buf = io.BytesIO(); sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(ims),
             'chunks': [{'layout': [[i] for i in range(len(ims))],
                         'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    (folder / f'{name}.piskel').write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'IRON MAW v7 dotified frames; variable timing in clips.json / native.apng.',
        'fps': 20, 'width': CANVAS[0], 'height': CANVAS[1], 'layers': [json.dumps(layer)]}}))


def main():
    native, pal = dotify_all()
    fresh(ART / 'Frames')
    for motion, fs in native.items():
        folder = ART / 'Frames' / motion
        folder.mkdir(parents=True)
        write_sequence(folder, fs, [110] * 8, motion)
    fresh(ART / 'Clips'); fresh(UNITY); meta(UNITY, 'folder')
    manifest = []
    specs = clips_from(native) + [('core-flash', [('stagger_recover', 3, 60), ('stagger_recover', 3, 80)], False,
                                   'core hit: the painted core only, white then hot, over the held Open pose')]
    for name, seq, loop, note in specs:
        frames = [native[m][i] for m, i, _ in seq]
        if name == 'core-flash':
            frames = [core_flash(frames[0], pal, k) for k in (0, 1)]
        if name in POWER:
            frames = [dim(f, pal, lvl) for f, lvl in zip(frames, POWER[name])]
        times = [t for _, _, t in seq]
        folder = ART / 'Clips' / name; folder.mkdir(parents=True)
        unity = UNITY / name; unity.mkdir(); meta(unity, 'folder')
        write_sequence(folder, frames, times, name, unity)
        manifest.append({'name': name, 'durations': times, 'loop': loop, 'note': note,
                         'sources': [f'{m}/frame-{i}' for m, i, _ in seq]})
    (UNITY / 'clips.json').write_text(json.dumps({'clips': [
        {'name': c['name'], 'durations': c['durations']} for c in manifest]}, indent=2))
    meta(UNITY / 'clips.json', 'text')
    (ART / 'manifest.json').write_text(json.dumps({
        'source': str(SRC.relative_to(R)), 'canvas': CANVAS, 'baselineRow': BASELINE,
        'scale': round(SCALE, 4), 'dropSlamScale': round(SCALE * DROP_SLAM_SIZE, 4),
        'palette': ['#%02x%02x%02x' % tuple(c) for c in pal], 'clips': manifest}, indent=2, ensure_ascii=False))
    qa(native)
    print('palette', len(pal), 'scale', round(SCALE, 3), 'clips', len(manifest), 'frames', sum(len(c['durations']) for c in manifest))


def qa(native, s=2):
    (ART / 'QA').mkdir(exist_ok=True)
    cw, ch = CANVAS[0] * s, CANVAS[1] * s
    sheet = Image.new('RGBA', (8 * (cw + 4) + 110, len(native) * (ch + 4)), (24, 26, 30, 255))
    d = ImageDraw.Draw(sheet)
    for r, (motion, fs) in enumerate(native.items()):
        d.text((4, r * (ch + 4) + ch // 2), motion, fill=(235, 235, 235, 255))
        for i, f in enumerate(fs):
            t = Image.new('RGBA', CANVAS, (46, 50, 58, 255))
            ImageDraw.Draw(t).line([(0, BASELINE + 1), (CANVAS[0], BASELINE + 1)], fill=(90, 98, 108, 255))
            t.alpha_composite(Image.fromarray(f))
            sheet.alpha_composite(t.resize((cw, ch), Image.NEAREST), (110 + i * (cw + 4), r * (ch + 4)))
    sheet.save(ART / 'QA/frames.png')


if __name__ == '__main__':
    main()
