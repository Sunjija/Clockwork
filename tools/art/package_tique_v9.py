"""Package reviewed full-pose traces into Unity without touching old assets."""
from pathlib import Path
import base64, hashlib, io, json, re, shutil, uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'art/return-v9-traced'
PROJECT = ROOT / 'unity/TiqueReturnPrototype'
OUT = PROJECT / 'Assets/Resources/ReturnV2/TiqueV9'
OLD = PROJECT / 'Assets/Resources/Return/Tique'
BASE = Image.open(OLD / 'Idle/00.png').convert('RGBA')
TIMES = {c['name']: c['durations'] for c in json.loads((OLD.parent / 'clips.json').read_text())['clips']}
TIMES.update({'Idle': [125] * 8, 'hurt-pose': [40, 50, 60]})
for direction in ('side', 'up', 'down'):
    TIMES['push-' + direction] = TIMES['Walk']
    TIMES['push-brace-' + direction] = [1000]
TIMES['dash-ghost'] = TIMES['Dash']
TEMPLATE = (OLD / 'Idle/00.png.meta').read_text()


def meta(path, kind):
    ident = uuid.uuid5(uuid.NAMESPACE_URL, 'clockwork-tique-v9/' + path.relative_to(ROOT).as_posix()).hex
    if kind == 'texture':
        text = re.sub(r'(?m)^guid:.*$', 'guid: ' + ident, TEMPLATE, count=1)
    else:
        text = 'fileFormatVersion: 2\nguid: ' + ident + '\n'
        if kind == 'folder': text += 'folderAsset: yes\n'
        text += ('TextScriptImporter' if kind == 'text' else 'DefaultImporter') + ':\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    target = path.with_name(path.name + '.meta')
    if not target.exists(): target.write_text(text)


def main():
    OUT.mkdir(parents=True, exist_ok=True); meta(OUT, 'folder')
    clips, frames = [], []
    for name, times in TIMES.items():
        source = OLD / name if name == 'Walk' else ART / name
        dest = OUT / name; dest.mkdir(exist_ok=True); meta(dest, 'folder')
        sheet = Image.new('RGBA', (64 * len(times), 64))
        images = []
        for index, duration in enumerate(times):
            path = source / f'{index:02d}.png'
            image = Image.open(path).convert('RGBA')
            assert image.size == (64, 64), path
            target = dest / path.name; shutil.copyfile(path, target); meta(target, 'texture')
            sheet.alpha_composite(image, (64 * index, 0)); images.append(image)
            frames.append({'clip': name, 'index': index, 'source': path.relative_to(ROOT).as_posix(),
                           'runtime': target.relative_to(ROOT).as_posix(),
                           'sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'duration': duration})
        # Editable exports contain exactly the real reviewed native frames.
        editable = ART / 'Editable' / name; editable.mkdir(parents=True, exist_ok=True)
        sheet.save(editable / 'sheet.png')
        if len(images) > 1:
            images[0].save(editable / 'native.apng', save_all=True, append_images=images[1:],
                           duration=times, loop=0, disposal=1, blend=0)
            decoded = Image.open(editable / 'native.apng'); assert decoded.n_frames == len(images)
            for i, image in enumerate(images):
                decoded.seek(i); assert decoded.convert('RGBA').tobytes() == image.tobytes()
                assert round(decoded.info['duration']) == times[i]
        buf = io.BytesIO(); sheet.save(buf, format='PNG')
        layer = {'name': name, 'opacity': 1, 'frameCount': len(images), 'chunks': [
            {'layout': [[i] for i in range(len(images))], 'base64PNG': 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()}]}
        (editable / (name + '.piskel')).write_text(json.dumps({'modelVersion': 2, 'piskel': {
            'name': name, 'description': 'Full-pose traces. Variable times in clips.json and APNG.',
            'fps': 20, 'width': 64, 'height': 64, 'layers': [json.dumps(layer)]}}))
        clips.append({'name': name, 'durations': times})
    manifest = OUT / 'clips.json'; manifest.write_text(json.dumps({'clips': clips}, indent=2)); meta(manifest, 'text')
    (ART / 'runtime-package.json').write_text(json.dumps({'revision': 'V9',
        'method': 'independent complete-character single pose images, native whole-body traces, deliberate contour/exposure edits',
        'sourcePolicy': 'No generated animation sheet/video; original neutral and approved Walk retained',
        'canvas': [64, 64], 'footPivot': [32, 56], 'frames': frames,
        'validationScope': 'Packaging and APNG roundtrip only; visual/runtime review recorded separately'}, indent=2))
    print(json.dumps({'clips': len(clips), 'nativeFrames': len(frames), 'runtime': str(OUT)}))


if __name__ == '__main__': main()
