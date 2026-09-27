"""Estimate BPM (onset autocorrelation) and print a 1-second energy profile (full + low band) for each file."""
import subprocess, sys
import numpy as np, imageio_ffmpeg
FF, SR = imageio_ffmpeg.get_ffmpeg_exe(), 22050
for f in sys.argv[1:]:
    x = np.frombuffer(subprocess.run([FF, "-v", "quiet", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
    hop = 256; fr = len(x) // hop
    env = np.array([np.sqrt((x[i * hop:(i + 1) * hop] ** 2).mean()) for i in range(fr)])
    on = np.maximum(0, np.diff(np.log(env + 1e-6))); on -= on.mean()
    ac = np.correlate(on[:6000], on[:6000], "full")[5999:]
    fps = SR / hop; lags = np.arange(len(ac)) / fps
    best = max(((60 / l, ac[i]) for i, l in enumerate(lags) if 0.33 < l < 1.0), key=lambda z: z[1])
    print(f"\n== {f.split('/')[-1]}  dur {len(x) / SR:.1f}s  BPM~{best[0]:.1f}")
    lp = np.convolve(x, np.ones(60) / 60, "same")
    row = []
    for s in range(0, int(len(x) / SR)):
        seg = x[s * SR:(s + 1) * SR]; ls = lp[s * SR:(s + 1) * SR]
        row.append(f"{s:3d}:{10 * np.log10((seg ** 2).mean() + 1e-12):5.1f}/{10 * np.log10((ls ** 2).mean() + 1e-12):5.1f}")
    for i in range(0, min(len(row), 48), 6): print("  " + "  ".join(row[i:i + 6]))
