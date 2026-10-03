#!/usr/bin/env python3
"""Compare captured production GUI glyph masks with the licensed native atlas.

Reads game-internal full-frame captures, never desktop screenshots. This is
pixel/geometry verification, not a human appearance or input approval.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
UI = REPO / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/UiV2'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--captures', type=Path, required=True)
    parser.add_argument('--fixtures', type=Path, required=True)
    args = parser.parse_args()
    font = json.loads((UI / 'font.json').read_text())
    atlas = Image.open(UI / 'font.png').convert('RGBA')
    lookup = {c: i for i, c in enumerate(font['characters'])}
    fixtures = {f['name']: f for f in json.loads(args.fixtures.read_text())}
    mapping = {'01-title.png': '01-title', '02-title-large.png': '17-title-enlarged',
               '03-puzzle-1.png': '02-puzzle-1', '04-puzzle-2.png': '03-puzzle-2',
               '05-puzzle-3.png': '04-puzzle-3'}
    observations = []
    for captured, planned in mapping.items():
        path = args.captures / captured
        frame = Image.open(path).convert('RGB')
        scale = min(frame.width // 640, frame.height // 360)
        assert scale >= 1
        ox, oy = (frame.width - 640 * scale) // 2, (frame.height - 360 * scale) // 2
        checked = 0
        for element in fixtures[planned]['plan']['elements']:
            if element['kind'] not in ('text', 'button'):
                continue
            size = element['size']
            assert size % 16 == 0
            x, y = element['x'], element['y']
            if element['kind'] == 'button':
                x += 12
                y += (element['height'] - size) // 2
            origin = x
            for char in element['text']:
                if char == '\n':
                    x, y = origin, y + size + 2
                    continue
                advance = size // 2 if ord(char) < 128 else size
                i = lookup[char]
                gx, gy = i % font['columns'] * 16, i // font['columns'] * 16
                mask = atlas.getchannel('A').crop((gx, gy, gx + 16, gy + 16))
                mask = mask.resize((size * scale, size * scale), Image.Resampling.NEAREST)
                # ASCII advances use half a cell: the next glyph may overlap
                # the transparent half, so compare only its actual advance.
                expected = np.asarray(mask)[:, :advance * scale] > 0
                pixels = np.asarray(frame.crop((ox + x * scale, oy + y * scale,
                    ox + (x + advance) * scale, oy + (y + size) * scale))).astype(int)
                if not expected.any():
                    x += advance
                    continue
                # Compare geometry rather than color management: the player's
                # GUI tint is transformed by its render color space. Infer the
                # flat stroke color, then require the WHOLE mask to match (both
                # missing strokes and filled counters fail this comparison).
                color = Counter(map(tuple, pixels[expected])).most_common(1)[0][0]
                actual = np.max(np.abs(pixels - np.array(color)), axis=2) <= 1
                assert np.array_equal(actual, expected), (
                    captured + '/' + element['id'] + '/' + char + ': native glyph mask differs')
                checked += 1
                x += advance
        observations.append({'file': captured, 'glyphsCompared': checked, 'integerScale': scale,
                             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    result = {'passed': True, 'scope': 'Exact binary glyph-mask comparison in actual production GUI captures; not human appearance/input approval',
              'nativeCell': 16, 'allowedTextSizes': [16, 32], 'observations': observations,
              'glyphsCompared': sum(r['glyphsCompared'] for r in observations)}
    output = args.captures / 'font-pixel-verification.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
