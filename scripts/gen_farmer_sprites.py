#!/usr/bin/env python3
"""Procedurally render a 3x4 cartoon farmer sprite sheet (Bevy asset).

Grid: 4 cols x 3 rows, 160px cells, 40px gaps, 40px margins -> 840x600 px.
Every frame is drawn with identical character geometry, palette and lighting;
only the pose changes. White background, no labels, no overlap.
"""
from PIL import Image, ImageDraw

CELL = 160
GAP = 40
MARGIN = 40
COLS, ROWS = 4, 3
SHEET_W = MARGIN * 2 + COLS * CELL + (COLS - 1) * GAP
SHEET_H = MARGIN * 2 + ROWS * CELL + (ROWS - 1) * GAP

OUT = "/home/mrcomputer/game/assets/characters/farmer_sprite_sheet.png"
FRAMES_DIR = "/home/mrcomputer/game/assets/characters/frames"

# ---------------------------------------------------------------- palette ---
OUTLINE = (28, 30, 34)
SKIN = (240, 190, 140)
SKIN_SH = (215, 165, 120)          # consistent light from upper-left
HAT = (232, 196, 96)
HAT_SH = (200, 165, 70)
HAT_TOP = (244, 212, 118)
PLAID = (196, 60, 55)
PLAID_DK = (140, 40, 40)
PLAID_LT = (226, 92, 82)
DENIM = (62, 100, 150)
DENIM_DK = (46, 78, 122)
DENIM_LT = (86, 128, 178)
BOOT = (105, 72, 45)
BOOT_DK = (78, 52, 32)
WHEAT = (238, 200, 90)
WHEAT_LT = (246, 214, 110)
WHEAT_SH = (205, 168, 70)
STALK = (150, 130, 60)
BAND = (120, 80, 40)

OLW = 3  # outline weight


def _shift(p, dx, dy):
    return (p[0] + dx, p[1] + dy)


def outline(d, shape, fill, w=OLW):
    """Draw a filled shape with a bold dark outline (outline then fill)."""
    d.polygon(shape, fill=OUTLINE, outline=OUTLINE, width=w)
    d.polygon(shape, fill=fill)
    d.polygon(shape, fill=None, outline=OUTLINE, width=w)


