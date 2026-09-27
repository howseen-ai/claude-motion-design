"""Download colour SVG logos from svgl.app for sources + CMS into h20/assets/svg/."""
import json, urllib.parse, urllib.request
from pathlib import Path
OUT = Path("assets/svg"); OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0"}
WANT = {"youtube": "youtube", "reddit": "reddit", "trustpilot": "trustpilot", "wikipedia": "wikipedia", "linkedin": "linkedin",
        "shopify": "shopify", "wordpress": "wordpress", "webflow": "webflow", "wix": "wix", "ghost": "ghost", "bigcommerce": "bigcommerce",
        "framer": "framer", "nextjs": "next"}
for name, q in WANT.items():
    try:
        res = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.svgl.app?search=" + urllib.parse.quote(q), headers=UA), timeout=30).read())
    except Exception as e:
        print(name, "ERR", e); continue
    pick = next((r for r in res if r["title"].lower().replace(".", "").startswith(q.replace(".", ""))), res[0] if res else None)
    if not pick: print(name, "none"); continue
    route = pick["route"] if isinstance(pick["route"], str) else pick["route"].get("light")
    (OUT / f"{name}.svg").write_bytes(urllib.request.urlopen(urllib.request.Request(route, headers=UA), timeout=30).read())
    print(name, "<-", pick["title"], route)
