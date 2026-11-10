"""Original music beds and sound effects for Captcha Failed videos.

Everything is synthesized here (Karplus-Strong plucks, sines, filtered noise):
no samples, no third-party recordings, so there is nothing to license.
"""
import subprocess
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t_axis(n):
    return np.arange(n) / SR


def env(n, attack=0.003, tau=0.25):
    t = t_axis(n)
    return np.clip(t / max(attack, 1e-4), 0, 1) * np.exp(-t / tau)


def lowpass(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2), btype="low")
    return lfilter(b, a, x)


def highpass(x, hz, order=2):
    b, a = butter(order, hz / (SR / 2), btype="high")
    return lfilter(b, a, x)


def bandpass(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return lfilter(b, a, x)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


# ------------------------------------------------------------- instruments

def pluck(freq, dur=0.6, decay=0.996, soft=0.45, tau=0.25, seed=0):
    """Karplus-Strong string, computed one period-block at a time."""
    rng = np.random.default_rng(seed)
    N = max(2, int(round(SR / freq)))
    n = int(SR * dur)
    y = np.zeros(N + 1 + n)
    burst = rng.uniform(-1, 1, N)
    y[1:N + 1] = lfilter([1 - soft], [1, -soft], burst)
    pos = N + 1
    while pos < len(y):
        end = min(pos + N, len(y))
        idx = np.arange(pos, end)
        y[pos:end] = decay * 0.5 * (y[idx - N] + y[idx - N - 1])
        pos = end
    return norm(y[N + 1:]) * env(n, 0.002, tau)


def tone(freq, dur, tau=0.4, partials=((1, 1.0),), attack=0.003):
    n = int(SR * dur)
    t = t_axis(n)
    x = sum(a * np.sin(2 * np.pi * freq * k * t) for k, a in partials)
    return norm(x) * env(n, attack, tau)


def sweep(f0, f1, dur, tau=None, shape="exp"):
    n = int(SR * dur)
    t = t_axis(n)
    if shape == "exp":
        f = f0 * (f1 / f0) ** (t / dur)
    else:
        f = f0 + (f1 - f0) * t / dur
    phase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(phase)
    return x * (env(n, 0.002, tau) if tau else np.hanning(n))


def noise(dur, seed=1):
    return np.random.default_rng(seed).uniform(-1, 1, int(SR * dur))


# ---------------------------------------------------------------- effects

def sfx_click():
    a = highpass(noise(0.03, 3), 2000) * env(int(0.03 * SR), 0.0005, 0.004)
    b = tone(3200, 0.03, tau=0.006)
    return norm(a * 0.6 + b * 0.5) * 0.55


def sfx_pop():
    return sweep(900, 260, 0.08, tau=0.045) * 0.5


def sfx_blip():
    return sweep(1100, 1900, 0.09, tau=0.05) * 0.3


def sfx_whoosh(dur=0.4, gain=0.3):
    n = int(SR * dur)
    x = bandpass(noise(dur, 5), 300, 2200)
    return norm(x) * np.sin(np.pi * np.arange(n) / n) ** 2 * gain


def sfx_ding(freq=1318.5, gain=0.35):
    return tone(freq, 1.0, tau=0.5, partials=((1, 1.0), (2.0, 0.3), (3.01, 0.1))) * gain


def sfx_tada(gain=0.35):
    out = np.zeros(int(1.3 * SR))
    for i, m in enumerate((84, 88, 91, 96)):  # C6 E6 G6 C7
        d = tone(midi_hz(m), 1.0, tau=0.45, partials=((1, 1.0), (2.0, 0.25)))
        s = int(i * 0.07 * SR)
        out[s:s + len(d)] += d
    return norm(out) * gain


def sfx_buzz(dur=0.42, gain=0.3):
    n = int(SR * dur)
    t = t_axis(n)
    x = np.sign(np.sin(2 * np.pi * 110 * t)) + np.sign(np.sin(2 * np.pi * 117 * t))
    x = lowpass(x, 1800)
    e = np.clip(t / 0.005, 0, 1) * np.clip((dur - t) / 0.06, 0, 1)
    return norm(x * e) * gain


def sfx_thud(gain=0.9):
    body = sweep(95, 50, 0.3, tau=0.16)
    hit = lowpass(noise(0.05, 9), 900) * env(int(0.05 * SR), 0.0005, 0.02)
    out = np.zeros(len(body))
    out[:len(hit)] += norm(hit) * 0.5
    return norm(out + body) * gain


def sfx_scribble(dur=0.35, gain=0.22):
    n = int(SR * dur)
    x = bandpass(noise(dur, 11), 2000, 6000)
    gate = (np.sin(2 * np.pi * 13 * t_axis(n)) > -0.2).astype(float)
    return norm(lowpass(gate, 80) * x) * gain


def sfx_tick(gain=0.25):
    return norm(tone(1800, 0.05, tau=0.012) + tone(2700, 0.05, tau=0.008) * 0.5) * gain


def sfx_zip(up=True, gain=0.22):
    return (sweep(300, 1200, 0.14, tau=0.09) if up else sweep(1200, 300, 0.14, tau=0.09)) * gain


def sfx_bonk(gain=0.45):
    return sweep(260, 110, 0.22, tau=0.12) * gain


def sfx_typing(dur=1.6, rate=12, gain=0.35, seed=21):
    """Keyboard clatter: short clicks at slightly random intervals."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(SR * dur) + SR // 10)
    t = 0.0
    while t < dur:
        k = sfx_click() * rng.uniform(0.5, 1.0)
        s = int(t * SR)
        out[s:s + len(k)] += k[: len(out) - s]
        t += rng.uniform(0.6, 1.4) / rate
    return norm(out) * gain


def sfx_boom(gain=0.9):
    """Confetti-cannon pop: low thump plus a bright noise burst."""
    body = sweep(120, 45, 0.45, tau=0.2)
    burst = highpass(noise(0.35, 13), 900) * env(int(0.35 * SR), 0.001, 0.08)
    out = np.zeros(len(body))
    out[:len(burst)] += norm(burst) * 0.6
    return norm(out + body) * gain


def sfx_rise(dur=2.4, gain=0.18):
    """Tension riser: sine gliding up with a little wobble."""
    n = int(SR * dur)
    t = t_axis(n)
    f = 220 * (4 ** (t / dur)) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return x * np.clip(t / 0.3, 0, 1) * np.clip((dur - t) / 0.05, 0, 1) * gain


def sfx_whistle(gain=0.2):
    """Innocent little whistle: a few sine notes with a touch of vibrato."""
    notes = ((83, 0.16), (88, 0.16), (86, 0.28), (83, 0.16), (84, 0.5))
    parts = []
    for m, d in notes:
        n = int(SR * d)
        t = t_axis(n)
        ph = 2 * np.pi * np.cumsum(midi_hz(m) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))) / SR
        x = np.sin(ph) + 0.08 * np.sin(2 * ph)
        parts.append(x * np.clip(t / 0.025, 0, 1) * np.clip((d - t) / 0.05, 0, 1))
        parts.append(np.zeros(int(SR * 0.03)))
    return np.concatenate(parts) * gain

def sfx_crickets(dur=1.6, gain=0.12):
    """Awkward-silence crickets: trains of short 4.3 kHz pulses."""
    n = int(SR * dur)
    t = t_axis(n)
    carrier = np.sin(2 * np.pi * 4300 * t)
    pulses = (np.sin(2 * np.pi * 28 * t) > 0.3).astype(float)
    chirp_gate = ((t % 0.42) < 0.16).astype(float)
    x = carrier * lowpass(pulses * chirp_gate, 400)
    return norm(x) * gain


# ------------------------------------------------------------------ beds

PATTERNS = {
    # Tiptoeing D minor, staccato, with a chromatic lean into A.
    "sneaky": dict(
        bpm=116,
        melody=[[62, None, 65, None, 69, None, 68, 69],
                [74, None, 72, 69, None, 65, 64, None],
                [62, None, 65, None, 69, None, 70, 69],
                [67, None, 64, 61, None, 62, None, None]],
        bass=[[38, 45, 38, 45], [38, 45, 41, 45], [38, 45, 38, 45], [33, 40, 33, 38]],
    ),
    # Bright C major, bouncy.
    "bouncy": dict(
        bpm=124,
        melody=[[72, None, 76, 79, None, 76, None, 72],
                [74, None, 77, 81, None, 77, 74, None],
                [76, None, 79, 84, None, 79, None, 76],
                [74, 71, 67, None, 72, None, None, None]],
        bass=[[48, 55, 48, 55], [50, 57, 50, 57], [52, 59, 48, 55], [43, 50, 48, None]],
    ),
}


def reverb(x, mix=0.16):
    wet = np.zeros_like(x)
    for d, g in ((1557, 0.77), (1617, 0.75), (1491, 0.73), (1422, 0.71)):
        a = np.zeros(d + 1)
        a[0], a[d] = 1, -g
        wet += lfilter([1], a, x)
    wet /= 4
    for d, g in ((225, 0.7), (556, 0.7)):
        b = np.zeros(d + 1)
        a = np.zeros(d + 1)
        b[0], b[d] = -g, 1
        a[0], a[d] = 1, -g
        wet = lfilter(b, a, wet)
    return x * (1 - mix) + wet * mix


def bed(kind, duration):
    p = PATTERNS[kind]
    eighth = 60 / p["bpm"] / 2
    n = int(duration * SR) + SR
    mel = np.zeros(n)
    bas = np.zeros(n)
    perc = np.zeros(n)
    cache = {}

    def note(m, dur, tau, decay, seed):
        key = (m, dur, tau, decay)
        if key not in cache:
            cache[key] = pluck(midi_hz(m), dur, decay=decay, tau=tau, seed=seed)
        return cache[key]

    t = 0.0
    bar = 0
    while t < duration:
        mb = p["melody"][bar % 4]
        bb = p["bass"][bar % 4]
        for i, m in enumerate(mb):
            if m is not None:
                s = int((t + i * eighth) * SR)
                x = note(m, 0.5, 0.16, 0.997, m)
                mel[s:s + len(x)] += x[: max(0, n - s)]
        for i, m in enumerate(bb):
            s = int((t + i * 2 * eighth) * SR)
            if m is not None:
                x = note(m, 0.7, 0.3, 0.998, m + 100)
                bas[s:s + len(x)] += x[: max(0, n - s)]
            if i in (1, 3):
                k = sfx_tick(1.0)
                perc[s:s + len(k)] += k[: max(0, n - s)]
        t += 8 * eighth
        bar += 1
    mix = mel * 0.5 + lowpass(bas, 700) * 0.62 + perc * 0.12
    return reverb(mix)[: int(duration * SR)]


# ------------------------------------------------------------------- mix

def mix(duration, kind, events, bed_gain=0.42, bed_curve=None):
    """events: [(time_s, samples)]. bed_curve: [(t, gain), ...] breakpoints."""
    n = int(duration * SR)
    out = np.zeros(n)
    b = norm(bed(kind, duration)) * bed_gain
    if bed_curve:
        ts, gs = zip(*bed_curve)
        b *= np.interp(t_axis(n), ts, gs)
    out += b
    for t, x in events:
        s = int(t * SR)
        if s < n:
            out[s:s + len(x)] += x[: n - s]
    fade = int(0.35 * SR)
    out[-fade:] *= np.linspace(1, 0, fade)
    # phones play quietly: bring the average level up, then round off the peaks
    out *= 0.16 / (np.sqrt(np.mean(out ** 2)) or 1)
    out = np.tanh(out / 0.9) * 0.9
    out = norm(out, 0.89)
    left = out
    right = np.concatenate([np.zeros(12), out[:-12]])
    return np.stack([left, right], axis=1)


def write_wav(path, stereo):
    data = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def mux(video_path, wav_path, out_path):
    tmp = out_path[:-4] + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_path, "-i", wav_path,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    import os
    os.replace(tmp, out_path)
    return out_path
