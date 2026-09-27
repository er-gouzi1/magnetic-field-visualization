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


def scaled(values, scale):
    return tuple(round(value * scale) for value in values)


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

    path = os.path.join(OUT, "horseshoe_magnet.png")
    trim_transparent(img).save(path)
    print("saved", path)


def solenoid_schematic():
    scale = 4
    W, H = 960, 500
    img = Image.new("RGBA", (W * scale, H * scale), (255, 255, 255, 0))
    d = ImageDraw.Draw(img)

    line = (82, 87, 94, 255)
    body_left, body_right = 118, 810
    body_top, body_bottom = 88, 268
    body_cy = (body_top + body_bottom) // 2
    end_rx, end_ry = 25, (body_bottom - body_top) // 2

    # Light grey cylinder with a restrained lower shade, matching the clean
    # line-art look of a textbook current-carrying solenoid.
    d.rectangle(
        scaled((body_left, body_top, body_right, body_bottom), scale),
        fill=(235, 236, 238, 255),
    )
    d.rectangle(
        scaled((body_left, body_cy + 38, body_right, body_bottom), scale),
        fill=(201, 204, 208, 255),
    )
    d.ellipse(
        scaled((body_left - end_rx, body_top, body_left + end_rx, body_bottom), scale),
        fill=(247, 248, 249, 255),
    )
    d.ellipse(
        scaled((body_right - end_rx, body_top, body_right + end_rx, body_bottom), scale),
        fill=(207, 210, 214, 255),
    )

    # Project a real helix around the cylinder. Rear segments are laid down
    # first and partly hidden by the cylinder; front segments are added later.
    coil_start, coil_end = body_left + 34, body_right - 34
    turn_count = 9
    samples_per_turn = 72
    coil_pitch = (coil_end - coil_start) / turn_count
    coil_ry = 108
    front_segments = []
    rear_segments = []
    front_segment = []
    rear_segment = []

    for step in range(turn_count * samples_per_turn + 1):
        theta = math.tau * step / samples_per_turn
        x = coil_start + coil_pitch * step / samples_per_turn
        y = body_cy - coil_ry * math.cos(theta)
        point = (round(x * scale), round(y * scale))
        depth = math.sin(theta)
        if depth >= 0:
            if rear_segment:
                rear_segments.append(rear_segment)
                rear_segment = []
            front_segment.append(point)
        else:
            if front_segment:
                front_segments.append(front_segment)
                front_segment = []
            rear_segment.append(point)

    if front_segment:
        front_segments.append(front_segment)
    if rear_segment:
        rear_segments.append(rear_segment)

    for segment in rear_segments:
        d.line(
            segment,
            fill=(166, 170, 176, 255),
            width=8 * scale,
            joint="curve",
        )
        d.line(
            segment,
            fill=(220, 222, 226, 255),
            width=2 * scale,
            joint="curve",
        )

    # Repaint the cylinder over the rear winding so only the portions that
    # pass above or below the body remain visible.
    d.rectangle(
        scaled((body_left, body_top, body_right, body_bottom), scale),
        fill=(235, 236, 238, 255),
    )
    d.rectangle(
        scaled((body_left, body_cy + 38, body_right, body_bottom), scale),
        fill=(201, 204, 208, 255),
    )
    d.ellipse(
        scaled((body_left - end_rx, body_top, body_left + end_rx, body_bottom), scale),
        fill=(247, 248, 249, 255),
    )
    d.ellipse(
        scaled((body_right - end_rx, body_top, body_right + end_rx, body_bottom), scale),
        fill=(207, 210, 214, 255),
    )

    # Cylinder outline, left opening, and right rounded end.
    d.line(
        [
            (body_left * scale, body_top * scale),
            (body_right * scale, body_top * scale),
        ],
        fill=line,
        width=4 * scale,
    )
    d.line(
        [
            (body_left * scale, body_bottom * scale),
            (body_right * scale, body_bottom * scale),
        ],
        fill=line,
        width=4 * scale,
    )
    d.ellipse(
        scaled((body_left - end_rx, body_top, body_left + end_rx, body_bottom), scale),
        outline=line,
        width=4 * scale,
    )
    d.arc(
        scaled((body_right - end_rx, body_top, body_right + end_rx, body_bottom), scale),
        -90,
        90,
        fill=line,
        width=4 * scale,
    )

    for segment in front_segments:
        d.line(
            segment,
            fill=(70, 76, 84, 255),
            width=9 * scale,
            joint="curve",
        )
        d.line(
            segment,
            fill=(146, 152, 160, 255),
            width=3 * scale,
            joint="curve",
        )

    img = img.resize((W, H), Image.Resampling.LANCZOS)
    path = os.path.join(OUT, "solenoid_schematic.png")
    trim_transparent(img).save(path)
    print("saved", path)


if __name__ == "__main__":
    bar_magnet()
    horseshoe_magnet()
    solenoid_schematic()
