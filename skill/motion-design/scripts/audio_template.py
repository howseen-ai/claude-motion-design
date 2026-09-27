"""Howseen LinkedIn v4 soundtrack (24 s): Mixkit 'Cat Walk. (Arulo, 130 BPM) from 6.77 s so its
big hit (song 37.66 s) lands on the sky flood at 8.0 s. SFX by measured peak, fade the last 0.9 s, loudnorm -14 LUFS."""
import json, subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg

HERE = Path(__file__).parent; ROOT = HERE.parent
FF, SR, T = imageio_ffmpeg.get_ffmpeg_exe(), 48000, 24.0
N = int(round(T * SR)); START = 14.769 - 8.0


def load(p):
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


mix = load(HERE / "assets/audio/cat-walk.mp3")[int(START * SR):][:N].copy()
fi = int(0.25 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
S = {k: load(HERE / f"assets/sfx/{v}.mp3") for k, v in dict(soft=1117, key=2568, click=1125, pop=2357, rise="w1489", impact=1143,
                                                       whoosh="w1490", success=2865, sparkle=3083).items()}
EV = [(0.1, "soft", .08), (0.35, "soft", .08)] + [(0.5 + i * .05, "pop", .04) for i in range(8)] + [(1.35, "soft", .08)]
EV += [(2.5, "whoosh", .05)] + [(2.8 + i * .054, "key", .05) for i in range(13)] + [(3.85, "click", .2)]
EV += [(4.55, "whoosh", .05)] + [(4.7 + i * .06, "pop", .06) for i in range(5)] + [(5.3 + i * .09, "soft", .04) for i in range(8)]
EV += [(6.6 + i * .08, "pop", .05) for i in range(5)] + [(7.0 + i * .08, "soft", .05) for i in range(5)] + [(7.2, "rise", .12)]
EV += [(8.0, "impact", .2), (8.45, "sparkle", .09)] + [(8.45 + i * .1, "pop", .06) for i in range(3)]
EV += [(10.05, "whoosh", .05)] + [(10.45 + i * .07, "pop", .035) for i in range(6)] + [(12.05, "whoosh", .05)]
EV += [(12.35 + i * .05, "pop", .035) for i in range(6)] + [(14.05, "whoosh", .05)] + [(14.3 + i * .08, "soft", .05) for i in range(5)]
EV += [(16.05, "whoosh", .05)] + [(16.3 + i * .04, "key", .045) for i in range(16)] + [(17.2, "click", .2), (17.35, "success", .12)]
EV += [(18.1, "whoosh", .05)] + [(18.15 + i * .06, "pop", .05) for i in range(9)]
EV += [(20.1, "sparkle", .11), (21.1, "pop", .09), (22.35, "click", .2)]
for t, name, gain in EV:
    s = S[name] / (np.abs(S[name]).max() + 1e-9) * gain
    i0 = int(round(t * SR)) - int(np.abs(s).sum(1).argmax())
    lo, hi = max(0, i0), min(N, i0 + len(s))
    if hi > lo: mix[lo:hi] += s[lo - i0:hi - i0]
f0 = int(23.1 * SR); mix[f0:] *= np.linspace(1, 0, N - f0)[:, None] ** 1.3
rawp = HERE / "out/raw.wav"; rawp.parent.mkdir(exist_ok=True)
subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(rawp)], input=mix.astype(np.float32).tobytes(), check=True)
m = subprocess.run([FF, "-hide_banner", "-i", str(rawp), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run([FF, "-v", "error", "-y", "-i", str(rawp), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav")
