# BRIEF — build agents (frame-locked remake of [REF VIDEO] for [BRAND])

Workdir (absolute): [WORKDIR] · Python: [VENV]/bin/python · page: http://localhost:[PORT]/[DIR]/index.html (server already running).

## Acceptance bar
Our render must match REF frame-by-frame in LAYOUT, SIZES, POSITIONS, TIMING, EASING, CAMERA, CUTS, BLUR, CURSOR PATH, TYPING CADENCE when shown side by side in sync ("original | copy" split-screen). Only content is swapped. Target: position/size error ≤1-2% of frame, cuts 0 frames off. Differences allowed only where the swap forces them (word widths) — report each.

## Swap rules (edit per project)
- [OLD BRAND] → [BRAND] (CORE.appIcon / CORE.mark), accent colours → brand tokens (CORE.T).
- Partner/co-brand marks: never imply a partnership that doesn't exist (e.g. "OpenAI ×" → a true co-mark like "Opus 5.5 ×").
- No photos of real people from REF: replace with logo tiles, cards or neutral shapes of the same size/motion.
- Copy must be TRUE for the brand; no invented numbers (mock UI numbers must read as examples).
- Never reuse REF music, voice or images.

## File rules
Write ONLY shots/<G>.js (IIFE, helpers prefixed <G>_, one SHOT({id,f0,f1,render}) per shot, contiguous range). Pure function of F (CORE.rand, never Math.random/Date/timers). Never edit core.js/index.html/scripts. Scratch in out/<G>/ and measure/<G>_*.

## Method
1. Read SPEC.md + core.js API.
2. MEASURE with numpy on ref/full frames (ink bboxes, typing char count, cursor tip, camera scale/offset, fade timing) → drive motion with CORE.samples.
3. Verify loop per shot: `remake_render.py compare out/<G> <frames…>` (first/last, keyframes, 2 frames into every transition, ≤15 per call); read compare_sheet.jpg; iterate. Never claim a match without viewing ref|ours.
4. Pitfalls: measure text widths only after fonts load (lazy); REF cursor is often not the macOS arrow (draw it from REF); REF whips may be crisp; seeded bursts; check REF's real cut frames (SPEC boundaries are often ±4 frames off).

## Report
Table: shot | frames | MATCHES/CLOSE/ROUGH | residual diff | frames that would drift | spec errors.
