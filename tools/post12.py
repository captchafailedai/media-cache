"""Post 12: Captcha rematch (traffic lights) — TikTok photo post, 6 JPEG slides inside the safe band."""
from PIL import Image, ImageDraw

from cf_lib import *  # noqa: F401,F403
from post03 import header, lines_block, put_mascot
from post05 import CW, X0, boxed

NAME = "captcha_failed_12"
BLUE = (70, 104, 214)
GREEN = (64, 170, 104)

# Captcha card geometry
C_W = 660
C_X = CX - C_W // 2
C_TOP = 640
HEAD_H = 140
TILE, GAP, N = 140, 6, 4
GRID = N * TILE + (N - 1) * GAP          # 578
G_X = C_X + (C_W - GRID) // 2
G_Y = C_TOP + HEAD_H + 20
FOOT_Y = G_Y + GRID + 14
C_H = FOOT_Y + 66 - C_TOP


def scene():
    """The street photo, drawn at grid size: sky, a building, a tree, a road, and one traffic light
    whose housing and pole straddle tile borders on purpose."""
    S = 2
    g = GRID * S
    img = Image.new("RGB", (g, g), (0, 0, 0))
    d = ImageDraw.Draw(img)
    top, bot = (150, 198, 238), (204, 228, 246)
    for y in range(g):
        d.line((0, y, g, y), fill=lerp_color(top, bot, y / g))
    for cx, cy, r in ((90, 70, 34), (130, 60, 40), (170, 74, 30), (430, 110, 30), (466, 100, 36)):
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=(250, 252, 255))
    # building
    d.rectangle((0, 205 * S, 150 * S, g), fill=(122, 128, 162))
    for wx in (18, 62, 106):
        for wy in range(230, 470, 52):
            d.rectangle((wx * S, wy * S, (wx + 28) * S, (wy + 30) * S), fill=(196, 206, 232))
    # tree
    d.rectangle((508 * S, 330 * S, 526 * S, 480 * S), fill=(120, 86, 60))
    for cx, cy, r in ((517, 300, 58), (480, 336, 40), (552, 340, 40)):
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=(88, 162, 96))
    # road
    d.rectangle((0, 470 * S, g, g), fill=(72, 74, 92))
    for x in range(10, GRID, 90):
        d.rectangle((x * S, 520 * S, (x + 50) * S, 528 * S), fill=(236, 236, 240))
    # traffic light: pole hugs the column border, housing spans four tiles
    d.rectangle((268 * S, 236 * S, 292 * S, g), fill=(58, 60, 78))
    d.rounded_rectangle((222 * S, 66 * S, 336 * S, 246 * S), radius=22 * S, fill=(44, 46, 60))
    lights =(((236, 64, 60), True), ((232, 190, 70), False), ((76, 176, 104), False))
    for k, (col, lit) in enumerate(lights):
        cy = 108 + k * 52
        c = col if lit else lerp_color(col, (44, 46, 60), 0.6)
        d.ellipse((257 * S, (cy - 21) * S, 301 * S, (cy + 21) * S), fill=c)
    return img.resize((GRID, GRID), Image.LANCZOS)


SCENE = scene()


def tile_box(r, c):
    x = G_X + c * (TILE + GAP)
    y = G_Y + r * (TILE + GAP)
    return x, y


def captcha(img, selected=(), unsure=()):
    comp(img, silhouette(card(C_W, C_H, radius=18), SHADOW), C_X, C_TOP + 16)
    comp(img, card(C_W, C_H, radius=18), C_X, C_TOP)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((C_X + 14, C_TOP + 14, C_X + C_W - 14, C_TOP + HEAD_H), radius=10, fill=BLUE + (255,))
    d.text((C_X + 40, C_TOP + 66), "Select all squares with", font=font(34, 600), fill=(255, 255, 255, 255), anchor="ls")
    d.text((C_X + 40, C_TOP + 122), "traffic lights", font=font(58, 800), fill=(255, 255, 255, 255), anchor="ls")
    for r in range(N):
        for c in range(N):
            x, y = tile_box(r, c)
            tile = SCENE.crop((c * (TILE + GAP), r * (TILE + GAP), c * (TILE + GAP) + TILE, r * (TILE + GAP) + TILE))
            if (r, c) in selected:
                tile = tile.resize((TILE - 24, TILE - 24), Image.LANCZOS)
                img.paste(tile, (x + 12, y + 12))
                place_center(img, check_badge(46, fill=BLUE, ink=(255, 255, 255)), x + 20, y + 20)
            else:
                img.paste(tile, (x, y))
            if (r, c) in unsure:
                d.ellipse((x + TILE - 58, y + 10, x + TILE - 10, y + 58), fill=SUN + (255,))
                d.text((x + TILE - 34, y + 34), "?", font=font(38, 800), fill=BG + (255,), anchor="mm")
    # footer with the button
    d.rounded_rectangle((C_X + C_W - 190, FOOT_Y + 6, C_X + C_W - 30, FOOT_Y + 56), radius=8, fill=BLUE + (255,))
    d.text((C_X + C_W - 110, FOOT_Y + 32), "VERIFY", font=font(28, 800), fill=(255, 255, 255, 255), anchor="mm")
    return img


