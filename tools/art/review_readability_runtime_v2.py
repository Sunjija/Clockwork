"""Package real Unity captures; make comparisons, never stand-in game renders."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "art/return-readability-image-first-v2"
PROJECT = ROOT / "unity/TiqueReturnPrototype"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--flow", required=True, type=Path)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--previous-review", type=Path)
    args = parser.parse_args()
    qa = PACKAGE / "QA"
    dst = qa / "Runtime"
    dst.mkdir(parents=True, exist_ok=True)
    review = json.loads((args.review / "result.json").read_text())
    flow = json.loads((args.flow / "result.json").read_text())
    for result in (review, flow):
        assert result["passed"] is True, result
        assert result["artRoot"] == "ReturnV2/ReadabilityArtV2/", result
    assert review["completedRooms"] == 3 and review["counterHits"] == 1
    assert flow["phase"] == "Ending"
    captures = {}
    for path in sorted(args.review.glob("*.png")):
        with Image.open(path) as image:
            assert image.size == (640, 360), (path, image.size)
        shutil.copy2(path, dst / path.name)
        captures[path.name] = sha(path)
    shutil.copy2(args.review / "result.json", dst / "result.json")
    shutil.copy2(args.flow / "result.json", dst / "full-flow-result.json")
    shutil.copy2(args.flow / "events.txt", dst / "full-flow-events.txt")
    for name in ("push-up", "push-side", "push-down", "08-ending"):
        path = args.flow / f"{name}.png"
        if path.exists():
            shutil.copy2(path, dst / f"flow-{path.name}")
            captures[f"flow-{path.name}"] = sha(path)

    # Exact native-resolution GPU output, with a label outside each capture.
    keys = ["puzzle-1-initial", "puzzle-2-initial", "puzzle-3-connected"]
    columns = 2 if args.previous_review else 1
    sheet = Image.new("RGB", (640 * columns, 388 * len(keys)), (17, 24, 31))
    draw = ImageDraw.Draw(sheet)
    for row, name in enumerate(keys):
        sources = [(args.review, "v2 generated-source native pixels")]
        if args.previous_review:
            sources.insert(0, (args.previous_review, "v1 readability prototype (preserved)"))
        for col, (folder, label) in enumerate(sources):
            draw.text((col * 640 + 10, row * 388 + 8), f"{name} | {label}", fill="white")
            with Image.open(folder / f"{name}.png") as capture:
                sheet.paste(capture.convert("RGB"), (col * 640, row * 388 + 28))
    sheet.save(qa / "runtime-comparison.png")
    sheet.convert("L").save(qa / "runtime-comparison-grayscale.png")

    # Trace assets and unchanged approved character/guardian art separately.
    resources = PROJECT / "Assets/Resources/ReturnV2"
    approved = {}
    for name in ("TiqueV10", "WardenV7"):
        approved[name] = {
            str(p.relative_to(resources)): sha(p)
            for p in sorted((resources / name).rglob("*.png"))
        }
    record = {
        "date": "2026-10-02",
        "passed": True,
        "scope": "Actual Unity 640x360 world-camera GPU captures and production-command fixtures. IMGUI, desktop interaction, physical keys, subjective art approval and human fun testing excluded.",
        "binary": str(args.binary),
        "binarySha256": sha(args.binary),
        "review": review,
        "fullFlow": flow,
        "captureSha256": captures,
        "approvedArtSha256": approved,
        "appearanceApproval": "pending human feedback; technical success is not appearance approval",
    }
    (qa / "runtime-validation.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"PASS v2 Unity evidence: {len(captures)} byte-preserved captures; full flow {flow['playSeconds']}s")


if __name__ == "__main__":
    main()
