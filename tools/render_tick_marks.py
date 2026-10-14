#!/usr/bin/env python3
"""Render docs/tick-marks.png: the four Tick Marks options side by side.

Draws an approximation of the face in normal mode at 10:10 (no complications)
from the repo's own assets (index_hours, index_minutes, hand images) for each
Tick Marks option, with the option name (from strings.xml) under it. The second
hand uses the default Accent Color read from watchface.xml. Geometry mirrors
watchface.xml (450-unit face, hands pivoting at the center, digits at radius
183 / 130). Requires Pillow.

Usage (from the repo root):  python3 tools/render_tick_marks.py [font.ttf]
"""
import math
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app/src/main/res")
DRAW = os.path.join(RES, "drawable-nodpi")
OUT = os.path.join(ROOT, "docs/tick-marks.png")
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf",
    "/usr/share/fonts/truetype/inter/Inter-VariableFont_opsz,wght.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
LAYERS = {  # ListOption id -> tick layers drawn (see watchface.xml tickMarks)
    "hour_minute": ["index_hours", "index_minutes"],
    "hour": ["index_hours"],
    "minute": ["index_minutes"],
    "none": [],
}
HOUR, MINUTE, SECOND = 10, 10, 35


def font(path, size, weight):
    f = ImageFont.truetype(path, size)
    try:
        f.set_variation_by_axes([14 if size < 20 else 24, weight])
    except Exception:
        pass
    return f


def config():
    root = ET.parse(os.path.join(RES, "raw/watchface.xml")).getroot()
    names = {e.get("name"): e.text for e in ET.parse(os.path.join(RES, "values/strings.xml")).getroot()}
    cc = root.find('UserConfigurations/ColorConfiguration[@id="themeColor"]')
    accent = next(o for o in cc.findall("ColorOption") if o.get("id") == cc.get("defaultValue"))
    accent = "#" + accent.get("colors").split()[0][-6:]
    lc = root.find('UserConfigurations/ListConfiguration[@id="tickMarks"]')
    opts = [(o.get("id"), names[o.get("displayName")]) for o in lc.findall("ListOption")]
    return accent, opts


def face(layers, accent, font_path, s=4):
    """Render one 450-unit face at scale s (RGBA)."""
    n = 450 * s
    c = n / 2
    im = Image.new("RGBA", (n, n), (0, 0, 0, 255))
    for name in layers:
        im.alpha_composite(Image.open(os.path.join(DRAW, name + ".png")).convert("RGBA").resize((n, n), Image.LANCZOS))
    d = ImageDraw.Draw(im)
    d.ellipse((c - 14 * s, c - 14 * s, c + 14 * s, c + 14 * s), fill="white")  # center circle

    def place(img, radius, angle):
        """Paste img centered at `radius` units along `angle` (deg, clockwise from 12)."""
        r = img.rotate(-angle, expand=True, resample=Image.BICUBIC)
        a = math.radians(angle)
        x = c + radius * s * math.sin(a) - r.width / 2
        y = c - radius * s * math.cos(a) - r.height / 2
        im.alpha_composite(r, (int(round(x)), int(round(y))))

    def hand(name, length, width, angle, tint=None):
        img = Image.open(os.path.join(DRAW, name + ".png")).convert("RGBA").resize((width * s, length * s), Image.LANCZOS)
        if tint:
            col = Image.new("RGBA", img.size, tint)
            col.putalpha(img.split()[3])
            img = col
        place(img, length / 2, angle)  # hand images run from the tip to the pivot

    ha = (HOUR % 12 + MINUTE / 60) * 30
    ma = MINUTE * 6
    hand("hand_minute", 209, 28, ma)
    hand("hand_hour", 150, 28, ha)

    f = font(font_path, 31 * s, 800)
    for txt, radius, angle, left in (("%02d" % MINUTE, 183, ma, MINUTE > 30),
                                     (str(HOUR), 130, ha, 6 <= HOUR % 12 < 12)):
        t = Image.new("RGBA", (40 * s, 30 * s), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((20 * s, 15 * s), txt, font=f, fill="black", anchor="mm")
        r = t.rotate(-(angle + (90 if left else -90)), expand=True, resample=Image.BICUBIC)
        a = math.radians(angle)
        im.alpha_composite(r, (int(round(c + radius * s * math.sin(a) - r.width / 2)),
                               int(round(c - radius * s * math.cos(a) - r.height / 2))))

    hand("hand_second", 218, 9, SECOND * 6, tint=accent)
    d.ellipse((c - 4.5 * s, c - 4.5 * s, c + 4.5 * s, c + 4.5 * s), fill=accent)

    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, n - 1, n - 1), fill=255)
    out = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def main():
    font_path = sys.argv[1] if len(sys.argv) > 1 else next(p for p in FONT_CANDIDATES if os.path.exists(p))
    accent, opts = config()

    k = 2  # same scale and outer width as docs/accent-colors.png
    pad = 20 * k
    w = 1480
    cw = (w - 2 * pad) // len(opts)
    dia = cw - 40 * k
    label_gap = 22 * k
    h = pad + dia + label_gap + 14 * k + pad
    im = Image.new("RGB", (w, h), "black")
    d = ImageDraw.Draw(im)
    f_name = font(font_path, 13 * k, 500)
    for i, (oid, label) in enumerate(opts):
        cx = pad + i * cw + cw // 2
        fc = face(LAYERS[oid], accent, font_path).resize((dia, dia), Image.LANCZOS)
        im.paste(fc, (cx - dia // 2, pad), fc)
        d.ellipse((cx - dia // 2, pad, cx + dia // 2, pad + dia), outline=(40, 40, 40), width=2)
        d.text((cx, pad + dia + label_gap), label, font=f_name, fill="white", anchor="mm")
    im.save(OUT, optimize=True)
    print(f"wrote {OUT} ({w}x{h}, {len(opts)} options)")


if __name__ == "__main__":
    main()
