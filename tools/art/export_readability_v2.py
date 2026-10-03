"""Export source-derived native readability candidates through the Return pipeline.

The six Source/Native PNGs come from actual generated anchors, not this script.
This pass preserves their body/silhouette/material pixels; it makes documented
integer-pixel state edits and reuses existing unmatched-port error marks only.
It never calls v1 shape-painting functions or replaces a source with primitives.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import base64
import colorsys
import hashlib
import io
import json
import re
import shutil
import uuid


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-readability-image-first-v2'
NATIVE = ROOT / 'Source/Native'
CLIP_ROOT = ROOT / 'Clips'
RESOURCE = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2'
OUT = RESOURCE / 'ReadabilityArtV2'
TIMING = {c['name']: c for c in json.loads((RESOURCE / 'StateArt/clips.json').read_text())['clips']}
META = (RESOURCE / 'StateArt/battery-idle/00.png.meta').read_text()
BASE = {}
PALETTE = set()
CLIPS = []
AUDIT = []
MAPPINGS = []
ERROR = (244, 87, 69, 255)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blank(size):
    return Image.new('RGBA', size, (0, 0, 0, 0))


def luminance(color):
    return color[0] * .2126 + color[1] * .7152 + color[2] * .0722


def tinted_highlight(color, role, amount=55):
    """Select an existing shared-palette highlight, never invent RGB colors."""
    if color[3] == 0:
        return color
    choices = [p for p in PALETTE if p != ERROR]
    if role == 'amber':
        choices = [p for p in choices if p[0] > p[2] * 1.22 and p[1] > p[2] * 1.05]
    elif role == 'cyan':
        choices = [p for p in choices if p[1] > p[0] * 1.12 and p[2] > p[0] * 1.12]
    target = min(245, luminance(color) + amount)
    return min(choices or list(PALETTE), key=lambda p: abs(luminance(p) - target))


def wall(mask):
    """Only connected border strips are replaced by sampled native interior.

    N=1 E=2 S=4 W=8. Reciprocal edges use the SAME central source strip so
    adjoining walls read as one structure. Exposed edges keep generated art.
    """
    source = BASE['wall']
    out = source.copy()
    width = 4
    for y in range(36):
        for depth in range(width):
            sx = 18 + depth
            if mask & 8:
                out.putpixel((depth, y), source.getpixel((sx, y)))
            if mask & 2:
                out.putpixel((35 - depth, y), source.getpixel((sx, y)))
    for x in range(36):
        sx = x
        if mask & 8 and x < width:
            sx = 18 + x
        if mask & 2 and x >= 36 - width:
            sx = 18 + 35 - x
        for depth in range(width):
            sy = 18 + depth
            if mask & 1:
                out.putpixel((x, depth), source.getpixel((sx, sy)))
            if mask & 4:
                out.putpixel((x, 35 - depth), source.getpixel((sx, sy)))
    return out


def weight(mode, frame):
    source = BASE['weight']
    out = source.copy()
    if mode == 'moving':
        # The carrying handle flexes a single source pixel. The heavy body and
        # foot contact never move, scale or change silhouette during pushing.
        shift = (0, 0, 1, 1, 1, 0, -1, -1, 0, 0, 0, 0)[frame]
        if shift:
            for y in range(8):
                for x in range(30):
                    out.putpixel((x, y), (0, 0, 0, 0))
            for y in range(8):
                for x in range(30):
                    if 0 <= x + shift < 30:
                        out.putpixel((x + shift, y), source.getpixel((x, y)))
        if frame in (2, 3, 4, 7, 8):
            # Source foot material catches the socket light; no extra dust art.
            for x in (5, 6, 23, 24):
                p = source.getpixel((x, 30))
                if p[3] and luminance(p) > 35:
                    out.putpixel((x, 30), tinted_highlight(p, 'amber', 25))
    elif mode == 'docked':
        for y in range(27, 31):
            for x in range(30):
                p = source.getpixel((x, y))
                if p[3] and (x <= 7 or x >= 22) and luminance(p) > 40:
                    out.putpixel((x, y), tinted_highlight(p, 'amber', 50))
    return out


def orb_seam_data():
    """Find the narrow central meridian already present in the generated orb.

    Only cyan inner pixels that are darker than neighbours are eligible. The
    static highlight, shadow, silhouette and weathered outer metal stay fixed.
    """
    source = BASE['orb']
    seams = []
    for y in range(5, 21):
        candidates = []
        for x in range(8, 18):
            p = source.getpixel((x, y))
            left, right = source.getpixel((x - 2, y)), source.getpixel((x + 2, y))
            if p[3] and p[1] > p[0] + 9 and p[2] > p[0] + 9:
                improvement = max(luminance(left), luminance(right)) - luminance(p)
                if improvement >= 18:
                    candidates.append((improvement, x, p, left, right))
        if candidates:
            _, x, p, left, right = max(candidates)
            replacement = max((left, right), key=luminance)
            if replacement[3]:
                seams.append((x, y, p, replacement))
    return seams


def orb(mode, frame):
    source = BASE['orb']
    out = source.copy()
    if mode == 'moving':
        # Integer cyclic motion of SOURCE meridian clusters only, not rotating
        # the whole orb or its upper-left illumination.
        shift = (0, -1, -3, -5, -6, -4, -2, 0, 2, 4, 6, 5, 3, 1)[frame]
        if shift:
            seam = orb_seam_data()
            for x, y, color, replacement in seam:
                out.putpixel((x, y), replacement)
            for x, y, color, _ in seam:
                tx = x + shift
                p = source.getpixel((tx, y)) if 0 <= tx < 26 else (0, 0, 0, 0)
                if 4 <= tx <= 21 and p[3] and p[1] > p[0] + 9 and p[2] > p[0] + 9:
                    out.putpixel((tx, y), color)
    elif mode == 'docked':
        for y in range(21, 25):
            for x in range(7, 19):
                p = source.getpixel((x, y))
                if p[3] and p[1] > p[0] + 9 and p[2] > p[0] + 9:
                    out.putpixel((x, y), tinted_highlight(p, 'cyan', 45))
    return out


def socket(kind, level=0, wrong=False):
    source = BASE['weight_socket' if kind == 'amber' else 'orb_socket']
    out = source.copy()
    for y in range(36):
        for x in range(36):
            p = source.getpixel((x, y))
            if not p[3] or luminance(p) < 40:
                continue
            # Illuminate four quadrants of the EXISTING outer rim in sequence.
            # This preserves the generated cavity and doesn't draw a new shape.
            outer = x < 7 or x > 28 or y < 7 or y > 28
            quadrant = 0 if x < 18 and y < 18 else 1 if y < 18 else 2 if x >= 18 else 3
            if outer and quadrant < level:
                out.putpixel((x, y), tinted_highlight(p, kind, 65))
    if wrong:
        reused = Image.open(RESOURCE / 'ReadabilityArt' / f'{kind}-slot-wrong/00.png').convert('RGBA')
        for y in range(36):
            for x in range(36):
                if reused.getpixel((x, y)) == ERROR:
                    out.putpixel((x, y), ERROR)
    return out


def meta(path, kind):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-readability-image-first-v2/' + path.relative_to(REPO).as_posix()).hex
    if kind == 'texture':
        body = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, META, count=1)
        body = body.replace('textureCompression: 1', 'textureCompression: 0')
        body = body.replace('filterMode: 1', 'filterMode: 0').replace('enableMipMap: 1', 'enableMipMap: 0')
        body = re.sub(r'(?m)^  spritePixelsToUnits:.*$', '  spritePixelsToUnits: 64', body)
    else:
        body = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder':
            body += 'folderAsset: yes\n'
        body += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    path.with_name(path.name + '.meta').write_text(body)


def export(name, images, native_asset, method, timing=None, loop=False):
    source = CLIP_ROOT / name
    runtime = OUT / name
    source.mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    meta(runtime, 'folder')
    times = TIMING[timing]['durations'] if timing else [1000]
    assert len(images) == len(times), (name, len(images), len(times))
    baseline = BASE[native_asset]
    w, h = images[0].size
    sheet = blank((w * len(images), h))
    edits = []
    source_edits = []
    for i, image in enumerate(images):
        assert image.size == (w, h)
        assert set(image.getchannel('A').getdata()) <= {0, 255}
        assert set(image.getdata()) <= PALETTE | {(0, 0, 0, 0)}, name
        image.save(source / f'{i:02}.png')
        shutil.copyfile(source / f'{i:02}.png', runtime / f'{i:02}.png')
        meta(runtime / f'{i:02}.png', 'texture')
        sheet.alpha_composite(image, (i * w, 0))
        delta = [[x, y, *image.getpixel((x, y))] for y in range(h) for x in range(w)
                 if image.getpixel((x, y)) != images[0].getpixel((x, y))]
        (source / f'{i:02}.pixels.json').write_text(json.dumps(delta, separators=(',', ':')))
        source_delta = [[x, y, *baseline.getpixel((x, y)), *image.getpixel((x, y))] for y in range(h) for x in range(w)
                        if image.getpixel((x, y)) != baseline.getpixel((x, y))]
        (source / f'{i:02}.source-edits.json').write_text(json.dumps(source_delta, separators=(',', ':')))
        edits.append({'frame': i, 'changedPixelsFromFirstFrame': len(delta),
                      'changedPixelsFromNativeSource': len(source_delta), 'bounds': image.getbbox(),
                      'rgbaSha256': hashlib.sha256(image.tobytes()).hexdigest(),
                      'pngSha256': sha(source / f'{i:02}.png')})
    sheet.save(source / 'sheet.png')
    if len(images) > 1:
        images[0].save(source / 'native.apng', format='PNG', save_all=True, append_images=images[1:],
                       duration=times, loop=0, disposal=1, blend=0)
        decoded = Image.open(source / 'native.apng')
        assert decoded.n_frames == len(images), (name, decoded.n_frames, len(images))
        for i, image in enumerate(images):
            decoded.seek(i)
            assert decoded.convert('RGBA').tobytes() == image.tobytes(), (name, i, 'apng')
            assert round(decoded.info['duration']) == times[i], (name, i, decoded.info)
    buf = io.BytesIO()
    sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(images), 'chunks': [
        {'layout': [[i] for i in range(len(images))], 'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    (source / (name + '.piskel')).write_text(json.dumps({'modelVersion': 2, 'piskel': {
        'name': name, 'description': 'Image-first native derivative. Exact variable timing in clips.json/APNG. Pixel edits recorded against generated native source.',
        'fps': 20, 'width': w, 'height': h, 'layers': [json.dumps(layer)]}}))
    c = {'name': name, 'durations': times, 'width': w, 'height': h, 'loop': loop,
         'tiqueTiming': TIMING[timing].get('tiqueTiming') if timing else None,
         'source': 'actual generated anchor -> registered native derivative -> documented integer-pixel state edits'}
    CLIPS.append(c)
    AUDIT.append({'name': name, 'nativeAsset': native_asset, 'method': method, 'frames': edits})
    MAPPINGS.append({'name': name, 'nativeSource': f'Source/Native/{native_asset}.png',
                     'nativeSha256': sha(NATIVE / f'{native_asset}.png'), 'method': method,
                     'stateEdits': f'Clips/{name}/{{frame:02}}.source-edits.json',
                     'runtimeClip': runtime.relative_to(REPO).as_posix(), 'frames': edits})


def validate_editable():
    for clip in CLIPS:
        name = clip['name']
        source = CLIP_ROOT / name
        piskel = json.loads((source / (name + '.piskel')).read_text())['piskel']
        layer = json.loads(piskel['layers'][0])
        sheet = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
        assert sheet.size == (clip['width'] * len(clip['durations']), clip['height'])
        assert layer['frameCount'] == len(clip['durations'])
        base = Image.open(source / '00.png').convert('RGBA')
        baseline = BASE[next(m['nativeAsset'] for m in AUDIT if m['name'] == name)]
        for i in range(layer['frameCount']):
            final = Image.open(source / f'{i:02}.png').convert('RGBA')
            replay = base.copy()
            for x, y, r, g, b, a in json.loads((source / f'{i:02}.pixels.json').read_text()):
                replay.putpixel((x, y), (r, g, b, a))
            assert replay.tobytes() == final.tobytes(), (name, i, 'delta-replay')
            source_replay = baseline.copy()
            for x, y, *colors in json.loads((source / f'{i:02}.source-edits.json').read_text()):
                assert source_replay.getpixel((x, y)) == tuple(colors[:4])
                source_replay.putpixel((x, y), tuple(colors[4:]))
            assert source_replay.tobytes() == final.tobytes(), (name, i, 'source-replay')
            frame = sheet.crop((i * final.width, 0, (i + 1) * final.width, final.height))
            assert frame.tobytes() == final.tobytes(), (name, i, 'piskel-replay')
            assert sha(source / f'{i:02}.png') == sha(OUT / name / f'{i:02}.png')
            settings = (OUT / name / f'{i:02}.png.meta').read_text()
            assert 'filterMode: 0' in settings and 'enableMipMap: 0' in settings
            assert 'textureCompression: 1' not in settings and 'spritePixelsToUnits: 64' in settings
        if name in TIMING:
            assert clip['durations'] == TIMING[name]['durations'], name
    for mask in range(16):
        a = wall(mask)
        if mask & 2:
            b = wall((mask & (1 | 4)) | 8)
            assert [a.getpixel((35, y)) for y in range(36)] == [b.getpixel((0, y)) for y in range(36)], ('EW', mask)
        if mask & 4:
            b = wall((mask & (2 | 8)) | 1)
            assert [a.getpixel((x, 35)) for x in range(36)] == [b.getpixel((x, 0)) for x in range(36)], ('NS', mask)


def enlarged(image, scale=4):
    return image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)


def qa():
    dest = ROOT / 'QA'
    dest.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1120, ((len(CLIPS) + 6) // 7) * 190), (17, 27, 36))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(CLIPS):
        image = enlarged(Image.open(OUT / c['name'] / f"{len(c['durations']) // 2:02}.png").convert('RGBA'))
        x, y = (i % 7) * 160, (i // 7) * 190
        sheet.paste(image, (x + (144 - image.width) // 2, y + 144 - image.height), image)
        d.text((x + 3, y + 151), c['name'], fill=(190, 215, 223))
        d.text((x + 3, y + 168), f"{c['width']}x{c['height']} / {len(c['durations'])}f", fill=(130, 158, 173))
    sheet.save(dest / 'clip-all-state-contact.png')
    ImageOps.grayscale(sheet).save(dest / 'clip-all-state-grayscale.png')
    occupied = Image.new('RGB', (700, 220), (17, 27, 36))
    for n, (kind, obj) in enumerate((('amber', weight('docked', 0)), ('cyan', orb('docked', 0)))):
        sample = BASE['floor'].copy()
        sample.alpha_composite(socket(kind, 4))
        sample.alpha_composite(obj, (3, 0) if kind == 'amber' else (5, 6))
        large = enlarged(sample, 5)
        occupied.paste(large, (30 + n * 330, 8), large)
    ImageDraw.Draw(occupied).text((20, 194), 'Native composition only: source rim + registered object. Not runtime capture.', fill=(190, 215, 223))
    occupied.save(dest / 'clip-occupied-rims.png')
    for mode, fn in (('weight', weight), ('orb', orb)):
        images = [enlarged(fn('moving', i), 6).convert('RGB') for i in range(len(TIMING[('battery' if mode == 'weight' else 'orb') + '-moving']['durations']))]
        images[0].save(dest / f'clip-{mode}-moving.gif', save_all=True, append_images=images[1:],
                       duration=TIMING[('battery' if mode == 'weight' else 'orb') + '-moving']['durations'], loop=0)


def main():
    global PALETTE
    for asset in ('wall', 'floor', 'weight', 'orb', 'weight_socket', 'orb_socket'):
        BASE[asset] = Image.open(NATIVE / f'{asset}.png').convert('RGBA')
        PALETTE |= {p for p in BASE[asset].getdata() if p[3]}
    PALETTE.add(ERROR)  # Reserved unchanged error-state RGB, recorded separately.
    assert len(PALETTE) <= 48, len(PALETTE)
    OUT.mkdir(parents=True, exist_ok=True)
    CLIP_ROOT.mkdir(parents=True, exist_ok=True)
    meta(OUT, 'folder')
    export('floor', [BASE['floor'].copy()], 'floor', 'Unchanged generated-source native floor')
    for mask in range(16):
        export(f'wall-{mask:02}', [wall(mask)], 'wall', f'Connected border strip samples only; adjacency mask {mask}')
    for mode in ('idle', 'moving', 'docked'):
        name = 'battery-' + mode
        export(name, [weight(mode, i) for i in range(len(TIMING[name]['durations']))], 'weight',
               'Source handle integer 1px flex; body/foot fixed. Docked source contact pixels highlight.' if mode != 'idle' else 'Unchanged native source', name, mode == 'moving')
        name = 'orb-' + mode
        export(name, [orb(mode, i) for i in range(len(TIMING[name]['durations']))], 'orb',
               'Source inner meridian clusters integer remap; fixed silhouette/light. Docked source contact highlight.' if mode != 'idle' else 'Unchanged native source', name, mode == 'moving')
    for kind in ('amber', 'cyan'):
        asset = 'weight_socket' if kind == 'amber' else 'orb_socket'
        export(kind + '-slot-empty', [socket(kind)], asset, 'Unchanged native source', kind + '-slot-empty')
        export(kind + '-slot-filled', [socket(kind, 4)], asset, 'Four source outer rim quadrants highlighted, cavity unchanged', kind + '-slot-filled')
        export(kind + '-slot-wrong', [socket(kind, 0, True)], asset, 'Unchanged existing red corner port marks reused over native socket', kind + '-slot-wrong')
        export(kind + '-slot-connect', [socket(kind, n) for n in (0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4)], asset,
               'Source outer rim quadrants light sequentially; existing Attack timing', kind + '-slot-connect')
    data = {'clips': CLIPS}
    (OUT / 'clips.json').write_text(json.dumps(data, indent=2))
    meta(OUT / 'clips.json', 'text')
    (CLIP_ROOT / 'clips.json').write_text(json.dumps(data, indent=2))
    provenance = json.loads((ROOT / 'Source/provenance.json').read_text())
    (CLIP_ROOT / 'export-manifest.json').write_text(json.dumps({
        'revision': 'readability-image-first-v2', 'date': '2026-10-02',
        'method': 'Actual generated anchors -> registered native-pixel derivation -> source-relative edits -> Return editable/export pipeline',
        'generatedAnimationStripsUsed': False, 'oldAssetsModified': False,
        'generatedSources': {name: {'path': path, 'sha256': sha(ROOT / path)} for name, path in provenance['selectedPreviewFiles'].items()},
        'nativePalettePath': 'Source/Native/palette.json', 'exportPalette': sorted([list(p) for p in PALETTE]),
        'reusedErrorMarks': [{'path': (RESOURCE / 'ReadabilityArt' / f'{kind}-slot-wrong/00.png').relative_to(REPO).as_posix(),
                             'sha256': sha(RESOURCE / 'ReadabilityArt' / f'{kind}-slot-wrong/00.png'), 'rgba': ERROR} for kind in ('amber', 'cyan')],
        'wallMask': {'N': 1, 'E': 2, 'S': 4, 'W': 8},
        'registration': {'weight': {'width': 30, 'height': 32, 'cellOffset': [3, 0]}, 'orb': {'width': 26, 'height': 26, 'cellOffset': [5, 6]}, 'tile': [36, 36], 'spritePixelsToUnits': 64},
        'mappings': MAPPINGS, 'runtimePath': OUT.relative_to(REPO).as_posix(),
        'scope': 'Technical export candidate. No visual approval or human playtest claim.'
    }, indent=2))
    (CLIP_ROOT / 'pixel-edit-audit.json').write_text(json.dumps(AUDIT, indent=2))
    validate_editable()
    qa()
    validation = {'clips': len(CLIPS), 'frames': sum(len(c['durations']) for c in CLIPS), 'paletteColors': len(PALETTE),
                  'alpha': [0, 255], 'point': True, 'mipmaps': False, 'compression': False, 'spritePixelsToUnits': 64,
                  'apngRoundtrip': 'all multi-frame clips byte-identical, timings identical',
                  'piskelReplay': 'all frames byte-identical', 'pixelDeltaReplay': 'all frames byte-identical',
                  'nativeSourceEditReplay': 'all frames byte-identical', 'pngRuntimeCopies': 'SHA256 exact',
                  'timingSource': 'ReturnV2/StateArt/clips.json', 'wallMaskReciprocalContinuity': True,
                  'orbMeridianSourcePixelCount': len(orb_seam_data()), 'rulesChanged': False,
                  'runtimeCapture': False, 'humanAppearanceApproval': 'pending'}
    (ROOT / 'QA/clip-validation.json').write_text(json.dumps(validation, indent=2))
    assert validation['clips'] == 31 and validation['frames'] == 77
    print(json.dumps(validation))


if __name__ == '__main__':
    main()
