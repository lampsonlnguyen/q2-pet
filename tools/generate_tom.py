#!/usr/bin/env python3
"""Generate Tom's built-in Q2 Buddy sheet from its approved white-cat artwork.

The repository stores a color-reduced, losslessly encoded PNG source as text
so GitHub can build Tom without installing a custom user buddy.png. This
build-time conversion restores full RGBA and never runs on the Q2 device.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw

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
    # Buddy overlays states 13/14 on top of the current expression.
    # The supplied reference sheet depicts full cats in those two cells;
    # replace them with accessory-only frames so no duplicate cat appears.
    for index in (12, 13):
        x = (index % 7) * 192
        y = (index // 7) * 192
        sheet.paste((0, 0, 0, 0), (x, y, x + 192, y + 192))
        accessory = Image.new("RGBA", (192, 192))
        d = ImageDraw.Draw(accessory)
        if index == 12:
            d.ellipse((68, 13, 124, 32), outline="#ffcd65", width=5)
            d.arc((71, 16, 121, 27), 180, 360, fill="#fff6bc", width=2)
        else:
            d.polygon([(58, 55), (62, 25), (79, 52)], fill="#f07d92")
            d.polygon([(113, 52), (130, 25), (134, 55)], fill="#f07d92")
            d.polygon([(63, 44), (64, 34), (70, 46)], fill="#ffc3cf")
            d.polygon([(121, 46), (128, 34), (129, 44)], fill="#ffc3cf")
        sheet.alpha_composite(accessory, (x, y))
    DEST.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(DEST, optimize=True)
    print(f"Tom: {DEST} ({sheet.width}x{sheet.height}, 14 frames)")

if __name__ == "__main__":
    main()
