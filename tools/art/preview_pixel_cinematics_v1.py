"""Read-only 4-up source-frame preview, not a runtime capture or final edit."""
from pathlib import Path
from bisect import bisect_right
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO/'art/return-pixel-cinematics-v1'


def main():
    clips = json.loads((ROOT/'Clips/clip-plan.json').read_text())['clips']
    colors = json.loads((ROOT/'Source/Native/palette.json').read_text())['colors']
    indexed_palette = Image.new('P', (1, 1))
    indexed_palette.putpalette([v for c in colors for v in c] + [0]*(768-3*len(colors)))
    packed_lookup = {(r<<16)+(g<<8)+b: i for i, (r, g, b) in enumerate(colors)}
    names = ['A2 RELAY POWER', 'A3 GUARDIAN CORE', 'B3 WORKSHOP WIDE', 'B4 SAME WORKSHOP CLOSE']
    prepared = []
    for clip in clips:
        end, total = [], 0
        for duration in clip['durations']:
            total += duration; end.append(total)
        frames = [Image.open(ROOT/'Clips'/clip['name']/f).convert('RGB') for f in clip['frames']]
        prepared.append((clip['name'], end, total, frames))
    samples, output = [], []
    for sample in range(60):
        time = sample*100
        board = Image.new('RGB', (1280, 776), tuple(colors[0]))
        draw = ImageDraw.Draw(board)
        draw.fontmode = '1'
        source_indices = {}
        for i, (name, ends, total, frames) in enumerate(prepared):
            index = bisect_right(ends, time % total)
            x, y = (i%2)*640, (i//2)*388
            draw.text((x+8, y+7), names[i]+' | OFFLINE CANDIDATE', fill=tuple(colors[28]))
            board.paste(frames[index], (x, y+24))
            source_indices[name] = index
        # Pillow's palette quantizer caches coarse RGB cells and may choose an
        # adjacent ramp color even when an exact entry exists. Direct lookup
        # guarantees byte-exact native preview pixels instead of re-quantizing.
        a = np.array(board).astype(np.uint32)
        packed = (a[..., 0]<<16)+(a[..., 1]<<8)+a[..., 2]
        unique, inverse = np.unique(packed, return_inverse=True)
        palette_indices = np.array([packed_lookup[int(c)] for c in unique], np.uint8)[inverse].reshape(packed.shape)
        encoded = Image.fromarray(palette_indices, 'P')
        encoded.putpalette(indexed_palette.getpalette())
        assert encoded.convert('RGB').tobytes() == board.tobytes(), 'Preview palette changed native source pixels'
        output.append(encoded); samples.append({'timeMs': time, 'clipSourceFrames': source_indices})
    path = ROOT/'QA/all-cuts-preview.gif'
    output[0].save(path, save_all=True, append_images=output[1:], duration=100, loop=0,
                   comment=b'4-up offline source-frame preview at10fps. Each clip loops independently. Not gameplay, video or final edit. Human appearance approval pending.')
    recovered = Image.open(path)
    times = []
    for i in range(recovered.n_frames):
        recovered.seek(i); times.append(recovered.info['duration'])
    assert sum(times) == 6000
    ends, total = [], 0
    for duration in times:
        total += duration; ends.append(total)
    for sample, original in enumerate(output):
        recovered.seek(bisect_right(ends, sample*100))
        assert recovered.convert('RGB').tobytes() == original.convert('RGB').tobytes(), 'GIF decode changed sampled source pixels'
    record = {'kind': 'offline4-up-source-frame-preview', 'runtimeCapture': False,
              'gameLaunched': False, 'humanAppearanceApproval': 'pending',
              'samplingIntervalMs': 100, 'previewLoopMs': 6000,
              'exactClipTimingAuthority': 'Clips/<name>/native.apng and Exports/clips.json',
              'allNativePreviewPixelsExact': True, 'samples': samples,
              'previewPath': path.relative_to(REPO).as_posix(),
              'previewSha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    (ROOT/'QA/preview-timing.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'preview': str(path), 'loopMs': 6000, 'nativePixelsExact': True}))


if __name__ == '__main__':
    main()
