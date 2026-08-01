#!/usr/bin/env python3
"""Derive four transparent puzzle quarters from the stable OpenMoji lantern."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "16.0.0/color/png-512/1F3EE.png"
OUTPUT = ROOT / "16.0.0/derived/lantern-parts"


def main() -> None:
    lantern = Image.open(SOURCE).convert("RGBA")
    if lantern.size != (512, 512):
        raise ValueError("The versioned lantern source must remain 512 × 512")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    boxes = {
        "top-left": (0, 0, 256, 256),
        "top-right": (256, 0, 512, 256),
        "bottom-left": (0, 256, 256, 512),
        "bottom-right": (256, 256, 512, 512),
    }
    for name, box in boxes.items():
        crop = lantern.crop(box)
        crop.save(OUTPUT / f"lantern-{name}-tile.png")
        canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        x = 0 if "left" in name else 256
        y = 0 if name.startswith("top") else 256
        canvas.paste(crop, (x, y), crop)
        canvas.save(OUTPUT / f"lantern-{name}.png")


if __name__ == "__main__":
    main()
