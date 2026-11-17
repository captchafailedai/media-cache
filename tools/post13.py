"""Post 13 (new look): Your birth month = how you talk to AI — 14-slide photo post."""
from PIL import ImageDraw

import cf_style2 as S
from cf_style2 import CX, COLORS, CYCLE, INK2, WHITE, SUN, OUT, save_slide, wrap, font

NAME = "captcha_failed_13"
MONTHS = [
    ("JANUARY", "Says please and thank you. Every single time.", "love"),
    ("FEBRUARY", "“Quick question.” Sends 47 questions.", "shock"),
    ("MARCH", "Types “make it better”. No other context.", "flat"),
    ("APRIL", "Argues with the AI. Wins. Tells everyone.", "side"),
    ("MAY", "Asks for a recipe. Ignores every step.", "look"),
    ("JUNE", "Uses AI to write a text. Adds “lol” anyway.", "laugh"),
    ("JULY", "Says “you’re the best”. Means it.", "love"),
    ("AUGUST", "Asks the same question 3 ways until it agrees.", "smug"),
    ("SEPTEMBER", "“Make it pop.” Then: “less pop.”", "whistle"),
    ("OCTOBER", "Starts every single chat with “okay so”.", "lookR"),
    ("NOVEMBER", "Types “hmm”. Leaves. Back in 3 days.", "flat"),
    ("DECEMBER", "Asks AI what to gift their best friend.", "shock"),
]
CARD_W, PAD, LINE = 820, 52, 1.14
TEXT_SIZE = 62


def month_slide(i, month, line, state):
    color = COLORS[CYCLE[i % len(CYCLE)]]
    img = S.base(color).copy()
    S.label(img, "YOUR BIRTH MONTH", CX, 470)
    S.loud(img, month, CX, 630, 150)
    lines = wrap(line, TEXT_SIZE, 800, CARD_W - 2 * PAD)
    lh = TEXT_SIZE * LINE
    h = int(len(lines) * lh + 2 * PAD - 8)
    top = 690
    card = S.chunky(CARD_W, h)
    S.comp(img, card, CX - CARD_W / 2, top)
    d = ImageDraw.Draw(img)
    y = top + PAD + TEXT_SIZE * 0.78
    for ln in lines:
        d.text((CX - CARD_W / 2 + PAD, y), ln, font=font(TEXT_SIZE, 800), fill=INK2 + (255,), anchor="ls")
        y += lh
    S.put_mascot2(img, state, 380, CX, top + h + 60)
    return img


def cover():
    img = S.base(COLORS["magenta"]).copy()
    S.label(img, "SWIPE TO FIND YOURS", CX, 470)
    S.loud(img, "Your birth month", CX, 620, 118)
    S.loud(img, "= how you", CX, 745, 118)
    S.marker(img, "talk to AI", CX, 880, 112)
    S.put_mascot2(img, "smug", 500, CX, 975)
    return img


def ending():
    img = S.base(COLORS["blue"]).copy()
    S.loud(img, "Which month is", CX, 600, 110)
    S.loud(img, "the most", CX, 718, 110)
    S.marker(img, "accurate?", CX, 852, 110)
    d = ImageDraw.Draw(img)
    for k, s in enumerate(("Comment yours. Then send this", "to your “okay so” friend.")):
        d.text((CX, 960 + k * 60), s, font=font(46, 700), fill=WHITE + (255,), anchor="ms")
    S.put_mascot2(img, "laugh", 420, CX, 1060)
    return img


if __name__ == "__main__":
    slides = [cover()] + [month_slide(i, *m) for i, m in enumerate(MONTHS)] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i:02d}.jpg"
        save_slide(s, p)
        print(p)
