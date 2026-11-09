"""Post 4: "can you make it shorter?" -> shortens until nothing is left."""
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_04"
DUR = 10.5

HOOK = text_sprite("POV: a human asks", 84, 800, WHITE, max_w=SAFE_W)
BUBBLE = chat_bubble("can you make it shorter?", 60, 600, max_w=840)
CAP_ON_IT = text_sprite("on it.", 72, 800, WHITE)
CAP_END = text_sprite("you said shorter.", 80, 800, SUN, max_w=SAFE_W)

DRAFTS = [  # (start time, text)
    (1.2, "Thanks so much for reaching out! I wanted to follow up on our chat from last week about the "
          "schedule, and share a few ideas on how we could move things forward together."),
    (3.6, "Thanks for reaching out! Following up on last week’s schedule chat with a few ideas."),
    (5.0, "Following up on the schedule."),
    (6.2, "Schedule?"),
    (7.2, "?"),
    (8.0, ""),
]
CARD_W, PAD_X, PAD_TOP, TEXT_SIZE, LH = 820, 44, 104, 42, 56
CARD_TOP = 560


def label_for(i, text):
    words = len(text.split())
    if i >= 4:
        n = len(text)
        return f"DRAFT {i + 1} · {n} character{'s' if n != 1 else ''}"
    return f"DRAFT {i + 1} · {words} word{'s' if words != 1 else ''}"


def card_height(text):
    lines = wrap(text, TEXT_SIZE, 500, CARD_W - 2 * PAD_X) if text else []
    return PAD_TOP + max(1, len(lines)) * LH + 40


def text_layer(i, text, cursor_on):
    """Card contents (label + text) as a transparent layer, card-sized."""
    S = 2
    h = card_height(text)
    img = Image.new("RGBA", (CARD_W * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((PAD_X * S, 62 * S), label_for(i, text), font=font(28 * S, 700), fill=MUTED + (255,), anchor="ls")
    f = font(TEXT_SIZE * S, 500)
    asc = f.getmetrics()[0]
    lines = wrap(text, TEXT_SIZE, 500, CARD_W - 2 * PAD_X) if text else [""]
    for k, s in enumerate(lines):
        d.text((PAD_X * S, (PAD_TOP - 14) * S + asc + k * LH * S), s, font=f, fill=INK + (255,), anchor="ls")
    if cursor_on:
        last = lines[-1]
        x = PAD_X * S + f.getlength(last) + 6 * S
        y0 = (PAD_TOP - 14 + 6 + (len(lines) - 1) * LH) * S
        d.rectangle((x, y0, x + 4 * S, y0 + 46 * S), fill=BG + (255,))
    return img.resize((CARD_W, h), Image.LANCZOS)


_layers = {}


def layer(i, cursor_on=False):
    key = (i, cursor_on)
    if key not in _layers:
        _layers[key] = text_layer(i, DRAFTS[i][1], cursor_on)
    return _layers[key]


def draft_index(t):
    i = 0
    for k, (ts, _) in enumerate(DRAFTS):
        if t >= ts:
            i = k
    return i


def draw_card(fr, t):
    pc = prog(t, 1.2, 1.5)
    if pc <= 0:
        return
    i = draft_index(t)
    ts = DRAFTS[i][0]
    h_now = card_height(DRAFTS[i][1])
    h_prev = card_height(DRAFTS[i - 1][1]) if i > 0 else h_now
    h = int(lerp(h_prev, h_now, ease_out_cubic(prog(t, ts, ts + 0.25))))
    s = 0.85 + 0.15 * ease_out_back(pc)
    a = clamp01(pc * 2.5)
    body = card(CARD_W, h, radius=30)
    x = CX - CARD_W / 2
    comp(fr, with_alpha(scaled(silhouette(body, SHADOW), s), a), x + (1 - s) * CARD_W / 2, CARD_TOP + 16)
    comp(fr, with_alpha(scaled(body, s), a), x + (1 - s) * CARD_W / 2, CARD_TOP)
    # outgoing draft fades quickly, incoming fades in
    if i > 0 and t < ts + 0.12:
        comp(fr, with_alpha(layer(i - 1).crop((0, 0, CARD_W, min(h, layer(i - 1).height))), a * (1 - prog(t, ts, ts + 0.12))), x, CARD_TOP)
    cursor = i == len(DRAFTS) - 1 and int(t * 2) % 2 == 0
    lay = layer(i, cursor)
    comp(fr, with_alpha(lay.crop((0, 0, CARD_W, min(h, lay.height))), a * prog(t, ts + 0.06, ts + 0.24) if i else a), x, CARD_TOP)


def mascot_state(t):
    if t < 3.6:
        return "normal"
    if t < 8.3:
        return "proud"
    return "flat"


def draw_frame(t):
    fr = BASE.copy()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, 270 - 24 * (1 - p))
    pb = prog(t, 0.15, 0.45)
    if pb > 0:
        place_center(fr, BUBBLE, CX, 420, alpha=clamp01(pb * 2.5), scale=0.85 + 0.15 * ease_out_back(pb))
    draw_card(fr, t)
    i = draft_index(t)
    card_bottom = CARD_TOP + card_height(DRAFTS[i][1])
    cap_y = max(card_bottom + 110, 900)
    a = fade_window(t, 3.65, 4.9)
    place_text(fr, CAP_ON_IT, CX, cap_y + 16 * (1 - ease_out_cubic(prog(t, 3.65, 3.9))), alpha=a)
    p3 = prog(t, 8.4, 8.65)
    place_text(fr, CAP_END, CX, cap_y, alpha=p3, scale=0.85 + 0.15 * ease_out_back(p3) if p3 > 0 else 0.85)
    draw_mascot(fr, t, mascot_state(t), size=440, x=CX - 223, y=1050)
    return fr.convert("RGB")


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (0.45, A.sfx_whoosh(0.5, 0.2)), (1.2, A.sfx_pop()),
          (3.65, A.sfx_pop() * 0.6), (8.35, A.sfx_bonk()), (8.6, A.sfx_crickets(1.7))]
    ev += [(ts, A.sfx_zip(False)) for ts, _ in DRAFTS[1:]]
    curve = [(0, 1), (8.2, 1), (8.3, 0), (DUR, 0)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
