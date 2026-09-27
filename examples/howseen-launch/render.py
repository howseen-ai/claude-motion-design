"""Render film.html frame by frame.
probe t1 t2 ... -> probe/sheet.png | beats -> one frame per beat | full -> N subframes/frame blended with tmix, 60 fps -> out/video.mp4 | pops -> single-frame pop scan.
Serve the folder first: python -m http.server 8000 (FILM_URL overrides the page URL)."""
import asyncio, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from playwright.async_api import async_playwright

HERE = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
import os
URL = os.environ.get("FILM_URL", "http://localhost:8000/film.html")
FPS, T, SUB = 60, 24.0, 8


async def open_page(p):
    b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = await b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type in ("error", "warning") else None)
    await pg.goto(URL)
    await pg.wait_for_function("window.ready === true", timeout=120000)
    return b, pg, errs


async def shot(pg, t, path, fmt="png"):
    await pg.evaluate(f"window.seek({t})")
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
    offs = [(j - (SUB - 1) / 2) / (FPS * SUB) for j in range(SUB)]
    async with async_playwright() as p:
        b, pg, errs = await open_page(p)
        for i in range(n):
            for o in offs:
                t = min(T - 1e-3, max(0.0, i / FPS + o))
                await shot(pg, t, sub / f"s_{k:05d}.jpg", "jpeg"); k += 1
            if i % 60 == 0: print(f"frame {i}/{n}", flush=True)
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    (HERE / "out").mkdir(exist_ok=True)
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS * SUB), "-i", str(sub / "s_%05d.jpg"),
                    "-vf", f"tmix=frames={SUB},select='eq(mod(n\\,{SUB})\\,{SUB - 1})',setpts=N/{FPS}/TB", "-r", str(FPS),
                    "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", str(HERE / "out/video.mp4")], check=True)
    print("video ->", HERE / "out/video.mp4")


def pops(path=None):
    path = path or HERE / "out/video.mp4"
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


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "probe": asyncio.run(probe([float(x) for x in sys.argv[2:]]))
    elif cmd == "beats": asyncio.run(probe([b * 0.5 + 0.45 for b in range(48)], "beats.png", cols=9))
    elif cmd == "full": asyncio.run(full())
    elif cmd == "pops": pops()
