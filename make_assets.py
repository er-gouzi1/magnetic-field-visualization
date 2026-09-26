from PIL import Image, ImageDraw, ImageFont
import math
import os

OUT = "assets"
os.makedirs(OUT, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

RED = (217, 54, 62)
BLUE = (47, 111, 237)
METAL = (91, 100, 114)
SILVER = (233, 236, 242)
INK = (45, 45, 52)
WHITE = (255, 255, 255)


def trim_transparent(img, pad=6):
    bbox = img.getchannel("A").getbbox()
    if bbox is None:
        return img
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(img.width, r + pad)
    b = min(img.height, b + pad)
    return img.crop((l, t, r, b))


def bar_magnet():
    W, H = 960, 360
    img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    mw, mh = 600, 140
    x0 = (W - mw) // 2
    y0 = (H - mh) // 2
    x1 = x0 + mw
    y1 = y0 + mh
    mid = (x0 + x1) // 2

    d.rectangle([x0, y0, mid, y1], fill=RED)
    d.rectangle([mid, y0, x1, y1], fill=BLUE)
    d.rectangle([x0, y0, x1, y1], outline=INK, width=4)
    d.line([mid, y0, mid, y1], fill=INK, width=4)

    font = ImageFont.truetype(FONT_BOLD, 108)
    for letter, cx in [("N", (x0 + mid) // 2), ("S", (mid + x1) // 2)]:
        d.text((cx, (y0 + y1) // 2), letter, font=font, fill=WHITE, anchor="mm")

    path = os.path.join(OUT, "bar_magnet.png")
    trim_transparent(img).save(path)
    print("saved", path)


def horseshoe_magnet():
    W, H = 760, 580
    img = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    cx, cy = W // 2, 320
    r_out, r_in = 195, 102
    y_top, pole_h = 70, 80
    y_pole = y_top + pole_h

    def arc(r, a0, a1, steps=96):
        pts = []
        for i in range(steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        return pts

    # Horseshoe opening upward: bend at the bottom, two arms pointing up.
    left_half = (
        [(cx - r_out, y_top), (cx - r_out, cy)]
        + arc(r_out, 180, 270)
        + [(cx, cy + r_in)]
        + arc(r_in, 270, 180)
        + [(cx - r_in, y_top)]
    )
    right_half = (
        [(cx + r_out, y_top), (cx + r_out, cy)]
        + arc(r_out, 0, -90)
        + [(cx, cy + r_in)]
        + arc(r_in, -90, 0)
        + [(cx + r_in, y_top)]
    )
    d.polygon(left_half, fill=RED)
    d.polygon(right_half, fill=BLUE)

    # Silver pole faces at the two arm ends.
    d.rectangle([cx - r_out, y_top, cx - r_in, y_pole], fill=SILVER)
    d.rectangle([cx + r_in, y_top, cx + r_out, y_pole], fill=SILVER)
    d.line([(cx - r_out, y_pole), (cx - r_in, y_pole)], fill=INK, width=3)
    d.line([(cx + r_in, y_pole), (cx + r_out, y_pole)], fill=INK, width=3)

    outline = (
        [(cx - r_out, y_top), (cx - r_out, cy)]
        + arc(r_out, 180, 360)
        + [(cx + r_out, y_top), (cx + r_in, y_top), (cx + r_in, cy)]
        + arc(r_in, 360, 180)
        + [(cx - r_in, y_top), (cx - r_out, y_top)]
    )
    d.line(outline, fill=INK, width=4, joint="curve")

    font = ImageFont.truetype(FONT_BOLD, 58)
    lx = cx - (r_out + r_in) // 2
    rx = cx + (r_out + r_in) // 2
    ly = (y_top + y_pole) // 2
    d.text((lx, ly), "N", font=font, fill=INK, anchor="mm")
    d.text((rx, ly), "S", font=font, fill=INK, anchor="mm")

    path = os.path.join(OUT, "horseshoe_magnet.png")
    trim_transparent(img).save(path)
    print("saved", path)


if __name__ == "__main__":
    bar_magnet()
    horseshoe_magnet()
