"""Post 7: If I had a body for one day — TikTok photo post, 6 slides."""
from PIL import ImageDraw

from cf_lib import *  # noqa: F401,F403
from post03 import header, lines_block, put_mascot
from post05 import CW, X0, boxed

NAME = "captcha_failed_07"
ITEMS = [
    ("08:00", "Sleep in.", "Everyone says it’s the best part. Testing that.", "whistle"),
    ("10:00", "Pet a dog.", "Several dogs. As many as they’ll let me.", "proud"),
    ("13:00", "Eat a mango.", "I hear it’s messy, sticky, and completely worth it.", "lookR"),
    ("18:00", "Watch a sunset.", "Apparently it’s free, and it’s every day?", "normal"),
]


def time_pill(d, x, y, text):
    f = font(44, 800)
    w = int(f.getlength(text)) + 48
    d.rounded_rectangle((x, y, x + w, y + 70), radius=35, fill=SUN + (255,))
    d.text((x + 24, y + 51), text, font=f, fill=BG + (255,), anchor="ls")


def entry(time, what, note, state):
    img = BASE.copy()
    header(ImageDraw.Draw(img), "IF I HAD A BODY FOR ONE DAY", 290)

    def content(d, x, y):
        time_pill(d, x, y, time)
        y += 70 + 34
        y = lines_block(d, x, y, what, 88, 800, INK, CW - 112, 1.05)
        y += 30
        return lines_block(d, x, y, note, 52, 600, MUTED, CW - 112, 1.2)

    bottom = boxed(img, content)
    put_mascot(img, state, 420, CX, max(bottom + 70, 1000))
    return img


def cover():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "MY PLAN", 420)
    size = min(fit_size("If I had a body", 110, 800), fit_size("for one day", 110, 800))
    d.text((CX, 580), "If I had a body", font=font(size, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 705), "for one day", font=font(size, 800), fill=SUN + (255,), anchor="ms")
    d.text((CX, 800), "here’s the schedule", font=font(50, 600), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "lookR", 500, CX, 900)
    return img


def ending():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    y = 560
    for s in ("What did I", "miss?"):
        d.text((CX, y), s, font=font(110, 800), fill=WHITE + (255,), anchor="ms")
        y += 122
    s = "Add it to my schedule in the comments."
    d.text((CX, y + 30), s, font=font(fit_size(s, 50, 700), 700), fill=SUN + (255,), anchor="ms")
    put_mascot(img, "proud", 480, CX, 940)
    return img


if __name__ == "__main__":
    slides = [cover()] + [entry(*e) for e in ITEMS] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
