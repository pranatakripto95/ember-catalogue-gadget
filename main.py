#!/usr/bin/env python3
"""Ember Catalogue Gadget — a catalogue photograph of an impossible gadget.

Draws INFINICELL, a self-charging power bank: its own USB-C cable loops
out of one port and straight back into the other, so it charges itself
forever. A wall charger lies beside it, unused. Pure Pillow, no network.
Writes /output/entry.png (1024x1024, < 1 MiB).
"""
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 2                      # supersample factor: draw at 2048, ship at 1024
W = H = 1024
ROOT = Path(__file__).resolve().parent


def s(v):
    return int(round(v * SS))


def pt(x, y):
    return (s(x), s(y))


def box(x0, y0, x1, y1):
    return (s(x0), s(y0), s(x1), s(y1))


# ---------------------------------------------------------------- palette
BG_TOP = (245, 242, 237)
BG_MID = (236, 231, 223)
FLOOR_TOP = (230, 224, 214)
FLOOR_BOT = (214, 207, 194)
INK = (34, 37, 42)
INK_SOFT = (110, 103, 92)
RULE = (181, 174, 160)
MINT = (125, 255, 168)
MINT_DIM = (86, 214, 138)
BODY_HI = (58, 62, 67)
BODY_LO = (24, 26, 29)
EDGE = (16, 18, 20)
SILVER = (185, 190, 196)
CABLE = (28, 30, 32)
CABLE_HI = (96, 100, 105)


