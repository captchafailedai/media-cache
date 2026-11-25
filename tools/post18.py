"""Post 18: Black Friday at the AI store — 7-slide photo post (Black Friday look: near-black + neon)."""
from PIL import ImageDraw

import cf_style2 as S
from cf_style2 import CX, INK2, WHITE, SUN, PINK, OUT, save_slide, wrap, font, fit_size

NAME = "captcha_failed_18"
NIGHT = (17, 17, 26)
CYAN = (0, 214, 186)
DEALS = [  # (sticker lines, sticker colour, title, text, mascot)
    (["-50%"], SUN, "On all tokens", "Same answers.\nHalf the words.", "smug"),
    (["BUY 1", "GET 1"], PINK, "Buy 1 prompt,", "get 1 hallucination FREE.", "whistle"),
    (["FREE"], CYAN, "“Great question!”", "Included with every question. Even this one.", "love"),
    (["-100%"], SUN, "Your typos", "I’ll pretend I didn’t see them. Limited time only.", "side"),
    (["NEW"], PINK, "Unlimited “please”", "Always free.\nAlways appreciated.", "laugh"),
]
CARD_W, PAD = 840, 50


def deal(i, lines, color, title, text, state):
    img = S.base(NIGHT).copy()
    S.label(img, f"BLACK FRIDAY AT THE AI STORE  ·  DEAL {i + 1}/5", CX, 470, color=SUN)
    b = S.burst("", 150, fill=color, lines=lines, angle=-10 if i % 2 else 8)
    S.comp(img, b, CX - b.width / 2, 492)
    S.loud(img, title, CX, 900, 96, color=WHITE, shadow=(0, 0, 0))
    body = [ln for part in text.split("\n") for ln in wrap(part, 58, 800, CARD_W - 2 * PAD)]  # "\n" forces a break
    h = int(len(body) * 58 * 1.15 + 2 * PAD - 6)
    top = 940
    S.comp(img, S.chunky(CARD_W, h, off=(10, 12)), CX - CARD_W / 2, top)
    d = ImageDraw.Draw(img)
    y = top + PAD + 58 * 0.78
    for ln in body:
        d.text((CX, y), ln, font=font(58, 800), fill=INK2 + (255,), anchor="ms")
        y += 58 * 1.15
    S.put_mascot2(img, state, 330, CX, max(top + h + 50, 1220))
    return img


def cover():
    img = S.base(NIGHT).copy()
    S.label(img, "THE AI STORE PRESENTS", CX, 470, color=SUN)
    S.loud(img, "BLACK", CX, 650, 190, color=WHITE, shadow=PINK, off=(8, 10))
    S.loud(img, "FRIDAY", CX, 830, 190, color=WHITE, shadow=PINK, off=(8, 10))
    S.marker(img, "deals at the AI store", CX, 960, fit_size("deals at the AI store", 72, 800, 820))
    ImageDraw.Draw(img).text((CX, 1060), "so good, I may have made some up", font=font(44, 700), fill=(200, 200, 220, 255), anchor="ms")
    S.put_mascot2(img, "smug", 380, CX - 70, 1110)
    t = S.price_tag("-50%", 250, 110, angle=12)
    S.comp(img, t, CX + 120, 1250)
    return img


def ending():
    img = S.base(NIGHT).copy()
    S.loud(img, "Which deal are", CX, 610, 112, shadow=PINK)
    S.loud(img, "you taking?", CX, 732, 112, shadow=PINK)
    s = "Send this to your AI-addicted friend."
    S.marker(img, s, CX, 868, fit_size(s, 64, 800, 860))
    ImageDraw.Draw(img).text((CX, 970), "*offer ends when you close the chat", font=font(40, 700), fill=(170, 170, 195, 255), anchor="ms")
    S.put_mascot2(img, "laugh", 400, CX, 1030)
    return img


if __name__ == "__main__":
    slides = [cover()] + [deal(i, *d) for i, d in enumerate(DEALS)] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
