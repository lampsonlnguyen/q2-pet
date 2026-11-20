#!/usr/bin/env python3
"""Export true procedural Kasper/Frosty frames using the same C renderer as Q2.

Artifacts are for preview and testing only; Kasper and Frosty remain procedural
on the device. Run: python3 tools/export_previews.py
"""
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "generated" / "previews"
LABELS = ("Normal", "Blink", "Happy", "Petted", "Surprised",
          "Annoyed", "Boo", "Dizzy", "Asleep", "Sad", "Sick",
          "Egg", "Halo", "Horns")
EXPECTED = (1344, 384)


def pam_to_rgba(path: Path) -> Image.Image:
    data = path.read_bytes()
    header, separator, pixels = data.partition(b"ENDHDR\n")
    if not separator or not header.startswith(b"P7\n"):
        raise ValueError("invalid P7 PAM output")
    if b"DEPTH 4\n" not in header or b"MAXVAL 255\n" not in header:
        raise ValueError("unexpected PAM channel format")
    if len(pixels) != EXPECTED[0] * EXPECTED[1] * 4:
        raise ValueError("incorrect procedural sprite sheet size")
    return Image.frombytes("RGBA", EXPECTED, pixels)


def guide(sheet: Image.Image) -> Image.Image:
    background = Image.new("RGBA", EXPECTED, (19, 24, 37, 255))
    background.alpha_composite(sheet)
    draw = ImageDraw.Draw(background)
    font_file = ROOT / "tools" / "LiberationSans-Bold.ttf"
    font = ImageFont.truetype(str(font_file), 14) if font_file.exists() else ImageFont.load_default()
    for i, label in enumerate(LABELS):
        x, y = (i % 7) * 192, (i // 7) * 192
        draw.rectangle((x, y, x + 191, y + 191), outline=(110, 122, 145))
        draw.text((x + 6, y + (172 if i > 11 else 6)), f"{i + 1}. {label}",
                  fill=(224, 230, 240), font=font)
    return background.convert("RGB")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        executable = Path(temp) / "fidget-host"
        subprocess.run(["cc", "-O2", "-fno-math-errno", "-DHOST",
                        str(ROOT / "fidget.c"), "-o", str(executable)],
                       check=True)
        for name, command in (("kasper", "template"), ("frosty", "template-frosty")):
            pam = Path(temp) / f"{name}.pam"
            subprocess.run([str(executable), command, str(pam)], check=True)
            sheet = pam_to_rgba(pam)
            assert sheet.getbbox() is not None
            sheet.save(OUT / f"{name}-template.png", optimize=True)
            guide(sheet).save(OUT / f"{name}-guide.png", optimize=True)
            print(f"Exported {name} PNG preview and 14-expression guide to {OUT}")


if __name__ == "__main__":
    main()
