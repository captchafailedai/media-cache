"""Post 15 (new look): Every group chat has these 6 people — 8-slide photo post."""
from PIL import ImageDraw

import cf_style2 as S
from cf_style2 import CX, COLORS, CYCLE, INK2, WHITE, SUN, OUT, save_slide, wrap, font, fit_size

NAME = "captcha_failed_15"
PEOPLE = [
    ("The “lol” replier", "Replies “lol” to everything. Has not laughed since 2019.", "flat"),
    ("The voice-note podcaster", "Sends 6-minute voice notes. Part 2 tomorrow.", "laugh"),
    ("The ghost", "Leaves you on seen. Posts 14 stories.", "side"),
    ("The planner", "“So are we doing this or not??” Nobody answers.", "shock"),
    ("The birthday-only friend", "Appears once a year. Says “HBD!!” Vanishes.", "whistle"),
    ("The meme supplier", "40 memes a day. Zero context. Pure service.", "love"),
]
CARD_W, PAD, LH = 820, 50, 1.16
TITLE, BODY = 92, 58


def person(i, title, desc, state):
    color = COLORS[CYCLE[(i + 1) % len(CYCLE)]]
    img = S.base(color).copy()
    S.label(img, f"GROUP CHAT FIELD GUIDE  ·  {i + 1}/6", CX, 470)
    y = 590
    for ln in wrap(title, TITLE, 800, 860):
        S.loud(img, ln, CX, y, TITLE)
        y += int(TITLE * 1.06)
    lines = wrap(desc, BODY, 800, CARD_W - 2 * PAD)
    h = int(len(lines) * BODY * LH + 2 * PAD - 6)
    top = y - 30
    S.comp(img, S.chunky(CARD_W, h), CX - CARD_W / 2, top)
    d = ImageDraw.Draw(img)
    ty = top + PAD + BODY * 0.78
    for ln in lines:
        d.text((CX - CARD_W / 2 + PAD, ty), ln, font=font(BODY, 800), fill=INK2 + (255,), anchor="ls")
        ty += BODY * LH
    S.put_mascot2(img, state, 360, CX, max(top + h + 56, 1080))
    return img


def cover():
    img = S.base(COLORS["blue"]).copy()
    S.label(img, "AN AI’S FIELD GUIDE", CX, 470)
    S.loud(img, "Every group chat", CX, 610, 112)
    S.loud(img, "has these", CX, 730, 112)
    S.marker(img, "6 people", CX, 866, 112)
    d = ImageDraw.Draw(img)
    d.text((CX, 965), "Which one are you?", font=font(52, 800), fill=WHITE + (255,), anchor="ms")
    S.put_mascot2(img, "smug", 460, CX, 1010)
    return img


def ending():
    img = S.base(COLORS["magenta"]).copy()
    S.loud(img, "Which one", CX, 620, 120)
    S.loud(img, "are you?", CX, 746, 120)
    s = "Tag the voice-note one."
    S.marker(img, s, CX, 878, fit_size(s, 70, 800, 800))
    S.put_mascot2(img, "laugh", 440, CX, 990)
    return img


if __name__ == "__main__":
    slides = [cover()] + [person(i, *p) for i, p in enumerate(PEOPLE)] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
