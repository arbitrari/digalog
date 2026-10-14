#!/usr/bin/env python3
"""Render docs/accent-colors.png from the Accent Color options in the repo.

Reads the themeColor ColorConfiguration from app/src/main/res/raw/watchface.xml
and the option names from app/src/main/res/values/strings.xml, in editor order,
and draws a 7x5 swatch grid on black (default option ringed). Requires Pillow.

Usage (from the repo root):  python3 tools/render_accent_colors.py [font.ttf]
"""
import os
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WATCHFACE = os.path.join(ROOT, "app/src/main/res/raw/watchface.xml")
STRINGS = os.path.join(ROOT, "app/src/main/res/values/strings.xml")
OUT = os.path.join(ROOT, "docs/accent-colors.png")

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf",
    "/usr/share/fonts/truetype/inter/Inter-VariableFont_opsz,wght.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_options():
    root = ET.parse(WATCHFACE).getroot()
    cc = root.find('UserConfigurations/ColorConfiguration[@id="themeColor"]')
    default = cc.get("defaultValue")
    names = {e.get("name"): e.text for e in ET.parse(STRINGS).getroot()}
    return [
        (names[o.get("displayName")],
         "#" + o.get("colors").split()[0][-6:].upper(),
         o.get("id") == default)
        for o in cc.findall("ColorOption")
    ]


def font(path, size, weight):
    f = ImageFont.truetype(path, size)
    try:  # variable Inter: optical size + weight
        f.set_variation_by_axes([14 if size < 20 else 24, weight])
    except Exception:
        pass
    return f


def main():
    font_path = sys.argv[1] if len(sys.argv) > 1 else next(
        p for p in FONT_CANDIDATES if os.path.exists(p))
    opts = load_options()

    k = 2  # render scale
    cols = 7
    rows = (len(opts) + cols - 1) // cols
    cw, ch, pad = 100 * k, 118 * k, 20 * k
    w, h = cols * cw + 2 * pad, rows * ch + 2 * pad
    im = Image.new("RGB", (w, h), "black")
    d = ImageDraw.Draw(im)
    f_name, f_hex = font(font_path, 13 * k, 500), font(font_path, 10 * k, 400)

    for i, (name, hx, is_default) in enumerate(opts):
        cx = pad + (i % cols) * cw + cw // 2
        cy = pad + (i // cols) * ch + 34 * k
        r = 26 * k
        if is_default:
            g = r + 6 * k
            d.ellipse((cx - g, cy - g, cx + g, cy + g), outline=(220, 220, 220), width=3)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hx)
        d.text((cx, cy + r + 16 * k), name, font=f_name, fill="white", anchor="mm")
        d.text((cx, cy + r + 33 * k), hx, font=f_hex, fill=(140, 140, 140), anchor="mm")

    im.save(OUT, optimize=True)
    print(f"wrote {OUT} ({w}x{h}, {len(opts)} colors)")


if __name__ == "__main__":
    main()
