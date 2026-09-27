---
name: motion-design
description: Code-only motion design pipeline (HTML + Playwright + ffmpeg, no After Effects, no Remotion). Use when asked to make a motion design video, a product launch or promo film, a showreel, a landing-page loop, a LinkedIn/X video, to remake a video from a prompt, or to change a video's music or sound effects. Covers inputs, beat map, stills review, the seek(t) engine, frame-by-frame rendering with motion blur, beat-synced music and SFX, free asset sourcing, and QA.
---

# Motion design in pure code

Output: an MP4 made from one HTML file whose every style is a pure function of time, rendered frame by frame with Playwright, blended with ffmpeg, and scored with free music and SFX aligned to the beat.
Reference implementation: `examples/howseen-launch` in this repo (24 s, 1080x1350, 60 fps).

## 0. Rules
- **Never fabricate data on screen.** Real numbers carry their source on screen; anything illustrative is labelled "Example data" / "Example" / "Illustration".
- **Captions stay true**: don't write "made in 10 minutes", "one shot" or "0 tools" unless it's literally true. Say how many iterations it took.
- No em dashes in copy you write for the user.

## 1. Flow (always in this order)
1. **Inputs**: if the brief lists inputs, ask for them with recommended defaults; otherwise choose defaults and say which.
2. **Beat map** (`BEATMAP.md`): BPM → beat length; every scene starts on a beat; the **music drop lands on the key visual moment** (a flood, the logo, the big reveal). Nothing holds still for more than 1 s.
3. **Stills**: render 4 stills (or one frame per beat), look at them, fix, and only then render the full film.
4. **Full render → pop scan → audio → mux**, then hand over the file path and a true caption.

## 2. The engine (one HTML file)
- Everything is computed inside `window.seek = async (t) => {…}`: **no CSS transitions, no timers, no state between frames.** Declare constants before the first `seek()`. Set `window.ready = true` once fonts and images are loaded.
- **Springs**: closed-form step response `step(tau, f, z)`; a value with several targets is the sum of one spring per change. Easings: cubic in-out, out, in, quint-out, expo. Never linear.
- **Camera**: one transform on a container, keyframes `[t, zoom, x, y]`, eased segments, **zoom interpolated in log space**, no zoom-in/zoom-out back to back. Beat punches: small scale bumps on beats (bigger on bars) after the drop, exponential decay.
- **Shared elements** for every handoff (a button carries its label into the page it grows into; a flood carries the text of the bubble it came from). Text swapping inside a morphing shape gets its own mask.
- **Text**: masked rise (translateY 105% inside overflow:hidden), word-by-word stagger (~55 ms) with a small rotation; gradient accent words with `background-clip:text`.
- **Floods**: a circle grows from the source object until it clears the **farthest corner** (`hypot` to the 4 corners × 1.05) in ~0.3-0.35 s, then contracts into the next object. Faster reads as a flash.
- **Effects library** (all portable to `seek(t)`): animated beam (gradient sweeping along an SVG path), border beam (conic gradient masked to a ring), orbiting logos, shape morph (sampled points between polygons), variable-font stretch (`font-variation-settings: 'wdth'`), CSS 3D cube snapping on beats, equalizer bars, liquid blob mask, drifting blurred color blobs, sheen sweep on scene changes, sparkle burst on the drop. 21st.dev components are React/framer-motion: port the idea, don't run them live.
- Set `z-index` on every layer; use `visibility: inherit` (not `visible`) for children of hidden parents.

## 3. Render (`scripts/render_template.py`)
- Serve the folder over HTTP (`python -m http.server`), Playwright Chromium with viewport = video size (1920x1080, 1080x1350 for LinkedIn 4:5, 1080x1080).
- `probe t1 t2…` → contact sheet; `beats` → one frame per beat; `full` → **N subframes per frame blended with `tmix`** (6-8 for fast moves; 4 leaves ghosting), 60 fps; `pops` → frames whose difference spikes > 3× their neighbours. Intentional beat cuts show up too: report them, don't hide them.
- Final encode: `scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p`, libx264 crf 16, AAC, `+faststart`.
- Cost: roughly 1-1.5 min of wall time per second of film at 8 subframes. Run long renders in the background, one `sub*/` folder per version.

