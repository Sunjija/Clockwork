#!/usr/bin/env python3
"""QA only: compare unchanged licensed font rasterization, no new typeface/art."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

repo = Path(__file__).resolve().parents[2]
ui = repo / 'unity/TiqueReturnPrototype/Assets/Resources/ReturnV2/UiV2'
meta = json.loads((ui / 'font.json').read_text())
atlas = Image.open(ui / 'font.png').convert('RGBA')
font_source = repo / 'art/return-v5-feedback/Source/Font/neodgm.ttf'
text = '회로 2/3 · 멈추는 곳   Z 되돌리기 · R 초기화\n막힌 부품은 Z로 되돌려, 밀 방향을 바꿔 보세요.'
board = Image.new('RGBA', (640, 380), '#1b2b34')
for row, (size, method) in enumerate([(12, 'point-16'), (12, 'native-source'), (14, 'point-16'), (14, 'native-source'), (16, 'point-16')]):
    y = row * 76
    ImageDraw.Draw(board).text((8, y), str(size) + 'px / ' + method, fill='white')
    x, gy = 12, y + 20
    for char in text:
        if char == '\n':
            x, gy = 12, gy + size + 2
            continue
        if method == 'point-16':
            index = meta['characters'].index(char)
            sx, sy = index % meta['columns'] * 16, index // meta['columns'] * 16
            glyph = atlas.crop((sx, sy, sx + 16, sy + 16)).resize((size, size), Image.Resampling.NEAREST)
        else:
            mask = Image.new('L', (size, size))
            ImageDraw.Draw(mask).text((0, 0), char, font=ImageFont.truetype(str(font_source), size), fill=255)
            glyph = Image.new('RGBA', (size, size), (255, 255, 255, 0))
            glyph.putalpha(mask.point(lambda p: 255 if p >= 128 else 0))
        board.alpha_composite(glyph, (x, gy))
        x += size // 2 if ord(char) < 128 else size
path = repo / 'art/return-ui-v2/QA/font-raster-comparison.png'
board.resize((1280, 760), Image.Resampling.NEAREST).save(path)
print(path)
