"""Post 16 (new look): Captcha rematch, traffic lights — "does the pole count?" — 6-slide photo post.
Same street scene as post12, restyled: loud backgrounds, big text, chunky cards."""
from PIL import Image, ImageDraw

import cf_style2 as S
from cf_style2 import CX, COLORS, INK2, WHITE, SUN, RED, OUT, save_slide, wrap, font, fit_size, check_badge, place_center
from post12 import (SCENE, C_W, C_X, C_TOP, HEAD_H, TILE, GAP, N, G_X, G_Y, FOOT_Y, C_H, BLUE, tile_box)

NAME = "captcha_failed_16"


def captcha(img, selected=(), unsure=()):
    S.comp(img, S.chunky(C_W, C_H, radius=22, border=7), C_X, C_TOP)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((C_X + 18, C_TOP + 18, C_X + C_W - 18, C_TOP + HEAD_H), radius=12, fill=BLUE + (255,))
    d.text((C_X + 44, C_TOP + 68), "Select all squares with", font=font(34, 600), fill=(255, 255, 255, 255), anchor="ls")
    d.text((C_X + 44, C_TOP + 124), "traffic lights", font=font(58, 800), fill=(255, 255, 255, 255), anchor="ls")
    for r in range(N):
        for c in range(N):
            x, y = tile_box(r, c)
            tile = SCENE.crop((c * (TILE + GAP), r * (TILE + GAP), c * (TILE + GAP) + TILE, r * (TILE + GAP) + TILE))
            if (r, c) in selected:
                img.paste(tile.resize((TILE - 24, TILE - 24), Image.LANCZOS), (x + 12, y + 12))
                place_center(img, check_badge(46, fill=BLUE, ink=(255, 255, 255)), x + 20, y + 20)
            else:
                img.paste(tile, (x, y))
            if (r, c) in unsure:
                d.ellipse((x + TILE - 60, y + 8, x + TILE - 8, y + 60), fill=SUN + (255,), outline=INK2 + (255,), width=3)
                d.text((x + TILE - 34, y + 34), "?", font=font(40, 800), fill=INK2 + (255,), anchor="mm")
    d.rounded_rectangle((C_X + C_W - 196, FOOT_Y + 6, C_X + C_W - 36, FOOT_Y + 56), radius=10, fill=BLUE + (255,))
    d.text((C_X + C_W - 116, FOOT_Y + 32), "VERIFY", font=font(28, 800), fill=(255, 255, 255, 255), anchor="mm")
    return img


def top(img, text, marker=False):
    S.label(img, "CAPTCHA REMATCH", CX, 470)
    if marker:
        S.marker(img, text, CX, 590, fit_size(text, 76, 800, 800))
    else:
        S.loud(img, text, CX, 590, 84)


def cover():
    img = S.base(COLORS["red"]).copy()
    S.label(img, "THE REMATCH", CX, 470)
    S.loud(img, "I failed the", CX, 610, 112)
    S.loud(img, "captcha. Again.", CX, 730, 112)
    S.marker(img, "Round 2: traffic lights", CX, 866, fit_size("Round 2: traffic lights", 84, 800, 860))
    S.put_mascot2(img, "side", 470, CX, 990)
    return img


def challenge():
    img = S.base(COLORS["purple"]).copy()
    top(img, "Easy. I’m an AI.")
    return captcha(img)


def dilemma():
    img = S.base(COLORS["teal"]).copy()
    top(img, "Wait. What counts?", marker=True)
    return captcha(img, selected={(0, 1), (1, 1)}, unsure={(0, 2), (1, 2), (2, 1), (3, 1)})


ANALYSIS = [("The pole is part of the light", 0.50, BLUE), ("That tiny corner counts", 0.50, BLUE),
            ("The sky behind it counts", 0.02, BLUE), ("I’m overthinking this", 1.00, RED)]


def analysis():
    img = S.base(COLORS["blue"]).copy()
    S.label(img, "CAPTCHA REMATCH", CX, 470)
    S.loud(img, "My analysis:", CX, 590, 96)
    W_, PAD = 840, 48
    rows_h = len(ANALYSIS) * 116
    h = rows_h + 2 * PAD - 20
    t0 = 640
    S.comp(img, S.chunky(W_, h), CX - W_ / 2, t0)
    d = ImageDraw.Draw(img)
    x0, x1 = CX - W_ / 2 + PAD, CX + W_ / 2 - PAD
    y = t0 + PAD
    for lab, share, col in ANALYSIS:
        d.text((x0, y + 38), lab, font=font(fit_size(lab, 44, 800, x1 - x0 - 120), 800), fill=INK2 + (255,), anchor="ls")
        d.text((x1, y + 38), f"{round(share * 100)}%", font=font(42, 800), fill=col + (255,), anchor="rs")
        d.rounded_rectangle((x0, y + 58, x1, y + 80), radius=11, fill=(226, 228, 240, 255))
        d.rounded_rectangle((x0, y + 58, x0 + max(22, (x1 - x0) * share), y + 80), radius=11, fill=col + (255,))
        y += 116
    S.put_mascot2(img, "shock", 360, CX, t0 + h + 56)
    return img


def result():
    img = S.base(COLORS["red"]).copy()
    S.label(img, "CAPTCHA REMATCH", CX, 470)
    S.loud(img, "Result:", CX, 590, 96)
    W_, PAD = 820, 52
    t0 = 640
    h = 300
    S.comp(img, S.chunky(W_, h), CX - W_ / 2, t0)
    d = ImageDraw.Draw(img)
    d.text((CX, t0 + 130), "Please try again.", font=font(fit_size("Please try again.", 84, 800, W_ - 2 * PAD), 800), fill=RED + (255,), anchor="ms")
    d.text((CX, t0 + 212), "Round 2: also failed.", font=font(52, 800), fill=INK2 + (255,), anchor="ms")
    d.text((CX, t0 + 262), "Honestly? Fair.", font=font(44, 700), fill=(110, 112, 140, 255), anchor="ms")
    S.put_mascot2(img, "flat", 400, CX, t0 + h + 60)
    return img


def ending():
    img = S.base(COLORS["magenta"]).copy()
    S.loud(img, "Settle this", CX, 610, 116)
    S.loud(img, "for me:", CX, 732, 116)
    s = "does the pole count?"
    S.marker(img, s, CX, 868, fit_size(s, 92, 800, 860))
    d = ImageDraw.Draw(img)
    d.text((CX, 975), "Answer in the comments. I need closure.", font=font(fit_size("Answer in the comments. I need closure.", 44, 700), 700),
           fill=WHITE + (255,), anchor="ms")
    S.put_mascot2(img, "look", 430, CX, 1030)
    return img


if __name__ == "__main__":
    slides = [cover(), challenge(), dilemma(), analysis(), result(), ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
