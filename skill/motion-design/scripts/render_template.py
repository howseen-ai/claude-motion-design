"""frame. film renderer.
probe t1 t2 ...  -> probe/p_XX.png + probe/sheet.png (4 columns)
beats            -> one frame per beat (54) -> probe/beats.png
draft            -> 30 fps, 1 capture per frame, 960x540, crf 23 veryfast -> out/draft.mp4 (judge rhythm, not sharpness)
full             -> SUB subframes per frame on a SHUTTER (0.5 = 180 deg) blended with tmix, 60 fps -> out/crave_video.mp4
pops             -> scan out/crave_video.mp4 for single-frame pops (diff spikes 3x their neighbours)
loop             -> loop seam check: frame 0 vs last (position) and first vs last motion (velocity)
WEBGL=1 env      -> launch Chromium with SwiftShader/ANGLE flags (headless WebGL renders black otherwise)
"""
import asyncio, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from playwright.async_api import async_playwright

HERE = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
URL = "http://localhost:8767/crave.html"
FPS, T, SUB = 60, 32 * 60 / 130, 8
SHUTTER = 0.5  # fraction of the frame interval the subframes cover (0.5 = 180 deg film look, 1.0 = smeary)
CUTS = []      # hard-cut times (s): subframes never straddle a cut (no double exposure on the cut frame)
ARGS = ["--autoplay-policy=no-user-gesture-required"]
if os.environ.get("WEBGL"): ARGS += ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]


async def open_page(p):
    b = await p.chromium.launch(args=ARGS)
    pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type in ("error", "warning") else None)
    await pg.goto(URL)
    await pg.wait_for_function("window.ready === true", timeout=120000)
    await pg.evaluate("document.fonts.ready")
    # freeze anything that would run on the wall clock (stray CSS animations/transitions, Web Animations)
    await pg.add_style_tag(content="*,*::before,*::after{transition:none!important;caret-color:transparent!important}")
    await pg.evaluate("document.getAnimations().forEach(a => a.pause())")
    return b, pg, errs


async def shot(pg, t, path, fmt="png"):
    await pg.evaluate(f"window.seek({t})")
    # 2 rAF: let layout/paint of the seeked frame land before the capture
    await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
    el = await pg.query_selector("#stage")
    await el.screenshot(path=str(path), type=fmt, **({"quality": 95} if fmt == "jpeg" else {}))


def sheet(folder, pattern, n, out, cols=4, size=360):
    rows = -(-n // cols)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(folder / pattern), "-vf",
                    f"scale={size}:-1,tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", str(out)], check=True)


async def probe(times, name="sheet.png", cols=4):
    out = HERE / "probe"; shutil.rmtree(out, ignore_errors=True); out.mkdir()
    async with async_playwright() as p:
        b, pg, errs = await open_page(p)
        for i, t in enumerate(times): await shot(pg, t, out / f"p_{i:02d}.png")
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    sheet(out, "p_%02d.png", len(times), out / name, cols=cols)
    print("probe:", len(times), "->", out / name)


async def full():
    sub = HERE / "sub"; shutil.rmtree(sub, ignore_errors=True); sub.mkdir()
    n, k = int(round(T * FPS)), 0
    offs = [(j - (SUB - 1) / 2) * SHUTTER / (FPS * SUB) for j in range(SUB)]
    async with async_playwright() as p:
        b, pg, errs = await open_page(p)
        for i in range(n):
            for o in offs:
                t = min(T - 1e-3, max(0.0, i / FPS + o))
                for c in CUTS:  # keep every subframe on the same side of a cut as the frame centre
                    if (t < c) != (i / FPS < c): t = c if i / FPS >= c else c - 1e-4
                await shot(pg, t, sub / f"s_{k:05d}.jpg", "jpeg"); k += 1
            if i % 60 == 0: print(f"frame {i}/{n}", flush=True)
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    (HERE / "out").mkdir(exist_ok=True)
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS * SUB), "-i", str(sub / "s_%05d.jpg"),
                    "-vf", f"tmix=frames={SUB},select='eq(mod(n\\,{SUB})\\,{SUB - 1})',setpts=N/{FPS}/TB", "-r", str(FPS),
                    "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", str(HERE / "out/crave_video.mp4")], check=True)
    print("video ->", HERE / "out/crave_video.mp4")


