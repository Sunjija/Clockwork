"""Derive true game-scale pixels from the six actual imagegen anchors.

This is a source conversion, not a shape authoring script. Every native pixel
has a recorded generated-source footprint. The original anchors, prompts and
provenance are read-only. Faint generated alpha specks are excluded at 128.
Like WardenV7, conversion uses premultiplied area sampling, a modest unsharp
pass, one constrained nondithered palette, restrained noise cleanup and binary
alpha. The contact sheet is a preview, not human visual approval.
"""
from pathlib import Path
import hashlib
import json
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO / 'art/return-readability-image-first-v2'
NATIVE = PACKAGE / 'Source/Native'
DERIVATION = PACKAGE / 'Source/Derivation'
QA = PACKAGE / 'QA'
ALPHA_THRESHOLD = 128
SPECS = {
    'wall': {'canvas': (36, 36), 'full_cell': True},
    'weight': {'canvas': (30, 32), 'full_cell': False},
    'orb': {'canvas': (26, 26), 'full_cell': False},
    'weight_socket': {'canvas': (36, 36), 'full_cell': False, 'fit': (32, 32)},
    'orb_socket': {'canvas': (36, 36), 'full_cell': False, 'fit': (32, 32)},
    'floor': {'canvas': (36, 36), 'full_cell': True},
}
# Reserved unchanged error-state color, not a newly generated anchor color.
# It is used only by the exporter's unchanged wrong-port indicator.
ERROR_RED = (244, 87, 69)
N4 = ((0, -1), (1, 0), (0, 1), (-1, 0))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=lambda v: v.item() if isinstance(v, np.generic) else list(v)) + '\n', encoding='utf-8')


def color_family(px):
    p = px.astype(float)
    r, g, b = p[..., 0], p[..., 1], p[..., 2]
    dark = np.max(p, axis=-1) < 40
    warm = (r > g * 1.22) & (r > b * 1.4) & ~dark
    cyan = (g > r * 1.6) & (g > b * .82) & ~dark & ~warm
    return np.where(dark, 0, np.where(warm, 2, np.where(cyan, 3, 1)))


