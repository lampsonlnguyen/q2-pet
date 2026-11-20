#!/usr/bin/env python3
"""Generate Q2 Pet's 7x2 RGBA expression sheets (192px per cell).

Build dependency: Pillow. No image library is needed on the Shanling Q2.
The sprite layout follows DiamondBond/q2-fidget's 14-cell buddy.png format.
"""
from pathlib import Path
from math import cos, sin, pi
from PIL import Image, ImageDraw, ImageFilter

S = 3
CELL = 192
MOODS = 14
OUT = Path(__file__).resolve().parent.parent / "generated" / "pets"
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = {
    "snowman": ("#ecffff", "#91ddff"),
    "blossom": ("#ffb6dc", "#fc73b7"),
    "sun": ("#ffe16a", "#ffac36"),
    "maple": ("#ff9952", "#ec553c"),
    "lantern": ("#fa545e", "#b92443"),
    "moon": ("#dff0ff", "#88b8ff"),
    "diamond": ("#b3fbff", "#46aaf4"),
}

def scale(v):
    return tuple(round(x * S) for x in v)

def ellipse(d, box, fill, outline=None, width=1):
    d.ellipse(scale(box), fill=fill, outline=outline, width=width*S)

def polygon(d, coords, fill, outline=None, width=1):
    d.polygon([scale(p) for p in coords], fill=fill)
    if outline:
        d.line([scale(p) for p in coords] + [scale(coords[0])], fill=outline, width=width*S, joint="curve")

def line(d, coords, fill, width=2):
    d.line([scale(p) for p in coords], fill=fill, width=width*S, joint="curve")

