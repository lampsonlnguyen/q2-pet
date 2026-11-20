#!/usr/bin/env python3
"""Generate Tom's built-in Q2 Buddy sheet from its approved white-cat artwork.

The repository stores a color-reduced, losslessly encoded PNG source as text
so GitHub can build Tom without installing a custom user buddy.png. This
build-time conversion restores full RGBA and never runs on the Q2 device.
"""
import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "tom_sprite.png.b64"
DEST = ROOT / "generated" / "pets" / "tom.png"

def clean_frame(frame):
    """Remove the AI source's grainy halo and keep Tom's actual silhouette.

    A connected dark outline defines the cat. The enclosed white body,
    nearby whiskers and dark details remain; background texture does not.
    All operations are host-side with Pillow only.
    """
    gray = frame.convert("L")
    pixels, light = frame.load(), gray.load()
    boundary = Image.new("L", (192, 192))
    bp = boundary.load()
    for y in range(192):
        for x in range(192):
            bp[x, y] = 255 if light[x, y] < 130 and pixels[x, y][3] > 100 else 0

    # Flood from the transparent outside until the connected outline.
    outside = boundary.copy()
    ImageDraw.floodfill(outside, (0, 0), 128, thresh=0)
    op = outside.load()
    regions = Image.new("L", (192, 192))
    rp = regions.load()
    for y in range(192):
        for x in range(192):
            rp[x, y] = 255 if op[x, y] != 128 else 0

    # Keep only the largest enclosed shape: the cat (or the egg).
    seen = bytearray(192 * 192)
    largest = []
    for y in range(192):
        for x in range(192):
            idx = y * 192 + x
            if seen[idx] or not rp[x, y]:
                continue
            seen[idx] = 1
            group = [idx]
            for p in group:
                u, v = p % 192, p // 192
                for nx, ny in ((u-1,v),(u+1,v),(u,v-1),(u,v+1)):
                    if nx < 0 or nx >= 192 or ny < 0 or ny >= 192:
                        continue
                    n = ny * 192 + nx
                    if seen[n] or not rp[nx, ny]:
                        continue
                    seen[n] = 1
                    group.append(n)
            if len(group) > len(largest):
                largest = group
    if len(largest) < 5000:
        raise ValueError("Tom's cat outline could not be isolated cleanly")
    core = Image.new("L", (192, 192))
    cp = core.load()
    for idx in largest:
        cp[idx % 192, idx // 192] = 255

    # Preserve whiskers and dark marks near the body, not floating noise.
    near = core.filter(ImageFilter.MaxFilter(39)).load()
    mask = Image.new("L", (192, 192))
    mp = mask.load()
    for y in range(192):
        for x in range(192):
            extra = light[x, y] < 150 and pixels[x, y][3] > 90 and near[x, y]
            mp[x, y] = 255 if cp[x, y] or extra else 0
    alpha = mask.filter(ImageFilter.GaussianBlur(.45)).load()

    # Remove gray paper texture within the cat without changing black eyes,
    # pink ears or other saturated details.
    for y in range(192):
        for x in range(192):
            r,g,b,a = pixels[x, y]
            if min(r,g,b) > 165 and max(r,g,b)-min(r,g,b) < 48:
                r = round(r*.25+255*.75)
                g = round(g*.25+255*.75)
                b = round(b*.25+255*.75)
            pixels[x, y] = (r,g,b,min(a,alpha[x,y]))
    return frame

def main():
    source = base64.b64decode(SOURCE.read_text(), validate=False)
    with Image.open(BytesIO(source)) as image:
        image.load()
        if image.size != (1344, 384):
            raise ValueError(f"Tom sprite must be 1344x384, got {image.size}")
        sheet = image.convert("RGBA")
    cleaned = Image.new("RGBA", sheet.size)
    for idx in range(12):
        x, y = (idx % 7) * 192, (idx // 7) * 192
        tile = clean_frame(sheet.crop((x,y,x+192,y+192)))
        cleaned.alpha_composite(tile, (x,y))
    sheet = cleaned
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