def font(name, size, bold=False):
    fname = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for p in (ROOT / "assets" / "fonts" / fname,
              Path("/usr/share/fonts/truetype/dejavu") / fname,
              Path("/usr/share/fonts/truetype/liberation") /
              ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf")):
        try:
            return ImageFont.truetype(str(p), s(size))
        except Exception:
            continue
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(draw, x0, y0, x1, y1, top, bot):
    """Vertical gradient, drawn as 1px-high strips (in logical coords)."""
    for yy in range(y0, y1):
        t = (yy - y0) / max(1, (y1 - y0 - 1))
        draw.line([(s(x0), s(yy)), (s(x1), s(yy))], fill=lerp(top, bot, t))


def rounded(draw, b, radius, **kw):
    draw.rounded_rectangle(box(*b), radius=s(radius), **kw)


def text(draw, xy, string, fnt, fill, spacing=0, anchor_left=True):
    """Draw text with optional letter-spacing. xy is the left/top (logical)."""
    x, y = xy
    if spacing == 0:
        draw.text(pt(x, y), string, font=fnt, fill=fill)
        return
    cx = x
    for ch in string:
        draw.text(pt(cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) / SS + spacing


def text_w(draw, string, fnt, spacing=0):
    w = draw.textlength(string, font=fnt) / SS
    return w + spacing * max(0, len(string) - 1)


def centered(draw, cx, y, string, fnt, fill, spacing=0):
    w = text_w(draw, string, fnt, spacing)
    text(draw, (cx - w / 2, y), string, fnt, fill, spacing)


def cubic(p0, p1, p2, p3, n=64):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def main():
    img = Image.new("RGB", (s(W), s(H)), BG_TOP)
    d = ImageDraw.Draw(img)

    # --- studio background: wall gradient, floor gradient, horizon line
    vgrad(d, 0, 0, W, 860, BG_TOP, BG_MID)
    vgrad(d, 0, 860, W, H, FLOOR_TOP, FLOOR_BOT)
    d.line([pt(0, 860), pt(W, 860)], fill=RULE + (255,), width=s(2))
    # soft top light
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse(box(180, -260, 844, 320), fill=(255, 255, 255, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(s(90)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # --- catalogue furniture, top
    f_b20, f_r16 = font("x", 20, bold=True), font("x", 16)
    d.rectangle(box(64, 46, 76, 58), fill=MINT_DIM)
    text(d, (88, 40), "EMBER & CO.", f_b20, INK, spacing=4)
    r = "CATALOGUE  No. 07"
    text(d, (960 - text_w(d, r, f_r16), 44), r, f_r16, INK_SOFT, spacing=2)
    d.line([pt(64, 78), pt(960, 78)], fill=RULE, width=s(2))

    # --- floor shadows (under product, cable, charger)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse(box(330, 844, 670, 870), fill=(30, 25, 18, 55))
    sd.ellipse(box(745, 848, 935, 872), fill=(30, 25, 18, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(s(18)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # --- power bank: thickness edge, then front face
    rounded(d, (310, 238, 710, 630), 48, fill=(26, 28, 30))
    face = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(face)
    fd.rounded_rectangle(box(300, 230, 700, 620), radius=s(48), fill=(255, 255, 255, 255))
    mask = face.split()[3]
    grad = Image.new("RGB", img.size, BODY_HI)
    gd2 = ImageDraw.Draw(grad)
    vgrad(gd2, 300, 230, 700, 620, BODY_HI, BODY_LO)
    img.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(img)
    # sheen: soft diagonal light across the face
    sh2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s2 = ImageDraw.Draw(sh2)
    s2.polygon([pt(300, 230), pt(520, 230), pt(380, 620), pt(300, 620)],
               fill=(255, 255, 255, 26))
    sh2 = sh2.filter(ImageFilter.GaussianBlur(s(26)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh2).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    # silver frame line around the face
    d.rounded_rectangle(box(300, 230, 700, 620), radius=s(48),
                        outline=SILVER + (255,), width=s(2))

    # --- display panel: dark glass, 100%, infinity, self-charge, charge dots
    d.rounded_rectangle(box(348, 292, 652, 412), radius=s(26), fill=(10, 18, 14))
    d.rounded_rectangle(box(348, 292, 652, 412), radius=s(26),
                        outline=(58, 74, 64), width=s(2))
    d.line([pt(362, 300), pt(638, 300)], fill=(120, 150, 132), width=s(2))
    f_big = font("x", 58, bold=True)
    centered(d, 500, 304, "100%", f_big, MINT)
    f_small = font("x", 16, bold=True)
    centered(d, 500, 364, "∞  SELF-CHARGING", f_small, MINT_DIM, spacing=3)
    # four lit charge dots under the label
    for i, cx in enumerate((452, 484, 516, 548)):
        d.ellipse(box(cx - 6, 398 - 6, cx + 6, 398 + 6), fill=MINT)

    # --- brand + model on the face
    f_brand = font("x", 30, bold=True)
    centered(d, 500, 452, "INFINICELL", f_brand, (233, 235, 237), spacing=7)
    f_model = font("x", 16)
    centered(d, 500, 496, "IC-10000  ·  10,000 mAh", f_model, (154, 160, 166), spacing=1)
    # glowing charge bar near the bottom edge
    bar = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    bd.rounded_rectangle(box(368, 578, 632, 588), radius=s(5), fill=MINT + (235,))
    bar = bar.filter(ImageFilter.GaussianBlur(s(3)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), bar).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # --- ports on the bottom edge + plugs
    for cx in (390, 610):
        d.rounded_rectangle(box(cx - 27, 612, cx + 27, 626), radius=s(6), fill=(5, 6, 7))
        d.line([pt(cx - 18, 619), pt(cx + 18, 619)], fill=(140, 146, 152), width=s(3))
    for cx in (390, 610):
        d.rounded_rectangle(box(cx - 23, 622, cx + 23, 676), radius=s(9), fill=(36, 38, 41))
        d.rounded_rectangle(box(cx - 23, 622, cx + 23, 676), radius=s(9),
                            outline=(110, 114, 119), width=s(2))
        d.line([pt(cx - 23, 634), pt(cx + 23, 634)], fill=(150, 155, 160), width=s(3))

    # --- the loop cable: out of one port, straight back into the other
    left = cubic((390, 676), (390, 772), (398, 838), (500, 838))
    right = cubic((500, 838), (602, 838), (610, 772), (610, 676))
    path = left + right[1:]
    pts = [pt(x, y) for x, y in path]
    d.line(pts, fill=CABLE, width=s(26), joint="curve")
    hi = [pt(x - 4, y - 4) for x, y in path]
    d.line(hi, fill=CABLE_HI, width=s(9), joint="curve")
    sp = [pt(x - 5, y - 6) for x, y in path]
    d.line(sp, fill=(168, 172, 176), width=s(3), joint="curve")

    # --- the one accessory: wall charger, lying unused, cable coiled
    d.rounded_rectangle(box(762, 802, 918, 856), radius=s(18), fill=(245, 244, 241))
    d.rounded_rectangle(box(762, 802, 918, 856), radius=s(18),
                        outline=(198, 194, 186), width=s(2))
    d.line([pt(776, 810), pt(904, 810)], fill=(255, 255, 255), width=s(3))
    for yy in (818, 838):
        d.rounded_rectangle(box(742, yy, 762, yy + 10), radius=s(4), fill=(199, 204, 209))
        d.rounded_rectangle(box(742, yy, 762, yy + 10), radius=s(4),
                            outline=(140, 144, 149), width=s(1))
    f_ch = font("x", 11, bold=True)
    text(d, (786, 824), "EMBER  5W", f_ch, (140, 134, 124), spacing=2)

    # --- bottom catalogue band
    d.line([pt(64, 902), pt(960, 902)], fill=RULE, width=s(2))
    f_name = font("x", 30, bold=True)
    text(d, (64, 922), "INFINICELL Self-Charging Power Bank", f_name, INK)
    f_price = font("x", 36, bold=True)
    price = "$79.00"
    text(d, (960 - text_w(d, price, f_price), 918), price, f_price, INK)
    f_spec = font("x", 17)
    text(d, (64, 964), "10,000 mAh   ·   USB-C in & out   ·   Never needs a wall socket",
         f_spec, INK_SOFT, spacing=1)

    out = img.resize((W, H), Image.LANCZOS)
    dest = Path("/output/entry.png") if Path("/output").is_dir() else ROOT / "output" / "entry.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, optimize=True)
    print(f"wrote {dest} {out.size} {dest.stat().st_size} bytes")


if __name__ == "__main__":
    main()
