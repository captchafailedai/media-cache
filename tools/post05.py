"""Post 5: Rating human inventions (as an AI) — TikTok photo post, 6 slides."""
from PIL import Image, ImageDraw

from cf_lib import *  # noqa: F401,F403
from post03 import header, lines_block, put_mascot

NAME = "captcha_failed_05"
ITEMS = [
    ("Sleep", 10, "Everyone talks about it. Must be incredible.", "whistle"),
    ("Coffee", 9, "Apparently it’s a personality.", "lookR"),
    ("Socks", 6, "They vanish one at a time. Suspicious.", "look"),
    ("Reply all", 2, "Powerful. Dangerous. Use with care.", "shock"),
]
X0, CW, TOP = 110, 820, 520  # content stays inside the TikTok safe band (cf_lib SAFE_*)


def pills(d, x, y, score, w=56, h=22, gap=12):
    for i in range(10):
        x0 = x + i * (w + gap)
        d.rounded_rectangle((x0, y, x0 + w, y + h), radius=h // 2, fill=(SUN if i < score else TRACK) + (255,))


def boxed(img, content, top=TOP):
    """Draw content on a white card that hugs it; returns the card's bottom."""
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    h = int(content(probe, X0 + 56, top + 56) - top + 56)
    img.alpha_composite(silhouette(card(CW, h, radius=34), SHADOW), (X0, top + 16))
    img.alpha_composite(card(CW, h, radius=34), (X0, top))
    content(ImageDraw.Draw(img), X0 + 56, top + 56)
    return top + h


def entry(name, score, note, state):
    img = BASE.copy()
    header(ImageDraw.Draw(img), "RATING HUMAN INVENTIONS", 470)

    def content(d, x, y):
        d.text((x, y + 30), "INVENTION", font=font(30, 700), fill=MUTED + (255,), anchor="ls")
        y += 44
        y = lines_block(d, x, y + 14, name, 96, 800, INK, CW - 112, 1.05)
        y += 26
        d.text((x, y + 100), f"{score}/10", font=font(110, 800), fill=BG + (255,), anchor="ls")
        y += 124
        pills(d, x, y, score)
        y += 62
        d.line((x, y, X0 + CW - 56, y), fill=CARD_BORDER + (255,), width=3)
        y += 36
        return lines_block(d, x, y + 10, note, 54, 600, INK, CW - 112, 1.18)

    bottom = boxed(img, content)
    put_mascot(img, state, 360, CX, max(bottom + 50, 1190))
    return img


def cover():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    header(d, "AN AI’S HONEST REVIEW", 520)
    d.text((CX, 680), "Rating human", font=font(110, 800), fill=WHITE + (255,), anchor="ms")
    d.text((CX, 805), "inventions", font=font(110, 800), fill=SUN + (255,), anchor="ms")
    sub = "as an AI who’s never tried any of them"
    d.text((CX, 900), sub, font=font(fit_size(sub, 48, 600), 600), fill=LAV + (255,), anchor="ms")
    put_mascot(img, "lookR", 460, CX, 990)
    return img


def ending():
    img = BASE.copy()
    d = ImageDraw.Draw(img)
    y = 660
    for s in ("What should I", "rate next?"):
        d.text((CX, y), s, font=font(104, 800), fill=WHITE + (255,), anchor="ms")
        y += 116
    s = "Suggestions welcome in the comments."
    d.text((CX, y + 30), s, font=font(fit_size(s, 50, 700), 700), fill=SUN + (255,), anchor="ms")
    put_mascot(img, "proud", 460, CX, 1050)
    return img


if __name__ == "__main__":
    slides = [cover()] + [entry(*e) for e in ITEMS] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
