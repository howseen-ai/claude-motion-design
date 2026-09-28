"""Phase 0: extract all frames + audio, detect cuts by mean-abs-diff spikes, build per-cut contact sheets."""
import subprocess, json
from pathlib import Path
import numpy as np, imageio_ffmpeg
from PIL import Image
FF = imageio_ffmpeg.get_ffmpeg_exe()
H = Path(__file__).parent
ref = H / "ref/reference.mp4"
full = H / "ref/full"; full.mkdir(parents=True, exist_ok=True)
if not any(full.iterdir()):
    subprocess.run([FF, "-v", "error", "-i", str(ref), "-start_number", "0", "-q:v", "3", str(full / "f%04d.jpg")], check=True)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(ref), "-vn", "-ac", "2", "-ar", "48000", str(H / "ref/audio.wav")], check=True)
frames = sorted(full.glob("f*.jpg"))
print("frames", len(frames))
small = [np.asarray(Image.open(f).convert("L").resize((192, 108)), dtype=np.float32) for f in frames]
d = np.array([0.0] + [np.abs(small[i] - small[i - 1]).mean() for i in range(1, len(small))])
np.save(H / "ref/diff.npy", d)
# spike = diff much larger than local median
cuts = []
for i in range(1, len(d)):
    lo, hi = max(1, i - 6), min(len(d), i + 7)
    loc = np.median(np.concatenate([d[lo:i], d[i + 1:hi]])) if hi - lo > 1 else 0
    if d[i] > 6 and d[i] > 3.5 * (loc + 0.5):
        cuts.append(i)
print("cuts", cuts)
json.dump({"fps": 24, "n": len(frames), "cuts": cuts, "diff": [round(float(x), 2) for x in d]}, open(H / "ref/cuts.json", "w"))
# contact sheet: every 6th frame with frame numbers, 2 per second
thumbs = []
for i in range(0, len(frames), 6):
    im = Image.open(frames[i]).resize((256, 144))
    thumbs.append((i, im))
cols = 10
from PIL import ImageDraw
for page in range(0, len(thumbs), 80):
    chunk = thumbs[page:page + 80]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 256, rows * 160), "white")
    dr = ImageDraw.Draw(sheet)
    for k, (i, im) in enumerate(chunk):
        x, y = (k % cols) * 256, (k // cols) * 160
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + 146), f"f{i}" + (" CUT" if i in cuts else ""), fill="red")
    sheet.save(H / f"ref/sheet/sheet_{page // 80}.jpg", quality=80)
print("sheets done")
