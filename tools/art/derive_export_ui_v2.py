"""Image-first compact UI skin conversion and Return editable-source export.

No appearance is painted here. Derivation requires actual, inspected panel and
button imagegen anchors. Every target pixel records its original area footprint.
Button states change only palette entries of the same silhouette. The licensed
pixel font and already-approved arrow glyphs are unchanged reuse, not generation.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import re
import shutil
import uuid

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont


REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / 'unity/TiqueReturnPrototype'
ROOT = REPO / 'art/return-ui-v2'
NATIVE = ROOT / 'Source/Native'
DERIVATION = ROOT / 'Source/Derivation'
CLIPS = ROOT / 'Clips'
QA = ROOT / 'QA'
OUT = PROJECT / 'Assets/Resources/ReturnV2/UiV2'
FEEDBACK = PROJECT / 'Assets/Resources/ReturnV2/Feedback'
FONT_SOURCE = REPO / 'art/return-v5-feedback/Source/Font'
SPECS = {'panel': {'width': 96, 'slice': [10, 6, 10, 6]},
         'button': {'width': 112, 'slice': [8, 5, 8, 5]}}
# Clockwork material-ramp normalization; no alpha or geometry is introduced by
# this fixed palette. Existing steel/cyan/brass ramps retain their established
# game roles. Source colors are assigned with dark/material family separation.
PALETTE = np.array([(9, 19, 27), (16, 25, 33), (25, 39, 48), (35, 51, 63),
                    (41, 57, 67), (60, 76, 87), (86, 116, 130), (121, 143, 153),
                    (164, 183, 188), (234, 255, 237),
                    (25, 108, 119), (25, 193, 209), (81, 224, 223), (167, 249, 241),
                    (121, 83, 51), (181, 139, 70), (239, 183, 88),
                    (255, 207, 122), (255, 241, 197)], np.uint8)
TEMPLATE = FEEDBACK / 'font.png.meta'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba_sha(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def write_json(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False,
                             indent=None if compact else 2,
                             separators=(',', ':') if compact else None) + '\n', encoding='utf-8')


def source_selection():
    path = ROOT / 'Source/provenance.json'
    data = json.loads(path.read_text())
    selected = data.get('selectedNativeSources', data.get('selectedPreviewFiles', {}))
    if not selected:
        selected = {s['asset']: 'Source/' + s['savedPath'] for s in data.get('sources', [])}
    inspected = data.get('generatedAnchorsInspected', data.get('generatedAnchorsInspectedByProductionAgent'))
    assert inspected is True and data.get('generatedAnchorsShown', True), 'STOP: parent inspection/show gate missing'
    assert set(SPECS) <= set(selected), 'STOP: actual panel and button anchors must be selected'
    return selected, path


def source_sample(path, width):
    original = Image.open(path).convert('RGBA')
    a = np.array(original)
    mask = a[..., 3] >= 128
    assert mask.any(), 'Actual source contains no alpha>=128 pixels'
    yy, xx = np.where(mask)
    crop = [int(xx.min()), int(yy.min()), int(xx.max() + 1), int(yy.max() + 1)]
    cut = original.crop(crop)
    # One uniform whole-asset conversion preserves the anchor's shape/aspect.
    size = [width, max(9, round(cut.height * width / cut.width))]
    small = cut.convert('RGBa').resize(size, Image.Resampling.BOX).convert('RGBA')
    sampled = np.array(small)
    sharpened = np.array(small.convert('RGB').filter(
        ImageFilter.UnsharpMask(radius=.4, percent=45, threshold=2)).convert('RGBA'))
    sharpened[..., 3] = np.where(sampled[..., 3] >= 128, 255, 0)
    sharpened[sharpened[..., 3] == 0] = 0
    return sharpened, {'generatedDimensions': list(original.size), 'cropRect': crop,
                       'nativeDimensions': size, 'alphaThreshold': 128,
                       'wholeAssetUniformScale': width / cut.width,
                       'unsharp': {'radius': .4, 'percent': 45, 'threshold': 2}}


def palette_map(a):
    out = a.copy()
    mask = a[..., 3] > 0
    pixels = a[mask, :3].astype(int)
    distances = ((pixels[:, None] - PALETTE[None].astype(int)) ** 2).sum(-1)
    # Preserve cyan and brass details rather than matching them to gray steel.
    warm = (pixels[:, 0] > pixels[:, 2] * 1.4) & (pixels[:, 0] > pixels[:, 1] * 1.08)
    # Dark navy is cool too, but it is NOT an emissive cyan accent. Without
    # this luminance gate, ordinary blue-gray source fill becomes turquoise.
    cyan = (pixels[:, 1] > pixels[:, 0] * 1.5) & (pixels[:, 2] > pixels[:, 0] * 1.5) & (pixels.max(-1) >= 90)
    dark = pixels.max(-1) < 44
    allowed = np.zeros(distances.shape, bool)
    allowed[dark, :5] = True
    allowed[warm & ~dark, 14:] = True
    allowed[cyan & ~dark & ~warm, 10:14] = True
    allowed[~dark & ~warm & ~cyan, :10] = True
    distances[~allowed] += 10 ** 8
    out[mask, :3] = PALETTE[distances.argmin(1)]
    return out


def pixels_delta(base, image, before=False):
    return [[x, y, *base.getpixel((x, y)), *image.getpixel((x, y))] if before
            else [x, y, *image.getpixel((x, y))]
            for y in range(image.height) for x in range(image.width)
            if base.getpixel((x, y)) != image.getpixel((x, y))]


def derive():
    selected, selection_path = source_selection()
    for folder in (NATIVE, DERIVATION, QA):
        folder.mkdir(parents=True, exist_ok=True)
    records = {}
    lookup = {tuple(c): i for i, c in enumerate(PALETTE.tolist())}
    for name, spec in SPECS.items():
        source = ROOT / selected[name]
        assert source.is_file(), 'STOP: actual generated source missing; no substitute'
        sampled, record = source_sample(source, spec['width'])
        mapped = palette_map(sampled)
        Image.fromarray(sampled).save(DERIVATION / f'{name}-area-sampled.png')
        native = Image.fromarray(mapped)
        native.save(NATIVE / f'{name}.png')
        crop, size = record['cropRect'], record['nativeDimensions']
        indices = [[lookup.get(tuple(map(int, mapped[y, x, :3])), -1)
                    if mapped[y, x, 3] else -1 for x in range(size[0])]
                   for y in range(size[1])]
        record.update({'generatedSource': selected[name], 'sourceSha256': sha(source),
                       'nativeSource': f'Source/Native/{name}.png',
                       'nativeSha256': sha(NATIVE / f'{name}.png'),
                       'slice': spec['slice'], 'alphaPixelsAdded': 0,
                       'paletteIndexMap': f'Source/Derivation/{name}-pixel-map.json'})
        write_json(DERIVATION / f'{name}-pixel-map.json', {
            'asset': name, 'source': selected[name], 'sourceSha256': sha(source),
            'cropRect': crop, 'sampleSize': size, 'unsharp': record['unsharp'],
            'sourceStep': [(crop[2] - crop[0]) / size[0], (crop[3] - crop[1]) / size[1]],
            'interpretation': 'Entry [y][x] is its fixed palette index or -1 transparent. '
                'Original BOX footprint is [left+x*stepX,top+y*stepY,left+(x+1)*stepX,top+(y+1)*stepY]. '
                'Unsharp reads adjacent area samples. Alpha comes from premultiplied original sampling '
                'thresholded at 128. No arbitrary silhouette or frame geometry is painted.',
            'paletteIndices': indices, 'cleanupEdits': []}, compact=True)
        records[name] = record
    write_json(NATIVE / 'palette.json', {'colors': PALETTE.tolist(), 'cap': 19, 'dither': False,
               'kind': 'fixed-clockwork-navy-steel-cyan-brass-material-normalization'})
    write_json(DERIVATION / 'native-derivation.json', {
        'version': 2, 'method': 'Actual imagegen anchors / ratio-preserving premultiplied BOX / mild unsharp / fixed material palette / binary alpha',
        'script': 'tools/art/derive_export_ui_v2.py', 'scriptSha256': sha(Path(__file__)),
        'selectionSource': 'Source/provenance.json', 'selectionSha256': sha(selection_path),
        'palette': 'Source/Native/palette.json', 'paletteSha256': sha(NATIVE / 'palette.json'),
        'assets': records, 'humanAppearanceApproval': 'pending', 'gameExecuted': False})
    native_contact(records)
    button_contact(Image.open(NATIVE / 'button.png').convert('RGBA'))
    print(json.dumps({'derivedAssets': 2, 'native': {n: m['nativeDimensions'] for n, m in records.items()},
                      'inspectionRequiredBeforeExport': True}))


def native_contact(records):
    board = Image.new('RGB', (1000, 520), (12, 22, 30))
    draw = ImageDraw.Draw(board)
    draw.text((16, 12), 'ACTUAL IMAGEGEN -> NATIVE CANDIDATE / NOT RUNTIME OR HUMAN APPROVAL', fill=(225, 235, 238))
    for i, name in enumerate(SPECS):
        x = 16 + i * 480
        record = records[name]
        raw = Image.open(ROOT / record['generatedSource']).convert('RGBA').crop(record['cropRect'])
        raw.thumbnail((410, 185), Image.Resampling.LANCZOS)
        board.paste(raw, (x + (410 - raw.width) // 2, 65 + (185 - raw.height) // 2), raw)
        draw.text((x, 40), name + ' / generated anchor', fill=(205, 220, 225))
        native = Image.open(NATIVE / f'{name}.png').convert('RGBA')
        enlarged = native.resize((native.width * 4, native.height * 4), Image.Resampling.NEAREST)
        draw.text((x, 275), f'Native {native.width}x{native.height} / 4x nearest', fill=(205, 220, 225))
        board.paste(enlarged, (x + 12, 302), enlarged)
        draw.text((x, 470), 'Actual 1x chip:', fill=(145, 165, 180))
        board.paste(native, (x + 100, 462), native)
    board.save(QA / 'native-source-comparison.png')


def meta(path, kind, borders=None):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-ui-v2/' + path.relative_to(REPO).as_posix()).hex
    if kind == 'texture':
        body = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, TEMPLATE.read_text(), count=1)
        body = body.replace('textureCompression: 1', 'textureCompression: 0')
        body = body.replace('filterMode: 1', 'filterMode: 0').replace('enableMipMap: 1', 'enableMipMap: 0')
        body = re.sub(r'(?m)^  spritePixelsToUnits:.*$', '  spritePixelsToUnits: 64', body)
        if borders:
            left, top, right, bottom = borders
            body = re.sub(r'(?m)^  spriteBorder:.*$',
                          f'  spriteBorder: {{x: {left}, y: {bottom}, z: {right}, w: {top}}}', body)
    else:
        body = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder':
            body += 'folderAsset: yes\n'
        body += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    path.with_name(path.name + '.meta').write_text(body)


def button_state(base, state):
    if state == 'button':
        return base.copy()
    ramps = {'button-selected': PALETTE[10:14], 'button-pressed': PALETTE[14:],
             'button-disabled': PALETTE[2:7]}
    ramp = ramps[state]
    out = base.copy()
    for y in range(base.height):
        for x in range(base.width):
            p = base.getpixel((x, y))
            if not p[3] or max(p[:3]) < 55:
                continue  # Source dark negative-space/interior remains unchanged.
            luminance = p[0] * .2126 + p[1] * .7152 + p[2] * .0722
            if state == 'button-disabled':
                luminance *= .60
            else:
                luminance += 12 if state == 'button-selected' else 7
            q = min(ramp, key=lambda c: abs(c[0] * .2126 + c[1] * .7152 + c[2] * .0722 - luminance))
            out.putpixel((x, y), (*map(int, q), 255))
    assert out.getchannel('A').tobytes() == base.getchannel('A').tobytes()
    return out


def button_contact(base):
    """Preview actual source-derived palette states without runtime export."""
    board = Image.new('RGB', (1000, 480), (12, 22, 30))
    draw = ImageDraw.Draw(board)
    draw.text((16, 12), 'SOURCE BUTTON / PALETTE-ONLY STATES / SAME ALPHA / PREVIEW ONLY', fill=(225, 235, 238))
    for i, name in enumerate(('button', 'button-selected', 'button-pressed', 'button-disabled')):
        frame = button_state(base, name)
        x, y = 16 + i % 2 * 480, 42 + i // 2 * 210
        draw.text((x, y), name, fill=(190, 210, 220))
        enlarged = frame.resize((frame.width * 4, frame.height * 4), Image.Resampling.NEAREST)
        board.paste(enlarged, (x, y + 26), enlarged)
        draw.text((x, y + 130), 'Actual 1x:', fill=(145, 165, 180))
        board.paste(frame, (x + 76, y + 126), frame)
    board.save(QA / 'native-button-palette-states.png')


def editable(name, frames, times, baseline, method, runtime=True):
    source = CLIPS / name
    source.mkdir(parents=True, exist_ok=True)
    w, h = frames[0].size
    sheet = Image.new('RGBA', (w * len(frames), h))
    records = []
    for i, frame in enumerate(frames):
        assert set(frame.getchannel('A').getdata()) <= {0, 255}
        frame.save(source / f'{i:02}.png')
        sheet.alpha_composite(frame, (i * w, 0))
        write_json(source / f'{i:02}.pixels.json', pixels_delta(frames[0], frame), compact=True)
        edits = pixels_delta(baseline, frame, before=True)
        write_json(source / f'{i:02}.source-edits.json', edits, compact=True)
        record = {'frame': i, 'pngSha256': sha(source / f'{i:02}.png'),
                  'rgbaSha256': rgba_sha(frame), 'nativeSourceChangedPixels': len(edits)}
        if runtime:
            folder = OUT / name
            folder.mkdir(parents=True, exist_ok=True)
            meta(folder, 'folder')
            dest = folder / f'{i:02}.png'
            shutil.copyfile(source / f'{i:02}.png', dest)
            meta(dest, 'texture', SPECS['panel' if name == 'panel' else 'button']['slice'])
            record['runtimePath'] = dest.relative_to(REPO).as_posix()
        records.append(record)
    sheet.save(source / 'sheet.png')
    # Even static clips carry the established APNG-compatible PNG source.
    frames[0].save(source / 'native.apng', format='PNG', save_all=True,
                   append_images=frames[1:], duration=times, loop=0, disposal=1, blend=0)
    buf = io.BytesIO()
    sheet.save(buf, format='PNG')
    layer = {'name': name, 'opacity': 1, 'frameCount': len(frames), 'chunks': [
        {'layout': [[i] for i in range(len(frames))],
         'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
    write_json(source / f'{name}.piskel', {'modelVersion': 2, 'piskel': {
        'name': name, 'description': method + '; exact timing/deltas included.',
        'fps': 20, 'width': w, 'height': h, 'layers': [json.dumps(layer)]}})
    decoded = Image.open(source / 'native.apng')
    assert getattr(decoded, 'n_frames', 1) == len(frames)
    decoded_sheet = Image.open(io.BytesIO(base64.b64decode(layer['chunks'][0]['base64PNG'].split(',', 1)[1]))).convert('RGBA')
    for i, frame in enumerate(frames):
        decoded.seek(i)
        assert decoded.convert('RGBA').tobytes() == frame.tobytes()
        if len(frames) > 1:
            assert round(decoded.info['duration']) == times[i]
        assert decoded_sheet.crop((i * w, 0, (i + 1) * w, h)).tobytes() == frame.tobytes()
        first_replay = frames[0].copy()
        for x, y, r, g, b, a in json.loads((source / f'{i:02}.pixels.json').read_text()):
            first_replay.putpixel((x, y), (r, g, b, a))
        assert first_replay.tobytes() == frame.tobytes()
        replay = baseline.copy()
        for x, y, *colors in json.loads((source / f'{i:02}.source-edits.json').read_text()):
            assert replay.getpixel((x, y)) == tuple(colors[:4])
            replay.putpixel((x, y), tuple(colors[4:]))
        assert replay.tobytes() == frame.tobytes()
    return {'name': name, 'width': w, 'height': h, 'durations': times,
            'method': method, 'frames': records}


def build_font():
    """Keep all approved glyph bitmaps exactly; add only missing source glyphs."""
    OUT.mkdir(parents=True, exist_ok=True)
    old_json = FEEDBACK / 'font.json'
    old_png = FEEDBACK / 'font.png'
    old = json.loads(old_json.read_text())
    assert old['cell'] == 16
    old_image = Image.open(old_png).convert('RGBA')
    fontpath = FONT_SOURCE / 'neodgm.ttf'
    licensepath = FONT_SOURCE / 'LICENSE.txt'
    approved_font = json.loads((FONT_SOURCE / 'provenance.json').read_text())
    assert sha(fontpath) == approved_font['sha256'], 'Licensed font source changed from approved source'
    assert sha(licensepath) == sha(FEEDBACK / 'FONT-LICENSE.txt'), 'Existing font license source mismatch'
    cmap = TTFont(str(fontpath)).getBestCmap()
    scripts = sorted((PROJECT / 'Assets/Scripts').glob('*.cs'))
    corpus = ''.join(p.read_text(encoding='utf-8-sig') for p in scripts)
    corpus += ''.join(chr(c) for c in range(32, 127)) + '↑↓←→◆●…·'
    required = sorted({c for c in corpus if not c.isspace() or c == ' '})
    additions = [c for c in required if c not in old['characters']]
    missing = [c for c in additions if ord(c) not in cmap]
    assert not missing, 'Missing licensed font glyphs: ' + repr(missing)
    chars = old['characters'] + ''.join(additions)
    cols = old['columns']
    atlas = Image.new('RGBA', (cols * 16, ((len(chars) + cols - 1) // cols) * 16))
    font = ImageFont.truetype(str(fontpath), 16)
    glyph_records = []
    for i, c in enumerate(chars):
        if i < len(old['characters']):
            tile = old_image.crop((i % cols * 16, i // cols * 16,
                                   i % cols * 16 + 16, i // cols * 16 + 16))
            method = 'unchanged-approved-atlas-tile'
        else:
            glyph = Image.new('L', (16, 16))
            ImageDraw.Draw(glyph).text((0, 0), c, font=font, fill=255, stroke_width=0)
            tile = Image.new('RGBA', (16, 16), (255, 255, 255, 0))
            tile.putalpha(glyph.point(lambda p: 255 if p >= 128 else 0))
            method = 'unchanged-licensed-font-outline-to-binary-16px-tile'
        atlas.alpha_composite(tile, (i % cols * 16, i // cols * 16))
        # Alpha_composite normalizes transparent RGB to zero; visible geometry
        # and binary mask remain exactly the approved unchanged source tile.
        glyph_records.append({'character': c, 'codepoint': ord(c), 'index': i,
                              'method': method, 'alphaSha256': hashlib.sha256(tile.getchannel('A').tobytes()).hexdigest()})
    atlas.save(OUT / 'font.png')
    retained_rgba_exact = True
    for i, c in enumerate(old['characters']):
        rect = (i % cols * 16, i // cols * 16, i % cols * 16 + 16, i // cols * 16 + 16)
        retained_rgba_exact &= old_image.crop(rect).tobytes() == atlas.crop(rect).tobytes()
    assert retained_rgba_exact, 'Existing approved glyph pixels changed during atlas packing'
    write_json(OUT / 'font.json', {'characters': chars, 'columns': cols, 'cell': 16})
    shutil.copyfile(licensepath, OUT / 'FONT-LICENSE.txt')
    for name in ('font.png', 'font.json', 'FONT-LICENSE.txt'):
        meta(OUT / name, 'texture' if name.endswith('.png') else 'text')
    # Historical non-grid-size experiments are preserved, but never regenerated
    # or bound by the renderer: this font's 16px grid needs integer scaling.
    rasters = []
    for size in (12, 14, 20, 24):
        path = OUT / f'font-{size}.png'
        if path.exists():
            rasters.append({'size': size, 'path': path.relative_to(REPO).as_posix(), 'sha256': sha(path),
                            'status': 'rejected-historical-candidate-not-loaded',
                            'reason': 'Non-integer 16px-grid rasterization loses or clips glyph strokes'})
    record = {'family': 'NeoDunggeunmo', 'version': '1.601', 'license': 'SIL OFL 1.1',
              'reuseBasis': 'Unchanged approved font outlines and old glyph/arrow masks; no new font design or generated lettering.',
              'source': fontpath.relative_to(REPO).as_posix(), 'sourceSha256': sha(fontpath),
              'licensePath': licensepath.relative_to(REPO).as_posix(), 'licenseSha256': sha(licensepath),
              'approvedAtlasSource': old_png.relative_to(REPO).as_posix(), 'approvedAtlasSha256': sha(old_png),
              'approvedIndexSha256': sha(old_json), 'preservedGlyphCount': len(old['characters']),
              'addedGlyphCount': len(additions), 'addedCharacters': ''.join(additions),
              'glyphCount': len(chars), 'missingGlyphs': [], 'cell': 16,
              'preservedGlyphRgbaExact': retained_rgba_exact,
              'runtimeRendererSizes': [16, 32], 'nativeSizedAtlases': [], 'rejectedHistoricalAtlases': rasters,
              'bodyRendererSizes': {'default': 16, 'largeText': 16},
              'headingRendererSizes': {'default': 16, 'largeText': 32},
              'rendererRule': 'Original 16px atlas sampled with Point; only integer multiples allowed',
              'feedbackAssetsModified': False,
              'coverageRule': 'Every non-whitespace codepoint in current Assets/Scripts/*.cs plus ASCII and approved control symbols.',
              'corpus': {p.relative_to(REPO).as_posix(): sha(p) for p in scripts},
              'runtimeAtlas': (OUT / 'font.png').relative_to(REPO).as_posix(),
              'runtimeAtlasSha256': sha(OUT / 'font.png'), 'glyphs': glyph_records}
    write_json(ROOT / 'Source/Font/provenance.json', record)
    write_json(QA / 'font-coverage.json', {'characters': len(chars), 'preservedGlyphs': len(old['characters']),
               'preservedGlyphRgbaExact': retained_rgba_exact, 'addedGlyphs': len(additions),
               'currentCSharpCorpusMissingCharacters': sorted(set(required) - set(chars)),
               'licensedCmapMissingCharacters': missing, 'binaryAlpha': set(atlas.getchannel('A').getdata()) <= {0, 255},
               'nativeSizedAtlases': [], 'rejectedHistoricalAtlases': rasters,
               'sourceCorpusSha256': record['corpus'], 'runtimeOrBuildExecuted': False})
    return record


def export():
    selected, selection_path = source_selection()
    native_record_path = DERIVATION / 'native-derivation.json'
    native = json.loads(native_record_path.read_text())
    assert native['selectionSha256'] == sha(selection_path), 'Immutable source selection changed after derivation'
    for name, record in native['assets'].items():
        assert sha(ROOT / selected[name]) == record['sourceSha256']
        assert sha(NATIVE / f'{name}.png') == record['nativeSha256']
    OUT.mkdir(parents=True, exist_ok=True)
    meta(OUT, 'folder')
    baseline_path = ROOT / 'Source/feedback-baseline.json'
    current_feedback = {p.relative_to(REPO).as_posix(): sha(p)
                        for p in FEEDBACK.rglob('*') if p.is_file()}
    if baseline_path.exists():
        before = json.loads(baseline_path.read_text())['files']
    else:
        # Freeze the earliest captured export baseline rather than silently
        # blessing current files after an unrelated change between reruns.
        old_manifest = ROOT / 'export-manifest.json'
        captured = json.loads(old_manifest.read_text()).get('oldFeedbackUnchanged', {}) if old_manifest.exists() else {}
        before = {Path(p).relative_to(REPO).as_posix() if Path(p).is_absolute() else p: digest
                  for p, digest in captured.items()} or current_feedback
        assert before == current_feedback, 'Feedback changed since first UI export'
        write_json(baseline_path, {'scope': 'Immutable old Feedback file/hash baseline captured before initial compact UI production',
                                   'files': before})
    assert before == current_feedback, 'Immutable Feedback file/hash baseline changed'
    panel = Image.open(NATIVE / 'panel.png').convert('RGBA')
    button = Image.open(NATIVE / 'button.png').convert('RGBA')
    records = [editable('panel', [panel], [1000], panel, 'Unchanged generated-source native panel')]
    states = []
    for state in ('button', 'button-selected', 'button-pressed', 'button-disabled'):
        frame = button_state(button, state)
        states.append(frame)
        records.append(editable(state, [frame], [1000], button,
                                'Generated-source button; documented palette-only state remap, identical alpha and silhouette'))
    preview = editable('button-state-preview', states, [800, 800, 800, 800], button,
                       'Diagnostic source-state preview, not an in-game animation', runtime=False)
    data = {'clips': [{k: rec[k] for k in ('name', 'width', 'height', 'durations')} for rec in records]}
    write_json(OUT / 'clips.json', data)
    write_json(CLIPS / 'clips.json', data)
    skins = {'version': 2, 'skins': [
        {'name': rec['name'], 'width': rec['width'], 'height': rec['height'],
         'margins': SPECS['panel' if rec['name'] == 'panel' else 'button']['slice']}
        for rec in records], 'sliceOrder': ['left', 'top', 'right', 'bottom'],
        'rendering': 'Keep corners native; crop/tile native edge pixels; do not scale whole skin geometry.'}
    write_json(OUT / 'skins.json', skins)
    for name in ('clips.json', 'skins.json'):
        meta(OUT / name, 'text')
    font = build_font()
    for p, digest in before.items():
        assert sha(REPO / p) == digest, 'Existing Feedback asset changed: ' + p
    palette = {tuple(p) + (255,) for p in PALETTE.tolist()} | {(0, 0, 0, 0)}
    for rec in records:
        for frame in rec['frames']:
            image = Image.open(REPO / frame['runtimePath']).convert('RGBA')
            assert set(image.getdata()) <= palette
            assert sha(REPO / frame['runtimePath']) == frame['pngSha256']
            settings = (REPO / (frame['runtimePath'] + '.meta')).read_text()
            assert 'filterMode: 0' in settings and 'enableMipMap: 0' in settings
            assert 'textureCompression: 1' not in settings and 'spritePixelsToUnits: 64' in settings
    write_json(ROOT / 'export-manifest.json', {
        'version': 2, 'date': '2026-10-02', 'source': 'Actual generated anchors inspected before native conversion',
        'sourceSelection': 'Source/provenance.json', 'sourceSelectionSha256': sha(selection_path),
        'nativeDerivation': 'Source/Derivation/native-derivation.json', 'nativeDerivationSha256': sha(native_record_path),
        'script': 'tools/art/derive_export_ui_v2.py', 'scriptSha256': sha(Path(__file__)),
        'clips': records, 'diagnosticStatePreview': preview, 'skins': skins,
        'font': {'path': 'Source/Font/provenance.json', 'sha256': sha(ROOT / 'Source/Font/provenance.json'),
                 'preservedGlyphCount': font['preservedGlyphCount'], 'addedGlyphCount': font['addedGlyphCount']},
        'runtimeResource': OUT.relative_to(REPO).as_posix(), 'oldFeedbackUnchanged': before,
        'feedbackBaseline': 'Source/feedback-baseline.json', 'feedbackBaselineSha256': sha(baseline_path),
        'humanAppearanceApproval': 'pending', 'runtimeCapture': False, 'gameExecuted': False})
    validation = {'runtimeClips': len(records), 'runtimeFrames': sum(len(r['durations']) for r in records),
                  'binaryAlpha': True, 'paletteCap': len(PALETTE), 'point': True,
                  'mipmaps': False, 'compression': False, 'piskelReplay': True,
                  'apngReplay': True, 'sourceDeltaReplay': True, 'runtimePngExactCopy': True,
                  'firstFramePixelDeltaReplay': True,
                  'buttonStateAlphaInvariant': True, 'fontRepertoire': font['glyphCount'],
                  'addedFontGlyphs': font['addedGlyphCount'], 'fontCoverage': True,
                  'feedbackAssetsUnchanged': True, 'runtimeOrBuildExecuted': False,
                  'humanAppearanceApproval': 'pending'}
    write_json(QA / 'export-validation.json', validation)
    print(json.dumps(validation))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--derive', action='store_true')
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--font-only', action='store_true')
    parser.add_argument('--inspected-anchors', action='store_true')
    parser.add_argument('--inspected-native', action='store_true')
    args = parser.parse_args()
    if args.derive:
        if not args.inspected_anchors:
            raise SystemExit('STOP: actual imagegen anchors must be inspected/shown first')
        derive()
    if args.export:
        if not args.inspected_native:
            raise SystemExit('STOP: parent must inspect native preview before runtime export')
        export()
    if args.font_only:
        print(json.dumps({'fontGlyphs': build_font()['glyphCount']}))


if __name__ == '__main__':
    main()
