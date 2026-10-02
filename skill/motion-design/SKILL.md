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
- `probe t1 t2…` → `probe/sheet.png`; `beats` → one frame per beat; `draft` → 30 fps, 1 capture/frame, 960×540, crf 23 veryfast (**always before the master**: judge rhythm, not sharpness); `full` → **N subframes per frame blended with `tmix`** (6-8 for fast moves, 4 = ghosting) spread over `SHUTTER = 0.5` of the frame (180° film shutter; 1.0 = smeary), 60 fps; `pops` → frame-diff spikes > 3× neighbours (intentional beat cuts show up too: say so, don't hide); `loop` → seam check in **position (last vs frame 0) AND velocity (motion into vs out of frame 0)**.
- Capture hygiene (built into the template): wait `document.fonts.ready`, pause `document.getAnimations()` and kill CSS transitions after load, and **wait 2 `requestAnimationFrame` after every `seek(t)`** before the screenshot. `WEBGL=1` launches Chromium with SwiftShader/ANGLE flags (headless WebGL otherwise renders black).
- Every film page also gets **preview controls** for Raphaël: Space = play/pause, ←/→ = previous/next frame, R = replay, a time readout. Playback calls the same `seek(t)` from a rAF loop (the only place a clock is allowed); the render never touches it.
- **Films > 25 s: always render in 3 parallel chunks** (`h20/lm55/render_par.py chunk <html> <T> k 3` x3 in background, then `concat`): ~20 min for 55 s instead of ~55 min sequential. Raphaël expects fast turnarounds; never launch a long single-process full render. Re-render only the changed seconds when possible (`part`).
- Use a separate `sub*/` folder per version so parallel renders don't clash. ~1-1.5 min of wall time per second of film at 8 subframes; run long renders in the background.
- Final encode: `scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p`, `-color_range tv -colorspace bt709`, libx264 crf 16, AAC 256k, `+faststart`.

## 4. Music & SFX (scripts/audio_template.py, analyze_song.py)
- **Music = Mixkit** (free commercial). Direct file: `https://assets.mixkit.co/music/<id>/<id>.mp3`. IDs: grep `music/[0-9]+/[0-9]+\.mp3` in the listing page HTML (page order = WebFetch list order).
- Used & measured: `audio/mixkit-207.mp3` 120 BPM (drop song 31.97 s), `mixkit-190` 120 BPM (drop bar 8 = 16.01 s), `mixkit-129` 120 BPM (drop 16.09 s), `minimal-techno-01` 119.99 BPM (true drop 39.98 s, auto grid is 2 beats off), **Cat Walk** (Arulo #371) 130 BPM drop **14.769 s** (`crave/assets/audio/cat-walk.mp3`), **Waka Floka Type** (Arulo #364, trap/US rap) drop **14.75 s** (`reel2/assets/m364.mp3`), **Driving Ambition** (#32, piano uplifting ~99 BPM) hit 37.66 s, **Classical vibes 4** (#684, Apple-ish classical ~94 BPM) lift ~7.95 s, **Head Bang** (#357, hip-hop half-time **74 BPM**, 4-bar quiet intro, drop **12.96 s** = beat 16; used by the viral "STOP PAYING FOR MOTION DESIGN SOFTWARE" loop prompt). Mixkit search ignores `?q=`: crawl genre pages (`/free-stock-music/<genre>/`) and match `item-grid-card__title` to `music/<id>/<id>.mp3`. Leo's framework: 60-80 BPM regal, 90-110 smooth, 115-123 elite/sophisticated, > 125 hype.
- **Find the drop by energy**, never trust an auto grid: per-bar low/full band energy, then 20-50 ms windows around the jump. Start the song at `drop_in_song - drop_in_film`.
- **SFX = Mixkit**, downloaded to `howseen-video/sfx/` (`https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`); search with `scripts/mixkit_sfx_search.py <tag>`. Map so far: click 1125, key 2568, soft tick 1117, check 1113, toggle 1120, toast 2573, pop 2364 / bubble 2357 / soap 2925, whoosh w1490, rise w1489, flip w1485, impact 1143, shutter 1430 / lens 1433, sparkle 3083, success 2865, bread crunch 118.
- **Place every SFX by its measured peak** (argmax of |s|), gain 0.04-0.3, keystrokes follow the same per-character rhythm as the typing animation. Fade the tail, **two-pass loudnorm to −14 LUFS**. Voice-over: Cartesia (Katie) with word timestamps → cues.json (promo60), music ducked ~9 dB under the voice.
- Minimal sound design for "premium/Apple" films: a handful of soft hits, remove anything that feels loud or out of place.

## 5. Assets
- **Photos**: Unsplash `https://unsplash.com/napi/search/photos?query=…&per_page=30` (curl ok) → `urls.raw + &w=2600&q=85&fm=jpg`; Pexels CDN `https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=1600` (search pages block curl: use WebFetch/WebSearch for IDs). Always build a contact sheet and **look at it** before using. Cutouts from dark backgrounds: luminance+warmth alpha, largest component, trim 5 px (see `baguette/assets/hero_cut_3k.png`).
- **Video**: Mixkit `assets.mixkit.co/videos/<ID>/<ID>-1080.mp4`, Pexels `pexels.com/download/video/<id>/`. Re-encode all-intra (`-g 1`), load as blob URL, await `seeked`.
- **Logos**: `scripts/svgl_logos.py` (svgl.app API, colour SVGs: openai, gemini, perplexity, google, claude, youtube, reddit, trustpilot, linkedin, shopify, wordpress, webflow, framer, nextjs); fallback simple-icons (`cdn.jsdelivr.net/npm/simple-icons@13/icons/<name>.svg`); Howseen marks in `promo60/logos/logo-mark*.png`. 21st.dev `search_logo` currently returns nothing: go to svgl directly.
- **21st.dev** components (Animated Beam id 919, Border Beam 1268, Orbiting Circles 1411…): `scripts/mcp21_client.py tools | call search '{…}' | call get_component '{"id":…}'`, key in `~/.config/21st.key` (free tier: 2 code retrievals/day). They're React/framer-motion: **port the idea to seek(t)**, never run them live.
- **Memes**: yt_dlp from the video venv (if YouTube says "page needs to be reloaded", pass `extractor_args={"youtube":{"player_client":["tv","web_safari","android","ios"]}}` and `ffmpeg_location=imageio_ffmpeg.get_ffmpeg_exe()`), `ytsearch6:<meme> meme template`, check a contact sheet (no burned-in captions, no watermarks, cut "Subscribe / link in description" end cards), re-encode H.264 1280 wide + AAC + setsar=1. Library in `~/Desktop/Howseen AI/illustrations/memes/` (clips/ ready to post, legendes/ captions, sources-brutes/ raw downloads, planches/ check sheets) (Michael Scott, DiCaprio pointing, Travolta, Keanu whoa, Bateman walk, This is fine, Homer bushes, Carrey typing fast, Gatsby toast, Peele sweating).

### 5b. Resource shortlist (checked 28/09/2026)
- **3D icons: 3dicons.co**, CC0 (commercial use, no attribution), 1,500+ renders. Fits the Howseen "glossy 3D on cream" look for videos, LinkedIn visuals and article covers. Download PNGs, cut-out already transparent; look at them on a contact sheet first.
- **seek-compatible animation libs** (can be driven frame by frame, so they fit the deterministic render):
  - **Anime.js** (animejs.com): create with `autoplay: false`, then `anim.seek(ms)` from `window.seek(t)` (`t*1000`, or set `engine.defaults.timeUnit` to seconds). Use timelines the same way.
  - **Theatre.js** (theatrejs.com): keyframes edited visually in Studio, then in the render build drop the Studio and set `sheet.sequence.position = t` (seconds) inside `window.seek(t)`. Good for complex hand-tuned camera moves. Check the sequence API before first use.
  - Never use libs that only animate in real time (Spline runtime, Unicorn Studio, CSS/framer-motion live): they can't be seeked, so frames drift.
- **Ideas to port to seek(t)** (don't run them live): Kinetics (kinetics.colorion.co, 150+ motion effects), CSS Text Effects (text-effects.colorion.co), Liquid Glass (glass.samasante.com, refraction), Motion Primitives, Magic UI, Aceternity, 21st.dev (MCP, see above).
- **For the Howseen site/app, not videos**: Magic UI / Aceternity / Motion Primitives (copy-paste animated React), Component Gallery + Navbar Gallery (references). Avoid Spline/Unicorn embeds on the site (kills the Lighthouse 100).

## 6. Gotchas (all hit for real)
- Unsplash napi can return 401: fallback = `picsum.photos/id/<id>/<w>/<h>` (Unsplash photos, same licence; `/id/<id>/info` gives the author). Covers that worked: 184 (desert night, orange), 1041 (wave, blue).
- An easing solved by bisection returns ~1e-9 at x=0: `if (e > 0)` guards fire early (a whole dive disc appeared 2 s early). Return exact 0/1 at the ends.
- Logo reveal from a line: squash the real mark vertically (scaleY 0.014 → 1, "eye opening") and overlay the solid line for the first 12 %; never crossfade a drawn lens into the PNG (grey ghost). Reference: `loop22/loop22.html` (canvas 1440², goo via `ctx.filter='url(#goo)'`, per-time motion-blur subframes 4/12, loop seam check in `render.py pops`).
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

## 9b. Studio conventions & director's brief (from the "Playbook Opus 5.5" doc, 02/10/2026)
"The prompt is 10 %, the harness is 90 %."
- **Film folder** = `brand/` (logo.svg, palette.txt, screenshots/, reference.mp4 optional but decisive) + **`facts.md`** (every number with its source + date; "no invented metric") + `<name>.html` + `render.py` + `out/`. No facts.md → no numbers on screen. For Howseen, facts come from the app/PostHog/Stripe or a sourced page.
- **Director's brief before any code** (first message, effort max): duration, master format, deliverable formats from the SAME timeline (16:9, 1:1, 9:16), subject + one-line promise, audience, channel, **a named reference style** ("Linear launch", "Stripe docs", "Apple bumper", never "premium modern"), then **states** with timestamps (hook type 0-2.5 → shape becomes screen 1 → transforms to screen 2 with cursor click → proof with a real number → logo + URL, back to state 0 if loop). Expected output: 6 beats + **layer list** + **sound plan** (silence / coded SFX / Mixkit track), then STOP for OK.
- **Anti-"AI motion" rules** (on top of §0/§2): ONE accent colour; **one thing moves at a time** (unless a slider drives a continuous transform); one shape/visual system from start to end, transformations not cuts; springs with damping ratio ≥ 0.72, tiny overshoot, never cartoon bounce; banned: rainbow gradients, particles, glowing chrome, emoji, lorem ipsum, gratuitous 3D flips; type big enough for a phone; 9:16 safe zone decided at storyboard (text inside the centre 1080×1080).
- **Silent "one sentence" test**: show the loop muted to someone; if they summarise it in one sentence ("the button became a player"), it works; if they hesitate, too much moves.
- **Prompt library** (adapt, never paste raw for a client):
  - *One-shot viral* (Stephan Livera, 24/09): "make a dynamic 15-second motion graphics video that shows what an incredible motion designer you are, like it's your showreel for a résumé. go all out." Use once to see the engine; generic output.
  - *One-shot branded*: "Make a 15-second showreel at 1920x1080, 30fps. Keep it in one self-contained index.html. HTML, CSS, JS, SVG or Canvas only. No CDN, no external URLs. Bold type and simple shapes. End on [BRAND]. Play and Replay. window.seek(t). Do not render the MP4 yet." + one accent hex + "no gradient template".
  - *UI morph* (@twoclipping): one shape through 8-12 UI states (button → loader → player → slider → toggle → tabs → chart → command palette → toast), a real slider, ~120 BPM, exact loop.
  - *Product launch / landing reveal* (@notdwd open prompt): inputs → direction → frame-by-frame structure → seek(t) build → gotchas → 4 stills before the full film.
  - *LinkedIn loops* (Eric Djavid): pure HTML/CSS, one charter, one "A becomes B" transform, 5-9 s loop, one thing moves, easings `cubic-bezier(.6,0,.2,1)` and `cubic-bezier(.2,.8,.2,1)`; micro-prompts: button → player, search → results, card → workspace, SVG curve, magnetic dock, hidden title.
  - *SaaS / app*: web = point at the repo (real design tokens); mobile = screenshots + "invent no feature"; storyboard first.
- **Critique prompt** (2-4 rounds, where the "AI look" goes away): capture a frame at every beat and 0.3 s after, contact sheet, score each shot /10 on readability, rhythm, shape continuity, branding, loop; fix only ≤ 7, don't touch shots at 9+.
- **Other routes** (only if asked): HyperFrames (HTML + GSAP, `npx skills add heygen-com/hyperframes`, CLI preview/render: brand content factory) and Remotion (React templates, `npx skills add remotion-dev/skills`: data-driven template library). Our route = bare HTML + seek(t), the one Opus picks on its own.

**Diagnostic when it's ugly**
| Symptom | Cause → fix |
|---|---|
| Same film as all of X | Livera prompt pasted with no charter/states → brief + facts + named style |
| Blurry text / washed logo | Went through a pixel video model → back to code, real SVG |
| Stutters on export | Timers / CSS transitions → pure seek(t), 2 rAF wait |
| Loop jumps | Position matched, velocity not → add the spring tails of the previous 2 cycles; `render.py loop` |
| Cheap, bouncy | Bounce easing → springs, damping ≥ 0.72 |
| Invented feature | No screenshots / repo / facts.md |
| Black WebGL | `WEBGL=1` (SwiftShader/ANGLE flags) |
| Cost explodes | Effort max on micro-fixes → medium for patches |

## 9c. Stolen from the other public motion skills (scan 02/10/2026)
- **Seek third-party libs instead of banning them** (HyperFrames adapters): GSAP skips the redraw when asked for the same time, so `tl.pause(); tl.totalTime(t + 0.001, true); tl.totalTime(t, true)`. WAAPI/CSS: `document.getAnimations().forEach(a => { a.pause(); a.currentTime = t * 1000 })`. Lottie `goToAndStop(t*1000)`, anime.js `seek`. Video sources: pre-extract frames with ffmpeg rather than waiting on `seeked` when it flakes.
- **Deterministic Chromium flags** for pixel-identical reruns: `--deterministic-mode --run-all-compositor-stages-before-draw --disable-threaded-animation --disable-checker-imaging --font-render-hinting=none --force-color-profile=srgb`. GPU WebGL on the Mac: `--use-angle=metal`.
- **Adaptive subframes** (Kimeur): measure the fastest element's px/frame; still → 1 sample, ≤ 20 px → 4, above → `ceil(px/5)` up to 64. Huge time saver vs a fixed 8 on mostly static films. **Never blur across a hard cut**: list the cuts in `CUTS` (template clamps subframes to the frame's side of the cut).
- **Targeted blur > full-frame blur** (HyperFrames): blur only the 1-3 slam moves; never blur text meant to be read or any move < one element width per frame. **Supersample 2×** (`device_scale_factor=2`, Lanczos down) for razor text, cheaper than tmix on static type.
- **Cut seams** (HyperFrames seam gate): cut at peak velocity; direction AND speed match on both sides; zoom keeps the sign of d(scale)/dt across the cut; seam blur scales with size (≈ 10 px text, 18-20 px full frame).
- **QA additions**: one-frame flash detector (built into `pops`: frame n differs from both neighbours while n-1 ≈ n+1); `loop` checks seek(0) vs seek(T), T-1f, T-1.75f; cycles must be integer `cyc(t, n)`. **Judge ≠ builder**: run the critique as a separate read-only sub-agent, and have a fresh agent restate the message from the frames alone (if it can't, the film fails).
- **Poster in frame 0** (X/Slack/Discord ignore the cover): `-filter_complex "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]"` with the poster PNG as input 1.
- **Music cues** (brag): onset strength per track, intensity = 0.45·onset + 0.25·contrast + 0.20·rms + 0.10·bass; reveals may shift ≤ 0.15 s (small entrances ≤ 0.10 s) to snap onto a cue. Silence detection adaptive: read `input_thresh` from `loudnorm print_format=json`, feed `silencedetect=noise=<thresh>dB`.
- **Captions** (Kimeur/HyperFrames): pop 1-3 words or karaoke 3-7, ≥ 0.7 s on screen, ≤ 17 chars/s, no 1-3 frame gaps, a word lights on its start frame never before; Whisper word timings, drop words hallucinated over trailing silence.
- **Preview HUD** (QasimTalkin): clickable scrubber, ←/→ ±0.5 s (Shift = 1 frame), clock synced to `out/mix.wav`, beat number shown, `?t=` deep link.
- **B-roll over a talking head** (Barty-Bart `/motion-broll`): full-frame cutaways 3-10 s with ≥ 2 s of face between, or transparent panels in the empty space; alpha clips via `screenshot(omit_background=True)` → `format=gbrap` → ProRes 4444; never `will-change` on an element the camera scales.

## 9d. From the YouTube walkthroughs (Bart Slodyczka, Moritz, Jack Roberts, 24-25/09; transcripts in vault `30 Ressources/.raw/`)
- **B-roll over an existing VO / talking head**: ask the **density** first (≈ 33 s: medium = 3 clips, heavy = 4-5; pick heavy, cutting is easier than adding). Input = word-timestamped transcript (whisper). Plan line by line, each graphic tagged *full cutaway* / *face stays* / *transparent panel in the empty space*, approved before rendering. Graphics land on the spoken word. The creator pre-edits (cuts + shrinks themself to a third of the frame) so the empty space is known. Deliver all clips in one local review page. Medium effort is enough.
- **VO pipeline**: TTS (Cartesia/ElevenLabs), speed up slightly + trim silences with ffmpeg (adaptive `silencedetect`, §9c), local whisper.cpp for word timings → ONE timing file that drives both captions and animation cues. Check words clipped at edits.
- **Long → Short**: one topic per Short (split rather than compress), faster cuts, quick real-face shots from the original footage, regenerate VO in pieces, model the creator's own short-form scripts.
- **Brand intake**: Firecrawl `scrape` with the **`branding` format** (not markdown) pulls a site's colours/fonts/identity into `brand/` (needs a Firecrawl key; otherwise Playwright screenshots + pixel sampling as in §11).
- **Fight the fingerprint**: Claude's default font and crowded vertical layouts are recognisable: always set the brand font, and on 9:16 talking heads keep speaker bottom / one graphic top / captions, nothing else.
- **Use cases that worked**: explainer from a doc/SOP/skill ("make it fun, not too serious"); a **mascot SVG narrator** carrying the story; a **video version of a sales proposal** with real discovery-call numbers (anonymised); static HTML slides → animated slide loops (5-20 s); 3 s logo sting + jingle (batchable: 100 logos, each in the brand's main colour); restyle from a reference image (savee.com / Pinterest), add a grain/film-burn pass if it falls flat. One-prompt launch films can fan out to parallel sub-agents per section (like remake Phase 2).

## 10. Remake mode — frame-locked 1:1 copy of an existing video (scripts/remake/)
Use when asked to "remake / recreate this launch video for my brand" (the split-screen "original | opus 5.5 copy" format). Proven on the Gojiberry launch (65 s, 28 shots) on 28/09/2026.
- **Phase 0, analysis (no building):** download REF (yt_dlp in the video venv, no browser cookies) → `remake_analyze.py` extracts all frames 0-based to ref/full, audio to ref/audio.wav, detects hard cuts (mean-abs-diff spikes) and writes 6-frame contact sheets. Read the sheets, write SPEC.md: shot table (id, f0–f1, REF content, brand swap), swap rules. Most "cuts" in modern launch films are continuous camera/morph moves: expect only ~10-15 hard cuts, and expect SPEC boundaries to be a few frames off (agents fix them).
- **Phase 1, engine (you, before agents):** copy `core.js` + `index.html` (seek(F) pure, SHOT registry, camera, cursor, words, pixelDissolve, palette filter that re-hues any leftover old-brand colour) and `remake_stub.py` (one placeholder file per group). Serve the folder, smoke-test with `remake_render.py compare out/test 10 600 1200`.
- **Phase 2, parallel build:** split shots into 4 contiguous groups, one agent each (fill `BRIEF_TEMPLATE.md`), each writes ONLY shots/Gx.js and verifies with side-by-side compare sheets. 5th agent = audio: analyse REF (BPM, drop, hard stop, SFX hits, VO slots via STT timings only), royalty-free Mixkit track stretched ≤8% and cut on bars so drops land on REF times, numpy SFX on REF hits, -14 LUFS. Never reuse REF music/voice. Typical wall time: ~25 min per agent in parallel.
- **Phase 3, integrate:** full render in 3 parallel chunks (`remake_render.py full out/full a b`), `remake_sync.py encode` (muxes out/mix.wav), `split` (the post format: two panels with a gap, black labels "original" / "opus 5.5 copy", setsar=1 or X distorts it), `stacked` (QA). `remake_qa.py`: ref|ours one frame per second + group seams + old-brand colour scan. Fix, re-render, deliver.
- **Honesty rules:** no fake "made in 15 minutes" if it wasn't; tag/credit the original brand in the post; never show "OpenAI × YourBrand"-style co-marks that imply a partnership; no REF people photos.
- Helpers every agent re-invented (add locally until core has them): text placed by ink edge + fitFont, hex colour mix, REF-shaped cursor, per-frame keyframe tables.

## 11. Product film mode — homepage SaaS film (from the "PROMPT MOTION DESIGN SAAS" brief, 29/09/2026)
Use for a 45-75 s product film that shows the whole product in action. Lean pass first (one language, 16:9, no VO, ~45-60 min), full treatment only when asked (overnight, Mac awake).
- **Story = a chain**: problem in the client's own words (3-5 s) → each step PRODUCES what the next one uses (the object leaving a step becomes the next scene, one continuous camera, no hard cuts) → the measurable result on screen → price twist → final CTA. Each step 2-7 s. Every element finishes animating and stays readable ≥ 1.5 s.
- **Screens are rebuilt in code, never pasted**: scan each screenshot in zoomed tiles, extract ONE `ui-tokens` file (exact colours by pixel sampling, fonts, radii, shadows, borders, spacing), rebuild components that animate element by element (rows cascading, counters, gauges, typing, cursor, toggles). Check each rebuilt screen side by side with its screenshot until it's recognisable at first glance.
- **i18n from day one**: no hard-coded text, one FR/EN dictionary; English written like a US SaaS UI, French = exact labels of the screenshots.
- **Anonymise**: one fictional company used everywhere (same domain, products, competitors in both languages); no real client, competitor or person; neutral avatar. Images containing text are rebuilt (code or photo part only + text re-typed).
- **Muted-first**: the homepage version autoplays without sound, so kinetic type carries the message. Safe margins 110 px (16:9) / 80 px (9:16); every title on ONE line.
- **Full treatment extras**: write a "motion bible" (30-40 checkable rules) from the references; 5 competing concepts (one-take, beat montage, metaphor, glass world, director's cut) scored by a jury and merged; after v1, 7 critics (motion, image, sound, story, muted readability, UI fidelity + translations, brand/copy rules), ≥ 3 rounds, each defect with frame numbers + severity + measurable fix; a new version only replaces the previous one if side-by-side judges find it better (keep a version log). Deliver 16:9 + recomposed 9:16 (not a crop), no-VO + VO EN/FR, separate WAV stems, README.
- **Machine hygiene**: one render at a time machine-wide (shared lock file), never parallel Whisper/heavy ffmpeg, delete superseded renders (keep current + previous), no built-in browser for sub-agents at night.
