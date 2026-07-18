#!/usr/bin/env python3
"""Build fixed-scale attack frames from approved transparent imagegen strips."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
GENERATED_ROOT = (
    ROOT
    / "lento-vertical-slice"
    / "assets"
    / "tique"
    / "generated"
)
V10_ROOT = GENERATED_ROOT / "v10-weapon-sheet-runs"
V11_ROOT = GENERATED_ROOT / "v11-attack-fixes"
V13_ROOT = GENERATED_ROOT / "v13-hammer-swing"
V14_ROOT = GENERATED_ROOT / "v14-greatsword-slash"

FRAME_SIZE = (640, 512)
OUTPUT_ANCHOR = (320, 480)

# The generated strips share one scene coordinate system per action. Keeping one
# scale and ground row per strip prevents long weapons from resizing Tique.
SEQUENCES = {
    "fist": {
        "strip": V11_ROOT / "fist" / "normalized" / "fist-attack-v11.png",
        "output": V11_ROOT / "fist" / "fixed",
        "count": 8,
        "scale": 1.25,
        "ground_y": 482,
        "anchor_x": [178, 171, 187, 169, 189, 187, 171, 166],
        # The generated sixth pose turns away. Reverse the clean attack poses for
        # recoil so the face, heart core, and connected neck remain readable.
        "slots": [0, 1, 2, 3, 4, 2, 1, 7],
        "fps": 22,
    },
    "greatsword": {
        "strip": V14_ROOT / "normalized" / "greatsword-slash-v14.png",
        "output": V14_ROOT / "fixed",
        "count": 10,
        "scale": 1.45,
        "output_anchor": (240, 430),
        "ground_y": [480, 477, 478, 480, 484, 484, 484, 488],
        "anchor_x": [134, 198, 180, 158, 139, 144, 153, 98],
        # Omit the two poses where image generation dropped the blade.
        "slots": [0, 2, 3, 4, 5, 6, 7, 9],
        "manual_bounds": {
            0: (0, 180, 270, 540),
            2: (420, 150, 700, 540),
            3: (570, 120, 910, 540),
            4: (840, 200, 1140, 550),
            5: (1040, 200, 1450, 560),
            6: (1260, 200, 1650, 560),
            7: (1480, 200, 1850, 560),
            9: (1920, 200, 2172, 550),
        },
        "fps": 15,
    },
    "hammer": {
        "strip": V13_ROOT / "normalized" / "hammer-swing-v13.png",
        "output": V13_ROOT / "fixed",
        "count": 10,
        "scale": 1.45,
        "ground_y": 473,
        "anchor_x": [84, 82, 99, 79, 79, 118, 94, 84],
        # Keep the readable diagonal swing and opposite-shoulder follow-through.
        # The generated forward-push and missing-weapon poses stay excluded.
        "slots": [0, 2, 3, 4, 4, 8, 9, 0],
        "manual_bounds": {
            0: (0, 220, 217, 474),
            # These rear-shoulder poses extend into the previous visual slot.
            # Wider crops restore the complete hammer head; component filtering
            # still removes unrelated neighboring poses.
            2: (350, 220, 652, 474),
            3: (560, 220, 869, 474),
            4: (869, 220, 1086, 474),
            8: (1738, 220, 1955, 474),
            9: (1955, 220, 2172, 474),
        },
        "fps": 13,
    },
}


def slot_bounds(width: int, index: int, count: int) -> tuple[int, int]:
    return round(index * width / count), round((index + 1) * width / count)


def connected_components(image: Image.Image) -> list[dict[str, Any]]:
    alpha = image.getchannel("A")
    width, height = image.size
    data = alpha.tobytes()
    visited = bytearray(width * height)
    components = []

    for start, alpha_value in enumerate(data):
        if alpha_value <= 16 or visited[start]:
            continue
        stack = [start]
        visited[start] = 1
        pixels = []
        min_x, min_y, max_x, max_y = width, height, 0, 0
        while stack:
            current = stack.pop()
            pixels.append(current)
            x, y = current % width, current // width
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
            for neighbor in (
                current - 1 if x > 0 else -1,
                current + 1 if x + 1 < width else -1,
                current - width if y > 0 else -1,
                current + width if y + 1 < height else -1,
            ):
                if neighbor >= 0 and not visited[neighbor] and data[neighbor] > 16:
                    visited[neighbor] = 1
                    stack.append(neighbor)
        components.append(
            {
                "pixels": pixels,
                "area": len(pixels),
                "bbox": (min_x, min_y, max_x + 1, max_y + 1),
                "center_x": (min_x + max_x + 1) / 2,
            }
        )
    return components


def group_components(strip: Image.Image, frame_count: int) -> list[list[dict[str, Any]]]:
    components = connected_components(strip)
    largest_area = max(component["area"] for component in components)
    seed_threshold = max(80, largest_area * 0.20)
    seeds = [component for component in components if component["area"] >= seed_threshold]
    if len(seeds) < frame_count:
        seeds = sorted(components, key=lambda component: component["area"], reverse=True)[:frame_count]
    seeds = sorted(
        sorted(seeds, key=lambda component: component["area"], reverse=True)[:frame_count],
        key=lambda component: component["center_x"],
    )
    if len(seeds) != frame_count:
        raise ValueError(f"Expected {frame_count} pose groups, found {len(seeds)}")

    seed_ids = {id(seed) for seed in seeds}
    groups = [[seed] for seed in seeds]
    noise_threshold = max(8, largest_area * 0.002)
    for component in components:
        if id(component) in seed_ids or component["area"] < noise_threshold:
            continue
        nearest = min(range(len(seeds)), key=lambda index: abs(seeds[index]["center_x"] - component["center_x"]))
        groups[nearest].append(component)
    return groups


def render_group(strip: Image.Image, group: list[dict[str, Any]]) -> tuple[Image.Image, tuple[int, int, int, int]]:
    width, height = strip.size
    left = max(0, min(component["bbox"][0] for component in group) - 4)
    top = max(0, min(component["bbox"][1] for component in group) - 4)
    right = min(width, max(component["bbox"][2] for component in group) + 4)
    bottom = min(height, max(component["bbox"][3] for component in group) + 4)
    output = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    source_pixels = strip.load()
    output_pixels = output.load()
    for component in group:
        for pixel_index in component["pixels"]:
            x, y = pixel_index % width, pixel_index // width
            output_pixels[x - left, y - top] = source_pixels[x, y]
    return output, (left, top, right, bottom)


def remove_tiny_components(image: Image.Image, min_area: int = 12) -> Image.Image:
    output = image.copy()
    pixels = output.load()
    width = output.width
    for component in connected_components(output):
        if component["area"] >= min_area:
            continue
        for pixel_index in component["pixels"]:
            pixels[pixel_index % width, pixel_index // width] = (0, 0, 0, 0)
    return output


def keep_largest_component(image: Image.Image) -> Image.Image:
    components = connected_components(image)
    if not components:
        return image
    main = max(components, key=lambda component: component["area"])
    output = Image.new("RGBA", image.size, (0, 0, 0, 0))
    source_pixels = image.load()
    output_pixels = output.load()
    for pixel_index in main["pixels"]:
        x, y = pixel_index % image.width, pixel_index // image.width
        output_pixels[x, y] = source_pixels[x, y]
    return output


def keep_component_near(image: Image.Image, target_x: int, target_y: int) -> Image.Image:
    components = [component for component in connected_components(image) if component["area"] >= 80]
    if not components:
        return image

    def distance_to_bbox(component: dict[str, Any]) -> tuple[int, int]:
        left, top, right, bottom = component["bbox"]
        dx = max(left - target_x, 0, target_x - (right - 1))
        dy = max(top - target_y, 0, target_y - (bottom - 1))
        return dx * dx + dy * dy, -component["area"]

    main = min(components, key=distance_to_bbox)
    output = Image.new("RGBA", image.size, (0, 0, 0, 0))
    source_pixels = image.load()
    output_pixels = output.load()
    for pixel_index in main["pixels"]:
        x, y = pixel_index % image.width, pixel_index // image.width
        output_pixels[x, y] = source_pixels[x, y]
    return output


def build_frame(
    strip: Image.Image,
    groups: list[list[dict[str, Any]]] | None,
    slot: int,
    count: int,
    scale: float,
    ground_y: int,
    anchor_x: int,
    manual_bounds: dict[int, tuple[int, int, int, int]] | None = None,
    output_anchor: tuple[int, int] = OUTPUT_ANCHOR,
) -> Image.Image:
    slot_left, _ = slot_bounds(strip.width, slot, count)
    global_anchor_x = slot_left + anchor_x
    if manual_bounds and slot in manual_bounds:
        bbox = manual_bounds[slot]
        pose = keep_component_near(
            remove_tiny_components(strip.crop(bbox)),
            round(global_anchor_x - bbox[0]),
            round(ground_y - bbox[1] - 80),
        )
    else:
        if groups is None:
            raise ValueError(f"No extraction group available for slot {slot}")
        pose, bbox = render_group(strip, groups[slot])
    scaled = pose.resize(
        (round(pose.width * scale), round(pose.height * scale)),
        Image.Resampling.NEAREST,
    )

    frame = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    paste_x = round(output_anchor[0] + (bbox[0] - global_anchor_x) * scale)
    paste_y = round(output_anchor[1] + (bbox[1] - ground_y) * scale)
    frame.alpha_composite(scaled, (paste_x, paste_y))
    return frame


def make_contact_sheet(name: str, frames: list[Image.Image], output: Path) -> None:
    cell_w, cell_h = 240, 210
    sheet = Image.new("RGB", (cell_w * 5, cell_h * 2), "#111820")
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(frames):
        preview = frame.copy()
        preview.thumbnail((cell_w - 16, cell_h - 28), Image.Resampling.NEAREST)
        x = (index % 5) * cell_w + (cell_w - preview.width) // 2
        y = (index // 5) * cell_h + cell_h - preview.height - 8
        sheet.paste(preview, (x, y), preview)
        draw.text(((index % 5) * cell_w + 8, (index // 5) * cell_h + 7), f"{name} {index:02}", fill="#dce8ec")
        draw.line(((index % 5) * cell_w + 8, (index // 5 + 1) * cell_h - 8, (index % 5 + 1) * cell_w - 8, (index // 5 + 1) * cell_h - 8), fill="#4f6b72")
    sheet.save(output)


def main() -> None:
    manifest = {"frameSize": list(FRAME_SIZE), "anchor": list(OUTPUT_ANCHOR), "sequences": {}}

    for name, config in SEQUENCES.items():
        strip_path = config["strip"]
        strip = Image.open(strip_path).convert("RGBA")
        manual_bounds = config.get("manual_bounds")
        groups = None if manual_bounds else group_components(strip, config["count"])
        output_dir = config["output"]
        frame_dir = output_dir / "frames"
        qa_dir = output_dir / "qa"
        frame_dir.mkdir(parents=True, exist_ok=True)
        qa_dir.mkdir(parents=True, exist_ok=True)

        frames = []
        frame_paths = []
        for output_index, slot in enumerate(config["slots"]):
            source_ground_y = config["ground_y"]
            if isinstance(source_ground_y, list):
                source_ground_y = source_ground_y[output_index]
            frame = build_frame(
                strip,
                groups,
                slot,
                config["count"],
                config["scale"],
                source_ground_y,
                config["anchor_x"][output_index],
                manual_bounds,
                config.get("output_anchor", OUTPUT_ANCHOR),
            )
            output_path = frame_dir / f"{output_index:02}.png"
            frame.save(output_path)
            frames.append(frame)
            frame_paths.append(output_path.relative_to(ROOT).as_posix())

        make_contact_sheet(name, frames, qa_dir / "contact-sheet.png")
        duration = round(1000 / config["fps"])
        frames[0].save(
            qa_dir / f"{name}-attack.gif",
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            disposal=2,
        )
        manifest["sequences"][name] = {
            "fps": config["fps"],
            "scale": config["scale"],
            "sourceGroundY": config["ground_y"],
            "slots": config["slots"],
            "anchor": list(config.get("output_anchor", OUTPUT_ANCHOR)),
            "frames": frame_paths,
        }

    manifest_path = GENERATED_ROOT / "fixed-attack-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(manifest_path)


if __name__ == "__main__":
    main()
