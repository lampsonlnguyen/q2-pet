#!/usr/bin/env python3
"""Render Buddy seasonal sprite sheets (7 columns x 2 rows of 192px RGBA cells).

The character centre is (96,112) per cell, matching DiamondBond's Buddy
template. All 14 states are rendered, with a transparent background.
This is intentionally host-side only: no Pillow dependency on the Q2.
"""
from math import cos, sin, pi
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
    "blossom": ("#ffb6de", "#f566b3"),
    "wilson": ("#f8fcff", "#a5d9ff"),
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
    y = 110 if kind != "snowman" else 74
    eyex = (75, 117)
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
            ellipse(d, (x-10,y-10,x+10,y+10), "#16264f")
            ellipse(d, (x-6,y-7,x-1,y-2), "white")
            ellipse(d, (x+3,y+3,x+5,y+5), "#acdbff")
            if mood==5:
                lines(d, [(x-9,y-13),(x+9,y-10)], "#172a4c", 3)
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
    if mood not in (10,11):
        ellipse(d, (52,y+12,66,y+21), "#ffb0cf")
        ellipse(d, (126,y+12,140,y+21), "#ffb0cf")

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
    elif kind == "blossom":
        # Five petals with distinct notched tips, unlike round flower blobs.
        for i in range(5):
            theta = (i*72-90)*pi/180
            dx, dy = cos(theta), sin(theta)
            tx, ty = -dy, dx
            petal = [(96,109)]
            for along, across in ((14,-23),(36,-31),(55,-23),
                                  (50,-7),(45,0),(50,7),
                                  (55,23),(36,31),(14,23)):
                petal.append((96+dx*along+tx*across,
                              109+dy*along+ty*across))
            poly(m, petal, 255)
        ellipse(m, (63,76,129,142), 255)
    elif kind == "wilson":
        ellipse(m, (36,45,156,165), 255)
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
    elif kind == "blossom":
        # Sakura: five authentic-looking notched cherry blossom petals.
        for i in range(5):
            theta = (i*72-90)*pi/180
            dx, dy = cos(theta), sin(theta)
            tx, ty = -dy, dx
            petal = [(96,109)]
            for along, across in ((14,-23),(36,-31),(55,-23),
                                  (50,-7),(45,0),(50,7),
                                  (55,23),(36,31),(14,23)):
                petal.append((96+dx*along+tx*across,
                              109+dy*along+ty*across))
            poly(d, petal, "#f7afd6", "#fbd3e8", 1)
            lines(d, [(96+dx*18,109+dy*18),
                      (96+dx*40,109+dy*40)], "#fbd9e9", 1)
        ellipse(d, (62,78,130,143), "#ffd7e9")
        ellipse(d, (70,86,122,136), "#ffedf5")
        # Fine stamens kept away from the main facial features.
        for angle in (-135,-95,-55,45,85,125):
            theta = angle*pi/180
            x2, y2 = 96+27*cos(theta), 110+27*sin(theta)
            lines(d, [(96,110),(x2,y2)], "#ffe7aa", 1)
            ellipse(d, (x2-2,y2-2,x2+2,y2+2), "#ffe58e")
    elif kind == "wilson":
        # Wilson: pale volleyball with curved stitched-panel seams,
        # rather than beach-ball radial wedges.
        colored = Image.new("RGBA", (SIZE, SIZE))
        wd = ImageDraw.Draw(colored)
        ellipse(wd, (36,45,156,165), "#f8fcff")
        ellipse(wd, (43,51,148,156), "#f0f8ff")
        seam = "#b9cde0"
        wd.arc(xy((35,43,161,174)), 204, 333, fill=seam, width=3*SCALE)
        wd.arc(xy((31,35,155,165)), 24, 151, fill=seam, width=3*SCALE)
        wd.arc(xy((59,34,139,172)), 62, 213, fill=seam, width=3*SCALE)
        wd.arc(xy((53,38,139,174)), 231, 358, fill=seam, width=3*SCALE)
        wd.arc(xy((42,75,158,158)), 194, 331, fill=seam, width=3*SCALE)
        alpha = Image.composite(colored.getchannel("A"),
                                Image.new("L", (SIZE, SIZE)), mask)
        colored.putalpha(alpha)
        result.alpha_composite(colored)
        d = ImageDraw.Draw(result)
    face(d,mood,kind)
    if mood==10:
        # Sick expression; retained so the original engine can add its green tint.
        ellipse(d,(145,100,152,108),"#75cc98")
    return result

for name in PALETTES:
    sheet=Image.new("RGBA",(7*CELL,2*CELL))
    for state in range(len(STATES)):
        frame=body(name,state).resize((CELL,CELL),Image.Resampling.LANCZOS)
        sheet.alpha_composite(frame,((state%7)*CELL,(state//7)*CELL))
    path=OUT/(name+".png")
    sheet.save(path,optimize=True)
    print(f"{name}: {path} ({sheet.width}x{sheet.height})")
