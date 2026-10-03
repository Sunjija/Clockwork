"""Independently replay the native mapping and offline clip composition."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import io
import json
import numpy as np

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / 'art/return-ending-elevator-v3'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def save(path, data):
    require(path.resolve().is_relative_to(ROOT.resolve()), 'QA output escaped candidate')
    if path.exists():
        require(path.read_bytes() == data, 'Preserving different QA output: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    provenance = json.loads((ROOT / 'Source/provenance.json').read_text())
    derivation = json.loads((ROOT / 'Source/Derivation/native-derivation.json').read_text())
    palette = np.array(json.loads((ROOT / 'Source/Native/palette.json').read_text())['colors'], np.uint8)
    for name, record in provenance['selectedSources'].items():
        require(sha(Path(record['sourcePath']).read_bytes()) == record['sourceSha256'], name + ': generated original changed')
        require(sha((ROOT / record['projectCopy']).read_bytes()) == record['sourceSha256'], name + ': source copy changed')
        for reference in record['references']:
            require(sha(Path(reference['sourcePath']).read_bytes()) == reference['sourceSha256'], name + ': original reference changed')
            require(sha((ROOT / reference['projectCopy']).read_bytes()) == reference['sourceSha256'], name + ': reference archive changed')
        asset = derivation['assets'][name]
        mapping = json.loads((ROOT / asset['pixelMap']).read_text())
        indexes = np.array(mapping['paletteIndices'])
        rgba = np.zeros((*indexes.shape, 4), np.uint8)
        mask = indexes >= 0
        rgba[mask, :3] = palette[indexes[mask]]
        rgba[mask, 3] = 255
        logical = Image.fromarray(rgba, 'RGBA')
        require(logical.tobytes() == Image.open(ROOT / asset['logicalOutput']).convert('RGBA').tobytes(), name + ': logical palette map mismatch')
        replay = logical.resize(tuple(mapping['nativeSize']), Image.Resampling.NEAREST)
        require(replay.tobytes() == Image.open(ROOT / asset['output']).convert('RGBA').tobytes(), name + ': native2x replay mismatch')
        require(mapping['cleanupEdits'] == [] and not mapping['silhouettePainted'], name + ': must not contain arbitrary painted redesign')
        require(sha((ROOT / asset['output']).read_bytes()) == asset['outputSha256'], name + ': native file hash mismatch')
    sources = json.loads((ROOT / 'Source/reused-assets.json').read_text())
    for key, record in sources['sources'].items():
        require(Path(record['sourcePath']).read_bytes() == (ROOT / record['projectCopy']).read_bytes(), key + ': reuse must stay byte exact')
        require(sha(Path(record['sourcePath']).read_bytes()) == record['sourceSha256'], key + ': reused original changed')
    font = ImageFont.truetype(str(ROOT / sources['font']['projectCopy']), 16)
    plan = json.loads((ROOT / 'Clips/clip-plan.json').read_text())
    registration = json.loads((ROOT / 'Source/registration.json').read_text())
    require(len(plan['clips']) == 2 and plan['sequences'] == [], 'Must be two independent clips')
    checks, selections = [], []
    for clip in plan['clips']:
        name = clip['name']
        composition = json.loads((ROOT / clip['sourceInfo']['composition']).read_text())
        count = 0
        wanted = [0, 550, 850] if name == 'guardian-collapse' else [0, 760, 2500, 3800, 4800, 6000]
        for row, filename, duration in zip(composition['exposures'], clip['frames'], clip['durations']):
            require(row['endMs'] - row['startMs'] == duration, name + ': merged frame timing')
            actual = Image.open(ROOT / 'Clips' / name / filename).convert('RGBA')
            require(sha(actual.tobytes()) == row['rgbaSha256'], name + ': RGBA hash')
            for exposure in row['subExposures']:
                if 'backgroundKey' in exposure:
                    background = ROOT / sources['sources'][exposure['backgroundKey']]['projectCopy']
                else:
                    background = ROOT / exposure['background']
                replay = Image.open(background).convert('RGBA')
                if 'carriage' in exposure:
                    car = exposure['carriage']
                    replay.alpha_composite(Image.open(ROOT / car['source']).convert('RGBA'), tuple(car['xy']))
                    require(car['xy'][1] + car['anchor'][1] == car['floorY'], 'Car floor registration')
                    if 760 <= exposure['startMs'] < 4200:
                        require(exposure['actors'][0]['foot'] == [registration['carCenterX'], car['floorY']], 'Rider must remain rigidly attached')
                for actor in exposure['actors']:
                    require(actor['scale'] == 1 and not actor['flipped'] and not actor['rotated'], 'Unchanged actor shape')
                    require([actor['xy'][i] + actor['anchor'][i] for i in (0, 1)] == actor['foot'], 'Actor anchor mismatch')
                    sprite = Image.open(ROOT / sources['sources'][actor['sourceKey']]['projectCopy']).convert('RGBA')
                    replay.alpha_composite(sprite, tuple(actor['xy']))
                if exposure.get('captionVisible'):
                    caption = exposure['caption']
                    mask = Image.new('1', (640, 360))
                    draw = ImageDraw.Draw(mask)
                    draw.fontmode = '1'
                    x = round((640 - draw.textlength(caption['text'], font=font)) / 2)
                    draw.text((x, 326), caption['text'], font=font, fill=1)
                    require(sha(mask.tobytes()) == caption['maskSha256'], 'Caption raster mismatch')
                    replay.paste((217, 228, 225, 255), mask=mask)
                require(actual.tobytes() == replay.tobytes(), name + ': complete exposure composition mismatch')
                require(np.all(np.array(actual)[..., 3] == 255), name + ': transparent output')
                if name == 'guardian-collapse':
                    require(exposure['doorClosed'] and exposure['backgroundKey'] == 'arena-closed', 'Collapse must not open exit')
                count += 1
            for time in wanted:
                if row['startMs'] <= time < row['endMs']:
                    selections.append((actual, name + ' ' + str(time) + 'ms'))
        expected = 3000 if name == 'guardian-collapse' else 7000
        require(sum(clip['durations']) == composition['durationMs'] == expected, name + ': duration')
        checks.append({'name': name, 'durationMs': expected, 'frameCount': len(clip['frames']),
                       'subExposuresReplayed': count, 'allCompositionRgbaExact': True})
    contact = Image.new('RGB', (1920, 3 * 390), (12, 18, 28))
    draw = ImageDraw.Draw(contact)
    for index, (picture, label) in enumerate(selections):
        x, y = (index % 3) * 640, (index // 3) * 390
        draw.fontmode = '1'
        draw.text((x + 12, y + 4), label + ' | PREVIEW', font=font, fill=(217, 228, 225))
        contact.paste(picture.convert('RGB'), (x, y + 24))
    buffer = io.BytesIO()
    contact.save(buffer, format='PNG')
    save(ROOT / 'QA/two-ending-contact.png', buffer.getvalue())
    validation = {'passed': True, 'clips': checks, 'generatedOriginalsAndReferencesUnchanged': True,
                  'reusedPngBytesUnchanged': True, 'nativePaletteMapRgbaExact': True,
                  'nativeInteger2xRgbaExact': True, 'wholeCompositionRgbaExact': True,
                  'closedArenaCollapse': True, 'rigidRiderAttachment': True,
                  'humanAppearanceApproval': 'pending', 'humanMotionApproval': 'pending',
                  'runtimeIntegrationTested': False, 'scope': 'Offline source mapping/composition technical check only',
                  'validatorSha256': sha(Path(__file__).read_bytes())}
    save(ROOT / 'QA/composition-validation.json', (json.dumps(validation, ensure_ascii=False, indent=2) + '\n').encode())
    print(json.dumps(validation))


if __name__ == '__main__':
    main()
