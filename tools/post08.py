"""Post 8: "can you make it pop?" -> keeps adding pop until the poster literally pops."""
import math
import random
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_08"
DUR = 10.5

HOOK = text_sprite("POV: a human asks", 84, 800, WHITE, max_w=SAFE_W)
BUBBLE = chat_bubble("can you make it pop?", 60, 600, max_w=840)
CAP_ON_IT = text_sprite("on it.", 72, 800, WHITE)
CAP_END = text_sprite("you said pop.", 84, 800, SUN, max_w=SAFE_W)

PW, PH = 560, 400            # poster card
MG = 80                      # canvas margin for stickers and tilt
P_CY = 570 + PH // 2         # poster centre on screen
CAP_Y = 1075
STEPS = [2.0, 3.2, 4.4, 5.6, 6.8]   # each one adds more "pop"
T_SWELL, T_POP = 7.6, 8.0
T_WHISTLE = 8.9

PINK = (255, 92, 170)
BLUE = (88, 118, 214)
GREEN = (64, 170, 104)
ORANGE = (240, 140, 50)
FROSTING = (255, 182, 203)
CONFETTI = [SUN, PINK, BLUE, GREEN, WHITE, RED, ORANGE]

_rng = random.Random(8)
DOTS = []
while len(DOTS) < 26:
    x, y = _rng.uniform(24, PW - 24), _rng.uniform(24, PH - 24)
    if 40 < x < PW - 40 and 60 < y < 240:
        continue
    if 190 < x < 370 and 225 < y < 395:
        continue
    DOTS.append((x, y, _rng.uniform(6, 12), _rng.choice([PINK, BLUE, GREEN, WHITE, ORANGE])))


# ------------------------------------------------------------------ poster

S = 2  # supersampling for the poster drawing


def P(x, y):
    return ((MG + x) * S, (MG + y) * S)


def cupcake(d, cx, cy):
    def pt(x, y):
        return P(cx + x, cy + y)
    d.polygon([pt(-46, 10), pt(46, 10), pt(34, 68), pt(-34, 68)], fill=LAV + (255,))
    for x in (-24, -8, 8, 24):
        d.line((*pt(x, 16), *pt(x * 0.75, 62)), fill=(150, 152, 205, 255), width=4 * S)
    for x, y, r in ((-24, -6, 28), (24, -6, 28), (0, -26, 32)):
        d.ellipse((*pt(x - r, y - r), *pt(x + r, y + r)), fill=FROSTING + (255,))
    d.rounded_rectangle((*pt(-52, -12), *pt(52, 16)), radius=13 * S, fill=FROSTING + (255,))
    d.line((*pt(2, -58), *pt(10, -76)), fill=(90, 140, 60, 255), width=4 * S)
    d.ellipse((*pt(-11, -70), *pt(11, -48)), fill=RED + (255,))


def sticker(img, text, center, r, angle, fill=RED):
    R = r * S
    sz = int(R * 2.6)
    st = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    c = sz / 2

    def star(dx, dy):
        pts = []
        for k in range(24):
            rr = R if k % 2 == 0 else R * 0.8
            a = math.pi * k / 12
            pts.append((c + dx + rr * math.cos(a), c + dy + rr * math.sin(a)))
        return pts
    d.polygon(star(5 * S, 6 * S), fill=SHADOW + (255,))
    d.polygon(star(0, 0), fill=fill + (255,))
    fs = fit_size(text, int(r * 0.6), 800, r * 1.25)
    d.text((c, c), text, font=font(fs * S, 800), fill=(255, 255, 255, 255), anchor="mm")
    st = st.rotate(angle, resample=Image.BICUBIC)
    img.alpha_composite(st, (int(center[0] - c), int(center[1] - c)))


