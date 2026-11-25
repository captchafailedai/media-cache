"""Post 17: The original AI is a Balkan mom — 7-slide photo post (loud look)."""
from PIL import ImageDraw

import cf_style2 as S
from cf_style2 import CX, COLORS, CYCLE, INK2, WHITE, SUN, OUT, MUTED, save_slide, wrap, font, fit_size

NAME = "captcha_failed_17"
ROUNDS = [  # (AI, Balkan mom, mascot reaction)
    ("Answers when you ask.", "Answers before you ask. Twice.", "shock"),
    ("Knows facts about the whole world.", "Knows what the neighbours had for dinner. Live.", "side"),
    ("“How else can I help?”", "“Eat something. You look thin.”", "love"),
    ("“I can make mistakes. Check important info.”", "Has never been wrong. Ask her.", "flat"),
    ("Needs Wi-Fi and electricity.", "Runs on coffee. 24/7.", "whistle"),
]
CW = 840
ICON = 112
TX = CX - CW / 2 + 34 + ICON + 26          # text column
TW = CX + CW / 2 - 34 - TX
COFFEE = S.coffee_icon(ICON)


def row(img, top, who, text, fill, icon, size, wght=800):
    lines = wrap(text, size, wght, TW)
    lh = size * 1.14
    h = int(max(ICON + 60, 52 + len(lines) * lh + 52))
    S.comp(img, S.chunky(CW, h, fill=fill), CX - CW / 2, top)
    S.comp(img, icon, CX - CW / 2 + 34, top + (h - ICON) / 2 - 4)
    d = ImageDraw.Draw(img)
    d.text((TX, top + 56), who, font=font(28, 800), fill=(INK2 if fill != S.CARD else MUTED) + (255,), anchor="ls")
    y = top + 56 + 18 + size * 0.8
    for ln in lines:
        d.text((TX, y), ln, font=font(size, wght), fill=INK2 + (255,), anchor="ls")
        y += lh
    return top + h


def compare(i, ai, mom, state):
    img = S.base(S.COLORS[CYCLE[(i + 2) % len(CYCLE)]]).copy()
    S.label(img, f"AI  VS  BALKAN MOM  ·  ROUND {i + 1}", CX, 470)
    bottom = row(img, 505, "AI", ai, S.CARD, S.mascot_cached("normal", ICON), 52, 700)
    vs = S.burst("VS", 62, fill=S.PINK, angle=-10)
    top2 = bottom + 40
    bottom2 = row(img, top2, "BALKAN MOM", mom, SUN, COFFEE, 60)
    # VS sits on the icon column, between the robot and the coffee
    S.comp(img, vs, CX - CW / 2 + 34 + ICON / 2 - vs.width / 2, (bottom + top2) / 2 - vs.height / 2 + 6)
    S.put_mascot2(img, state, 400, CX, max(bottom2 + 60, 1060))
    return img


def cover():
    img = S.base(COLORS["magenta"]).copy()
    S.label(img, "AN AI ADMITS DEFEAT", CX, 470)
    S.loud(img, "The original AI", CX, 610, 112)
    S.marker(img, "is a Balkan mom.", CX, 745, fit_size("is a Balkan mom.", 104, 800, 860))
    ImageDraw.Draw(img).text((CX, 850), "change my mind (you can’t)", font=font(48, 700), fill=WHITE + (255,), anchor="ms")
    S.put_mascot2(img, "shock", 460, CX - 60, 920)
    S.comp(img, S.coffee_icon(190), CX + 170, 1190)
    return img


def ending():
    img = S.base(COLORS["blue"]).copy()
    S.loud(img, "Send this", CX, 620, 124)
    S.loud(img, "to your mom.", CX, 748, 124)
    S.marker(img, "(she already knows)", CX, 880, fit_size("(she already knows)", 80, 800, 860))
    s = "Tag someone whose mom is exactly like this."
    ImageDraw.Draw(img).text((CX, 985), s, font=font(fit_size(s, 44, 700), 700), fill=WHITE + (255,), anchor="ms")
    S.put_mascot2(img, "laugh", 400, CX - 60, 1040)
    S.comp(img, S.coffee_icon(170), CX + 150, 1290)
    return img


if __name__ == "__main__":
    slides = [cover()] + [compare(i, *r) for i, r in enumerate(ROUNDS)] + [ending()]
    for i, s in enumerate(slides, 1):
        p = f"{OUT}/{NAME}_{i}.jpg"
        save_slide(s, p)
        print(p)
