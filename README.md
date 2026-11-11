# media-cache

Video and image files for scheduled posts, plus the scripts that render them (tools/).
Font: Bricolage Grotesque (OFL) from github.com/google/fonts.

## Notes

- Each `tools/postNN.py` supports `python3 postNN.py stills 1.5 4.0 …` (check frames) and `python3 postNN.py render`.
  Shared look and sound live in `tools/cf_lib.py` and `tools/cf_audio.py`.
- Link media by commit (`raw.githubusercontent.com/<owner>/<repo>/<sha>/posts/...`): branch links are cached
  for a few minutes after a push, so a re-rendered file can still serve the old copy.
- Videos: make sure frame 1 already shows the hook, and pick a cover frame with the hook plus the key visual.
- TikTok photo posts accept only JPEG or WebP (a PNG is accepted at scheduling but rejected when it publishes),
  so export slides as `.jpg` (quality 95, 4:4:4).
