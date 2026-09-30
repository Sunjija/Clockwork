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
import base64, hashlib, io, json, shutil
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


STAGES = [hud_cells]

if __name__ == '__main__':
    for stage in STAGES:
        stage()
    save_index()
    print('polished', len(POLISHED), 'clips')
