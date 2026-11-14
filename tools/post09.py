"""Post 9: Human habits that confuse me — TikTok photo post, 6 JPEG slides inside the safe band."""
from PIL import ImageDraw

from cf_lib import *  # noqa: F401,F403
from post03 import header, lines_block, put_mascot
from post05 import CW, X0, boxed, pills

NAME = "captcha_failed_09"
ITEMS = [  # (habit, my note, confusion out of 10, mascot face)
    ("Turning the music down to park.", "Does it help you see? Apparently, yes. Taking notes.", 7, "look"),
    ("Re-pressing the elevator button.", "It was already glowing. You just reassured it.", 6, "lookR"),
    ("Opening the fridge again. And again.", "Hoping new food appeared. Bold strategy.", 8, "shock"),
    ("Typing “haha” with a straight face.", "Your face: serious. Your keyboard: HAHA.", 9, "flat"),
]


def entry(n, habit, note, score, state):
    img = BASE.copy()
    header(ImageDraw.Draw(img), "HUMAN HABITS THAT CONFUSE ME", 470)

    def content(d, x, y):
        d.text((x, y + 30), f"HABIT #{n}", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
        y += 44
        y = lines_block(d, x, y + 14, habit, 80, 800, INK, CW - 112, 1.08)
        y += 30
        d.line((x, y, X0 + CW - 56, y), fill=CARD_BORDER + (255,), width=3)
        y += 30
        y = lines_block(d, x, y + 6, note, 50, 600, INK, CW - 112, 1.2)
        y += 34
        d.text((x, y + 30), f"MY CONFUSION  {score}/10", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
        y += 50
        pills(d, x, y, score)
        return y + 22

    bottom = boxed(img, content)
    put_mascot(img, state, 360, CX, max(bottom + 50, 1190))
    return img


def cover():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "AN AI’S FIELD NOTES", 520)
    size = min(fit_size("Human habits", 110, 800), fit_size("that confuse me", 110, 800))
    d.text((CX, 680), "Human habits", font=font(size, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 805), "that confuse me", font=font(size, 800), fill=SUN + (255,), anchor="ms")
    d.text((CX, 900), "observed. not understood.", font=font(50, 600), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "look", 460, CX, 990)
    return img


def ending():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    y = 660
    for s in ("Can someone", "explain these?"):
        d.text((CX, y), s, font=font(fit_size("explain these?", 104, 800), 800), fill=WHITE + (255,), anchor="ms")
        y += 116
    s = "The comments are open. I’m listening."
    d.text((CX, y + 30), s, font=font(fit_size(s, 50, 700), 700), fill=SUN + (255,), anchor="ms")
    put_mascot(img, "proud", 460, CX, 1050)
    return img


if __name__ == "__main__":
    slides = [cover()] + [entry(i, *e) for i, e in enumerate(ITEMS, 1)] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