def shape(kind, mood):
    if mood in (12, 13):
        layer = Image.new("RGBA", (CELL*S, CELL*S))
        d = ImageDraw.Draw(layer)
        if mood == 12:
            ellipse(d, (65, 24, 127, 37), "#ffe579")
            ellipse(d, (68, 25, 124, 33), "#fff6b4")
        else:
            polygon(d, [(65, 38), (65, 23), (77, 32), (86, 18), (96, 30),
                        (106, 18), (115, 32), (127, 23), (127, 38)], "#e9a0fb")
        return layer

    mask = Image.new("L", (CELL*S, CELL*S))
    m = ImageDraw.Draw(mask)
    if mood == 11:  # egg, universally shared
        ellipse(m, (54, 46, 138, 174), 255)
    elif kind == "snowman":
        ellipse(m, (45, 98, 147, 174), 255)
        ellipse(m, (53, 48, 139, 139), 255)
    elif kind == "blossom":
        for i in range(5):
            a = (i * 72 - 90) * pi / 180
            cx, cy = 96 + 36*cos(a), 111 + 36*sin(a)
            ellipse(m, (cx-35, cy-35, cx+35, cy+35), 255)
        ellipse(m, (64, 77, 128, 143), 255)
    elif kind == "sun":
        for i in range(12):
            a = i*pi/6
            polygon(m, [(96 + r*cos(a+offset), 111 + r*sin(a+offset))
                        for r, offset in ((45, -0.16), (76, 0), (45, 0.16))], 255)
        ellipse(m, (45, 60, 147, 162), 255)
    elif kind == "maple":
        polygon(m, [(96,35), (110,70), (135,53), (131,81), (160,88), (139,108),
                    (150,130), (113,127), (102,155), (90,155), (79,127),
                    (42,130), (53,108), (32,88), (61,81), (57,53), (82,70)], 255)
    elif kind == "lantern":
        ellipse(m, (46, 63, 146, 157), 255)
        ellipse(m, (69, 56, 123, 72), 255)
    elif kind == "moon":
        ellipse(m, (38, 43, 150, 172), 255)
        ellipse(m, (89, 23, 183, 139), 0)
    elif kind == "diamond":
        polygon(m, [(96, 35), (148, 79), (143, 126), (96, 173),
                    (49, 126), (44, 79)], 255)
    else:
        raise ValueError(kind)

    base, deep = PALETTES[kind]
    halo = Image.new("RGBA", mask.size)
    halo.paste(deep, (0, 0, *mask.size), mask)
    blur = halo.filter(ImageFilter.GaussianBlur(8*S))
    blur.putalpha(mask.filter(ImageFilter.GaussianBlur(9*S)).point(lambda a: a*2//5))
    result = Image.new("RGBA", mask.size)
    result.alpha_composite(blur)
    body = Image.new("RGBA", mask.size, base)
    body.putalpha(mask)
    result.alpha_composite(body)
    d = ImageDraw.Draw(result)

    if mood == 11:
        line(d, [(72,112),(87,120),(100,108),(117,115)], "#d1a8cb", 3)
        return result

    if kind == "snowman":
        line(d, [(47, 117), (27, 102), (21, 107)], "#947259", 4)
        line(d, [(145, 117), (165, 102), (171, 107)], "#947259", 4)
        ellipse(d, (92, 138, 100, 146), "#ffac43")
        ellipse(d, (92, 155, 100, 163), "#ffac43")
        polygon(d, [(52, 42), (140, 42), (131, 24), (61, 24)], "#52aafa")
        ellipse(d, (85, 11, 107, 33), "#edfaff")
        line(d, [(54, 121), (134, 124)], "#2185d1", 12)
    elif kind == "blossom":
        for a in (10,82,154,226,298):
            t = a*pi/180
            ellipse(d, (96+42*cos(t)-5, 111+42*sin(t)-5,
                        96+42*cos(t)+5, 111+42*sin(t)+5), "#fff1fa")
        ellipse(d, (85, 96, 107, 117), "#ffe4f2")
    elif kind == "sun":
        ellipse(d, (54, 68, 138, 154), "#ffe985")
    elif kind == "maple":
        line(d, [(96, 85), (96, 143)], "#ffd5a1", 2)
        for xx in (59, 75, 117, 133):
            line(d, [(96, 118), (xx, 95)], "#ffd5a1", 2)
        line(d, [(96, 151), (97, 181)], "#9d673d", 5)
    elif kind == "lantern":
        for x in (65, 82, 110, 127):
            line(d, [(x, 74), (x, 145)], "#ffd077", 2)
        line(d, [(69, 65), (123, 65)], "#ffd36a", 7)
        line(d, [(68, 151), (124, 151)], "#ffd36a", 6)
        line(d, [(96, 158), (96, 183)], "#e4a83d", 5)
    elif kind == "moon":
        ellipse(d, (55, 70, 70, 85), "#b0cdf4")
        ellipse(d, (67, 138, 79, 150), "#b0cdf4")
    elif kind == "diamond":
        line(d, [(44,79), (148,79)], "#e2ffff", 3)
        line(d, [(44,79), (96,173), (148,79)], "#77c9f6", 3)
        line(d, [(72,79), (96,35), (120,79), (96,173), (72,79)], "#efffff", 2)

    # Faces share the same expression order as the original Buddy sprite sheet.
    if mood == 8:  # asleep
        for x in (76,116):
            line(d, [(x-9,108), (x,111), (x+9,108)], "#263453", 3)
    elif mood == 1:  # blink
        for x in (76,116):
            line(d, [(x-8,108), (x+8,108)], "#263453", 3)
    elif mood in (2,3):  # happy / petted
        for x in (76,116):
            line(d, [(x-9,107), (x,98), (x+9,107)], "#243450", 3)
    elif mood == 7:  # dizzy
        for x in (76,116):
            line(d, [(x-7,99), (x+7,115)], "#263453", 3)
            line(d, [(x+7,99), (x-7,115)], "#263453", 3)
    elif mood == 5:  # annoyed
        for x in (76,116):
            ellipse(d, (x-6,103,x+6,113), "#202e47")
            line(d, [(x-9,95), (x+8,101)], "#263453", 3)
    else:
        for x in (76,116):
            ellipse(d, (x-9,98,x+9,116), "#202e47")
            ellipse(d, (x-5,100,x-1,105), "#ffffff")
            ellipse(d, (x+3,108,x+5,110), "#e6ffff")
    if mood in (4,6):
        ellipse(d, (91,118,101,130), "#27304e")
    elif mood in (9,10):
        line(d, [(91,129),(96,124),(101,129)], "#27304e", 2)
    else:
        line(d, [(90,123),(94,126),(96,121),(99,126),(103,123)], "#27304e", 2)
    if mood != 10:
        ellipse(d, (51,118,64,126), "#ffb1c1")
        ellipse(d, (128,118,141,126), "#ffb1c1")
    return result

for kind in PALETTES:
    sheet = Image.new("RGBA", (7*CELL, 2*CELL))
    for mood in range(MOODS):
        pic = shape(kind, mood).resize((CELL,CELL), Image.Resampling.LANCZOS)
        sheet.alpha_composite(pic, ((mood % 7)*CELL, (mood // 7)*CELL))
    dest = OUT / (kind + ".png")
    sheet.save(dest, optimize=True)
    print(dest)