def derive_sampling(name, spec, selected):
    source_path = PACKAGE / selected
    original = Image.open(source_path).convert('RGBA')
    a = np.array(original)
    mask = a[..., 3] >= ALPHA_THRESHOLD
    ys, xs = np.where(mask)
    crop = [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)]
    cut = original.crop(crop)
    cw, ch = spec['canvas']
    if spec['full_cell']:
        size = (cw, ch)
        offset = (0, 0)
    else:
        fw, fh = spec.get('fit', (cw, ch))
        factor = min(fw / cut.width, fh / cut.height)
        size = (max(1, round(cut.width * factor)), max(1, round(cut.height * factor)))
        # Planted props retain the established last-row baseline. Recessed
        # sockets are centered within a 36px tile, beneath rather than above it.
        offset = ((cw - size[0]) // 2, (ch - size[1]) // 2 if 'socket' in name else ch - size[1])
    # RGBa is premultiplied alpha: transparent RGB cannot darken colored edges.
    small = cut.convert('RGBa').resize(size, Image.Resampling.BOX).convert('RGBA')
    small_arr = np.array(small)
    rgb = small.convert('RGB').filter(ImageFilter.UnsharpMask(radius=.65, percent=65, threshold=3))
    native_small = np.array(rgb.convert('RGBA'))
    native_small[..., 3] = np.where(small_arr[..., 3] >= 128, 255, 0)
    native_small[native_small[..., 3] == 0] = 0
    detail_edits = []
    if name == 'weight_socket':
        # At 32px the anchor's thin amber rim occupies less than a complete
        # target pixel. Plain area sampling mixes it with the black cavity and
        # loses its generated material identity. A restrained source-detail
        # bias keeps a rim only where actual opaque bright brass occupies at
        # least 22% of that pixel's BOX footprint; it never draws a new border.
        raw = np.array(cut)
        for ty in range(size[1]):
            for tx in range(size[0]):
                x0, y0 = int(tx * cut.width / size[0]), int(ty * cut.height / size[1])
                x1, y1 = int(np.ceil((tx + 1) * cut.width / size[0])), int(np.ceil((ty + 1) * cut.height / size[1]))
                roi = raw[y0:y1, x0:x1]
                rp = roi[..., :3].astype(float)
                bright_brass = (roi[..., 3] >= 128) & (rp[..., 0] > rp[..., 2] * 1.5) & (rp[..., 0] >= rp[..., 1] * .95) & (rp.mean(-1) >= 120)
                if bright_brass.mean() >= .22 and native_small[ty, tx, 3]:
                    before = native_small[ty, tx, :3].copy()
                    color = np.round(rp[bright_brass].mean(0)).astype(np.uint8)
                    native_small[ty, tx, :3] = color
                    if not (before == color).all():
                        detail_edits.append({'x': int(tx + offset[0]), 'y': int(ty + offset[1]), 'operation': 'source-thin-brass-rim-detail-bias',
                                             'sourceRect': [x0 + crop[0], y0 + crop[1], x1 + crop[0], y1 + crop[1]],
                                             'opaqueBrightBrassCoverage': round(float(bright_brass.mean()), 4), 'beforeRgb': before.astype(int).tolist(), 'sampleRgb': color.astype(int).tolist()})
    canvas = np.zeros((ch, cw, 4), np.uint8)
    canvas[offset[1]:offset[1] + size[1], offset[0]:offset[0] + size[0]] = native_small
    pixel_origins = np.full((ch, cw, 2), -1, np.int16)
    pixel_origins[offset[1]:offset[1] + size[1], offset[0]:offset[0] + size[0]] = np.stack(np.meshgrid(np.arange(size[0]), np.arange(size[1])), axis=-1)
    edits = detail_edits
    if spec['full_cell']:
        # The generated panels have slight chamfered corner transparency. Grid
        # cells cannot expose background corners: continue their nearest source
        # edge sample, recording precisely which native sample was continued.
        filled = np.argwhere(canvas[..., 3] > 0)
        for y, x in np.argwhere(canvas[..., 3] == 0):
            sy, sx = filled[((filled - [y, x]) ** 2).sum(1).argmin()]
            canvas[y, x] = canvas[sy, sx]
            pixel_origins[y, x] = pixel_origins[sy, sx]
            edits.append({'x': int(x), 'y': int(y), 'operation': 'source-edge-continuation', 'fromNative': [int(sx), int(sy)]})
    Image.fromarray(canvas).save(DERIVATION / f'{name}-area-sampled.png')
    return canvas, pixel_origins, edits, {
        'generatedSource': selected, 'sourceSha256': sha(source_path),
        'generatedDimensions': list(original.size), 'cropAlphaThreshold': 128,
        'cropRect': crop, 'targetCanvas': list(spec['canvas']),
        'fitSize': list(size), 'offset': list(offset), 'fullCellContinuation': spec['full_cell'],
        'registration': {'gridCell': [36, 36], 'runtimeOffset': [3, 0] if name == 'weight' else [5, 6] if name == 'orb' else [0, 0],
                         'nativeGroundRow': ch - 1 if name in ('weight', 'orb') else None},
    }


def build_palette(frames):
    pixels = np.concatenate([a[a[..., 3] > 0, :3] for a in frames]).astype(float)
    families = color_family(pixels)
    # 47 anchor-derived colors plus unchanged error-red, total at most 48.
    allocations = [5, 14, 16, 12]
    entries, labels = [], []
    for family, k in enumerate(allocations):
        px = pixels[families == family]
        if not len(px):
            continue
        strip = Image.fromarray(px.astype(np.uint8).reshape(1, -1, 3))
        quantized = strip.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
        used = len(quantized.getcolors())
        centers = np.array(quantized.getpalette()[:used * 3], float).reshape(-1, 3)
        for _ in range(10):
            nearest = ((px[:, None] - centers[None]) ** 2).sum(-1).argmin(1)
            for index in range(len(centers)):
                group = px[nearest == index]
                if len(group):
                    centers[index] = group.mean(0)
        for center in centers:
            color = tuple(np.round(center).astype(int))
            if color not in entries:
                entries.append(color)
                labels.append(['dark', 'steel', 'brass', 'cyan'][family])
    entries.append(ERROR_RED)
    labels.append('unchanged-error-indicator-reuse')
    return np.array(entries, np.uint8), labels


def palette_mapping(a, palette):
    out = a.copy()
    mask = a[..., 3] > 0
    pixels = a[mask, :3].astype(int)
    distances = ((pixels[:, None] - palette[None].astype(int)) ** 2).sum(-1)
    # The reserved existing error red must never intrude into anchor conversion.
    distances[:, -1] = 10 ** 9
    out[mask, :3] = palette[distances.argmin(1)]
    return out


def cleanup(a, palette, full_cell, name):
    out = a.copy()
    edits = []
    h, w = a.shape[:2]
    # Only low-contrast lone generator tones are folded; high-contrast rivets,
    # seam pixels and highlights are left intact.
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            me = tuple(a[y, x])
            if not me[3]:
                continue
            around = [tuple(a[y + dy, x + dx]) for dx, dy in N4]
            if any(not p[3] for p in around) or me in around:
                continue
            majority, count = Counter(around).most_common(1)[0]
            if count >= 2 and np.linalg.norm(np.array(me[:3]) - np.array(majority[:3])) < 28:
                source_neighbor = next([x + dx, y + dy] for dx, dy in N4 if tuple(a[y + dy, x + dx]) == majority)
                out[y, x] = majority
                edits.append({'x': x, 'y': y, 'operation': 'low-contrast-single-pixel-fold', 'before': list(me), 'after': list(majority), 'fromNative': source_neighbor})
    if not full_cell and 'socket' not in name:
        mask = a[..., 3] > 0
        padded = np.pad(mask, 1)
        edge = mask & ~(padded[:-2, 1:-1] & padded[2:, 1:-1] & padded[1:-1, :-2] & padded[1:-1, 2:])
        # Generated silhouette and handle-hole edges receive a shared dark ink.
        # No alpha pixel is added and no negative-space hole is closed.
        ink = palette[np.argmin(palette.astype(int).sum(1))]
        for y, x in np.argwhere(edge):
            before = list(map(int, out[y, x]))
            if tuple(out[y, x, :3]) != tuple(ink):
                out[y, x, :3] = ink
                edits.append({'x': int(x), 'y': int(y), 'operation': 'source-silhouette-dark-ink', 'before': before, 'after': list(map(int, out[y, x]))})
    return out, edits


def record_pixels(name, final, origins, info, edits, palette):
    crop = info['cropRect']
    fw, fh = info['fitSize']
    sx, sy = (crop[2] - crop[0]) / fw, (crop[3] - crop[1]) / fh
    lookup = {tuple(map(int, color)): i for i, color in enumerate(palette)}
    by_pixel = {}
    for edit in edits:
        by_pixel.setdefault((edit['x'], edit['y']), []).append(edit)
    pixels = []
    for y in range(final.shape[0]):
        for x in range(final.shape[1]):
            ox, oy = map(int, origins[y, x])
            rgba = list(map(int, final[y, x]))
            row = {'target': [x, y], 'rgba': rgba, 'paletteEntry': lookup.get(tuple(rgba[:3])) if rgba[3] else None}
            if ox >= 0 and oy >= 0:
                row['sourceRect'] = [round(crop[0] + ox * sx, 4), round(crop[1] + oy * sy, 4), round(crop[0] + (ox + 1) * sx, 4), round(crop[1] + (oy + 1) * sy, 4)]
                row['sampleNative'] = [ox, oy]
            else:
                row['sourceRect'] = None
                row['reason'] = 'registration-padding'
            if (x, y) in by_pixel:
                row['cleanup'] = by_pixel[(x, y)]
            pixels.append(row)
    write_json(DERIVATION / f'{name}-pixel-map.json', {
        'asset': name, 'generatedSource': info['generatedSource'], 'sourceSha256': info['sourceSha256'],
        'interpretation': 'Each sourceRect is the premultiplied BOX area footprint before palette conversion. The recorded unsharp filter also reads adjacent area samples; source-edge and tone-fold edits name their native source. Square-socket source-detail bias keeps actual bright brass present in at least 22% of an area sample and records its exact original source rectangle and color. Ink is a shared anchor-derived palette color, not an invented shape.',
        'unsharp': {'radius': .65, 'percent': 65, 'threshold': 3}, 'pixels': pixels,
    })


def contact_sheets(frames, info):
    names = list(SPECS)
    width, height = 720, 440
    board = Image.new('RGB', (width, height), (14, 22, 30))
    gray = Image.new('RGB', (720, 235), (18, 24, 31))
    comparison = Image.new('RGB', (720, 750), (14, 22, 30))
    draw, gd, cd = ImageDraw.Draw(board), ImageDraw.Draw(gray), ImageDraw.Draw(comparison)
    draw.text((14, 10), 'IMAGE-FIRST / NATIVE PIXEL PREVIEW (not approved final art)', fill=(213, 233, 232))
    gd.text((14, 10), 'NATIVE GRAYSCALE / SHAPE CHECK', fill=(225, 230, 228))
    cd.text((14, 10), 'GENERATED ANCHOR -> NATIVE PIXELS / SAME IDENTITY', fill=(225, 230, 228))
    for i, name in enumerate(names):
        col, row = i % 3, i // 3
        im = Image.fromarray(frames[name])
        x, y = 20 + col * 235, 40 + row * 195
        draw.text((x, y), f'{name} {im.width}x{im.height}', fill=(205, 216, 221))
        enlarged = im.resize((im.width * 4, im.height * 4), Image.Resampling.NEAREST)
        board.paste(enlarged, (x + 10, y + 24), enlarged)
        # Separate 1x actual-size chip to avoid implying that enlargement equals
        # in-game readability. Floor keeps transparency-free source fill.
        board.paste(im, (x + 175, y + 100), im)
        gx, gy = 12 + i * 117, 40
        gd.text((gx, gy), name, fill=(214, 218, 218))
        bw = ImageOps.grayscale(im).convert('RGBA')
        bw.putalpha(im.getchannel('A'))
        bw = bw.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)
        gray.paste(bw, (gx, gy + 30), bw)
        cx, cy = 15 + col * 235, 45 + row * 345
        cd.text((cx, cy), name, fill=(219, 231, 230))
        original = Image.open(PACKAGE / info[name]['generatedSource']).convert('RGBA').crop(info[name]['cropRect'])
        original.thumbnail((195, 160), Image.Resampling.LANCZOS)
        comparison.paste(original, (cx + (205 - original.width) // 2, cy + 28), original)
        cd.text((cx, cy + 196), 'native / nearest 3x', fill=(173, 194, 196))
        nat = im.resize((im.width * 3, im.height * 3), Image.Resampling.NEAREST)
        comparison.paste(nat, (cx + 45, cy + 216), nat)
    board.save(QA / 'native-contact.png')
    gray.save(QA / 'native-grayscale-contact.png')
    comparison.save(QA / 'native-source-comparison.png')


def main():
    for folder in (NATIVE, DERIVATION, QA):
        folder.mkdir(parents=True, exist_ok=True)
    provenance = json.loads((PACKAGE / 'Source/provenance.json').read_text())
    sampled, origins, source_edits, info = {}, {}, {}, {}
    for name, spec in SPECS.items():
        sampled[name], origins[name], source_edits[name], info[name] = derive_sampling(name, spec, provenance['selectedPreviewFiles'][name])
    palette, families = build_palette(list(sampled.values()))
    palette_record = {'kind': 'image-first-anchor-derived-shared-palette', 'paletteCap': 48, 'colors': palette.astype(int).tolist(), 'families': families,
                      'derivedColorCount': len(palette) - 1, 'dither': False,
                      'reservedReuse': {'color': list(ERROR_RED), 'source': 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/ReadabilityArt/amber-slot-wrong/00.png and cyan-slot-wrong/00.png; unchanged corner wrong-port X pixels only', 'notUsedByNativeAnchors': True},
                      'sourceHashes': {name: meta['sourceSha256'] for name, meta in info.items()}}
    write_json(NATIVE / 'palette.json', palette_record)
    frames = {}
    for name, a in sampled.items():
        mapped = palette_mapping(a, palette)
        Image.fromarray(mapped).save(DERIVATION / f'{name}-palette-mapped.png')
        frames[name], cleanup_edits = cleanup(mapped, palette, SPECS[name]['full_cell'], name)
        all_edits = source_edits[name] + cleanup_edits
        native_path = NATIVE / f'{name}.png'
        Image.fromarray(frames[name]).save(native_path)
        info[name].update({'output': f'Source/Native/{name}.png', 'outputSha256': sha(native_path),
                           'pixelMap': f'Source/Derivation/{name}-pixel-map.json',
                           'cleanupCount': len(all_edits), 'cleanupOperations': dict(Counter(e['operation'] for e in all_edits)),
                           'uniqueOpaqueColors': len(np.unique(frames[name][frames[name][..., 3] > 0, :3], axis=0)),
                           'opaquePixels': int((frames[name][..., 3] > 0).sum())})
        record_pixels(name, frames[name], origins[name], info[name], all_edits, palette)
        assert set(np.unique(frames[name][..., 3])) <= {0, 255}
        assert len(np.unique(frames[name][frames[name][..., 3] > 0, :3], axis=0)) <= 48
        if SPECS[name]['full_cell']:
            assert (frames[name][..., 3] == 255).all()
    audit = {'version': 2, 'approval': 'Native preview; human appearance approval pending',
             'sourceGeneration': 'Six actual built-in imagegen anchors selected in immutable Source/provenance.json; no original changed and no new generation substituted.',
             'method': 'alpha>=128 crop / premultiplied BOX / mild source unsharp / square-socket actual source brass-rim detail bias / 47 source palette colors + unchanged error red / nondithered nearest color / limited source silhouette and tone cleanup / fixed native registration',
             'relatedEstablishedPipeline': ['tools/art/dotify_guardian_motion.py', 'tools/art/prepare_tique_v10.py'],
             'script': 'tools/art/derive_readability_native_v2.py', 'scriptSha256': sha(Path(__file__)),
             'palette': 'Source/Native/palette.json', 'paletteSha256': sha(NATIVE / 'palette.json'), 'assets': info,
             'technicalVersusAppearance': 'Dimensions, alpha, source hashes and repeatable conversion are technical evidence only. Native contact sheets and runtime feedback remain human visual/playtest gates.'}
    write_json(DERIVATION / 'native-derivation.json', audit)
    contact_sheets(frames, info)
    print(json.dumps({'nativeAssets': len(frames), 'sharedPaletteColors': len(palette), 'assets': {n: {'dimensions': m['targetCanvas'], 'crop': m['cropRect'], 'cleanup': m['cleanupOperations']} for n, m in info.items()}}, indent=2))


if __name__ == '__main__':
    main()
