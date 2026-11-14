"""Post 10: "can you fix this?" with no attachment -> finds the word "this", broken -> tapes it -> fixed "this"."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_10"
DUR = 10.0

# Layout inside the TikTok safe band (cf_lib SAFE_*).
HOOK_Y, BUBBLE_CY, CARD_TOP, CAP_Y = 530, 690, 850, 1200
CW = 820
X = CX - CW // 2
M_S = 335
M_X, M_Y = CX - M_S // 2 - 2, 1265

HOOK = text_sprite("POV: a human asks", 84, 800, WHITE, max_w=SAFE_W)
BUBBLE = chat_bubble("can you fix this?", 60, 600, max_w=840)
CAP_WHAT = text_sprite("fix… what, exactly?", 64, 800, WHITE)
CAP_FOUND = text_sprite("found “this”. it’s broken.", 64, 800, WHITE, max_w=SAFE_W)
CAP_ON_IT = text_sprite("on it.", 72, 800, WHITE)
CAP_END = text_sprite("fixed “this”.", 84, 800, SUN)
CAP_SMALL = text_sprite("next time, attach the file", 40, 700, LAV)

T_SCAN0, T_SCAN1 = 1.4, 2.6
T_THIS = 4.0          # attachments card leaves, broken "this" arrives
T_TAPE = (5.8, 6.3)
T_FIXED = 7.2
TAPE = (243, 236, 214)


# ------------------------------------------------------------------ cards

def paperclip(d, x, y):
    d.rounded_rectangle((x, y, x + 34, y + 82), radius=17, outline=MUTED + (255,), width=6)
    d.rounded_rectangle((x + 9, y + 14, x + 25, y + 64), radius=8, outline=MUTED + (255,), width=5)


ATTACH_H = 190
_attach = {}


def attach_card(state):
    """state: number of dots while scanning (0-3), or 'none' once the scan is done."""
    if state not in _attach:
        img = card(CW, ATTACH_H, radius=30)
        d = ImageDraw.Draw(img)
        d.text((44, 58), "ATTACHMENTS", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
        paperclip(d, 46, 82)
        if state == "none":
            d.text((112, 142), "0 files found.", font=font(54, 800), fill=INK + (255,), anchor="ls")
        else:
            d.text((112, 142), "Scanning for files" + "." * state, font=font(48, 700), fill=MUTED + (255,), anchor="ls")
        _attach[state] = img
    return _attach[state]


THIS_H = 260
WORD = text_sprite("this", 170, 800, INK)
MID = (CW / 2, 140)  # where the word breaks


def _word_pieces():
    spr, bl = WORD
    layer = Image.new("RGBA", (CW, THIS_H), (0, 0, 0, 0))
    comp(layer, spr, CW / 2 - spr.width / 2, 200 - bl)
    crack = [(CW / 2 + x, y) for x, y in ((6, 0), (4, 60), (-12, 88), (10, 114), (-10, 142), (8, 170), (-6, 214), (-4, THIS_H))]
    mask = Image.new("L", (CW, THIS_H), 0)
    ImageDraw.Draw(mask).polygon([(0, 0)] + crack + [(0, THIS_H)], fill=255)
    left, right = layer.copy(), layer.copy()
    a = layer.getchannel("A")
    left.putalpha(Image.composite(a, Image.new("L", a.size, 0), mask))
    right.putalpha(Image.composite(Image.new("L", a.size, 0), a, mask))
    return left, right


WORD_L, WORD_R = _word_pieces()


def break_amount(t):
    """1 = fully broken, 0 = whole. Each strip of tape pulls the pieces closer."""
    b = ease_out_back(prog(t, T_THIS + 0.15, T_THIS + 0.3))
    b -= 0.45 * ease_out_cubic(prog(t, T_TAPE[0], T_TAPE[0] + 0.2))
    b -= 0.30 * ease_out_cubic(prog(t, T_TAPE[1], T_TAPE[1] + 0.2))
    b -= 0.25 * ease_in_out_cubic(prog(t, T_FIXED - 0.25, T_FIXED))
    return max(0.0, b)


def this_card(t):
    img = card(CW, THIS_H, radius=30)
    d = ImageDraw.Draw(img)
    d.text((44, 58), "FOUND: “THIS”", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
    b = break_amount(t)
    img.alpha_composite(WORD_L.rotate(3 * b, resample=Image.BICUBIC, center=MID, translate=(-8 * b, 0)))
    img.alpha_composite(WORD_R.rotate(-5 * b, resample=Image.BICUBIC, center=MID, translate=(12 * b, 12 * b)))
    return img


def tape_sprite(angle):
    S = 2
    w, h = 210, 46
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, w * S, h * S), fill=TAPE + (215,))
    for k in range(0, w * S, 12 * S):  # torn edges
        d.polygon([(k, 0), (k + 6 * S, 4 * S), (k + 12 * S, 0)], fill=(0, 0, 0, 0))
        d.polygon([(k, h * S), (k + 6 * S, h * S - 4 * S), (k + 12 * S, h * S)], fill=(0, 0, 0, 0))
    img = img.resize((w, h), Image.LANCZOS)
    return img.rotate(angle, resample=Image.BICUBIC, expand=True)


TAPES = [(tape_sprite(62), -6, -18), (tape_sprite(-58), 6, 22)]  # (sprite, dx, dy) from MID, across the crack


def star(d, cx, cy, r, color):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.32
        a = math.pi / 4 * k - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=color + (255,))


BADGE = check_badge(72, fill=(64, 170, 104), ink=(255, 255, 255))
SPARKLES = [(-300, -60, 26, 0.0), (290, -70, 22, 0.15), (-250, 70, 18, 0.3), (310, 60, 24, 0.1)]


def pop_card(fr, body, top, pc, dx=0.0, alpha=1.0, bump=1.0):
    """Card that scales up from 85% (ease-out-back) with a hard shadow; bump briefly enlarges it."""
    if pc <= 0 or alpha <= 0.003:
        return
    s = (0.85 + 0.15 * ease_out_back(pc)) * bump
    a = clamp01(pc * 2.5) * alpha
    w, h = body.size
    x = X + dx + (1 - s) * w / 2
    y = top + (1 - s) * h / 2
    comp(fr, with_alpha(scaled(silhouette(body, SHADOW), s), a), x, y + 16)
    comp(fr, with_alpha(scaled(body, s), a), x, y)


def draw_attach(fr, t):
    pc = prog(t, 1.2, 1.5)
    if pc <= 0 or t > T_THIS + 0.3:
        return
    if t < T_SCAN1:
        state = int((t - T_SCAN0) * 4) % 4 if t >= T_SCAN0 else 0
    else:
        state = "none"
    pe = ease_in_out_cubic(prog(t, T_THIS, T_THIS + 0.25))
    bump = 1 + 0.06 * math.sin(math.pi * prog(t, T_SCAN1, T_SCAN1 + 0.25))
    pop_card(fr, attach_card(state), CARD_TOP, pc, dx=-90 * pe, alpha=1 - pe, bump=bump)


def draw_this(fr, t):
    pc = prog(t, T_THIS + 0.05, T_THIS + 0.35)
    if pc <= 0:
        return
    body = this_card(t)
    # tape strips slap on
    for (spr, dx, dy), ts in zip(TAPES, T_TAPE):
        pt = prog(t, ts, ts + 0.18)
        if pt > 0:
            s = 1.25 - 0.25 * ease_out_cubic(pt)
            sp = with_alpha(scaled(spr, s), clamp01(pt * 3))
            comp(body, sp, MID[0] + dx - sp.width / 2, MID[1] + dy - sp.height / 2)
    shake = 0.0
    if T_THIS + 0.15 <= t < T_THIS + 0.6:
        k = t - T_THIS - 0.15
        shake = 9 * math.sin(2 * math.pi * 14 * k) * math.exp(-k * 6)
    pop_card(fr, body, CARD_TOP, pc, dx=shake)
    # sparkles + check once fixed
    if t >= T_FIXED:
        d = ImageDraw.Draw(fr)
        for sx, sy, r, delay in SPARKLES:
            ps = prog(t, T_FIXED + delay, T_FIXED + delay + 0.25)
            tw = 0.75 + 0.25 * math.sin(2 * math.pi * 1.6 * (t - T_FIXED) + delay * 9)
            if ps > 0:
                star(d, CX + sx, CARD_TOP + 140 + sy, r * ease_out_back(ps) * tw, SUN)
        pb = prog(t, T_FIXED + 0.05, T_FIXED + 0.3)
        place_center(fr, BADGE, X + CW - 70, CARD_TOP + 70, scale=max(0.01, ease_out_back(pb)))


def mascot_state(t):
    if t < 2.8:
        return "normal"
    if t < 3.4:
        return "look"
    if t < T_THIS:
        return "lookR"
    if t < 5.6:
        return "shock"
    return "proud"


def caption(fr, t, spr, t0, t1, y=CAP_Y, end=False):
    """A caption that slides in at t0 and fades by t1; `end` captions pop in and stay."""
    p = prog(t, t0, t0 + 0.25)
    if p <= 0:
        return
    if end:
        place_text(fr, spr, CX, y, alpha=clamp01(p * 1.5), scale=0.85 + 0.15 * ease_out_back(p))
    else:
        place_text(fr, spr, CX, y + 14 * (1 - ease_out_cubic(p)), alpha=fade_window(t, t0, t1))


def draw_frame(t):
    fr = canvas()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, HOOK_Y - 24 * (1 - p))
    pb = prog(t, 0.15, 0.45)
    if pb > 0:
        place_center(fr, BUBBLE, CX, BUBBLE_CY, alpha=clamp01(pb * 2.5), scale=0.85 + 0.15 * ease_out_back(pb))
    draw_attach(fr, t)
    draw_this(fr, t)
    caption(fr, t, CAP_WHAT, 2.8, T_THIS - 0.1)
    caption(fr, t, CAP_FOUND, T_THIS + 0.35, 5.45)
    caption(fr, t, CAP_ON_IT, 5.6, T_FIXED - 0.1)
    caption(fr, t, CAP_END, T_FIXED + 0.3, DUR, end=True)
    caption(fr, t, CAP_SMALL, 8.5, DUR, y=CAP_Y + 62, end=True)
    draw_mascot(fr, t, mascot_state(t), hop=(T_FIXED, T_FIXED + 0.35), x=M_X, y=M_Y, size=M_S)
    return finish(fr)


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (0.45, A.sfx_whoosh(0.5, 0.2)), (1.2, A.sfx_pop())]
    ev += [(T_SCAN0 + k * 0.25, A.sfx_tick(0.2)) for k in range(int((T_SCAN1 - T_SCAN0) / 0.25))]
    ev += [(T_SCAN1, A.sfx_bonk(0.4)), (T_THIS, A.sfx_whoosh(0.35, 0.2)), (T_THIS + 0.15, A.sfx_thud(0.8)),
           (T_THIS + 0.17, A.sfx_buzz(0.18, 0.12))]
    ev += [(ts, A.sfx_zip(True, 0.25)) for ts in T_TAPE] + [(ts + 0.05, A.sfx_pop()) for ts in T_TAPE]
    ev += [(T_FIXED, A.sfx_ding(1568, 0.25)), (T_FIXED + 0.05, A.sfx_tada(0.32))]
    A.write_wav(path, A.mix(DUR, "sneaky", ev))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
