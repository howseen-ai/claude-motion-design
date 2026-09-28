/* core.js — shared, deterministic helpers for the frame-locked remake.
   Everything is a PURE function of the global frame F (24 fps). No timers, no Date, no Math.random.
   Shot files register with SHOT({id, f0, f1, render(lf, F)}) and return an HTML string for the 1920x1080 stage. */
(function () {
  const FPS = 24, W = 1920, H = 1080;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;
  const inv = (a, b, x) => clamp((x - a) / (b - a));

  // ---- easing set
  const E = {
    lin: t => t,
    inQ: t => t * t, outQ: t => 1 - (1 - t) * (1 - t), ioQ: t => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
    inC: t => t * t * t, outC: t => 1 - Math.pow(1 - t, 3), ioC: t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
    outQuart: t => 1 - Math.pow(1 - t, 4), ioQuart: t => t < .5 ? 8 * t ** 4 : 1 - Math.pow(-2 * t + 2, 4) / 2,
    outExpo: t => t >= 1 ? 1 : 1 - Math.pow(2, -10 * t), ioExpo: t => t <= 0 ? 0 : t >= 1 ? 1 : t < .5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2,
    outBack: t => { const c = 1.70158, c3 = c + 1; return 1 + c3 * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); },
  };
  // spring (closed form, underdamped) from 0 -> 1, tau in frames
  const spring = (tau, f = 2.2, z = 0.55) => { if (tau <= 0) return 0; const t = tau / FPS; const w = 2 * Math.PI * f; return 1 - Math.exp(-z * w * t) * Math.cos(w * Math.sqrt(1 - z * z) * t); };

  // kf(F, [[f, v], [f, v], ...], ease|easeArray) -> piecewise interpolation, holds ends
  function kf(F, keys, ease = E.ioC) {
    if (F <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      if (F <= keys[i][0]) {
        const [f0, v0] = keys[i - 1], [f1, v1] = keys[i];
        const e = Array.isArray(ease) ? (ease[i - 1] || E.ioC) : ease;
        return lerp(v0, v1, e((F - f0) / (f1 - f0)));
      }
    }
    return keys[keys.length - 1][1];
  }
  // samples(F, f0, arr): linear interp inside a per-frame measured array starting at frame f0
  function samples(F, f0, arr) {
    const x = F - f0; if (x <= 0) return arr[0]; if (x >= arr.length - 1) return arr[arr.length - 1];
    const i = Math.floor(x), t = x - i; return lerp(arr[i], arr[i + 1], t);
  }
  // seeded hash rand in [0,1)
  const rand = (n, s = 1) => { let x = Math.sin(n * 127.1 + s * 311.7) * 43758.5453; return x - Math.floor(x); };

  // ---- brand tokens (Howseen)
  const T = {
    bg: '#ffffff', ink: '#0f172a', sub: '#64748b', line: '#e5e7eb', soft: '#f5f7fa',
    a1: '#38bdf8', a2: '#a78bfa', aDeep: '#0369a1', blue: '#2f7bf5', green: '#22c55e',
    grad: 'linear-gradient(90deg,#38bdf8 0%,#a78bfa 100%)',
    font: "'Geist', 'Inter', -apple-system, 'SF Pro Display', Helvetica, Arial, sans-serif",
  };
  const A = n => 'assets/' + n; // asset path

  // ---- camera: wraps inner HTML, scale around origin + translate, optional blur
  function camera(inner, { s = 1, tx = 0, ty = 0, ox = W / 2, oy = H / 2, blur = 0, op = 1, dblur = null } = {}) {
    const f = [];
    if (blur > 0.01) f.push(`blur(${blur.toFixed(2)}px)`);
    const filt = f.length ? `filter:${f.join(' ')};` : '';
    const db = dblur ? `filter:url(#${dblur});` : '';
    return `<div style="position:absolute;inset:0;transform-origin:${ox}px ${oy}px;transform:translate(${tx}px,${ty}px) scale(${s});opacity:${op};${filt}${db}">${inner}</div>`;
  }
  // directional motion blur via SVG filter defs; returns [defsHTML, id]
  function mblurDefs(id, dx, dy) {
    return `<svg width="0" height="0" style="position:absolute"><filter id="${id}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="${Math.abs(dx).toFixed(2)} ${Math.abs(dy).toFixed(2)}"/></filter></svg>`;
  }
  // ---- cursor (macOS arrow), tip at (x,y); press 0..1 scales down slightly
  function cursor(x, y, { press = 0, scale = 1, op = 1 } = {}) {
    const s = scale * (1 - 0.12 * press);
    return `<svg style="position:absolute;left:${x}px;top:${y}px;transform-origin:0 0;transform:scale(${s});opacity:${op};overflow:visible;z-index:50" width="28" height="40" viewBox="0 0 28 40">
      <path d="M2 2 L2 31 L9.5 24 L14.5 36 L19 34 L14 22.5 L24 22.5 Z" fill="#000" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>`;
  }
  // ---- text helpers
  // reveal chars: returns text truncated to n chars (typing)
  const typed = (s, n) => s.slice(0, Math.max(0, Math.floor(n)));
  // per-word reveal spans with opacity/blur/y driven by t (0..1) staggered
  function words(s, t, { stagger = 0.12, dur = 0.35, y = 14, blur = 6, color = null, accent = [] } = {}) {
    const ws = s.split(' ');
    return ws.map((w, i) => {
      const p = clamp((t - i * stagger) / dur);
      const e = E.outC(p);
      const col = accent.includes(i) ? `background:${T.grad};-webkit-background-clip:text;background-clip:text;color:transparent;` : (color ? `color:${color};` : '');
      return `<span style="display:inline-block;opacity:${e};transform:translateY(${(1 - e) * y}px);filter:blur(${(1 - e) * blur}px);${col}">${w}</span>`;
    }).join('<span style="display:inline-block;width:.28em"></span>');
  }
  // gradient text span
  const gtext = s => `<span style="background:${T.grad};-webkit-background-clip:text;background-clip:text;color:transparent">${s}</span>`;
  // ---- logos
  // Howseen mark (black glyph PNG used as mask so any fill works)
  function mark(size, fill = T.ink) {
    return `<div style="width:${size}px;height:${size}px;background:${fill};-webkit-mask:url(${A('logo-mark.png')}) center/contain no-repeat;mask:url(${A('logo-mark.png')}) center/contain no-repeat"></div>`;
  }
  // app icon tile (rounded square with gradient + white mark), like the REF app icon
  function appIcon(size, { grad = T.grad } = {}) {
    return `<div style="width:${size}px;height:${size}px;border-radius:${size * .24}px;background:${grad};display:flex;align-items:center;justify-content:center;box-shadow:0 ${size * .06}px ${size * .18}px rgba(56,189,248,.25)">${mark(size * .62, '#fff')}</div>`;
  }
  const img = (n, size, extra = '') => `<img src="${A(n)}" style="width:${size}px;height:${size}px;object-fit:contain;${extra}">`;
  const ENGINES = [['logo-chatgpt-v2.png', 'ChatGPT'], ['logo-gemini.png', 'Gemini'], ['logo-perplexity.png', 'Perplexity'], ['logo-google.png', 'AI Overviews'], ['logo-claude.png', 'Claude']];

  // ---- pixel dissolve: grid of squares covering a rect, each square flips at a seeded threshold
  function pixelDissolve(x, y, w, h, t, { cell = 24, colors = [T.a1, T.a2, '#e0f2fe', '#ede9fe'], seed = 3 } = {}) {
    const cols = Math.ceil(w / cell), rows = Math.ceil(h / cell); let out = '';
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const k = r * cols + c, th = rand(k, seed);
      const on = t > th * 0.8 && t < th * 0.8 + 0.35;
      if (!on) continue;
      out += `<div style="position:absolute;left:${x + c * cell}px;top:${y + r * cell}px;width:${cell}px;height:${cell}px;background:${colors[k % colors.length]};opacity:${(0.35 + 0.65 * rand(k, seed + 1)).toFixed(2)}"></div>`;
    }
    return out;
  }

  // ---- palette filter: re-hue any leftover Gojiberry reds/oranges to Howseen sky/violet (applied to final HTML string)
  function hexToRgb(h) { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); const n = parseInt(h, 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }
  function rgbToHsl(r, g, b) { r /= 255; g /= 255; b /= 255; const mx = Math.max(r, g, b), mn = Math.min(r, g, b); let h = 0, s = 0; const l = (mx + mn) / 2; if (mx !== mn) { const d = mx - mn; s = l > .5 ? d / (2 - mx - mn) : d / (mx + mn); h = mx === r ? (g - b) / d + (g < b ? 6 : 0) : mx === g ? (b - r) / d + 2 : (r - g) / d + 4; h /= 6; } return [h * 360, s, l]; }
  function hslToHex(h, s, l) { h /= 360; const f = n => { const k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l); const c = l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)); return Math.round(c * 255).toString(16).padStart(2, '0'); }; return '#' + f(0) + f(8) + f(4); }
  function paletteFilter(html) {
    return html.replace(/#[0-9a-fA-F]{6}\b/g, m => {
      const [r, g, b] = hexToRgb(m); const [h, s, l] = rgbToHsl(r, g, b);
      if (s > 0.35 && (h < 45 || h > 330)) { const nh = h > 330 || h < 15 ? 262 : 199; return hslToHex(nh, Math.min(s, .9), l); }
      return m;
    });
  }

  // ---- registry + seek
  const SHOTS = [];
  window.SHOT = def => { SHOTS.push(def); SHOTS.sort((a, b) => a.f0 - b.f0); };
  window.CORE = { FPS, W, H, clamp, lerp, inv, E, spring, kf, samples, rand, T, A, camera, mblurDefs, cursor, typed, words, gtext, mark, appIcon, img, ENGINES, pixelDissolve, paletteFilter };
  window.seek = t => {
    const F = Math.round(t * FPS);
    const st = document.getElementById('stage');
    const s = SHOTS.find(x => F >= x.f0 && F < x.f1) || SHOTS[SHOTS.length - 1];
    let html = '';
    if (s && F >= s.f0 && F < s.f1) { try { html = s.render(F - s.f0, F); } catch (e) { html = `<div style="color:red;font:30px monospace;padding:40px">${s.id} error: ${e}</div>`; console.error(s.id, e); } }
    else html = `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:40px monospace;color:#bbb">F${F} — no shot</div>`;
    st.innerHTML = paletteFilter(html);
    return F;
  };
})();