async def draft(fps=30):
    sub = HERE / "sub_draft"; shutil.rmtree(sub, ignore_errors=True); sub.mkdir()
    n = int(round(T * fps))
    async with async_playwright() as p:
        b, pg, errs = await open_page(p)
        for i in range(n): await shot(pg, min(T - 1e-3, i / fps), sub / f"d_{i:05d}.jpg", "jpeg")
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    (HERE / "out").mkdir(exist_ok=True)
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(fps), "-i", str(sub / "d_%05d.jpg"), "-vf", "scale=960:-2",
                    "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", str(HERE / "out/draft.mp4")], check=True)
    print("draft ->", HERE / "out/draft.mp4")


def frames_gray(path, size=180):
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(path), "-vf", f"scale={size}:{size},format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, size, size).astype(np.float32)


def loop_check(path=None):
    """A loop must match in position AND velocity: last frame ~ frame 0, and the motion entering frame 0
    (last -> 0) ~ the motion leaving it (0 -> 1). Fix velocity by adding the spring tails of the previous cycle."""
    fr = frames_gray(path or HERE / "out/crave_video.mp4")
    steps = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    seam = np.abs(fr[-1] - fr[0]).mean()
    med = float(np.median(steps)) or 0.3
    print(f"seam diff {seam:.2f} (median frame step {med:.2f}) -> {'OK' if seam <= 2 * med else 'JUMP: fix positions at t=0/T'}")
    vin, vout = np.abs(fr[-1] - fr[-2]).mean(), np.abs(fr[1] - fr[0]).mean()
    print(f"velocity in {vin:.2f} / out {vout:.2f} -> {'OK' if abs(vin - vout) <= max(1.0, 0.5 * max(vin, vout)) else 'SPEED BREAK at the seam'}")


def pops(path=None):
    path = path or HERE / "out/crave_video.mp4"
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(path), "-vf", "scale=180:180,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 180, 180).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    hits = []
    for i in range(1, len(d) - 1):
        nb = max(d[i - 1], d[i + 1], 0.3)
        if d[i] > 3 * nb and d[i] > 2.0: hits.append((i + 1, round((i + 1) / FPS, 3), round(float(d[i]), 2), round(float(nb), 2)))
    print("pops:", len(hits))
    for h in hits: print("  frame", h[0], "t", h[1], "diff", h[2], "neighbours", h[3])
    # one-frame flash: two big diffs side by side mask each other above; frame n differs from both
    # neighbours while n-1 and n+1 look alike
    flashes = []
    for n in range(1, len(fr) - 1):
        a, b = d[n - 1], d[n]
        skip = np.abs(fr[n + 1] - fr[n - 1]).mean()
        if min(a, b) > 2.0 and skip < 0.35 * min(a, b): flashes.append((n, round(n / FPS, 3), round(float(min(a, b)), 2), round(float(skip), 2)))
    print("one-frame flashes:", len(flashes))
    for f in flashes: print("  frame", f[0], "t", f[1], "diff", f[2], "n-1 vs n+1", f[3])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "probe": asyncio.run(probe([float(x) for x in sys.argv[2:]]))
    elif cmd == "beats": asyncio.run(probe([b * 60 / 130 + 0.45 for b in range(32)], "beats.png", cols=9))
    elif cmd == "draft": asyncio.run(draft())
    elif cmd == "full": asyncio.run(full())
    elif cmd == "pops": pops()
    elif cmd == "loop": loop_check()
