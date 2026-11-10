"""Post 6: an email opens with "Per my last email," -> tone check climbs to DANGER -> the only safe reply."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_06"
DUR = 10.5

HOOK = text_sprite("POV: the email says", 84, 800, WHITE, max_w=SAFE_W)
CAP_SCAN = text_sprite("analyzing tone…", 64, 800, WHITE)
CAP_UHOH = text_sprite("uh oh.", 84, 800, WHITE)
CAP_END = text_sprite("the only safe reply.", 80, 800, SUN, max_w=SAFE_W)

CW = 820
X = CX - CW // 2
EMAIL_TOP, EMAIL_H = 340, 300
TONE_TOP, TONE_H = 680, 214
REPLY_H = 190
CAP_Y = 1000

BODY = "Per my last email,"
TYPE_T0, TYPE_T1 = 0.8, 2.3

GREEN = (64, 170, 104)
BLUE = (88, 118, 214)
ORANGE = (232, 132, 44)
LEVELS = [  # (time, label, share of the bar, colour)
    (3.0, "Friendly", 0.15, GREEN),
    (3.8, "Professional", 0.40, BLUE),
    (4.6, "Concerning", 0.70, ORANGE),
    (5.4, "DANGER", 1.00, RED),
]
T_DANGER = LEVELS[-1][0]
T_SWAP = 7.3          # tone card leaves, reply card arrives
T_SAFE = 8.0          # check mark + final caption


# ------------------------------------------------------------------ cards

def email_static():
    img = card(CW, EMAIL_H, radius=30)
    d = ImageDraw.Draw(img)
    d.text((44, 82), "Re: Re: Re: quick question", font=font(44, 800), fill=INK + (255,), anchor="ls")
    d.text((44, 128), "to: me  ·  cc: everyone", font=font(30, 600), fill=MUTED + (255,), anchor="ls")
    d.line((44, 158, CW - 44, 158), fill=TRACK + (255,), width=3)
    return img


EMAIL = email_static()
BODY_F = font(68, 800)
_bodies = {}


def body_layer(n, cursor):
    key = (n, cursor)
    if key not in _bodies:
        img = Image.new("RGBA", (CW, 130), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        s = BODY[:n]
        d.text((44, 86), s, font=BODY_F, fill=INK + (255,), anchor="ls")
        if cursor:
            x = 44 + BODY_F.getlength(s) + 6
            d.rectangle((x, 86 - 58, x + 5, 86 + 10), fill=BG + (255,))
        _bodies[key] = img
    return _bodies[key]


def tone_static():
    img = card(CW, TONE_H, radius=30)
    ImageDraw.Draw(img).text((44, 62), "TONE CHECK", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
    return img


TONE = tone_static()
LABELS = {lab: text_sprite(lab, 64, 800, col) for _, lab, _, col in LEVELS}
PCT_F = font(44, 800)


def reply_static():
    img = card(CW, REPLY_H, radius=30)
    d = ImageDraw.Draw(img)
    d.text((44, 62), "MY REPLY", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
    d.text((44, 140), "Thanks so much!!", font=font(64, 800), fill=INK + (255,), anchor="ls")
    return img


REPLY = reply_static()
BADGE = check_badge(72, fill=GREEN, ink=(255, 255, 255))


def level_at(t):
    i = -1
    for k, (ts, *_rest) in enumerate(LEVELS):
        if t >= ts:
            i = k
    return i


def tone_layer(t):
    img = TONE.copy()
    d = ImageDraw.Draw(img)
    i = level_at(t)
    track = (44, 160, CW - 44, 182)
    d.rounded_rectangle(track, radius=11, fill=TRACK + (255,))
    if i < 0:
        return img
    ts, lab, share, col = LEVELS[i]
    prev_share = LEVELS[i - 1][2] if i else 0.0
    prev_col = LEVELS[i - 1][3] if i else col
    p = lerp(prev_share, share, ease_out_cubic(prog(t, ts, ts + 0.35)))
    c = lerp_color(prev_col, col, prog(t, ts, ts + 0.2))
    if p > 0.01:
        d.rounded_rectangle((44, 160, 44 + max(22, (CW - 88) * p), 182), radius=11, fill=c + (255,))
    d.text((CW - 44, 136), f"{int(round(p * 100))}%", font=PCT_F, fill=MUTED + (255,), anchor="rs")
    # outgoing label fades fast, incoming one pops
    if i > 0 and t < ts + 0.1:
        spr, bl = LABELS[LEVELS[i - 1][1]]
        comp(img, with_alpha(spr, 1 - prog(t, ts, ts + 0.1)), 44 - PAD, 136 - bl)
    pl = prog(t, ts + 0.04, ts + 0.3)
    if pl > 0:
        spr, bl = LABELS[lab]
        s = 0.8 + 0.2 * ease_out_back(pl)
        comp(img, with_alpha(scaled(spr, s), clamp01(pl * 2.5)), 44 - PAD * s, 136 - bl * s)
    if i == len(LEVELS) - 1:  # red alarm outline, pulsing
        a = int(255 * (0.55 + 0.45 * math.cos(2 * math.pi * 3 * (t - ts))))
        d.rounded_rectangle((2, 2, CW - 3, TONE_H - 3), radius=30, outline=RED + (a,), width=7)
    return img


def pop_card(fr, body, top, pc, dx=0.0, alpha=1.0):
    """Card that scales up from 85% (ease-out-back) with a hard shadow."""
    if pc <= 0 or alpha <= 0.003:
        return
    s = 0.85 + 0.15 * ease_out_back(pc)
    a = clamp01(pc * 2.5) * alpha
    w, h = body.size
    x = X + dx + (1 - s) * w / 2
    y = top + (1 - s) * h / 2
    comp(fr, with_alpha(scaled(silhouette(body, SHADOW), s), a), x, y + 16)
    comp(fr, with_alpha(scaled(body, s), a), x, y)


def draw_email(fr, t):
    pc = prog(t, 0.15, 0.45)
    pop_card(fr, EMAIL, EMAIL_TOP, pc)
    if pc <= 0:
        return
    n = int(round(len(BODY) * prog(t, TYPE_T0, TYPE_T1)))
    typing = TYPE_T0 <= t < TYPE_T1
    cursor = typing or (t < 2.6 and int(t * 2.4) % 2 == 0)
    if n or cursor:
        a = clamp01(pc * 2.5)
        comp(fr, with_alpha(body_layer(n, cursor), a), X, EMAIL_TOP + 150)


def draw_tone(fr, t):
    pc = prog(t, 2.6, 2.9)
    if pc <= 0 or t > T_SWAP + 0.3:
        return
    shake = 0.0
    if t >= T_DANGER:
        k = t - T_DANGER
        shake = 12 * math.sin(2 * math.pi * 13 * k) * math.exp(-k * 3.2)
    pe = ease_in_out_cubic(prog(t, T_SWAP, T_SWAP + 0.25))
    pop_card(fr, tone_layer(t), TONE_TOP, pc, dx=shake - 90 * pe, alpha=1 - pe)


def draw_reply(fr, t):
    pc = prog(t, T_SWAP + 0.12, T_SWAP + 0.45)
    pop_card(fr, REPLY, TONE_TOP, pc)
    pb = prog(t, T_SAFE, T_SAFE + 0.25)
    if pb > 0:
        place_center(fr, BADGE, X + CW - 44 - 36, TONE_TOP + 112, scale=max(0.01, ease_out_back(pb)))


def draw_sweat_at(fr, t, mx, my, size, t_in):
    """Library sweat drop, repositioned for a smaller mascot."""
    pw = prog(t, t_in, t_in + 0.2)
    if my is None or pw <= 0:
        return
    k = size / M_SIZE
    s = max(0.01, ease_out_back(pw)) * k
    slide = 26 * k * ease_in_out_cubic(prog(t, t_in + 0.2, t_in + 1.5))
    spr = scaled(SWEAT_SPR, s)
    comp(fr, spr, mx + 404 * k - spr.width / 2, my + 104 * k + slide - spr.height / 2)


def mascot_state(t):
    if t < 3.0:
        return "normal"
    if t < T_DANGER:
        return "look"
    if t < T_SAFE - 0.4:
        return "shock"
    return "proud"


M_X, M_Y, M_S = CX - 223, 1050, 440


def draw_frame(t):
    fr = BASE.copy()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, 270 - 24 * (1 - p))  # visible from frame 1, so the default cover isn't blank
    draw_email(fr, t)
    draw_tone(fr, t)
    draw_reply(fr, t)
    a = fade_window(t, 3.0, 5.3)
    place_text(fr, CAP_SCAN, CX, CAP_Y + 14 * (1 - ease_out_cubic(prog(t, 3.0, 3.25))), alpha=a)
    pu = prog(t, 5.5, 5.75)
    if pu > 0 and t < 7.3:
        place_text(fr, CAP_UHOH, CX, CAP_Y, alpha=fade_window(t, 5.5, 7.15),
                   scale=0.85 + 0.15 * ease_out_back(pu))
    pe = prog(t, T_SAFE + 0.1, T_SAFE + 0.35)
    if pe > 0:
        place_text(fr, CAP_END, CX, CAP_Y, alpha=pe, scale=0.85 + 0.15 * ease_out_back(pe))
    my = draw_mascot(fr, t, mascot_state(t), hop=(T_SAFE - 0.4, T_SAFE), x=M_X, y=M_Y, size=M_S)
    draw_sweat_at(fr, t, M_X, my, M_S, T_DANGER + 0.15)
    return fr.convert("RGB")


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (TYPE_T0, A.sfx_typing(TYPE_T1 - TYPE_T0, 12, 0.3)),
          (2.6, A.sfx_whoosh(0.4, 0.22)), (3.0, A.sfx_rise(T_DANGER - 3.0, 0.13))]
    ev += [(ts, A.sfx_blip()) for ts, *_rest in LEVELS[:-1]]
    ev += [(T_DANGER, A.sfx_buzz(0.5, 0.32)), (T_DANGER, A.sfx_thud(0.8))]
    ev += [(t0, A.sfx_thud(0.42)) for t0 in (6.0, 6.24, 6.7, 6.94)]  # nervous heartbeat
    ev += [(T_SWAP, A.sfx_whoosh(0.35, 0.2)), (T_SWAP + 0.12, A.sfx_pop()), (T_SAFE, A.sfx_tada(0.32))]
    curve = [(0, 1), (T_DANGER - 0.05, 1), (T_DANGER + 0.05, 0), (T_SWAP + 0.05, 0), (T_SWAP + 0.3, 1), (DUR, 1)]
    A.write_wav(path, A.mix(DUR, "sneaky", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
