"""QA sheets: ref|ours per second (2 pages) + group seams (last 2 / first 2 frames) + old-brand colour scan."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
H = Path(__file__).parent
Q = H / "out/qa"; Q.mkdir(parents=True, exist_ok=True)
def pair(F):
    r = Image.open(H / f"ref/full/f{F:04d}.jpg").convert("RGB").resize((480, 270))
    o = Image.open(H / f"out/full/o_f{F:04d}.png").convert("RGB").resize((480, 270))
    c = Image.new("RGB", (970, 290), "white"); c.paste(r, (0, 20)); c.paste(o, (490, 20))
    ImageDraw.Draw(c).text((4, 4), f"F{F}", fill="red"); return c
def sheet(frames, name, cols=3):
    tiles = [pair(F) for F in frames]; rows = -(-len(tiles) // cols)
    s = Image.new("RGB", (cols * 970, rows * 290), "white")
    for i, t in enumerate(tiles): s.paste(t, ((i % cols) * 970, (i // cols) * 290))
    s.save(Q / name, quality=78)
secs = list(range(0, 1557, 24))
sheet(secs[:33], "persec_1.jpg"); sheet(secs[33:], "persec_2.jpg")
sheet([526, 527, 528, 529, 902, 903, 904, 905, 906, 907, 1152, 1153, 1154, 1155], "seams.jpg", cols=2)
# old-brand colour scan: reddish/orange saturated pixels in ours
bad = []
for F in range(0, 1557, 4):
    a = np.asarray(Image.open(H / f"out/full/o_f{F:04d}.png").convert("RGB").resize((480, 270)), dtype=np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (r > 180) & (r - g > 60) & (r - b > 60) & (g > 60)
    if m.sum() > 150: bad.append((F, int(m.sum())))
print("old-brand-colour frames:", bad[:40], "count", len(bad))
