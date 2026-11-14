"""Contact sheet of slides or stills with TikTok's UI shaded: python3 preview.py out.png [--photo] img1 img2 ..."""
import sys

from PIL import Image

from cf_lib import ui_overlay

out, args = sys.argv[1], sys.argv[2:]
photo = "--photo" in args
paths = [a for a in args if a != "--photo"]
w, h, g = 300, 533, 8
cols = min(6, len(paths))
rows = (len(paths) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + g), rows * (h + g)), (255, 255, 255))
for k, p in enumerate(paths):
    sheet.paste(ui_overlay(Image.open(p), photo=photo).resize((w, h), Image.LANCZOS), ((k % cols) * (w + g), (k // cols) * (h + g)))
sheet.save(out)
print(out)
