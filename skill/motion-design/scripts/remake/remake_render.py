"""render.py — Playwright renderer for the frame-locked remake.
usage:
  render.py stills  OUT F1 F2 ...      -> OUT/o_FNNNN.png
  render.py compare OUT F1 F2 ...      -> OUT/c_FNNNN.jpg (ref | ours, labelled) + OUT/compare_sheet.jpg
  render.py full    OUT F0 F1          -> OUT/fNNNN.png for F0 <= F < F1
Use a separate OUT dir per agent (e.g. out/G2) so parallel runs never collide. Max ~15 frames per call for stills/compare.
"""
import asyncio, sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from playwright.async_api import async_playwright

H = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
import os
URL = os.environ.get("REMAKE_URL", "http://localhost:8768/remake/index.html")  # set REMAKE_URL to your served index.html
FPS = 24


async def run(frames, out: Path, fmt="png"):
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--disable-gpu-vsync", "--font-render-hinting=none"])
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        await pg.goto(URL)
        await pg.wait_for_function("window.ready === true", timeout=120000)
        el = await pg.query_selector("#stage")
        paths = []
        for F in frames:
            await pg.evaluate(f"window.seek({F / FPS + 1e-6})")
            await pg.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            pth = out / f"o_f{F:04d}.png"
            await el.screenshot(path=str(pth))
            paths.append(pth)
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:10])
    return paths


def compare(frames, out: Path):
    paths = asyncio.run(run(frames, out))
    try: font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
    except Exception: font = ImageFont.load_default()
    tiles = []
    for F, p in zip(frames, paths):
        ref = Image.open(H / f"ref/full/f{F:04d}.jpg").convert("RGB").resize((960, 540))
        ours = Image.open(p).convert("RGB").resize((960, 540))
        c = Image.new("RGB", (1930, 590), "white"); c.paste(ref, (0, 50)); c.paste(ours, (970, 50))
        d = ImageDraw.Draw(c); d.text((10, 8), f"REF f{F}", fill="red", font=font); d.text((980, 8), f"OURS f{F}", fill="blue", font=font)
        cp = out / f"c_f{F:04d}.jpg"; c.save(cp, quality=85); tiles.append(c)
    cols = 2; rows = -(-len(tiles) // cols)
    sheet = Image.new("RGB", (cols * 965, rows * 295), "white")
    for i, t in enumerate(tiles): sheet.paste(t.resize((965, 295)), ((i % cols) * 965, (i // cols) * 295))
    sheet.save(out / "compare_sheet.jpg", quality=80)
    print("compare ->", out / "compare_sheet.jpg")


if __name__ == "__main__":
    mode, out = sys.argv[1], H / sys.argv[2]
    nums = [int(x) for x in sys.argv[3:]]
    if mode == "stills":
        asyncio.run(run(nums, out)); print("stills ->", out)
    elif mode == "compare":
        compare(nums, out)
    elif mode == "full":
        asyncio.run(run(list(range(nums[0], nums[1])), out)); print("full", nums, "->", out)
