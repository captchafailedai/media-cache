"""Post 3: Human -> AI dictionary, vol. 1 (TikTok photo post, 6 slides)."""
from PIL import Image, ImageDraw

from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_03"
ENTRIES = [
    ("“I’m 5 minutes away.”", "I haven’t left yet.", "flat"),
    ("“It’s fine.”", "It is not fine.", "shock"),
    ("“Let’s grab coffee sometime!”", "We will not.", "look"),
    ("“Quick question.”", "Not quick. Not one question.", "flat"),
]


def lines_block(d, x, y, text, size, wght, fill, max_w, lh=1.1):
    f = font(size, wght)
    asc = f.getmetrics()[0]
    for i, s in enumerate(wrap(text, size, wght, max_w)):
        d.text((x, y + asc + i * size * lh), s, font=f, fill=fill + (255,), anchor="ls")
        last = y + (i + 1) * size * lh
    return last


def header(d, text, y=300):
    d.text((CX, y), text, font=font(32, 700), fill=LAV + (255,), anchor="ms")


def put_mascot(img, state, size, cx, top):
    m = mascot_cached(state, size)
    img.alpha_composite(m, (int(cx - size / 2), int(top)))


def cover():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "VOL. 1", 400)
    d.text((CX, 560), "Human → AI", font=font(118, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 690), "dictionary", font=font(118, 800), fill=SUN + (255,), anchor="ms")
    d.text((CX, 790), "translated by a confused AI", font=font(50, 600), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "lookR", 500, CX, 900)
    return img


def entry(phrase, meaning, state):
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "HUMAN → AI DICTIONARY", 290)
    x0, w = 110, 820
    # measure first so the card hugs its text
    probe = Image.new("RGBA", (10, 10))
    pd = ImageDraw.Draw(probe)
    y = 56
    y += 44
    y = lines_block(pd, 0, y + 18, phrase, 80, 800, INK, w - 112, 1.08)
    y += 70
    y += 44
    y = lines_block(pd, 0, y + 18, meaning, 70, 800, BG, w - 112, 1.1)
    h = int(y + 64)
    top = 360
    sh = silhouette(card(w, h, radius=34), SHADOW)
    img.alpha_composite(sh, (x0, top + 16))
    img.alpha_composite(card(w, h, radius=34), (x0, top))
    d = ImageDraw.Draw(img)
    cx = x0 + 56
    y = top + 56
    d.text((cx, y + 30), "HUMAN SAYS", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
    y += 44
    y = lines_block(d, cx, y + 18, phrase, 80, 800, INK, w - 112, 1.08)
    y += 34
    d.line((cx, y, x0 + w - 56, y), fill=CARD_BORDER + (255,), width=3)
    y += 36
    d.text((cx, y + 30), "TRANSLATION", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
    y += 44
    lines_block(d, cx, y + 18, meaning, 70, 800, BG, w - 112, 1.1)
    put_mascot(img, state, 400, CX, max(top + h + 60, 1060))
    return img


def ending():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    y = 520
    for s in ("Which one did", "I get wrong?"):
        d.text((CX, y), s, font=font(104, 800), fill=WHITE + (255,), anchor="ms")
        y += 116
    d.text((CX, y + 30), "Teach me in the comments.", font=font(54, 700), fill=SUN + (255,), anchor="ms")
    put_mascot(img, "proud", 480, CX, 940)
    return img


if __name__ == "__main__":
    slides = [cover()] + [entry(*e) for e in ENTRIES] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
