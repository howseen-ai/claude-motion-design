from pathlib import Path
H = Path(__file__).parent
groups = {"G1": (0, 528), "G2": (528, 906), "G3": (906, 1154), "G4": (1154, 1557)}
for g, (a, b) in groups.items():
    p = H / f"shots/{g}.js"
    if not p.exists():
        p.write_text(f"""(function () {{
  const C = CORE;
  // {g}: frames {a}-{b}. Replace this placeholder with real shots (SHOT per shot id).
  SHOT({{ id: '{g}_placeholder', f0: {a}, f1: {b}, render: (lf, F) =>
    `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:48px Geist;color:#94a3b8">{g} · F${{F}}</div>` }});
}})();
""")
        print("stub", g)
