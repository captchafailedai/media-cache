"""Soundtrack for post 1 (captcha): sneaky bed that cuts out on ACCESS DENIED."""
import cf_audio as A

DUR = 11.0
events = [
    (0.20, A.sfx_pop()),
    (0.55, A.sfx_whoosh(0.5, 0.2)),
    (1.30, A.sfx_whoosh(1.4, 0.12)),
    (3.00, A.sfx_pop()),
    (5.15, A.sfx_pop()),
    (5.30, A.sfx_blip()),
    (7.15, A.sfx_scribble()),
    (7.60, A.sfx_whoosh(0.35, 0.12)),
    (7.96, A.sfx_click()),
    (8.00, A.sfx_ding()),
    (8.70, A.sfx_thud()),
    (8.72, A.sfx_buzz()),
    (9.20, A.sfx_tada()),
]
# music stops dead on the stamp, then comes back for "worth it."
curve = [(0, 1), (8.66, 1), (8.70, 0), (9.15, 0), (9.35, 1), (DUR, 1)]
stereo = A.mix(DUR, "sneaky", events, bed_gain=0.45, bed_curve=curve)
A.write_wav("/home/claude/tiktok/post01.wav", stereo)
A.mux("/home/claude/tiktok/joined.mp4", "/home/claude/tiktok/post01.wav",
      "/home/claude/tiktok/captcha_failed_01.mp4")
print("ok")
