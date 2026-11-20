#!/usr/bin/env python3
"""Dedicated Frosty sprite template for Buddy (14 frames, 7x2, 192px cells).

Original winter character drawn from simple vector shapes inspired by the
user-provided snowman reference. The ghost remains the original built-in pet.
This renders all expressions without copying pixels from the reference.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

CELL = 192
SCALE = 3
SIZE = CELL * SCALE
OUT = Path(__file__).resolve().parent.parent / "generated" / "pets"
STATES = ("normal", "blink", "happy", "petted", "surprised", "annoyed",
          "boo", "dizzy", "asleep", "sad", "sick", "egg", "halo", "horns")

def at(box):
    return tuple(round(v * SCALE) for v in box)

def line(d, points, color, width=2):
    d.line([at(p) for p in points], fill=color, width=width*SCALE, joint="curve")

def ellipse(d, box, color, outline=None, width=1):
    d.ellipse(at(box), fill=color, outline=outline, width=width*SCALE)

def polygon(d, points, color, outline=None, width=1):
    p = [at(v) for v in points]
    d.polygon(p, fill=color)
    if outline:
        d.line(p+[p[0]], fill=outline, width=width*SCALE, joint="curve")

def frame(mood):
    if mood == 11:
        # Tamagotchi egg stage: no fully grown snowman before hatching.
        result = Image.new("RGBA", (SIZE, SIZE))
        d = ImageDraw.Draw(result)
        ellipse(d, (65, 63, 127, 169), "#d6f4ff")
        ellipse(d, (70, 67, 122, 161), "#ffffff")
        ellipse(d, (89, 108, 94, 113), "#425568")
        ellipse(d, (105, 108, 110, 113), "#425568")
        return result
    if mood in (12, 13):
        result = Image.new("RGBA", (SIZE, SIZE))
        d = ImageDraw.Draw(result)
        if mood == 12:
            ellipse(d, (68, 10, 124, 24), "#ffd957", "#fff6b6", 2)
            ellipse(d, (78, 14, 114, 20), "#fff3a2")
        else:
            polygon(d, [(62, 35), (62, 13), (80, 32), (96, 24),
                        (112, 32), (130, 13), (130, 35)], "#ef9cce")
        return result

    # Snowman's plump two-ball body and head, plus arms and hat.
    mask = Image.new("L", (SIZE, SIZE), 0)
    m = ImageDraw.Draw(mask)
    ellipse(m, (39, 99, 153, 183), 255)
    ellipse(m, (54, 49, 138, 137), 255)
    line(m, [(52, 127), (30, 118), (17, 107)], 255, 6)
    line(m, [(140, 127), (162, 118), (175, 107)], 255, 6)
    polygon(m, [(62, 59), (74, 23), (94, 11), (116, 16),
                (145, 48), (137, 69)], 255)
    ellipse(m, (137, 35, 158, 56), 255)
    ellipse(m, (49, 55, 145, 78), 255)

    result = Image.new("RGBA", (SIZE, SIZE))
    # Glow is baked into the transparent sprite, as with earlier Frosty.
    for blur, opacity in ((13, 0.30), (5, 0.45)):
        b = mask.filter(ImageFilter.GaussianBlur(blur*SCALE))
        layer = Image.new("RGBA", (SIZE, SIZE), "#8de4ff")
        layer.putalpha(b.point(lambda v: int(v*opacity)))
        result.alpha_composite(layer)
    d = ImageDraw.Draw(result)

    # Twig arms behind the snowballs.
    bark = "#a3b1b8"
    line(d, [(53, 128), (32, 120), (17, 107)], bark, 4)
    line(d, [(27, 117), (25, 104)], bark, 4)
    line(d, [(24, 113), (14, 117)], bark, 4)
    line(d, [(139, 128), (160, 120), (175, 107)], bark, 4)
    line(d, [(165, 116), (167, 104)], bark, 4)
    line(d, [(169, 112), (180, 116)], bark, 4)

    # Full round body, with a subtle cyan snow shadow.
    ellipse(d, (39, 99, 153, 183), "#d5f4fd")
    ellipse(d, (44, 103, 148, 177), "#f6fdff")
    ellipse(d, (54, 49, 138, 137), "#d7f5fd")
    ellipse(d, (58, 51, 134, 128), "#ffffff")

    # Two coal buttons stay below the scarf.
    for y in (151, 170):
        ellipse(d, (92, y-4, 100, y+4), "#95b6c4")

    # Soft Santa hat: back of the hat and floppy pointed tip.
    polygon(d, [(59, 66), (69, 33), (90, 18), (113, 17),
                (140, 48), (144, 62)], "#ef858e")
    polygon(d, [(75, 32), (91, 19), (111, 18), (134, 47),
                (110, 39)], "#fba8ae")
    ellipse(d, (138, 35, 158, 56), "#e9fbff")
    ellipse(d, (142, 38, 154, 52), "#f0fafb")
    # Fluffy, curved white brim.
    ellipse(d, (50, 54, 144, 79), "#e9fbff")
    ellipse(d, (53, 57, 140, 70), "#fcffff")

    # Scarf at neck, covering the join without obscuring face.
    ellipse(d, (60, 120, 134, 141), "#ef9aa8")
    ellipse(d, (68, 121, 125, 134), "#ffbdc6")
    polygon(d, [(115, 132), (129, 133), (132, 163),
                (118, 162)], "#f19eaa")
    line(d, [(122, 136), (123, 156)], "#ffcbd0", 2)

    # Ghost-inspired eye spacing, but use expressive winter closed eyes
    # as in the reference image. No cheek blush.
    y = 95
    for x in (77, 116):
        if mood in (1, 8, 9, 10):
            line(d, [(x-8,y), (x,y+3), (x+8,y)], "#556a7c", 2)
        elif mood in (2, 3):
            line(d, [(x-8,y+4), (x,y-5), (x+8,y+4)], "#556a7c", 2)
        elif mood == 7:
            line(d, [(x-7,y-6), (x+7,y+6)], "#556a7c", 2)
            line(d, [(x+7,y-6), (x-7,y+6)], "#556a7c", 2)
        elif mood == 5:
            line(d, [(x-8,y-2), (x+8,y+4)], "#556a7c", 2)
        else:
            # Friendly crescent eyes and tiny highlights.
            line(d, [(x-8,y+4), (x-5,y-4), (x+1,y-6),
                     (x+7,y+2)], "#556a7c", 2)

    # Small sideways carrot nose, proportioned for the Q2 screen.
    polygon(d, [(94, 102), (102, 99), (109, 103), (99, 112),
                (91, 110)], "#ffc18b")
    # Mood-dependent mouth, avoiding overlap with nose.
    if mood == 6:
        ellipse(d, (92, 114, 103, 127), "#53677b")
    elif mood in (9, 10):
        line(d, [(89,124), (97,120), (105,124)], "#53677b", 2)
    elif mood == 4:
        ellipse(d, (94,116,101,123), "#4f4047")
    else:
        line(d, [(91,117), (93,123), (98,125), (103,121)], "#53677b", 2)

    if mood == 10:
        ellipse(d, (135, 115, 141, 121), "#a9dfc4")
    # Feather the sprite edges to match the ghost's smooth silhouette.
    return result.filter(ImageFilter.GaussianBlur(0.65*SCALE))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for retired in ("blossom.png", "wilson.png", "beach-ball.png"):
        (OUT / retired).unlink(missing_ok=True)
    sheet = Image.new("RGBA", (7*CELL, 2*CELL))
    for idx, state in enumerate(STATES):
        image = frame(idx).resize((CELL, CELL), Image.Resampling.LANCZOS)
        sheet.alpha_composite(image, ((idx % 7)*CELL, (idx // 7)*CELL))
    dest = OUT / "snowman.png"
    sheet.save(dest, optimize=True)
    print(f"Frosty: {dest} ({sheet.width}x{sheet.height}), {len(STATES)} states")

if __name__ == "__main__":
    main()
