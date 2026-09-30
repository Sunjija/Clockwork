"""Review actual Unity screenshots, without fabricating or redrawing artwork.

Uses the fixture's recorded model positions and times. Crops magnify actual
Unity GPU captures, never source sprites. The report declares whether these are
full-window screenshots or the world-camera RenderTexture without IMGUI.
"""
from pathlib import Path
import argparse
import html
import json
import math
from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    folder = args.folder.resolve()
    result = json.loads((folder / 'result.json').read_text(encoding='utf-8-sig'))
    assert result['passed'], 'Fixture did not pass'
    source_scope = result.get('scope', 'Actual Unity render captures')
    groups = {}
    for row in result['observations']:
        groups.setdefault(row['scenario'], []).append(row)
    out = folder / 'Preview'
    out.mkdir(exist_ok=True)
    links = []
    for scenario, rows in groups.items():
        cells, durations = [], []
        for index, row in enumerate(rows):
            name = row.get('file') or f"{scenario}-{row['clip']}-{row['frame']:02d}"
            screenshot = Image.open(folder / (name + '.png')).convert('RGB')
            w, h = screenshot.size
            scale = max(1, min(w // 640, h // 360))
            ox, oy = (w - 640 * scale) // 2, (h - 360 * scale) // 2
            # Include surrounding floor, effects and both hands to check contact.
            cx, cy = math.floor(row['x']), math.floor(row['y'])
            box = (ox + (cx - 48) * scale, oy + (cy - 72) * scale,
                   ox + (cx + 48) * scale, oy + (cy + 16) * scale)
            crop = screenshot.crop(box).resize((288, 264), Image.Resampling.NEAREST)
            cells.append(crop)
            end = rows[index + 1]['time'] if index + 1 < len(rows) else 1.2
            durations.append(max(10, round(1000 * (end - row['time']))))
        columns = min(6, len(cells))
        contact = Image.new('RGB', (columns * 288, math.ceil(len(cells) / columns) * 304), '#12212c')
        draw = ImageDraw.Draw(contact)
        for i, (cell, row) in enumerate(zip(cells, rows)):
            x, y = (i % columns) * 288, (i // columns) * 304
            contact.paste(cell, (x, y + 40))
            draw.text((x + 5, y + 4), f"{row['clip']} {row['frame']:02d}  {row['time']:.3f}s", fill='white')
            draw.text((x + 5, y + 19), f"x={row['x']:.1f} y={row['y']:.1f} vy={row['velocity']:.1f}", fill='#63d9e8')
        contact.save(out / (scenario + '-contact.png'))
        # GIF is a review aid; the full PNG files remain authoritative.
        cells[0].save(out / (scenario + '.gif'), save_all=True, append_images=cells[1:],
                      duration=durations, loop=0, disposal=2)
        links.append(f'<article><h2>{html.escape(scenario)}</h2><img src="{scenario}.gif" alt="Actual Unity captures"><p>{len(rows)} captured transitions</p><a href="{scenario}-contact.png">Contact sheet with model times</a></article>')
    page = '<!doctype html><meta charset="utf-8"><title>Tique actual render review</title><style>body{background:#101c25;color:#e8ecdf;font:16px system-ui;margin:28px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px}article{background:#192d39;padding:16px}img{width:288px;image-rendering:pixelated}a{color:#63d9e8}</style><h1>Tique — actual Unity render sequences</h1><p>Scripted production inputs. Position-following crops from complete game screenshots; recorded model-time durations. This does not verify physical keyboard input.</p><main>' + ''.join(links) + '</main>'
    page = page.replace('Position-following crops from complete game screenshots; recorded model-time durations.', 'Position-following crops from actual Unity GPU captures; recorded model-time durations.')
    page = page.replace('<main>', '<p>' + html.escape(source_scope) + '</p><main>')
    (out / 'index.html').write_text(page, encoding='utf-8')
    print(json.dumps({'passed': True, 'scenarios': len(groups), 'screenshots': len(result['observations']), 'preview': str(out / 'index.html')}))


if __name__ == '__main__':
    main()
