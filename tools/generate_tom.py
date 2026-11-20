#!/usr/bin/env python3
"""Generate Tom's built-in Q2 Buddy sheet from its approved white-cat artwork.

The repository stores a color-reduced, losslessly encoded PNG source as text
so GitHub can build Tom without installing a custom user buddy.png. This
build-time conversion restores full RGBA and never runs on the Q2 device.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "tom_sprite.png.b64"
DEST = ROOT / "generated" / "pets" / "tom.png"

def main():
    source = base64.b64decode(SOURCE.read_text(), validate=False)
    with Image.open(BytesIO(source)) as image:
        image.load()
        if image.size != (1344, 384):
            raise ValueError(f"Tom sprite must be 1344x384, got {image.size}")
        sheet = image.convert("RGBA")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(DEST, optimize=True)
    print(f"Tom: {DEST} ({sheet.width}x{sheet.height}, 14 frames)")

if __name__ == "__main__":
    main()