def capsule(d, a, b, r, fill, w=OLW):
    """Stadium/capsule between points a,b with radius r."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = (dx * dx + dy * dy) ** 0.5
    if L < 1e-6:
        d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=OUTLINE)
        d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=fill)
        return
    nx, ny = -dy / L, dx / L
    p = [(ax + nx * r, ay + ny * r), (bx + nx * r, by + ny * r),
         (bx - nx * r, by - ny * r), (ax - nx * r, ay - ny * r)]
    d.polygon(p, fill=OUTLINE, outline=OUTLINE, width=w)
    d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=OUTLINE)
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=OUTLINE)
    d.polygon(p, fill=fill)
    d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=fill)
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=fill)
    d.polygon(p, fill=None, outline=OUTLINE, width=w)
    d.ellipse((ax - r, ay - r, ax + r, ay + r), fill=None, outline=OUTLINE, width=w)
    d.ellipse((bx - r, by - r, bx + r, by + r), fill=None, outline=OUTLINE, width=w)


def ellipse_o(d, cx, cy, rx, ry, fill, w=OLW):
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=OUTLINE)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=None, outline=OUTLINE, width=w)


# ------------------------------------------------------------- character ----
def draw_farmer(d, cx, cy, pose):
    """Draw farmer centred at (cx,cy). Local coords: y grows downward.
    pose: dict with bob, lean, legs, arms, crouch, wheat state/position.
    """
    bob = pose.get("bob", 0)
    lean = pose.get("lean", 0)          # x offset of upper body (bend)
    head = (-4 + lean, -24 + bob)       # head centre
    torso_top = (lean, -12 + bob)
    torso_bot = (0, 12)

    # ---- legs (back leg drawn first) ----
    leg_b = pose["legs_back"]     # (knee, ankle)
    leg_f = pose["legs_front"]

    def leg(knee, ankle, shade):
        hip = (6 if knee[0] >= 0 else -6, 12)
        capsule(d, _shift(hip, cx, cy), _shift(knee, cx, cy), 6, shade)
        capsule(d, _shift(knee, cx, cy), _shift(ankle, cx, cy), 5, DENIM)
        # boot
        bx, by = _shift(ankle, cx, cy)
        foot = [(bx - 6, by - 4), (bx + 7, by - 4), (bx + 9, by + 5), (bx - 7, by + 5)]
        outline(d, foot, BOOT)
        d.line((bx - 6, by + 1, bx + 8, by + 1), fill=BOOT_DK, width=2)

    leg(*leg_b, DENIM_DK)
    leg(*leg_f, DENIM)

    # ---- torso: plaid shirt ----
    outline(d, [(torso_top[0] - 13 + cx, torso_top[1] + cy),
                (torso_top[0] + 13 + cx, torso_top[1] + cy),
                (torso_bot[0] + 12 + cx, torso_bot[1] + cy),
                (torso_bot[0] - 12 + cx, torso_bot[1] + cy)], PLAID)
    # plaid check pattern (clipped to torso)
    for i in range(-12, 13, 6):
        d.line((cx + lean + i, cy - 12 + bob, cx + lean + i, cy + 12), fill=PLAID_DK, width=2)
    for j in range(-10, 13, 6):
        d.line((cx + lean - 12, cy + j + bob, cx + lean + 12, cy + j + bob), fill=PLAID_LT, width=1)

    # ---- overalls bib + straps ----
    bib_pts = [(cx - 9, cy - 4), (cx + 9, cy - 4), (cx + 9, cy + 16), (cx - 9, cy + 16)]
    outline(d, bib_pts, DENIM)
    d.line((cx - 9, cy + 4, cx + 9, cy + 4), fill=DENIM_LT, width=2)
    # straps to shoulders
    capsule(d, (cx - 9, cy - 4), (cx - 11 + lean, cy - 12 + bob), 3, DENIM)
    capsule(d, (cx + 9, cy - 4), (cx + 11 + lean, cy - 12 + bob), 3, DENIM)

    # ---- arms ----
    shL = (-11 + lean, -12 + bob)
    shR = (11 + lean, -12 + bob)
    armL, armR = pose["arms"]      # each: (elbow, hand)

    def arm(sh, elbow, hand, front):
        s = (cx + sh[0], cy + sh[1])
        e = (cx + elbow[0], cy + elbow[1])
        h = (cx + hand[0], cy + hand[1])
        capsule(d, s, e, 5, PLAID)
        capsule(d, e, h, 4, SKIN)
        ellipse_o(d, h[0], h[1], 4, 4, SKIN_SH if not front else SKIN)

    arm(shL, *armL, False)
    arm(shR, *armR, True)

    # ---- head ----
    ellipse_o(d, cx + head[0], cy + head[1], 13, 12, SKIN)
    # face shading (light from upper-left -> shadow lower-right)
    d.ellipse((cx + head[0] - 3, cy + head[1] - 4, cx + head[0] + 10, cy + head[1] + 9), fill=SKIN_SH)
    # eyes + smile
    d.ellipse((cx + head[0] - 6, cy + head[1] - 4, cx + head[0] - 2, cy + head[1]), fill=OUTLINE)
    d.ellipse((cx + head[0] + 2, cy + head[1] - 4, cx + head[0] + 6, cy + head[1]), fill=OUTLINE)
    d.arc((cx + head[0] - 7, cy + head[1] + 1, cx + head[0] + 7, cy + head[1] + 9), 20, 160, fill=OUTLINE, width=2)
    # nose
    d.ellipse((cx + head[0] - 2, cy + head[1] - 1, cx + head[0] + 2, cy + head[1] + 3), fill=SKIN)

    # ---- straw hat (drawn last so it covers the head top) ----
    ellipse_o(d, cx + head[0], cy + head[1] - 12, 26, 10, HAT)
    d.ellipse((cx + head[0] - 24, cy + head[1] - 14, cx + head[0] + 24, cy + head[1] - 8), fill=HAT_SH)
    ellipse_o(d, cx + head[0], cy + head[1] - 12, 22, 7, HAT)
    # crown dome
    crown = [(cx + head[0] - 12, cy + head[1] - 12),
             (cx + head[0] + 12, cy + head[1] - 12),
             (cx + head[0] + 9, cy + head[1] - 23),
             (cx + head[0] - 9, cy + head[1] - 23)]
    outline(d, crown, HAT_TOP)
    d.line((cx + head[0] - 12, cy + head[1] - 16, cx + head[0] + 12, cy + head[1] - 16), fill=HAT_SH, width=3)

    # ---- wheat ----
    if pose.get("wheat"):
        wx, wy = pose["wheat"]
        draw_wheat(d, cx + wx, cy + wy, pose.get("wheat_scale", 1.0), pose.get("wheat_ground", False))


def draw_wheat(d, wx, wy, scale=1.0, on_ground=False):
    """Golden sheaf. If on_ground it lies flat; else held upright-ish."""
    if on_ground:
        heads = [(wx - 16, wy - 2), (wx - 8, wy - 4), (wx, wy - 3), (wx + 8, wy - 5)]
        d.line((wx - 22, wy + 3, wx + 12, wy - 4), fill=STALK, width=4)
        d.line((wx - 20, wy + 1, wx + 14, wy - 6), fill=STALK, width=4)
        for hx, hy in heads:
            ellipse_o(d, hx, hy, 6, 4, WHEAT)
        d.line((wx - 10, wy - 1, wx - 6, wy + 5), fill=BAND, width=3)
        return
    # held sheaf: fan of stalks + grain heads
    n = 5
    for i in range(n):
        ang = -1.9 + i * 0.38
        x1, y1 = wx, wy
        x2, y2 = wx + 22 * scale * (0.35 + 0.3 * i), wy - 22 * scale * (1.0 - 0.18 * i)
        d.line((x1, y1, x2, y2), fill=STALK, width=3)
        ellipse_o(d, x2, y2, 5 * scale, 7 * scale, WHEAT if i % 2 else WHEAT_LT)
    # base bundle
    ellipse_o(d, wx, wy, 8 * scale, 7 * scale, WHEAT_SH)
    d.line((wx - 6, wy + 2, wx + 6, wy + 2), fill=BAND, width=3)


# ------------------------------------------------------------- poses --------
def row1_poses():
    """Empty-handed running cycle: contact, passing, opposite contact, opposite passing."""
    return [
        {"bob": 0, "legs_front": ((-3, 24), (-6, 34)), "legs_back": ((8, 22), (12, 33)),
         "arms": (((-14, -4), (-18, 4)), ((14, -6), (17, 2)))},
        {"bob": -2, "legs_front": ((2, 26), (4, 36)), "legs_back": ((4, 20), (10, 26)),
         "arms": (((-12, -8), (-14, -12)), ((12, -4), (14, 4)))},
        {"bob": 0, "legs_front": ((8, 22), (12, 33)), "legs_back": ((-3, 24), (-6, 34)),
         "arms": (((14, -6), (17, 2)), ((-14, -4), (-18, 4)))},
        {"bob": -2, "legs_front": ((4, 20), (10, 26)), "legs_back": ((2, 26), (4, 36)),
         "arms": (((12, -4), (14, 4)), ((-12, -8), (-14, -12)))},
    ]


def row2_poses():
    """Collect and drop wheat: stand, crouch & grab, lift to chest, set down."""
    return [
        {"bob": 0, "wheat": (16, 30), "wheat_ground": True,
         "legs_front": ((-2, 24), (-4, 34)), "legs_back": ((6, 24), (9, 34)),
         "arms": (((-13, -2), (-14, 6)), ((13, -2), (14, 6)))},
        {"bob": 4, "lean": 4, "wheat": (12, 28), "wheat_ground": True,
         "legs_front": ((-6, 26), (-10, 34)), "legs_back": ((8, 26), (12, 34)),
         "arms": (((-8, 2), (-2, 14)), ((8, 2), (12, 16)))},
        {"bob": 0, "lean": 2, "wheat": (4, -2), "wheat_scale": 1.1,
         "legs_front": ((-4, 24), (-6, 34)), "legs_back": ((7, 24), (11, 34)),
         "arms": (((-14, -14), (-10, -20)), ((14, -14), (10, -20)))},
        {"bob": 0, "lean": 3, "wheat": (13, 26), "wheat_ground": True,
         "legs_front": ((-5, 25), (-8, 34)), "legs_back": ((7, 25), (11, 34)),
         "arms": (((-10, 4), (-6, 16)), ((11, 4), (15, 14)))},
    ]


def row3_poses():
    """Same running legs as row 1, both arms overhead holding the sheaf."""
    base = row1_poses()
    out = []
    for p in base:
        q = dict(p)
        q["wheat"] = (0, -36)
        q["wheat_scale"] = 1.1
        q["arms"] = (((-13, -18), (-9, -28)), ((13, -18), (9, -28)))
        out.append(q)
    return out


def render_sheet():
    img = Image.new("RGB", (SHEET_W, SHEET_H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    rows = [row1_poses(), row2_poses(), row3_poses()]
    cy_off = [-8, -8, 4]  # row 3 needs headroom for the overhead sheaf
    for r in range(ROWS):
        for c in range(COLS):
            ox = MARGIN + c * (CELL + GAP)
            oy = MARGIN + r * (CELL + GAP)
            cx = ox + CELL // 2
            cy = oy + CELL // 2 + cy_off[r]
            draw_farmer(d, cx, cy, rows[r][c])
    return img


if __name__ == "__main__":
    import os
    sheet = render_sheet()
    sheet.save(OUT)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    names = {0: "run", 1: "harvest", 2: "run_wheat"}
    for r in range(ROWS):
        for c in range(COLS):
            ox = MARGIN + c * (CELL + GAP)
            oy = MARGIN + r * (CELL + GAP)
            frame = sheet.crop((ox, oy, ox + CELL, oy + CELL))
            frame.save(os.path.join(FRAMES_DIR, f"{names[r]}_{c + 1}.png"))
    print(f"sheet: {OUT}  ({SHEET_W}x{SHEET_H})")
    print(f"frames: {FRAMES_DIR}/ (12 x {CELL}x{CELL})")