def poster(level, border_col=None):
    img = Image.new("RGBA", ((PW + 2 * MG) * S, (PH + 2 * MG) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bg = SUN if level >= 2 else CARD
    border = border_col or (PINK if level >= 4 else (SUN_DARK if level >= 2 else CARD_BORDER))
    bw = 14 if level >= 4 else 2
    d.rounded_rectangle((*P(0, 0), *P(PW - 1, PH - 1)), radius=26 * S, fill=bg + (255,),
                        outline=border + (255,), width=bw * S)
    if level >= 3:
        for x, y, r, c in DOTS:
            d.ellipse((*P(x - r, y - r), *P(x + r, y + r)), fill=c + (255,))
    title = "BAKE SALE!!!" if level >= 5 else "BAKE SALE"
    size, wght = (64, 400) if level == 0 else (fit_size(title, 100, 800, PW - 70), 800)
    f = font(size * S, wght)
    tx, ty = P(PW / 2, 158)
    if level >= 3:
        d.text((tx + 7 * S, ty + 7 * S), title, font=f, fill=PINK + (255,), anchor="ms")
    d.text((tx, ty), title, font=f, fill=INK + (255,), anchor="ms")
    sub = "SATURDAY!!! 10AM!!!" if level >= 5 else "Saturday · 10am"
    sw = 700 if level >= 1 else 500
    ss = fit_size(sub, 36, sw, PW - 80)
    d.text(P(PW / 2, 214), sub, font=font(ss * S, sw), fill=(INK if level >= 2 else MUTED) + (255,), anchor="ms")
    cupcake(d, PW / 2, 312)
    if level >= 4:
        sticker(img, "WOW!", P(PW - 22, 16), 72, 14)
    if level >= 5:
        sticker(img, "!!!", P(30, PH - 26), 58, -12, fill=BLUE)
    return img.resize((PW + 2 * MG, PH + 2 * MG), Image.LANCZOS)


POSTERS = [poster(lv) for lv in range(5)]
P_MAX = [poster(5, c) for c in (PINK, BLUE, GREEN)]


def level_at(t):
    return sum(1 for s in STEPS if t >= s)


def draw_poster(fr, t):
    pc = prog(t, 1.2, 1.5)
    if pc <= 0 or t >= T_POP:
        return
    lv = level_at(t)
    s = 0.85 + 0.15 * ease_out_back(pc)
    a = clamp01(pc * 2.5)
    if lv:
        ts = STEPS[lv - 1]
        s *= 1 + 0.08 * math.sin(math.pi * prog(t, ts, ts + 0.3))
    ang = -5 * ease_out_back(prog(t, STEPS[3], STEPS[3] + 0.35)) if lv >= 4 else 0.0
    dx = dy = 0.0
    if lv >= 5:
        s *= 1 + 0.035 * math.sin(2 * math.pi * 4 * (t - STEPS[4]))
        dx = 5 * math.sin(2 * math.pi * 17 * t)
        dy = 4 * math.cos(2 * math.pi * 13 * t)
    sw = prog(t, T_SWELL, T_POP)
    if sw > 0:  # about to burst
        s *= 1 + 0.2 * sw * sw
        amp = 6 + 20 * sw
        dx = amp * math.sin(2 * math.pi * 23 * t)
        dy = amp * math.cos(2 * math.pi * 19 * t)
    img = P_MAX[int(t * 8) % 3] if lv >= 5 else POSTERS[lv]
    if ang:
        img = img.rotate(ang, resample=Image.BICUBIC, expand=True)
    img = scaled(img, s)
    x, y = CX - img.width / 2 + dx, P_CY - img.height / 2 + dy
    comp(fr, with_alpha(silhouette(img, SHADOW), a), x, y + 16)
    comp(fr, with_alpha(img, a), x, y)


# ------------------------------------------------------------------ the pop

def make_particles(n=150):
    rng = random.Random(42)
    out = []
    for _ in range(n):
        x = CX + rng.uniform(-PW / 2, PW / 2) * 1.2
        y = P_CY + rng.uniform(-PH / 2, PH / 2) * 1.2
        ang = math.atan2(y - P_CY, x - CX) + rng.uniform(-0.5, 0.5)
        sp = rng.uniform(450, 1400)
        vx, vy = sp * math.cos(ang), sp * math.sin(ang) - rng.uniform(250, 750)
        out.append((x, y, vx, vy, rng.uniform(14, 26), rng.uniform(8, 14), rng.uniform(0, 6.28),
                    rng.uniform(-12, 12), rng.uniform(0, 6.28), rng.choice(CONFETTI)))
    return out


PARTS = make_particles()
DRAG, V_FALL = 2.2, 270.0


def draw_particles(fr, t, fit=None):
    """Confetti, drawn straight onto the final frame (mapped through `fit`) so it can fly
    past the edges of the shrunken content."""
    k = t - T_POP
    if k < 0:
        return
    d = ImageDraw.Draw(fr)
    f = (1 - math.exp(-DRAG * k)) / DRAG
    s = fit[0] if fit else 1.0
    for x, y, vx, vy, w, h, r0, vr, ph, c in PARTS:
        px = x + vx * f + 18 * math.sin(2 * math.pi * 0.8 * k + ph) * clamp01(k * 2)
        py = y + V_FALL * k + (vy - V_FALL) * f
        if fit:
            px, py = fit_point(px, py, fit)
        if py > H + 40 or px < -40 or px > W + 40:
            continue
        w, h = w * s, h * s
        a = r0 + vr * k
        ww = w * abs(math.cos(a * 0.7)) + 2
        ca, sa = math.cos(a), math.sin(a)
        pts = [(px + ca * qx - sa * qy, py + sa * qx + ca * qy)
               for qx, qy in ((-ww / 2, -h / 2), (ww / 2, -h / 2), (ww / 2, h / 2), (-ww / 2, h / 2))]
        d.polygon(pts, fill=c + (255,))


def draw_flash(fr, t):
    k = prog(t, T_POP, T_POP + 0.3)
    if k <= 0 or k >= 1:
        return
    r = 60 + 560 * ease_out_cubic(k)
    ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    a = int(230 * (1 - k))
    kf = prog(t, T_POP, T_POP + 0.08)  # brief bright core, gone before the ring settles
    if kf < 1:
        rf = 120 + 260 * ease_out_cubic(kf)
        d.ellipse((CX - rf, P_CY - rf, CX + rf, P_CY + rf), fill=(255, 240, 190, int(255 * (1 - kf) ** 2)))
    d.ellipse((CX - r, P_CY - r, CX + r, P_CY + r), outline=(255, 255, 255, a), width=int(34 * (1 - k)) + 4)
    fr.alpha_composite(ov)


# ------------------------------------------------------------------ frame

M_X, M_Y, M_S = CX - 193, 1110, 380


def mascot_state(t):
    if t < STEPS[0]:
        return "normal"
    if t < T_SWELL:
        return "proud"
    if t < T_WHISTLE:
        return "shock"
    return "whistle"


def draw_frame(t):
    fr = canvas()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, 270 - 24 * (1 - p))
    pb = prog(t, 0.15, 0.45)
    if pb > 0:
        place_center(fr, BUBBLE, CX, 420, alpha=clamp01(pb * 2.5), scale=0.85 + 0.15 * ease_out_back(pb))
    draw_poster(fr, t)
    draw_flash(fr, t)
    place_text(fr, CAP_ON_IT, CX, CAP_Y + 16 * (1 - ease_out_cubic(prog(t, 2.0, 2.25))), alpha=fade_window(t, 2.0, 3.1))
    pe = prog(t, T_POP + 0.25, T_POP + 0.5)
    if pe > 0:
        place_text(fr, CAP_END, CX, CAP_Y, alpha=pe, scale=0.85 + 0.15 * ease_out_back(pe))
    my = draw_mascot(fr, t, mascot_state(t), hop=(STEPS[0], STEPS[0] + 0.35), x=M_X, y=M_Y, size=M_S)
    draw_sweat_at(fr, t, M_X, my, M_S, T_WHISTLE + 0.1)
    return finish(fr, OLD_LAYOUT_FIT, under=lambda out: draw_particles(out, t, OLD_LAYOUT_FIT))


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (0.45, A.sfx_whoosh(0.5, 0.2)), (1.2, A.sfx_pop())]
    for ts, m in zip(STEPS, (76, 79, 83, 86, 88)):  # rising arpeggio, one note per upgrade
        ev += [(ts, A.sfx_pop()), (ts + 0.02, A.sfx_ding(A.midi_hz(m), 0.22))]
    ev += [(STEPS[4], A.sfx_rise(T_POP - STEPS[4], 0.14)), (T_POP, A.sfx_boom(1.0)),
           (T_POP + 0.05, A.sfx_whoosh(0.7, 0.16)), (T_WHISTLE, A.sfx_whistle(0.22))]
    curve = [(0, 1), (T_POP - 0.04, 1), (T_POP + 0.02, 0), (DUR, 0)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
