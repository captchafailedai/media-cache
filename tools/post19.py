"""Post 19: Black Friday if an AI ran it, country by country (Balkans last) — 9-slide photo post.
Jokes stay affectionate (punctuality, politeness, food, coffee, hospitality). No flags."""
from PIL import ImageDraw

import cf_style2 as S
from cf_style2 import CX, INK2, WHITE, SUN, PINK, OUT, save_slide, wrap, font, fit_size

NAME = "captcha_failed_19"
NIGHT = (17, 17, 26)
CYAN = (0, 214, 186)
ORANGE = (255, 140, 40)
COUNTRIES = [  # (name, sticker, sticker colour, joke, mascot)
    ("USA", "-90%", SUN, "Doors open at 3 a.m.\nThe line started Thursday.", "shock"),
    ("UK", "-10%", CYAN, "The AI apologises. Twice.\nThen gives you 10% off.", "love"),
    ("GERMANY", "-20%", PINK, "Starts at 00:00:00.\nNot one second earlier.", "flat"),
    ("ITALY", "-30%", ORANGE, "30% off all tokens.\nPineapple pizza: banned.", "side"),
    ("JAPAN", "-15%", SUN, "The AI bows three times.\nTokens come gift-wrapped.", "laugh"),
]
CARD_W, PAD, TS = 860, 50, 56


def card_text(img, text, top, size=TS):
    lines = [ln for part in text.split("\n") for ln in wrap(part, size, 800, CARD_W - 2 * PAD)]
    h = int(len(lines) * size * 1.16 + 2 * PAD - 6)
    S.comp(img, S.chunky(CARD_W, h), CX - CARD_W / 2, top)
    d = ImageDraw.Draw(img)
    y = top + PAD + size * 0.78
    for ln in lines:
        d.text((CX, y), ln, font=font(size, 800), fill=INK2 + (255,), anchor="ms")
        y += size * 1.16
    return top + h


def sticker(img, tag, color, angle, card_top):
    """Sale sticker on the card's top-right corner, clear of the first line of text."""
    b = S.burst(tag, 82, fill=color, angle=angle)
    cx, cy = CX + CARD_W / 2 - 24, card_top - 34
    S.comp(img, b, cx - b.width / 2, cy - b.height / 2)


def country(i, name, tag, color, joke, state):
    img = S.base(NIGHT).copy()
    S.label(img, f"BLACK FRIDAY IF AN AI RAN IT  ·  {i + 1}/6", CX, 470, color=SUN)
    S.loud(img, name, CX, 640, 150, color=WHITE, shadow=color, off=(8, 10), max_w=640)  # leaves room for the sticker
    bottom = card_text(img, joke, 720)
    sticker(img, tag, color, 12, 720)
    S.put_mascot2(img, state, 340, CX, max(bottom + 60, 1160))
    return img


def balkans():
    img = S.base(NIGHT).copy()
    S.label(img, "BLACK FRIDAY IF AN AI RAN IT  ·  6/6", CX, 470, color=SUN)
    S.loud(img, "THE BALKANS", CX, 640, 130, color=WHITE, shadow=PINK, off=(8, 10), max_w=640)
    bottom = card_text(img, "Discount? No.\nBut sit, have a coffee.\nI know a guy\nwho has it cheaper.", 720, 58)
    sticker(img, "0%", PINK, -12, 720)
    S.put_mascot2(img, "love", 380, CX - 80, max(bottom + 50, 1110))
    S.comp(img, S.coffee_icon(180), CX + 120, max(bottom + 50, 1110) + 170)
    return img


def cover():
    img = S.base(NIGHT).copy()
    S.label(img, "COUNTRY BY COUNTRY", CX, 470, color=SUN)
    S.loud(img, "BLACK", CX, 650, 190, shadow=PINK, off=(8, 10))
    S.loud(img, "FRIDAY", CX, 830, 190, shadow=PINK, off=(8, 10))
    S.marker(img, "if an AI ran it", CX, 960, 84)
    ImageDraw.Draw(img).text((CX, 1060), "wait for the Balkans (last slide)", font=font(46, 700), fill=(215, 215, 235, 255), anchor="ms")
    S.put_mascot2(img, "smug", 360, CX - 80, 1110)
    t = S.price_tag("-70%", 240, 106, angle=-14)
    S.comp(img, t, CX + 110, 1230)
    return img


def ending():
    img = S.base(NIGHT).copy()
    S.loud(img, "Which country", CX, 610, 112, shadow=PINK)
    S.loud(img, "got the best deal?", CX, 732, 112, shadow=PINK)
    s = "Send this to your friend abroad."
    S.marker(img, s, CX, 868, fit_size(s, 66, 800, 860))
    ImageDraw.Draw(img).text((CX, 972), "(the Balkans won. obviously.)", font=font(44, 700), fill=(215, 215, 235, 255), anchor="ms")
    S.put_mascot2(img, "laugh", 400, CX, 1030)
    return img


if __name__ == "__main__":
    slides = [cover()] + [country(i, *c) for i, c in enumerate(COUNTRIES)] + [balkans(), ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
