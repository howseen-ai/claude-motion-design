# claude-motion-design

A Claude Code skill to make motion design videos **in pure code**: HTML + Playwright + ffmpeg. No After Effects, no Remotion license, no editing app.

Every frame is computed from time, rendered frame by frame, blended for motion blur, and cut to the beat of the music. Every sound effect lands on its measured peak.

<p align="center"><img src="examples/howseen-launch/preview.gif" width="320" alt="Howseen launch video, made with this skill"></p>

The example above is the launch video of [Howseen](https://howseen.ai) (AI visibility tracking: see if ChatGPT, Gemini and Perplexity recommend your brand). It was made with Claude Opus 5.5 and this skill, in 5 iterations. Its full source is in [`examples/howseen-launch`](examples/howseen-launch).

## Why code instead of an editor

- **Deterministic**: the whole film is one `seek(t)` function. Same input, same frames, every time. Fix one scene without touching the rest.
- **Free**: Chromium, ffmpeg, Python. No license, no subscription.
- **Beat-synced by construction**: scenes are placed on a beat map, the music drop is aligned to the key visual moment, SFX are placed by peak.
- **Iterable by an AI**: "make the transitions faster", "change the music", "add a 3D cube on the drop" are just code changes.

## Install

1. Copy the skill into Claude Code:
   ```bash
   mkdir -p ~/.claude/skills && cp -r skill/motion-design ~/.claude/skills/
   ```
2. Python deps: `pip install playwright imageio-ffmpeg numpy pillow && python -m playwright install chromium`
3. In Claude Code, ask for a video, or type `/motion-design`.

## Run the example

```bash
cd examples/howseen-launch
python fetch_assets.py              # downloads the free music, SFX, logos and font (not redistributed here)
python -m http.server 8000 &        # serve the film
python render.py probe 1 8 15 20    # quick stills -> probe/sheet.png
python render.py full               # 24 s, 60 fps, subframe motion blur -> out/video.mp4
python audio.py                     # music + SFX by peak, -14 LUFS -> out/audio.wav
```
Then mux: `ffmpeg -i out/video.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v libx264 -crf 16 -c:a aac -shortest out/final.mp4`

## What the skill covers

- **Flow**: inputs → beat map → 4 stills approved → full render → pop scan → audio → final.
- **Engine**: `seek(t)` only (no CSS transitions, no timers), closed-form springs, a camera keyed in log space, shared-element handoffs, color floods that clear the farthest corner, masked word-by-word text, and ports of 21st.dev components (Animated Beam, Border Beam) to `seek(t)`.
- **Render**: Playwright screenshots, N subframes per frame blended with `tmix`, BT.709 TV-range encode, single-frame pop detection.
- **Audio**: find the real drop by band energy (never trust an auto beat grid), start the song so the drop hits the key frame, place each SFX by its measured peak, two-pass loudnorm to -14 LUFS.
- **Assets**: free sources only (Mixkit music/SFX/video, Pexels, Unsplash, svgl logos, simple-icons). Scripts to search and download them.
- **Remake mode** (`skill/motion-design/scripts/remake/`): frame-locked 1:1 remake of any launch video for your brand, the "original | opus 5.5 copy" split-screen. Phase 0 extracts every frame, detects cuts and writes a shot-by-shot spec; phase 1 is a shared `seek(F)` engine with a palette filter; phase 2 runs 4 build agents (one per shot group, each verifying side-by-side compare sheets against the reference) plus 1 audio agent (royalty-free track stretched to the reference BPM, synthesized SFX on the reference hit times); phase 3 renders, encodes the split-screen and a stacked sync check. Brief template included. Never reuse the reference's music, voice or people photos.
- **Honesty rules**: illustrative data is labelled "Example data" on screen; captions stay true.

## Credits and licenses

Code: MIT. Third-party media is downloaded by `fetch_assets.py` and stays under its own license (Mixkit free license, Pexels/Unsplash licenses, OFL for Geist). Brand logos belong to their owners. The Howseen mark in the example belongs to Howseen AI.

Made by [Raphaël Aubry](https://www.linkedin.com/in/raphaelaubry03), founder of [Howseen](https://howseen.ai).
