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
    y = 110 if kind != "snowman" else 76
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
        # Two overlapping snowballs: small, round head above a larger body.
        ellipse(m, (28,83,164,184), 255)
        ellipse(m, (55,37,137,119), 255)
    elif kind == "blossom":
        for i in range(5):
            theta = (i*72-90)*pi/180
            cx,cy=96+39*cos(theta),109+39*sin(theta)
            ellipse(m, (cx-34,cy-34,cx+34,cy+34), 255)
        ellipse(m, (67,78,125,139), 255)
    elif kind == "wilson":
        ellipse(m, (36,45,156,165), 255)
    base, glow = PALETTES[kind]
    result = Image.new("RGBA", (SIZE,SIZE))
    # Soft ambient bloom plus a brighter close halo, like the original ghost.
    for blur, strength in ((15, 0.36), (5, 0.58)):
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
        # Frosty: fat rounded lower snowball, smaller round head, no accessories.
        ellipse(d, (29,84,163,183), "#d7f4ff")
        ellipse(d, (35,89,156,175), "#eefbff")
        ellipse(d, (55,37,137,119), "#d8f5ff")
        ellipse(d, (59,40,133,112), "#f6fdff")
        ellipse(d, (66,44,122,86), "#ffffff")
    elif kind == "blossom":
        # Sakura: five softly shaded petals and an uncluttered central face.
        for i in range(5):
            theta = (i*72-90)*pi/180
            cx, cy = 96+39*cos(theta), 109+39*sin(theta)
            ellipse(d, (cx-29,cy-29,cx+29,cy+29), "#fba9d2")
            ellipse(d, (cx-24,cy-25,cx+22,cy+21), "#ffd8ed")
        ellipse(d, (64,81,128,145), "#ffc8e2")
        ellipse(d, (71,86,121,133), "#ffdeee")
    elif kind == "wilson":
        # Wilson: a pale volleyball with broad curved panel seams, not
        # beach-ball wedges. Panels stay readable at the Q2's small sizes.
        colored = Image.new("RGBA", (SIZE, SIZE))
        wd = ImageDraw.Draw(colored)
        ellipse(wd, (36,45,156,165), "#f7fcff")
        ellipse(wd, (47,51,146,155), "#e9f7ff")
        # Curved panels evoke volleyball stitching; avoid a central hub.
        wd.arc(xy((43,47,150,156)), 18, 155, fill="#96c6e4", width=3*SCALE)
        wd.arc(xy((47,46,150,154)), 197, 341, fill="#9fcbea", width=3*SCALE)
        wd.arc(xy((63,40,138,171)), 58, 220, fill="#afd3e9", width=3*SCALE)
        wd.arc(xy((56,40,135,166)), 235, 355, fill="#afd3e9", width=3*SCALE)
        wd.arc(xy((44,72,151,151)), 225, 329, fill="#afd3e9", width=2*SCALE)
        # Clip the panels so their seams cannot extend past the ball.
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
