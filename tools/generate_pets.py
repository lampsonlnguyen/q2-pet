#!/usr/bin/env python3
"""Render Buddy seasonal sprite sheets (7 columns x 2 rows of 192px RGBA cells).

The character centre is (96,112) per cell, matching DiamondBond's Buddy
template. All 14 states are rendered, with a transparent background.
This is intentionally host-side only: no Pillow dependency on the Q2.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

CELL = 192
SCALE = 3
SIZE = CELL * SCALE
OUT = Path(__file__).resolve().parent.parent / "generated" / "pets"
OUT.mkdir(parents=True, exist_ok=True)
# Original look order in DiamondBond/q2-fidget:
STATES = ["normal","blink","happy","petted","surprised","annoyed","boo",
          "dizzy","asleep","sad","sick","egg","halo","horns"]
PALETTES = {
    "snowman": ("#efffff", "#73c8ff"),
}

def xy(vals):
    return tuple(int(round(x * SCALE)) for x in vals)

def ellipse(d, box, fill, outline=None, width=1):
    d.ellipse(xy(box), fill=fill, outline=outline, width=width*SCALE)

def poly(d, points, fill, outline=None, width=1):
    pts = [xy(v) for v in points]
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts+[pts[0]], fill=outline, width=width*SCALE, joint="curve")

def lines(d, points, fill, width=2):
    d.line([xy(v) for v in points], fill=fill, width=width*SCALE, joint="curve")

def overlay(base, mask, color):
    layer = Image.new("RGBA", (SIZE, SIZE), color)
    layer.putalpha(mask)
    base.alpha_composite(layer)

def face(d, mood, kind):
    # All expressions remain visible on the character, even after shrinking
    # to the Q2's actual display size.
    y = 74
    # Kasper's original ghost uses eyes spaced 52 px apart, tall ovals,
    # a cyan-lit lower rim and two white specular reflections.
    eyex = (70, 122)
    if mood in (1,8):
        for x in eyex:
            lines(d, [(x-9,y),(x,y+2),(x+9,y)], "#1c2449", 3)
    elif mood in (2,3):
        for x in eyex:
            lines(d, [(x-9,y+2),(x,y-6),(x+9,y+2)], "#1c2449", 3)
    elif mood == 7:
        for x in eyex:
            lines(d, [(x-7,y-6),(x+7,y+8)], "#1c2449", 3)
            lines(d, [(x+7,y-6),(x-7,y+8)], "#1c2449", 3)
    else:
        for x in eyex:
            # Recreate Kasper's procedural open-eye styling in Frosty's PNG:
            # tall dark iris, bright cyan lower gradient, two catchlights.
            ellipse(d, (x-14,y-17,x+14,y+17), "#83dfff")
            ellipse(d, (x-13,y-16,x+13,y+16), "#14254b")
            ellipse(d, (x-12,y+1,x+12,y+15), "#245d91")
            ellipse(d, (x-10,y+7,x+10,y+15), "#56bdec")
            ellipse(d, (x-11,y-15,x+11,y+5), "#14254b")
            ellipse(d, (x-8,y-10,x-1,y-3), "#ffffff")
            ellipse(d, (x+4,y+4,x+7,y+7), "#ffffff")
            if mood==5:
                lines(d, [(x-12,y-18),(x+12,y-13)], "#172a4c", 3)
    if mood == 6:
        ellipse(d, (89,y+15,103,y+32), "#331c45")
    elif mood in (4,7):
        ellipse(d, (92,y+14,100,y+26), "#331c45")
    elif mood in (9,10):
        lines(d, [(89,y+27),(96,y+23),(103,y+27)], "#40283b", 2)
    elif mood in (2,3):
        ellipse(d, (88,y+15,105,y+26), "#6b2b5c")
        ellipse(d, (93,y+21,101,y+26), "#ff8598")
    else:
        lines(d, [(89,y+21),(94,y+23),(96,y+19),(99,y+23),(104,y+21)], "#182a4f", 2)

def body(kind, mood):
    if mood in (12,13): # Adult overlays: halo / horns
        pic = Image.new("RGBA", (SIZE,SIZE))
        d = ImageDraw.Draw(pic)
        if mood == 12:
            ellipse(d, (62,16,130,31), "#ffd658")
            ellipse(d, (70,19,122,25), "#fff5b2")
        else:
            poly(d, [(59,36),(61,15),(79,32),(96,23),(113,32),(131,15),(133,36)], "#f5a4ff")
        return pic

    mask = Image.new("L", (SIZE,SIZE))
    m = ImageDraw.Draw(mask)
    if mood == 11:
        ellipse(m, (57,45,135,174), 255)
    elif kind == "snowman":
        # Frosty: a large round head on an extra-plump body.
        ellipse(m, (24,75,168,185), 255)
        ellipse(m, (42,24,150,124), 255)
    base, glow = PALETTES[kind]
    result = Image.new("RGBA", (SIZE,SIZE))
    # Soft ambient bloom plus a brighter close halo, like the original ghost.
    for blur, strength in ((16, 0.34), (7, 0.56)):
        blurred = mask.filter(ImageFilter.GaussianBlur(blur*SCALE))
        halo = Image.new("RGBA", (SIZE, SIZE), glow)
        halo.putalpha(blurred.point(lambda a: min(255, int(a*strength))))
        result.alpha_composite(halo)
    overlay(result, mask, base)
    d=ImageDraw.Draw(result)

    if mood == 11:
        ellipse(d,(68,63,90,76),"#fefefe")
        lines(d,[(77,111),(90,122),(105,112)],"#dc9cbd",3)
        return result

    if kind == "snowman":
        # Frosty: oversized round head and a very fat body, no accessories.
        ellipse(d, (24,76,168,184), "#d8f4ff")
        ellipse(d, (30,82,160,176), "#eefbff")
        ellipse(d, (42,24,150,124), "#d8f5ff")
        ellipse(d, (48,28,144,116), "#eefcff")
        ellipse(d, (58,34,132,92), "#ffffff")
    face(d,mood,kind)
    if mood==10:
        # Sick expression; retained so the original engine can add its green tint.
        ellipse(d,(145,100,152,108),"#75cc98")
    return result

# Clear sprites retired in prior versions before regenerating the winter artwork.
for retired in ("blossom.png", "wilson.png", "beach-ball.png"):
    (OUT / retired).unlink(missing_ok=True)

for name in PALETTES:
    sheet=Image.new("RGBA",(7*CELL,2*CELL))
    for state in range(len(STATES)):
        frame=body(name,state).resize((CELL,CELL),Image.Resampling.LANCZOS)
        sheet.alpha_composite(frame,((state%7)*CELL,(state//7)*CELL))
    path=OUT/(name+".png")
    sheet.save(path,optimize=True)
    print(f"{name}: {path} ({sheet.width}x{sheet.height})")