## 4. Music and SFX (`scripts/audio_template.py`, `scripts/analyze_song.py`)
- Free music: Mixkit (`https://assets.mixkit.co/music/<id>/<id>.mp3`). BPM guide: 60-80 regal/cinematic, 90-110 smooth, 115-123 elite/sophisticated, 125+ hype.
- **Find the drop by energy**, never trust an auto beat grid: per-bar low-band and full-band energy, then 20-50 ms windows around the jump. Start the song at `drop_in_song - drop_in_film`.
- Free SFX: Mixkit (`https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`), search with `scripts/mixkit_sfx_search.py <tag>`. Useful ids: click 1125, keypress 2568, soft tick 1117, check 1113, pop 2357/2364, whoosh 1490, rise 1489, impact 1143, camera shutter 1430, sparkle 3083, success tone 2865.
- **Place every SFX by its measured peak** (argmax of the absolute signal), gains 0.04-0.3; keystrokes follow the same per-character rhythm as the typing animation. Fade the tail, **two-pass loudnorm to -14 LUFS**. With a voice-over, duck the music ~9 dB under the voice.
- "Premium" films: very few, soft SFX. Remove anything that feels loud or out of place.

## 5. Assets (free sources)
- Photos: Unsplash (`unsplash.com/napi/search/photos?query=…`, then `urls.raw + &w=2600`), Pexels CDN (`images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?w=1600`). Always look at a contact sheet before using anything.
- Video: Mixkit (`assets.mixkit.co/videos/<ID>/<ID>-1080.mp4`). Re-encode all-intra (`-g 1`), load as a blob URL, await `seeked` before drawing.
- Logos: `scripts/svgl_logos.py` (svgl.app colour SVGs), fallback simple-icons (`cdn.jsdelivr.net/npm/simple-icons@13/icons/<name>.svg`).
- 21st.dev components: `scripts/mcp21_client.py` (needs `API_KEY_21ST` or `~/.config/21st.key`).
- Fonts: Google Fonts (Geist, Archivo variable for width animation, Instrument Serif).

## 6. Gotchas
- No system ffmpeg? `imageio_ffmpeg.get_ffmpeg_exe()`.
- Some APIs block Python's default user agent: send a custom `User-Agent`.
- Measure text with canvas `measureText` when a camera scale is applied (DOM rects include the transform).
- A hash-only `goto` doesn't reload the page: set state with `evaluate`.
- Keep text sharp during a handoff: swap only the fill, never scale a blurred copy.

## 7. Delivery checklist
☐ stills approved ☐ drop on the key moment ☐ 0 unexplained pops ☐ -14 LUFS ☐ BT.709 TV range ☐ "Example data" labels ☐ caption true ☐ file path given.

## 8. Critique loop (make the model watch its own frames)
Before any full render, and after it:
```
ffmpeg -i out/final.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 out/contact.png      # overview
ffmpeg -ss <t-0.1> -i out/final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 out/strip.png  # 12 frames around a fast move
ffmpeg -i out/final.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 out/phone.png         # readability at phone width
ffmpeg -stream_loop 1 -i out/final.mp4 -c copy out/loop_check.mp4                            # loop seam (loops only)
```
Open them and **score 1-10**: hook in the first 2 s · readability at 360 px · motion quality (springs, no dead frames) · variety (something new every 2-4 s) · composition · brand/data accuracy · sound sync. Write the 3 worst problems with timestamps (hunt for: text overlapping during swaps, anything moving linearly, corner labels/frame borders, centred title on a gradient, blurry scaled text, a dead beat, a loop stutter). Fix, re-render only the affected seconds, re-score. **Repeat until every score is 8+.** Be a harsh motion director, not a proud author.

## 9. Extra rules
- **Determinism**: never `Math.random`; use a seeded PRNG (mulberry32). Rendering the same second twice must give identical frames.
- **Reference first**: with a reference video/frame, extract a frame every 0.5 s with ffmpeg, write `docs/style_guide.md` (palette hex, type, shot lengths, transitions, camera, texture, text in/out) and `docs/shotlist.md` on the beat grid. Take the grammar, never the content or logos. Wait for OK before code.
- **Real product only**: capture the real UI (Playwright screenshots of the site/app) into `./assets` and list what you found; never invent screens. If a paywall blocks it, ask the user for screenshots or clearly label a recreated UI as illustrative.
- **Spring presets** (stiffness k, damping d): snappy UI 320/30, default containers/camera 170/26, heavy type/logos 120/24, playful mascots 180/12. Leading and trailing edges of a stretching indicator on different springs.
- **Formats**: write scenes against a layout function, then render 9:16, 1:1, 16:9 and 4:5 from the same timeline, reframing type and UI per format (never crop).
- **Synthesized sound option**: when no track is supplied, SFX can be synthesized in code (click = short decaying sine, pop = rising sine, thump = falling sine, whoosh = windowed noise) on the same timeline.
- **Effort**: medium for small fixes, xhigh for a new film, max when the first 3 seconds carry a launch.
