#!/usr/bin/env python3
"""Render Q2 Pet sprite sheets (7 columns x 2 rows of 192px RGBA cells).

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
    "beach-ball": ("#fff8dc", "#61beff"),
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
    y = 110 if kind != "snowman" else 91
    eyex = (75, 117)
    if kind == "beach-ball":
        # Blue sunglasses with dark navy lenses. Blink/dizzy still affects the mouth.
        poly(d, [(56,y-14),(92,y-12),(87,y+6),(64,y+6)], "#112d65", "#78c8ff", 3)
        poly(d, [(100,y-12),(137,y-14),(129,y+6),(107,y+6)], "#112d65", "#78c8ff", 3)
        lines(d, [(90,y-11),(100,y-11)], "#0f2752", 4)
        lines(d, [(65,y-10),(75,y-10)], "#d9f3ff", 3)
        lines(d, [(109,y-10),(119,y-10)], "#d9f3ff", 3)
    elif mood in (1,8):
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
        ellipse(m, (43,97,149,172), 255)
        ellipse(m, (49,46,143,139), 255)
    elif kind == "blossom":
        for i in range(5):
            theta = (i*72-90)*pi/180
            cx,cy=96+39*cos(theta),109+39*sin(theta)
            ellipse(m, (cx-34,cy-34,cx+34,cy+34), 255)
        ellipse(m, (67,78,125,139), 255)
    elif kind == "beach-ball":
        ellipse(m, (36,45,156,165), 255)
    base, glow = PALETTES[kind]
    result = Image.new("RGBA", (SIZE,SIZE))
    blurred = mask.filter(ImageFilter.GaussianBlur(10*SCALE))
    halo = Image.new("RGBA", (SIZE,SIZE), glow)
    halo.putalpha(blurred.point(lambda a: a//2))
    result.alpha_composite(halo)
    overlay(result, mask, base)
    d=ImageDraw.Draw(result)

    if mood == 11:
        ellipse(d,(68,63,90,76),"#fefefe")
        lines(d,[(77,111),(90,122),(105,112)],"#dc9cbd",3)
        return result

    if kind == "snowman":
        # Two snowballs, vivid blue winter cap, contrasting red scarf.
        ellipse(d, (50,52,142,133), "#f1fdff")
        ellipse(d, (65,54,90,72), "#ffffff")
        lines(d, [(44,121),(23,104),(18,110)], "#b57740", 5)
        lines(d, [(148,121),(169,104),(174,110)], "#b57740", 5)
        ellipse(d, (89,142,100,153), "#3479d9")
        ellipse(d, (89,157,100,168), "#3479d9")
        lines(d, [(57,123),(134,124)], "#ef3d51", 13)
        poly(d, [(117,119),(136,123),(137,164),(119,164)], "#f23c51")
        lines(d, [(123,126),(124,154)], "#ff7d8a", 2)
        poly(d, [(51,66),(60,32),(132,32),(143,66)], "#3189e5", "#9cddff", 2)
        for x in (70,85,101,116):
            lines(d, [(x,39),(x-3,65)], "#61b6fd", 2)
        ellipse(d, (80,17,111,41), "#ffffff")
        ellipse(d, (87,18,106,29), "#d8f7ff")
    elif kind == "blossom":
        # 5 separate glowing petals with line-work and golden pollen.
        for i in range(5):
            theta=(i*72-90)*pi/180
            cx,cy=96+39*cos(theta),109+39*sin(theta)
            ellipse(d,(cx-22,cy-21,cx+21,cy+22),"#ffc2e3")
            lines(d,[(96,106),(96+48*cos(theta),109+48*sin(theta))],"#fa84bb",2)
        for x,y in [(88,84),(104,84),(79,94),(113,94),(96,76)]:
            ellipse(d,(x-4,y-4,x+4,y+4),"#ffd452")
            ellipse(d,(x-2,y-3,x+1,y),"#fff3a8")
    elif kind == "beach-ball":
        # Segmented red / yellow / blue / white beach ball.
        # Clip the sector illustration exactly to the circular silhouette.
        colored=Image.new("RGBA",(SIZE,SIZE))
        wd=ImageDraw.Draw(colored)
        cx,cy=96,105
        palette=["#ffffff","#fa6269","#ffffff","#ffd54c","#ffffff","#51aefe"]
        for i in range(6):
            a=(i*2*pi/6)-pi/2
            b=((i+1)*2*pi/6)-pi/2
            points=[(cx,cy)] + [(cx+79*cos(a+(b-a)*t/12),cy+79*sin(a+(b-a)*t/12))
                                   for t in range(13)]
            poly(wd,points,palette[i])
        colored.putalpha(Image.composite(colored.getchannel("A"),Image.new("L",(SIZE,SIZE)),mask))
        result.alpha_composite(colored)
        d=ImageDraw.Draw(result)
        ellipse(d,(85,91,108,112),"#fffefa")
        ellipse(d,(89,95,103,104),"#f4f5ff")
        # Sunglasses are drawn in face() at a consistent fixed position.
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
