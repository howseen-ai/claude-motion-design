---
name: motion-design
description: Code-only motion design pipeline (no After Effects) for Raphaël / Howseen: launch films, showreels, product promos, LinkedIn/X videos, meme clips. Use when asked to make a motion design video, a promo/launch film, a showreel, "remake this video", a video from a prompt (e.g. "make a 15s motion graphics video…"), to change a video's music/SFX, or to prepare memes for posts. Covers the brief → beat map → stills → seek(t) HTML engine → Playwright render → ffmpeg → music/SFX → QA flow, plus asset sourcing (Mixkit, Pexels, Unsplash, svgl, 21st.dev) and every gotcha hit so far.
---

# Motion design, 100 % code (Howseen pipeline)

Built and battle-tested 25-27/09/2026 on: promo60 (60 s VO ad), loop, launch film, showreel v1/v2, frame. (Apple-keynote prompt), Crave (food-app prompt), reel15 (howseen.ai in 1 prompt + "make it better" pass), Baguette Pro (Apple framework parody), Howseen LinkedIn v1→v5 (4:5).
Workdir: `~/Desktop/Howseen AI/howseen-video/` (one folder per film). Every film folder = `<name>.html` + `render.py` + `audio.py` + `out/`.

**Our stack vs the "AI motion" stack people post** (Opus + Higgsfield + Blender + After Effects + Suno + Soundly): we replace Blender/After Effects with a deterministic HTML engine rendered frame by frame, Higgsfield with real stock (Pexels/Unsplash) or coded visuals, Suno with Mixkit music, Soundly with Mixkit SFX. 0 € and fully reproducible. Suno/Envato/Higgsfield only if Raphaël asks and has credits.

## 0. Non-negotiables
- **Zero fabrication on screen**: real data is sourced on screen (e.g. "12 logged-out ChatGPT answers · 25 Sep 2026"); anything illustrative is labelled **"Example data" / "Example answer" / "Illustration"**. Never claim product features that don't exist (check the app code). Native CMS = WordPress, Shopify, Ghost, BigCommerce; others "via webhook".
- **Captions must stay true**: no "made in 10 minutes" if it wasn't, no "0 external tools" if Cartesia/Mixkit were used, no "one shot" after iterations. Mixkit SFX are *placed* by code, not generated.
- Illustrations/covers: **no Howseen name/logo** in AI-generated images (rule 25/09). Howseen can appear in our own coded promo films.
- No em/en dashes in any copy we write.

## 1. Flow (always in this order)
1. **Inputs**: if the brief has an `<inputs>` block, ask for them (AskUserQuestion, recommended defaults first). Otherwise pick sensible defaults and say so.
2. **Beat map** (`BEATMAP.md`): BPM → beat length, every scene on a beat, the **music drop on the key visual moment** (flood, logo, big reveal). Nothing still for > 1 s.
3. **4 stills** (or a one-frame-per-beat sheet) → look at them (Read) → fix → only then the full render.
4. Full render → pops scan → audio → mux → **open -R** the file and give the path + a true caption.

## 2. The engine (one HTML file)
- Everything computed from time inside `window.seek = async (t) => {…}`; **no CSS transitions, no timers, no state between frames**. Declare all constants before the first `seek()`. Set `window.ready = true` after fonts/images load.
- **Springs** = closed-form step response `step(tau, f, z)`; a value with many targets = sum of one spring per change. Easings: `io` (cubic in-out), `out`, `in`, `o5`, `expo`. Linear motion = cheap, never.
- **Camera** = one transform on a container, keys `[t, zoom, x, y]`, eased segments, **zoom interpolated in log space**, never zoom in/out back-to-back. Beat punches: `+0.012` per beat, `+0.03` per bar after the drop, exp decay.
- **Shared elements** for every handoff (the bubble carries its words into the flood, the button carries its label into the page). Text that swaps inside a morphing shape gets its own mask.
- **Masked text rise** (translateY 105% inside overflow:hidden), word-by-word stagger (55 ms) with a small rotation; accent words with a moving gradient (`background-clip:text`).
- **Floods**: circle from the source object, must **clear the farthest corner** (`hypot` to the 4 corners ×1.05) in ~0.3-0.35 s, then contract into the next object.
- Glass / goo / iris / variable-font squeeze / 3D cube / equalizer / blob mask / animated beam / border beam: reference implementations in `frame/frame.html` (liquid glass via canvas displacement, goo, 6-blade iris, Archivo wdth squeeze), `reel2/reel2.html` (morph shapes, cube, EQ, blob), `h20/h28.html` (21st.dev Animated Beam + Border Beam ported to seek(t), dotted grid, drifting blobs, sheen sweep, sparkles).
- `z-index` on every layer. `visibility:inherit` (not `visible`) on children of hidden parents.
- Look: warm off-white `#f5f5f2`/`#f7f7f5` or ink `#0b0b0c`; Howseen sky `#38bdf8`, ink `#0f172a`, lime `#cdf24f`, orange `#ff6a2a`, violet `#a78bfa`. Fonts in `crave/fonts/geist-latin.woff2`, `frame/fonts/archivo-var.woff2` (wdth 62-125), `crave/fonts/instrument-serif.woff2`.

