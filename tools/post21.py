"""Post 21 (Cyber Monday): an AI tries to sell Cyber Monday deals to a Balkan dad — chat video."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
import cf_style2 as S
from cf_style2 import (CX, COLORS, INK2, SUN, WHITE, PINK, OUT, comp, scaled, with_alpha, prog, clamp01,
                       ease_out_back, ease_out_cubic, ease_in_out_cubic, render_video, stills, font, fit_size, wrap)

NAME = "captcha_failed_21"
BGC = COLORS["teal"]
BG_IMG = S.base(BGC)
AI_BLUE = (38, 84, 240)
GREY = (236, 238, 246)

CHAT = [  # (sender, text)
    ("ai", "Cyber Monday deal: 50% off a new phone!"),
    ("dad", "Mine works."),
    ("ai", "The screen is cracked."),
    ("dad", "I put tape on it."),
    ("ai", "It’s from 2014."),
    ("dad", "Good year."),
    ("ai", "It doesn’t turn on."),
    ("dad", "It does if you know how."),
    ("ai", "…70% off?"),
    ("dad", "Do you know how much I paid for this phone?"),
]
T0, STEP = 0.0, 1.0   # the first message is already there on frame 1
TIMES = [T0 + i * STEP + (0.35 if i == len(CHAT) - 1 else 0) for i in range(len(CHAT))]
TIMES[0] = -0.3   # fully popped in on frame 1 (it doubles as the cover)   # dramatic pause before the last line
T_END = TIMES[-1] + 1.4
DUR = T_END + 2.6

PANEL_W, PANEL_H = 840, 750
PX, PY = CX - PANEL_W // 2, 690
HEAD_H = 104
AREA = (PX + 26, PY + HEAD_H + 14, PX + PANEL_W - 26, PY + PANEL_H - 22)   # message viewport
AW, AH = AREA[2] - AREA[0], AREA[3] - AREA[1]
FS, BUB_MAX, PADX, PADY, GAP = 50, 650, 28, 20, 16


def avatar(d_):
    S2 = 4
    img = Image.new("RGBA", (d_ * S2, d_ * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, d_ * S2 - 1, d_ * S2 - 1), fill=(168, 196, 255, 255), outline=INK2 + (255,), width=3 * S2)
    u = d_ * S2 / 100
    # eyebrows + mustache: the universal dad
    d.line([(26 * u, 36 * u), (42 * u, 32 * u)], fill=INK2 + (255,), width=int(6 * u))
    d.line([(58 * u, 32 * u), (74 * u, 36 * u)], fill=INK2 + (255,), width=int(6 * u))
    d.ellipse((33 * u, 42 * u, 41 * u, 50 * u), fill=INK2 + (255,))
    d.ellipse((59 * u, 42 * u, 67 * u, 50 * u), fill=INK2 + (255,))
    must = [(22 * u, 66 * u), (34 * u, 58 * u), (50 * u, 62 * u), (66 * u, 58 * u), (78 * u, 66 * u),
            (66 * u, 70 * u), (50 * u, 67 * u), (34 * u, 70 * u)]
    d.polygon(must, fill=INK2 + (255,))
    return img.resize((d_, d_), Image.LANCZOS)


def panel_base():
    img = S.chunky(PANEL_W, PANEL_H, radius=34)
    d = ImageDraw.Draw(img)
    comp(img, avatar(70), 30, 18)
    d.text((118, 54), "Dad", font=font(42, 800), fill=INK2 + (255,), anchor="ls")
    d.ellipse((120, 68, 132, 80), fill=(40, 180, 90, 255))
    d.text((140, 80), "online", font=font(28, 700), fill=(110, 112, 140, 255), anchor="ls")
    d.line((24, HEAD_H, PANEL_W - 24, HEAD_H), fill=(226, 228, 240, 255), width=3)
    return img


PANEL = panel_base()


def bubble(sender, text):
    lines = wrap(text, FS, 700, BUB_MAX - 2 * PADX)
    f = font(FS, 700)
    w = int(max(f.getlength(ln) for ln in lines) + 2 * PADX)
    h = int(len(lines) * FS * 1.18 + 2 * PADY)
    S2 = 2
    img = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill, ink = (AI_BLUE, WHITE) if sender == "ai" else (GREY, INK2)
    d.rounded_rectangle((0, 0, w * S2 - 1, h * S2 - 1), radius=30 * S2, fill=fill + (255,))
    y = (PADY + FS * 0.82) * S2
    for ln in lines:
        d.text((PADX * S2, y), ln, font=font(FS * S2, 700), fill=ink + (255,), anchor="ls")
        y += FS * 1.18 * S2
    return img.resize((w, h), Image.LANCZOS)


BUBBLES = [bubble(s, t) for s, t in CHAT]
TOPS = []
_y = 0
for b in BUBBLES:
    TOPS.append(_y)
    _y += b.height + GAP


def typing_dots(t):
    S2 = 2
    w, h = 110, 62
    img = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w * S2 - 1, h * S2 - 1), radius=30 * S2, fill=GREY + (255,))
    for k in range(3):
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t - k * 0.9))
        cx = (30 + k * 25) * S2
        d.ellipse((cx - 7 * S2, h * S2 / 2 - 7 * S2, cx + 7 * S2, h * S2 / 2 + 7 * S2), fill=(120, 122, 150, int(255 * a)))
    return img.resize((w, h), Image.LANCZOS)


def scroll_at(t):
    """How far the conversation has scrolled up so the newest message stays in view."""
    off = 0.0
    for i, ti in enumerate(TIMES):
        start = ti - 0.55 if CHAT[i][0] == "dad" else ti   # make room as soon as dad starts typing
        need = max(0.0, TOPS[i] + BUBBLES[i].height - AH)
        if t >= start:
            p = ease_out_cubic(prog(t, start, start + 0.3))
            off = off + (need - off) * p if need > off else off
    return off


def draw_chat(fr, t):
    comp(fr, PANEL, PX, PY)
    view = Image.new("RGBA", (AW, AH), (0, 0, 0, 0))
    off = scroll_at(t)
    for i, (b, ti) in enumerate(zip(BUBBLES, TIMES)):
        sender = CHAT[i][0]
        # typing indicator before dad's lines
        if sender == "dad" and ti - 0.55 <= t < ti:
            dots = typing_dots(t)
            comp(view, dots, 0, TOPS[i] - off)
        p = prog(t, ti, ti + 0.22)
        if p <= 0:
            continue
        s = 0.85 + 0.15 * ease_out_back(p)
        sb = scaled(b, s)
        x = AW - sb.width if sender == "ai" else 0
        y = TOPS[i] - off + (b.height - sb.height) / 2
        comp(view, with_alpha(sb, clamp01(p * 2.5)), x, y)
    comp(fr, view, AREA[0], AREA[1])


def hook(fr):
    S.loud(fr, "AI vs Balkan dad", CX, 548, 108)
    S.marker(fr, "Cyber Monday edition", CX, 650, 58)


SCORE = None


def score_card():
    w, h = 760, 400
    img = S.chunky(w, h, fill=SUN, radius=36)
    d = ImageDraw.Draw(img)
    d.text((w / 2, 130), "Balkan dad: 1", font=font(92, 800), fill=INK2 + (255,), anchor="ms")
    d.text((w / 2, 232), "AI: 0", font=font(92, 800), fill=INK2 + (255,), anchor="ms")
    d.text((w / 2, 320), "Send this to your dad.", font=font(52, 800), fill=INK2 + (255,), anchor="ms")
    return img


SCORE = score_card()


def draw_frame(t):
    fr = BG_IMG.copy()
    hook(fr)
    draw_chat(fr, t)
    pe = prog(t, T_END, T_END + 0.35)
    if pe > 0:
        # score card over the top of the chat; dad's last line stays readable underneath
        s = 0.8 + 0.2 * ease_out_back(pe)
        sc = scaled(SCORE, s)
        comp(fr, with_alpha(sc, clamp01(pe * 2)), CX - sc.width / 2, 900 - sc.height / 2)
        m = S.mascot_cached("flat", 230)
        comp(fr, with_alpha(m, clamp01(pe * 2)), CX + 230, 940 + 8 * math.sin(t * 3))
    return fr.convert("RGB")


def soundtrack(path):
    ev = []
    for (sender, _), ti in zip(CHAT, TIMES):
        ev.append((ti, A.sfx_pop() if sender == "ai" else A.sfx_blip()))
    ev += [(T_END, A.sfx_thud(0.7)), (T_END + 0.1, A.sfx_tada(0.3))]
    curve = [(0, 0.8), (TIMES[-1] - 0.4, 0.8), (TIMES[-1] - 0.3, 0.0), (T_END - 0.05, 0.0), (T_END + 0.2, 0.9), (DUR, 0.9)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
