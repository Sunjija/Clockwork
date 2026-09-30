"""Author V10 jump frames from actual sprite-gen whole-pose extractions.

The generated source and canonical extract are immutable inputs. Corrections are
native, explicitly enumerated pixel edits, with whole-image integer registration.
No body/head rectangle overwrite, part resize, blur, or interpolated alpha is used.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v10-spritegen'
RUN = ART / 'jump'
ORIGINAL = ROOT / 'unity/TiqueReturnPrototype/Assets/Resources/Return/Tique/Idle/00.png'
KEYS = ('preload', 'takeoff', 'early-rise', 'rise', 'apex', 'fall', 'land', 'boost')
original = Image.open(ORIGINAL).convert('RGBA')
PALETTE = [p for p, count in Counter(p[:3] for p in original.get_flattened_data() if p[3]).most_common()]
COLORS = [(*p, 255) for p in PALETTE]
TRANSPARENT = (0, 0, 0, 0)

# Native landmarks measured on the complete decoded source, before registration.
# Each source forearm remains in place; only the compact terminal hand is cleaned.
HANDS = {
    'preload': ((18, 43), (44, 44)),
    'takeoff': ((27, 40), (45, 40)),
    'early-rise': ((23, 41), (44, 41)),
    'rise': ((19, 42), (45, 42)),
    'apex': ((18, 41), (45, 41)),
    'fall': ((19, 39), (45, 39)),
    'land': ((19, 46), (45, 46)),
    'boost': ((17, 40), (46, 42)),
}
REGISTER = {
    'preload': (0, 0), 'takeoff': (0, 0), 'rise': (-1, 2),
    'early-rise': (0, -1),
    'apex': (0, -1), 'fall': (0, 1), 'land': (0, 0), 'boost': (0, 0),
}

# Hand spur pixels outside the shared 5x5 circle, measured in native source space.
# Keep the immediate wrist/forearm; these remove old thumb-like/bulky cap residue.
SPURS = {
    'preload': [(17, 44), (18, 45), (19, 45), (20, 45), (21, 45), (22, 45)],
    'takeoff': [],
    'early-rise': [(22, 44), (23, 44), (24, 44), (25, 44), (43, 44), (44, 44)],
    'rise': [(18, 45), (19, 45), (46, 44), (47, 44)],
    'apex': [(18, 44), (19, 44), (45, 44), (46, 44)],
    'fall': [(18, 42), (19, 42), (20, 42), (45, 42), (46, 42)],
    'land': [(18, 49), (19, 49), (20, 49), (45, 49), (46, 49)],
    'boost': [],
}

# Small isolated cyan quantization residue on bronze limb pixels, not core/eyes.
PIXELS = {
    'preload': {(29, 52): 0},
    'takeoff': {},
    'early-rise': {},
    'rise': {(25, 46): 0},
    'apex': {},
    'fall': {},
    'land': {},
    'boost': {},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assign(im: Image.Image, xy: tuple[int, int], code: int | None) -> None:
    im.putpixel(xy, TRANSPARENT if code is None else COLORS[code])


def translate(im: Image.Image, delta: tuple[int, int]) -> Image.Image:
    out = Image.new('RGBA', (64, 64))
    out.paste(im, delta)
    return out


def semantic_glow_cleanup(im: Image.Image, dy: int) -> list[dict]:
    """Correct only eye/heart glow pixels, never the enclosing face or chest.

    Source poses reproduce these tiny fixed-design clusters with occasional
    1px quantization errors. The original explicitly defines their identity.
    Bronze, shade and outline elsewhere in the full traced pose remain intact.
    """
    changes = []
    glow = set(PALETTE[7:12])
    for name, region in [('eye-glow', (27, 18, 47, 27)), ('heart-glow', (30, 37, 43, 48))]:
        x0, y0, x1, y1 = region
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                target = original.getpixel((xx, yy))
                xy = (xx, yy + dy)
                old = im.getpixel(xy)
                # Restore original cyan geometry/color only where either current
                # or target belongs to the semantic glow. No rectangle pasting.
                if (target[:3] in glow or old[:3] in glow) and old != target:
                    im.putpixel(xy, target)
                    changes.append({'xy': list(xy), 'from': list(old), 'to': list(target), 'cluster': name})
    return changes


def corrected_key(key: str) -> tuple[Image.Image, dict]:
    source_path = RUN / 'frames' / key / 'frame-0.png'
    decoded = Image.open(source_path).convert('RGBA')
    edited = decoded.copy()
    template = json.loads((ART / 'round-hand.json').read_text(encoding='utf-8'))['rows']
    for center in HANDS[key]:
        x0, y0 = center[0] - 2, center[1] - 2
        for yy, row in enumerate(template):
            for xx, code in enumerate(row):
                assign(edited, (x0 + xx, y0 + yy), None if code == '.' else int(code))
    for xy in SPURS[key]:
        # Exclude pixels within the newly authored caps.
        if not any(abs(xy[0]-c[0]) <= 2 and abs(xy[1]-c[1]) <= 2 for c in HANDS[key]):
            assign(edited, xy, None)
    for xy, code in PIXELS[key].items():
        assign(edited, xy, code)
    changes = []
    for y in range(64):
        for x in range(64):
            a, b = decoded.getpixel((x, y)), edited.getpixel((x, y))
            if a != b:
                changes.append({'xy': [x, y], 'from': list(a), 'to': list(b)})
    aligned = translate(edited, REGISTER[key])
    glow_changes = semantic_glow_cleanup(aligned, 2 if key == 'land' else 0)
    note = {
        'key': key, 'raw': f'raw/{key}.png',
        'canonicalExtract': str(source_path.relative_to(RUN)).replace('\\', '/'),
        'canonicalExtractSha256': sha(source_path),
        'method': 'actual complete sprite-gen pixel-unfake extraction, followed by enumerated native terminal-hand/isolated-color cleanup and whole-image integer registration',
        'wholeRegistration': list(REGISTER[key]),
        'sourceHandCenters': [list(p) for p in HANDS[key]],
        'changedNativePixels': len(changes), 'pixelDelta': changes,
        'semanticGlowPixelDelta': glow_changes,
        'sourceBBox': list(decoded.getbbox()), 'authoredBBox': list(aligned.getbbox()),
        'noPartRescale': True, 'noHeadOrChestRectangleReplacement': True,
        'visualReview': 'Actual whole source and decoded/authored contact visually reviewed; both round hands and both shoes remain visible. Offline candidate, actual runtime/user motion review pending.',
    }
    return aligned, note


def variant(im: Image.Image, edits: dict[tuple[int, int], int | None]) -> Image.Image:
    out = im.copy()
    for xy, code in edits.items():
        assign(out, xy, code)
    return out


def delta(a: Image.Image, b: Image.Image) -> list[dict]:
    return [{'xy': [x, y], 'from': list(a.getpixel((x,y))), 'to': list(b.getpixel((x,y)))}
            for y in range(64) for x in range(64) if a.getpixel((x,y)) != b.getpixel((x,y))]


def author_intermediates(keys: dict[str, Image.Image]) -> tuple[dict[str, Image.Image], list[dict]]:
    """Explicit whole-native drawings bridge the source poses, no part rig."""
    authored, notes = {}, []
    specs = [
        ('preload-soft', 'preload', {
            (25,50): 1, (26,50): 2, (27,50): 2, (28,50): 5,
            (36,50): 5, (37,50): 1, (38,50): 1,
        }, 'A few knee/boot shading pixels soften preparation; complete source silhouette retained.'),
        ('apex-unfold', 'apex', {
            (29,52): 5, (29,53): 0, (37,52): 5, (37,53): 0,
            (27,54): 0, (28,54): 0, (36,54): 0, (37,54): 0,
        }, 'Full native intermediate opens the two compact knee/heel contours by one pixel.'),
        ('fall-early', 'fall', {
            (25,54): 0, (26,54): 0, (27,54): 0,
            (36,54): 0, (37,54): 0, (38,54): 0,
            (27,56): None, (28,56): None, (35,56): None, (36,56): None,
        }, 'Native toe/sole cleanup keeps the feet compact as the knees unfold into descent.'),
        ('boost-release', 'boost', {
            (28,51): 1, (29,51): 2, (30,51): 5,
            (36,51): 4, (37,51): 1, (38,51): 2,
            (31,54): 0, (32,54): 0, (37,55): 0,
        }, 'Native bent-knee/shoe edge pixels open the actual boost pose for release.'),
        ('apex-approach', 'rise', {
            (27,52): 0, (28,52): 0, (29,52): 0,
            (33,55): 5, (34,55): 1, (35,55): 0,
            (32,57): None, (33,57): None,
        }, 'Native ankle/toe pixels reduce the trailing toe while approaching the apex.'),
    ]
    for name, source, edits, reason in specs:
        out = variant(keys[source], edits)
        authored[name] = out
        notes.append({'name': name, 'wholePoseSource': source, 'method': 'explicit native pixel contour drawing; no moved/resized limb pieces', 'reason': reason, 'pixelDelta': delta(keys[source],out)})
    # One whole image rises by one pixel during ground recovery. Extend the same
    # full-pose sole contours to the baseline, rather than bottom-pin a body part.
    recovery = translate(keys['land'], (0,-1))
    for x in (25,26,27,28,35,36,37,38,39,40):
        assign(recovery,(x,55),0)
    authored['recovery'] = recovery
    notes.append({'name': 'recovery', 'wholePoseSource': 'land', 'method': 'whole-image integer shift [0,-1] then native sole contour drawing', 'reason': 'Knees release one pixel; solid head/chest rise together and soles remain56.', 'pixelDelta': delta(keys['land'],recovery)})
    return authored, notes


def export_clips(keys: dict[str, Image.Image], intermediates: dict[str, Image.Image]) -> dict:
    pool = dict(keys, **intermediates, neutral=original)
    sequence = {
        'Jump': ['neutral','preload-soft','preload','takeoff','early-rise','rise','apex','apex-unfold','fall-early','fall','land','recovery','preload','neutral','neutral'],
        'DoubleJump': ['neutral','apex-unfold','boost','boost-release','rise','apex-approach','apex','fall-early','fall','land','recovery','preload','neutral'],
    }
    duration_data = json.loads((ROOT/'unity/TiqueReturnPrototype/Assets/Resources/Return/clips.json').read_text(encoding='utf-8'))
    durations = {c['name']: c['durations'] for c in duration_data['clips']}
    clips = {}
    intermediate_sources = {'preload-soft': 'preload', 'apex-unfold': 'apex', 'fall-early': 'fall', 'boost-release': 'boost', 'apex-approach': 'rise', 'recovery': 'land'}
    for clip, names in sequence.items():
        directory = ART/clip
        directory.mkdir(parents=True, exist_ok=True)
        frames = []
        for index, name in enumerate(names):
            dest = directory/f'{index:02}.png'
            # Original neutral PNG bytes are preserved, including metadata.
            if name == 'neutral':
                dest.write_bytes(ORIGINAL.read_bytes())
            else:
                pool[name].save(dest)
            frames.append({'index': index, 'pose': name, 'durationMs': durations[clip][index], 'sourcePose': intermediate_sources.get(name,name), 'file': str(dest.relative_to(ART)).replace('\\','/'), 'sha256': sha(dest)})
        assert len(names) == len(durations[clip])
        clips[clip] = {'frameCount': len(names), 'durations': durations[clip], 'totalDurationMs': sum(durations[clip]), 'frames': frames, 'runtimeReview': 'pending actual Unity sequence review; offline contact is not live human play'}
        contact([(f'{clip} {i:02} {name}',pool[name]) for i,name in enumerate(names)], RUN/f'qa/{clip.lower()}-contact-5x.png',5,5)
        background = Image.new('RGBA',(64,64),'#14222e')
        gifs = []
        for name in names:
            frame = background.copy(); frame.alpha_composite(pool[name]); gifs.append(frame.convert('RGB').resize((384,384),Image.Resampling.NEAREST))
        gifs[0].save(RUN/f'qa/{clip.lower()}-clean-6x.gif',save_all=True,append_images=gifs[1:],duration=durations[clip],loop=0,optimize=False,disposal=2)
    (RUN/'timing-manifest.json').write_text(json.dumps(clips,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return clips


def check_clips(clips: dict) -> dict:
    expected_head = (16,8,47,35)
    reports = []
    for clip, data in clips.items():
        for frame in data['frames']:
            path = ART/frame['file']
            im = Image.open(path).convert('RGBA')
            pose = frame['pose']
            shift = 2 if pose == 'land' else 1 if pose == 'recovery' else 0
            head = im.crop((0,shift,64,35+shift)).getbbox()
            assert im.size == (64,64), path
            assert set(im.getchannel('A').get_flattened_data()) <= {0,255}, path
            assert all(p[:3] in PALETTE for p in im.get_flattened_data() if p[3]), path
            assert head == expected_head, (path,head)
            # Canonical cyan cluster dimensions/color stay fixed after pose registration.
            glow = set(PALETTE[7:12])
            for region in ((27,18,47,27),(30,37,43,48)):
                x0,y0,x1,y1 = region
                for y in range(y0,y1):
                    for x in range(x0,x1):
                        ref = original.getpixel((x,y))
                        cur = im.getpixel((x,y+shift))
                        if ref[:3] in glow or cur[:3] in glow:
                            assert cur == ref, (path,x,y,'semantic glow drift')
            if pose == 'neutral':
                assert path.read_bytes() == ORIGINAL.read_bytes(), path
            if pose in ('neutral','preload','preload-soft','land','recovery'):
                assert im.getbbox()[3] == 56, (path,'ground soles')
            opaque = {(x,y) for y in range(64) for x in range(64) if im.getpixel((x,y))[3]}
            pending = [opaque.pop()]
            while pending:
                x,y = pending.pop()
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        xy = (x+dx,y+dy)
                        if xy in opaque:
                            opaque.remove(xy); pending.append(xy)
            assert not opaque, (path,'detached opaque pixels')
            reports.append({'clip':clip,'index':frame['index'],'pose':pose,'rgbaSha256':hashlib.sha256(im.tobytes()).hexdigest(),'bbox':list(im.getbbox()),'headBBoxRegistered':list(head),'binaryAlpha':True,'canonicalPalette':True,'singleOpaqueComponent8Connected':True,'eyesAndCyanHeartIdentity':True,'groundSoles56':pose in ('neutral','preload','preload-soft','land','recovery'),'neutralOriginalBytes':pose=='neutral'})
    provenance = json.loads((RUN/'generation-provenance.json').read_text(encoding='utf-8'))
    rejected = [p for p in provenance if 'REJECTED' in p.get('sourceReview','')]
    result = {'status':'technical checks passed; natural motion requires actual runtime and user review','framesChecked':len(reports),'generatedSources':len(provenance),'selectedWholePoseSources':len(provenance)-len(rejected),'rejectedSourceCandidates':len(rejected),'durationMs':{k:v['totalDurationMs'] for k,v in clips.items()},'frameReports':reports}
    (RUN/'qa/native-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def contact(items: list[tuple[str, Image.Image]], path: Path, cols: int = 4, scale: int = 5) -> None:
    rows = (len(items) + cols - 1) // cols
    tile_w, tile_h = 64 * scale, 64 * scale + 26
    page = Image.new('RGB', (cols * tile_w, rows * tile_h), '#14222e')
    draw = ImageDraw.Draw(page)
    for idx, (name, im) in enumerate(items):
        x, y = (idx % cols) * tile_w, (idx // cols) * tile_h
        draw.text((x+6, y+5), name, fill='#e9eef3')
        page.paste(im.resize((64*scale, 64*scale), Image.Resampling.NEAREST), (x, y+26), im.resize((64*scale, 64*scale), Image.Resampling.NEAREST))
    path.parent.mkdir(parents=True, exist_ok=True)
    page.save(path)


def main() -> None:
    native = RUN / 'native-keys'
    native.mkdir(parents=True, exist_ok=True)
    authored, notes = {}, []
    for key in KEYS:
        im, note = corrected_key(key)
        im.save(native / f'{key}.png')
        authored[key] = im
        notes.append(note)
    (RUN / 'native-cleanup.json').write_text(json.dumps(notes, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    contact([('original', original)] + list(authored.items()), RUN / 'qa/all-authored-keys-5x.png')
    intermediate, intermediate_notes = author_intermediates(authored)
    for name, im in intermediate.items():
        im.save(native/f'{name}.png')
    (RUN/'native-intermediates.json').write_text(json.dumps(intermediate_notes,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    clips = export_clips(authored,intermediate)
    check_clips(clips)
    print(json.dumps({'authoredKeys': len(authored), 'changedPixels': {n['key']: n['changedNativePixels'] for n in notes}, 'contact': str(RUN/'qa/all-authored-keys-5x.png')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