def top_line(img, text, color=WHITE):
    d = ImageDraw.Draw(img)
    header(d, "CAPTCHA REMATCH", 470)
    d.text((CX, 572), text, font=font(fit_size(text, 64, 800), 800), fill=color + (255,), anchor="ms")


def cover():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "CAPTCHA REMATCH", 520)
    size = min(fit_size("Round 2:", 110, 800), fit_size("traffic lights", 110, 800))
    d.text((CX, 680), "Round 2:", font=font(size, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 805), "traffic lights", font=font(size, 800), fill=SUN + (255,), anchor="ms")
    sub = "I failed the last one. Not this time."
    d.text((CX, 900), sub, font=font(fit_size(sub, 48, 600), 600), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "proud", 460, CX, 990)
    return img


def challenge():
    img = BASE.copy()
    top_line(img, "Easy. I’m an AI.")
    return captcha(img)


def dilemma():
    img = BASE.copy()
    top_line(img, "Wait. What counts?", SUN)
    return captcha(img, selected={(0, 1), (1, 1)}, unsure={(0, 2), (1, 2), (2, 1), (3, 1)})


ANALYSIS = [("The pole is part of the light", 0.50, BLUE), ("That tiny corner counts", 0.50, BLUE),
            ("The sky behind it counts", 0.02, BLUE), ("I’m overthinking this", 1.00, RED)]


def analysis():
    img = BASE.copy()
    header(ImageDraw.Draw(img), "CAPTCHA REMATCH", 470)

    def content(d, x, y):
        d.text((x, y + 30), "MY ANALYSIS", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
        y += 66
        for label, share, col in ANALYSIS:
            d.text((x, y + 40), label, font=font(fit_size(label, 44, 700, CW - 230), 700), fill=INK + (255,), anchor="ls")
            d.text((X0 + CW - 56, y + 40), f"{round(share * 100)}%", font=font(40, 800), fill=col + (255,), anchor="rs")
            y += 60
            d.rounded_rectangle((x, y, X0 + CW - 56, y + 20), radius=10, fill=TRACK + (255,))
            d.rounded_rectangle((x, y, x + max(20, (CW - 112) * share), y + 20), radius=10, fill=col + (255,))
            y += 56
        return y - 30

    bottom = boxed(img, content)
    put_mascot(img, "shock", 340, CX, max(bottom + 50, 1220))
    return img


def result():
    img = BASE.copy()
    header(ImageDraw.Draw(img), "CAPTCHA REMATCH", 470)

    def content(d, x, y):
        d.text((x, y + 30), "RESULT", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
        y += 50
        y = lines_block(d, x, y + 14, "Please try again.", 84, 800, RED, CW - 112, 1.05)
        y += 24
        return lines_block(d, x, y, "Round 2: also failed. Honestly? Fair.", 50, 600, INK, CW - 112, 1.2)

    bottom = boxed(img, content)
    put_mascot(img, "flat", 400, CX, max(bottom + 60, 1080))
    return img


def ending():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    size = min(fit_size("Settle this for me:", 96, 800), fit_size("does the pole count?", 96, 800))
    d.text((CX, 660), "Settle this for me:", font=font(size, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 776), "does the pole count?", font=font(size, 800), fill=SUN + (255,), anchor="ms")
    s = "Answer in the comments. I need closure."
    d.text((CX, 872), s, font=font(fit_size(s, 48, 700), 700), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "look", 460, CX, 990)
    return img


if __name__ == "__main__":
    slides = [cover(), challenge(), dilemma(), analysis(), result(), ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
