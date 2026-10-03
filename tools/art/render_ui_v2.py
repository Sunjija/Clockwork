#!/usr/bin/env python3
"""Offline review of exact production UiPlan commands, never a Unity capture.

Only composes actual image-first exported skins, unchanged licensed font tiles,
approved sprites and earlier world-camera samples. Does not author new assets,
change game state, launch Unity or claim live input/GUI correctness.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / 'unity/TiqueReturnPrototype'
RESOURCES = PROJECT / 'Assets/Resources/ReturnV2'
UI = RESOURCES / 'UiV2'
COLORS = {
    'ink': (232, 242, 242, 255), 'dim': (153, 178, 191, 255),
    'cyan': (99, 227, 222, 255), 'gold': (242, 186, 92, 255),
    'red': (255, 92, 71, 255), 'shade': (5, 9, 13, 209),
}
INPUTS = {}
MISSING = set()


def recorded(path):
    path = Path(path)
    INPUTS[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def read_json(path):
    return json.loads(recorded(path).read_text())


def png(path):
    return Image.open(recorded(path)).convert('RGBA')


def tint(image, color):
    pixels = np.asarray(image, dtype=np.uint16)
    return Image.fromarray(((pixels * np.array(color, dtype=np.uint16)) // 255).astype(np.uint8))


def nine_slice(canvas, skin, margins, box):
    x, y, w, h = box
    left = min(margins[0], w // 2)
    right = min(margins[2], w - left)
    top = min(margins[1], h // 2)
    bottom = min(margins[3], h - top)
    dx, dy = [x, x + left, x + w - right, x + w], [y, y + top, y + h - bottom, y + h]
    sx, sy = [0, left, skin.width - right, skin.width], [0, top, skin.height - bottom, skin.height]
    for row in range(3):
        for col in range(3):
            dw, dh = dx[col + 1] - dx[col], dy[row + 1] - dy[row]
            if dw <= 0 or dh <= 0:
                continue
            patch = skin.crop((sx[col], sy[row], sx[col + 1], sy[row + 1]))
            if (row == 1) != (col == 1):
                # Exactly matches native tile/crop edge sampling in UiFrame.
                for ty in range(0, dh, patch.height):
                    for tx in range(0, dw, patch.width):
                        crop = patch.crop((0, 0, min(patch.width, dw - tx), min(patch.height, dh - ty)))
                        canvas.alpha_composite(crop, (dx[col] + tx, dy[row] + ty))
            else:
                canvas.alpha_composite(patch.resize((dw, dh), Image.Resampling.NEAREST), (dx[col], dy[row]))


def approved_image(key):
    if key.startswith('fx-'):
        return png(RESOURCES / 'Feedback' / key[3:] / '00.png')
    if key.startswith('state-'):
        for folder in ('ReadabilityArtV2', 'ReadabilityArt', 'StateArt'):
            path = RESOURCES / folder / key[6:] / '00.png'
            if path.exists():
                return png(path)
    raise ValueError('No approved image binding: ' + key)


def text(canvas, element, atlas, font, dy=0):
    lookup = {char: i for i, char in enumerate(font['characters'])}
    x, y, size = element['x'], element['y'] + dy, element['size']
    if size < font['cell'] or size % font['cell']:
        raise ValueError('Font requires integer native-pixel scale: ' + str(size))
    for char in element['text']:
        if char == '\n':
            x, y = element['x'], y + size + 2
            continue
        if char in lookup:
            i, cell = lookup[char], font['cell']
            gx, gy = i % font['columns'] * cell, i // font['columns'] * cell
            glyph = atlas.crop((gx, gy, gx + cell, gy + cell)).resize((size, size), Image.Resampling.NEAREST)
            glyph = tint(glyph, COLORS.get(element.get('color'), COLORS['ink']))
            canvas.alpha_composite(glyph, (x, y))
        elif char != ' ':
            MISSING.add(char)
        x += size // 2 if ord(char) < 128 else size


def render(fixture, skins, atlas, font):
    background = png(REPO / fixture['background'])
    if background.size != (640, 360):
        raise ValueError('Fixture world must already be native 640x360: ' + fixture['background'])
    canvas = background.copy()
    if fixture['plan']['phase'] == 'Title':
        canvas.alpha_composite(png(RESOURCES / 'TiqueV10/Idle/00.png'), (62, 232))
    for element in fixture['plan']['elements']:
        kind = element['kind']
        box = tuple(element[k] for k in ('x', 'y', 'width', 'height'))
        if kind == 'panel':
            skin, margins = skins[element['asset'] or 'panel']
            nine_slice(canvas, skin, margins, box)
        elif kind == 'fill':
            canvas.alpha_composite(Image.new('RGBA', (box[2], box[3]), COLORS.get(element['color'], COLORS['ink'])), box[:2])
        elif kind == 'text':
            text(canvas, element, atlas, font)
        elif kind == 'image':
            sprite = approved_image(element['asset']).resize(box[2:], Image.Resampling.NEAREST)
            if element.get('color') not in ('', 'ink', None):
                sprite = tint(sprite, COLORS.get(element['color'], COLORS['ink']))
            canvas.alpha_composite(sprite, box[:2])
        elif kind == 'button':
            style = 'button-disabled' if not element['enabled'] else 'button-selected' if element['index'] == fixture['menuSelection'] else 'button'
            skin, margins = skins[style]
            nine_slice(canvas, skin, margins, box)
            label = dict(element, x=element['x'] + 12, y=element['y'] + (element['height'] - element['size']) // 2,
                         width=element['width'] - 24, color='ink' if element['enabled'] else 'dim')
            text(canvas, label, atlas, font)
        else:
            raise ValueError('Unknown production UI element: ' + kind)
    return canvas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixtures', type=Path, default=REPO / 'art/return-ui-v2/QA/model-regression/CompactUi/draw-plan-fixtures.json')
    parser.add_argument('--output', type=Path, default=REPO / 'art/return-ui-v2/QA/layout-preview')
    args = parser.parse_args()
    fixture_path = args.fixtures.resolve()
    fixtures = read_json(fixture_path)
    font, atlas = read_json(UI / 'font.json'), png(UI / 'font.png')
    skin_metadata = read_json(UI / 'skins.json')
    skins = {s['name']: (png(UI / s['name'] / '00.png'), s['margins']) for s in skin_metadata['skins']}
    for source in ('ReworkUi.cs', 'ReworkGame.cs', 'CompactUiLayout.cs', 'AdaptiveGuidance.cs'):
        recorded(PROJECT / 'Assets/Scripts' / source)
    recorded(PROJECT / 'Tools/ModelChecks/CompactUiLayoutChecks.cs')
    args.output.mkdir(parents=True, exist_ok=True)
    previews, output_hashes = {}, {}
    for fixture in fixtures:
        preview = render(fixture, skins, atlas, font)
        previews[fixture['name']] = preview
        for suffix, rendered in [('native', preview), ('2x', preview.resize((1280, 720), Image.Resampling.NEAREST))]:
            path = args.output / (fixture['name'] + '-' + suffix + '.png')
            rendered.save(path)
            output_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    if MISSING:
        raise ValueError('Missing licensed glyphs: ' + ''.join(sorted(MISSING)))
    chosen = ['01-title', '05-puzzle-auto-help', '09-combat-core', '12-pause']
    overview = Image.new('RGB', (1280, 792), '#0b131b')
    draw = ImageDraw.Draw(overview)
    label_font = ImageFont.load_default(size=16)
    for i, name in enumerate(chosen):
        x, y = i % 2 * 640, i // 2 * 396
        draw.text((x + 12, y + 8), name + ' / OFFLINE FIXTURE', fill='#d4e2e8', font=label_font)
        overview.paste(previews[name].convert('RGB'), (x, y + 36))
    overview.save(args.output / 'overview.png')
    report = {
        'scope': 'Offline composition of exact production draw-plan over earlier world-camera samples; NOT live gameplay, not a Unity GUI capture or playtest',
        'fixtures': len(fixtures), 'missingGlyphs': [], 'nativeCanvas': [640, 360], 'displayScale': 2,
        'renderer': 'Native fixed corners, tiled/cropped edge strips, Point center; prewrapped glyphs and exact integer advances; original sprite colors',
        'limitations': ['World images are historical fixture samples, not synchronized to the fixture model.',
                        'Unity color space, GPU sampling and live input require a separate runtime check.'],
        'humanAppearanceApproval': 'pending', 'inputSha256': INPUTS, 'outputSha256': output_hashes,
    }
    (args.output / 'review-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'fixtures': len(fixtures), 'missingGlyphs': 0, 'overview': str(args.output / 'overview.png'), 'scope': report['scope']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
