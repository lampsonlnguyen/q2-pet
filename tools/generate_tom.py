#!/usr/bin/env python3
"""Draw Tom, a white chubby kawaii cat for Buddy's 14-frame sprite layout.

Artwork is rendered on the build computer (Pillow), not on the Shanling Q2.
Each frame is 192x192, arranged 7x2 in standard Buddy order. The cat
keeps the silhouette of the supplied reference: upright ears, rounded body,
small glossy eyes, tiny 'w' mouth, slender whiskers, front paws, curled tail.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

CELL = 192
SCALE = 3
SIZE = CELL * SCALE
OUT = Path(__file__).resolve().parent.parent / "generated" / "pets"
STATES = ("normal", "blink", "happy", "petted", "surprised", "annoyed",
          "boo", "dizzy", "asleep", "sad", "sick", "egg", "halo", "horns")

def coords(values):
    return tuple(round(value * SCALE) for value in values)

def ellipse(draw, box, color, outline=None, width=1):
    draw.ellipse(coords(box), fill=color, outline=outline,
                 width=max(1, round(width * SCALE)))

def polygon(draw, points, color):
    draw.polygon([coords(p) for p in points], fill=color)

def stroke(draw, points, color, width=2):
    draw.line([coords(p) for p in points], fill=color,
              width=max(1, round(width * SCALE)), joint="curve")

def frame(state):
    image = Image.new("RGBA", (SIZE, SIZE))
    d = ImageDraw.Draw(image)
    outline = "#56677a"
    snow = "#fcfdff"
    shade = "#dce6f0"

    if state in (12, 13):
        if state == 12:
            ellipse(d, (66, 14, 126, 32), "#ffe18b", "#f1bf52", 2)
            ellipse(d, (74, 17, 119, 25), "#fffbda")
        else:
            polygon(d, [(54,62),(60,20),(79,51)], "#e690a9")
            polygon(d, [(112,51),(133,20),(139,62)], "#e690a9")
        return image.resize((CELL, CELL), Image.Resampling.LANCZOS)

    if state == 11:
        mask = Image.new("L", (SIZE, SIZE))
        ellipse(ImageDraw.Draw(mask), (59,46,133,173),255)
        for blur, alpha in ((12, .3), (4, .48)):
            glow = Image.new("RGBA",(SIZE,SIZE),"#a8d7ff")
            glow.putalpha(mask.filter(ImageFilter.GaussianBlur(blur*SCALE))
                          .point(lambda a:round(a*alpha)))
            image.alpha_composite(glow)
        ellipse(d, (59,46,133,173), "#cfdeee")
        ellipse(d, (64,50,128,167), snow)
        # Cat's egg is gently decorated with a face and ears.
        polygon(d, [(79,108),(83,92),(94,103),(106,103),
                    (117,92),(121,108)], "#d7e5f1")
        ellipse(d,(84,111,90,117),outline)
        ellipse(d,(103,111,109,117),outline)
        stroke(d,[(91,121),(96,125),(101,121)],outline,2)
        return image.filter(ImageFilter.GaussianBlur(.2*SCALE)).resize(
            (CELL,CELL),Image.Resampling.LANCZOS)

    # Build a silhouette mask for a restrained blue glow, as with Kasper.
    mask = Image.new("L", (SIZE, SIZE))
    m = ImageDraw.Draw(mask)
    # curled tail behind the body
    stroke(m, [(137,136),(160,133),(166,118),(161,110)],255,12)
    ellipse(m,(49,65,143,157),255)
    ellipse(m,(49,111,143,176),255)
    polygon(m, [(51,91),(54,42),(84,63),(108,64),(137,42),(143,91)],255)
    for blur, alpha in ((10,.14),(3,.22)):
        glow = Image.new("RGBA", (SIZE,SIZE),"#b7deee")
        glow.putalpha(mask.filter(ImageFilter.GaussianBlur(blur*SCALE))
                      .point(lambda a:round(a*alpha)))
        image.alpha_composite(glow)

    # Soft-edged tail. Slightly darker than the white snow-like coat.
    stroke(d,[(137,136),(160,133),(166,118),(161,110)],shade,10)
    stroke(d,[(138,135),(157,131),(161,118),(157,111)],snow,6)

    # Chubby teardrop body, two visible paws.
    ellipse(d,(50,109,143,175),shade)
    ellipse(d,(53,113,140,170),snow)
    ellipse(d,(73,130,121,169),"#ffffff")
    ellipse(d,(65,152,96,179),shade)
    ellipse(d,(99,152,130,179),shade)
    ellipse(d,(68,149,94,176),snow)
    ellipse(d,(101,149,127,176),snow)

    # Pointed ears with small warm-pink insets.
    polygon(d,[(51,96),(54,42),(82,66),(109,66),(137,42),(143,96)],shade)
    polygon(d,[(57,85),(60,54),(80,75)],"#ffc2ce")
    polygon(d,[(114,75),(132,54),(137,85)],"#ffc2ce")
    ellipse(d,(49,63,143,148),shade)
    ellipse(d,(52,65,140,142),snow)
    ellipse(d,(58,69,134,123),"#ffffff")
    # Soft middle forehead patch, barely visible.
    ellipse(d,(78,71,115,88),"#f5f8fc")

    # Two straight front-leg strokes, friendly small character features.
    stroke(d,[(74,144),(77,166)],"#bdcbd9",1)
    stroke(d,[(118,144),(115,166)],"#bdcbd9",1)
    stroke(d,[(96,156),(96,173)],"#bdcbd9",1)

    eyes=(78,115)
    for x in eyes:
        if state in (1,8):
            stroke(d,[(x-8,99),(x,103),(x+8,99)],outline,2)
        elif state in (2,3):
            stroke(d,[(x-9,102),(x,93),(x+9,102)],outline,2)
        elif state == 7:
            stroke(d,[(x-7,92),(x+7,105)],outline,2)
            stroke(d,[(x+7,92),(x-7,105)],outline,2)
        elif state == 5:
            stroke(d,[(x-9,93),(x+9,98)],outline,2)
            ellipse(d,(x-7,97,x+7,105),outline)
        elif state in (9,10):
            stroke(d,[(x-8,99),(x,103),(x+8,99)],outline,2)
        else:
            ellipse(d,(x-7,92,x+7,107),outline)
            ellipse(d,(x-4,93,x-1,97),"#ffffff")
            ellipse(d,(x+3,100,x+4,102),"#ffffff")

    # Keep the short and recognizable w-shaped cat mouth.
    if state == 6:
        ellipse(d,(93,118,100,128),outline)
    elif state == 4:
        ellipse(d,(95,119,101,125),outline)
    elif state in (9,10):
        stroke(d,[(90,126),(97,122),(104,126)],outline,2)
    elif state in (2,3):
        stroke(d,[(88,119),(93,126),(97,123),(101,126),(106,119)],outline,2)
    else:
        stroke(d,[(88,119),(93,123),(97,119),(101,123),(106,119)],outline,2)

    # Fine unobtrusive whiskers.
    for a,b in [((64,110),(41,105)),((64,117),(41,120)),
                ((128,110),(151,105)),((128,117),(151,120))]:
        stroke(d,[a,b],"#8697a7",1)
    if state==10:
        ellipse(d,(136,118,142,124),"#a0dac3")
    return image.filter(ImageFilter.GaussianBlur(.32*SCALE)).resize(
        (CELL,CELL),Image.Resampling.LANCZOS)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    sheet=Image.new("RGBA",(CELL*7,CELL*2))
    for i,name in enumerate(STATES):
        sprite=frame(i)
        sheet.alpha_composite(sprite,((i%7)*CELL,(i//7)*CELL))
    dest=OUT/"tom.png"
    sheet.save(dest,optimize=True)
    print(f"Tom: {dest} ({sheet.width}x{sheet.height})")

if __name__=="__main__":
    main()