## 3. Render (scripts/render_template.py)
- Serve the folder over HTTP (`python -m http.server 876x --directory …`, background), Playwright Chromium, viewport = video size (1920×1080, 1080×1350 for LinkedIn 4:5, 1440×1440 square).
- `probe t1 t2…` → `probe/sheet.png`; `beats` → one frame per beat; `full` → **N subframes per frame blended with `tmix`** (6-8 for fast moves, 4 = ghosting), 60 fps; `pops` → frame-diff spikes > 3× neighbours (intentional beat cuts show up too: say so, don't hide).
- Use a separate `sub*/` folder per version so parallel renders don't clash. ~1-1.5 min of wall time per second of film at 8 subframes; run long renders in the background.
- Final encode: `scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p`, `-color_range tv -colorspace bt709`, libx264 crf 16, AAC 256k, `+faststart`.

## 4. Music & SFX (scripts/audio_template.py, analyze_song.py)
- **Music = Mixkit** (free commercial). Direct file: `https://assets.mixkit.co/music/<id>/<id>.mp3`. IDs: grep `music/[0-9]+/[0-9]+\.mp3` in the listing page HTML (page order = WebFetch list order).
- Used & measured: `audio/mixkit-207.mp3` 120 BPM (drop song 31.97 s), `mixkit-190` 120 BPM (drop bar 8 = 16.01 s), `mixkit-129` 120 BPM (drop 16.09 s), `minimal-techno-01` 119.99 BPM (true drop 39.98 s, auto grid is 2 beats off), **Cat Walk** (Arulo #371) 130 BPM drop **14.769 s** (`crave/assets/audio/cat-walk.mp3`), **Waka Floka Type** (Arulo #364, trap/US rap) drop **14.75 s** (`reel2/assets/m364.mp3`), **Driving Ambition** (#32, piano uplifting ~99 BPM) hit 37.66 s, **Classical vibes 4** (#684, Apple-ish classical ~94 BPM) lift ~7.95 s. Leo's framework: 60-80 BPM regal, 90-110 smooth, 115-123 elite/sophisticated, > 125 hype.
- **Find the drop by energy**, never trust an auto grid: per-bar low/full band energy, then 20-50 ms windows around the jump. Start the song at `drop_in_song - drop_in_film`.
- **SFX = Mixkit**, downloaded to `howseen-video/sfx/` (`https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`); search with `scripts/mixkit_sfx_search.py <tag>`. Map so far: click 1125, key 2568, soft tick 1117, check 1113, toggle 1120, toast 2573, pop 2364 / bubble 2357 / soap 2925, whoosh w1490, rise w1489, flip w1485, impact 1143, shutter 1430 / lens 1433, sparkle 3083, success 2865, bread crunch 118.
- **Place every SFX by its measured peak** (argmax of |s|), gain 0.04-0.3, keystrokes follow the same per-character rhythm as the typing animation. Fade the tail, **two-pass loudnorm to −14 LUFS**. Voice-over: Cartesia (Katie) with word timestamps → cues.json (promo60), music ducked ~9 dB under the voice.
- Minimal sound design for "premium/Apple" films: a handful of soft hits, remove anything that feels loud or out of place.

## 5. Assets
- **Photos**: Unsplash `https://unsplash.com/napi/search/photos?query=…&per_page=30` (curl ok) → `urls.raw + &w=2600&q=85&fm=jpg`; Pexels CDN `https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=1600` (search pages block curl: use WebFetch/WebSearch for IDs). Always build a contact sheet and **look at it** before using. Cutouts from dark backgrounds: luminance+warmth alpha, largest component, trim 5 px (see `baguette/assets/hero_cut_3k.png`).
- **Video**: Mixkit `assets.mixkit.co/videos/<ID>/<ID>-1080.mp4`, Pexels `pexels.com/download/video/<id>/`. Re-encode all-intra (`-g 1`), load as blob URL, await `seeked`.
- **Logos**: `scripts/svgl_logos.py` (svgl.app API, colour SVGs: openai, gemini, perplexity, google, claude, youtube, reddit, trustpilot, linkedin, shopify, wordpress, webflow, framer, nextjs); fallback simple-icons (`cdn.jsdelivr.net/npm/simple-icons@13/icons/<name>.svg`); Howseen marks in `promo60/logos/logo-mark*.png`. 21st.dev `search_logo` currently returns nothing: go to svgl directly.
- **21st.dev** components (Animated Beam id 919, Border Beam 1268, Orbiting Circles 1411…): `scripts/mcp21_client.py tools | call search '{…}' | call get_component '{"id":…}'`, key in `~/.config/21st.key` (free tier: 2 code retrievals/day). They're React/framer-motion: **port the idea to seek(t)**, never run them live.
- **Memes**: yt-dlp standalone (`$CLAUDE_JOB_DIR/tmp/yt-dlp_macos` or reinstall), `ytsearch5:<meme> original`, check a contact sheet (no burned-in captions, no watermarks), re-encode H.264 1280 wide + AAC. Library in `promo60/memes/` (Michael Scott, DiCaprio, Travolta, Keanu whoa, Bateman walk, This is fine, Homer bushes).

## 6. Gotchas (all hit for real)
- Worktree sandbox: no heredocs / `cd && …` chains / loops with computed commands / `$(…)` in Bash → write `.py` scripts and run plain commands. Paths with spaces: use the symlink `$CLAUDE_JOB_DIR/tmp/hv` → howseen-video.
- No brew ffmpeg: `imageio_ffmpeg.get_ffmpeg_exe()` or `howseen-video/bin/ffmpeg`. Python venv: `howseen-video/.venv`.
- Cloudflare blocks Python's default UA on some APIs: send `User-Agent: claude-code-mcp-client/1.0`.
- Hash-only `goto` doesn't reload: set state via `evaluate`. Measure text with canvas (`measureText`) not DOM rects when a camera scale is applied.
- Text that must stay sharp during a handoff: never scale a blurry copy, crossfade only the fill.
- LinkedIn video: 4:5 1080×1350; X: 16:9 or 1:1, ≤ 2:20; captions go in the post, burned banners ("Commente MOTION") only for LinkedIn lead magnets.

## 7. Delivery checklist
☐ stills approved ☐ 0 unexplained pops ☐ drop on the key moment ☐ −14 LUFS ☐ TV-range BT.709 ☐ "Example data" labels ☐ caption true ☐ file revealed in Finder + path given.

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

## 10. Remake mode — frame-locked 1:1 copy of an existing video (scripts/remake/)
Use when asked to "remake / recreate this launch video for my brand" (the split-screen "original | opus 5.5 copy" format). Proven on the Gojiberry launch (65 s, 28 shots) on 28/09/2026.
- **Phase 0, analysis (no building):** download REF (yt_dlp in the video venv, no browser cookies) → `remake_analyze.py` extracts all frames 0-based to ref/full, audio to ref/audio.wav, detects hard cuts (mean-abs-diff spikes) and writes 6-frame contact sheets. Read the sheets, write SPEC.md: shot table (id, f0–f1, REF content, brand swap), swap rules. Most "cuts" in modern launch films are continuous camera/morph moves: expect only ~10-15 hard cuts, and expect SPEC boundaries to be a few frames off (agents fix them).
- **Phase 1, engine (you, before agents):** copy `core.js` + `index.html` (seek(F) pure, SHOT registry, camera, cursor, words, pixelDissolve, palette filter that re-hues any leftover old-brand colour) and `remake_stub.py` (one placeholder file per group). Serve the folder, smoke-test with `remake_render.py compare out/test 10 600 1200`.
- **Phase 2, parallel build:** split shots into 4 contiguous groups, one agent each (fill `BRIEF_TEMPLATE.md`), each writes ONLY shots/Gx.js and verifies with side-by-side compare sheets. 5th agent = audio: analyse REF (BPM, drop, hard stop, SFX hits, VO slots via STT timings only), royalty-free Mixkit track stretched ≤8% and cut on bars so drops land on REF times, numpy SFX on REF hits, -14 LUFS. Never reuse REF music/voice. Typical wall time: ~25 min per agent in parallel.
- **Phase 3, integrate:** full render in 3 parallel chunks (`remake_render.py full out/full a b`), `remake_sync.py encode` (muxes out/mix.wav), `split` (the post format: two panels with a gap, black labels "original" / "opus 5.5 copy", setsar=1 or X distorts it), `stacked` (QA). `remake_qa.py`: ref|ours one frame per second + group seams + old-brand colour scan. Fix, re-render, deliver.
- **Honesty rules:** no fake "made in 15 minutes" if it wasn't; tag/credit the original brand in the post; never show "OpenAI × YourBrand"-style co-marks that imply a partnership; no REF people photos.
- Helpers every agent re-invented (add locally until core has them): text placed by ink edge + fitFont, hex colour mix, REF-shaped cursor, per-frame keyframe tables.
