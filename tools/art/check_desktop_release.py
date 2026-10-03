#!/usr/bin/env python3
"""Verify a copied-project macOS release and desktop shortcut without UI control."""
import argparse
import hashlib
import json
import plistlib
from pathlib import Path
import re
import subprocess

REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / 'unity/TiqueReturnPrototype'
QA = REPO / 'art/return-ui-v2/QA/desktop-release'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged-project', type=Path, required=True)
    parser.add_argument('--shortcut', type=Path, required=True)
    parser.add_argument('--app', type=Path, required=True)
    parser.add_argument('--qa', type=Path, default=QA)
    parser.add_argument('--ui-review', type=Path)
    args = parser.parse_args()
    qa = args.qa.resolve()
    assert args.shortcut.is_symlink() and args.shortcut.resolve() == args.app.resolve()
    info = plistlib.loads((args.app / 'Contents/Info.plist').read_bytes())
    executable = args.app / 'Contents/MacOS' / info['CFBundleExecutable']
    assert executable.is_file() and executable.stat().st_mode & 0o111
    signing = subprocess.run(['/usr/bin/codesign', '--verify', '--deep', '--strict', str(args.app)],
                             capture_output=True, text=True, check=True)
    assets = {}
    for original in sorted((PROJECT / 'Assets').rglob('*')):
        if original.suffix not in {'.cs', '.png', '.json', '.unity', '.wav'}:
            continue
        relative = original.relative_to(PROJECT)
        staged = args.staged_project / relative
        assert staged.is_file() and sha(original) == sha(staged), 'Build input differs: ' + str(relative)
        assets[str(relative)] = sha(original)
    frozen = json.loads((REPO / 'art/return-ui-v2/Source/feedback-baseline.json').read_text())['files']
    assert all(sha(REPO / path) == digest for path, digest in frozen.items()), 'Original Feedback baseline changed'
    build = (qa / 'unity-build.log').read_text()
    assert 'RETURN_V2_BUILD Succeeded' in build
    assert not re.search(r'error CS\d+|BuildFailedException', build)
    log = (qa / 'runtime-smoke.log').read_text()
    glyph_count = len(json.loads((PROJECT / 'Assets/Resources/ReturnV2/UiV2/font.json').read_text())['characters'])
    expected = ['TIQUE_ART_ROOT ReturnV2/TiqueV10/', 'WARDEN_ART_ROOT ReturnV2/WardenV8/',
                'PUZZLE_ART_ROOT ReturnV2/ReadabilityArtV2/', f'COMPACT_UI_ROOT ReturnV2/UiV2/ glyphs={glyph_count} skins=5']
    assert all(message in log for message in expected), 'Runtime art/version not loaded'
    assert not re.search(r'Exception|Missing compact UI|Missing UI reuse', log), 'Runtime exception'
    result = json.loads((qa / 'runtime-smoke/result.json').read_text())
    assert result['passed'] and result['phase'] == 'Ending' and 'RETURN_V2_SMOKE PASS' in log
    record = {
        'passed': True, 'scope': 'Actual macOS build, signature, resource loading and input-only GPU offscreen smoke; not human GUI/input approval',
        'app': str(args.app.resolve()), 'desktopShortcut': str(args.shortcut), 'shortcutType': 'Symbolic link to actual .app; normal Finder launch with no QA args',
        'executable': info['CFBundleExecutable'], 'executableSha256': sha(executable),
        'buildLogSha256': sha(qa / 'unity-build.log'), 'runtimeLogSha256': sha(qa / 'runtime-smoke.log'),
        'signatureVerified': signing.returncode == 0, 'latestResourcesLoaded': expected, 'smoke': result,
        'inputAssetCount': len(assets), 'inputAssetSha256': assets,
        'originalFeedbackFilesPreserved': len(frozen), 'buildUsedIsolatedCopy': True,
        'normalGameWindowLaunched': False, 'liveMouseKeyboardGuiTested': False,
        'note': 'Offscreen captures contain world-camera GPU render only, not the OnGUI HUD.',
    }
    if args.ui_review:
        ui = json.loads((args.ui_review / 'result.json').read_text())
        assert ui['passed'] and len(ui['observations']) == 15
        for row in ui['observations']:
            assert (args.ui_review / row['file']).is_file()
            assert row['integerScale'] >= 1
            assert all(size.startswith(('16px:base-atlas:', '32px:base-atlas:')) for size in row['textSizes'])
        record['fullGameFrameGuiCapture'] = ui
        record['note'] = '15 actual full game-frame GUI fixtures captured; not physical input testing or human appearance approval. Falling opening unchanged.'
        previous = json.loads((QA / 'release-verification.json').read_text())['inputAssetSha256']
        preserved = ['ReturnFeedback.cs', 'CorePuzzle.cs', 'ReworkModel.cs', 'ReworkChecks.cs',
                     'ReworkPilot.cs', 'TiqueAnimation.cs', 'WardenAnimation.cs']
        for filename in preserved:
            key = 'Assets/Scripts/' + filename
            assert assets[key] == previous[key], 'Gameplay/opening source unexpectedly changed: ' + filename
        record['gameplayAndFallingOpeningSourcePreserved'] = preserved
    (qa / 'release-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ('passed', 'desktopShortcut', 'inputAssetCount', 'signatureVerified', 'originalFeedbackFilesPreserved', 'smoke')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
