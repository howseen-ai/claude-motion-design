"""Download the third-party assets for the example (not redistributed in this repo; check each license):
Mixkit music + SFX (Mixkit free license), svgl.app / simple-icons logos (brand marks belong to their owners), Geist font (OFL)."""
import json, urllib.request
from pathlib import Path
H = Path(__file__).parent; UA = {"User-Agent": "Mozilla/5.0"}
def get(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()); print("ok", dest.relative_to(H))
get("https://assets.mixkit.co/music/371/371.mp3", H / "assets/audio/cat-walk.mp3")
for sid in ["1117", "2568", "1125", "2357", "1143", "2865", "3083"]:
    get(f"https://assets.mixkit.co/active_storage/sfx/{sid}/{sid}-preview.mp3", H / f"assets/sfx/{sid}.mp3")
for name, url in {"w1490": "https://assets.mixkit.co/active_storage/sfx/1490/1490-preview.mp3", "w1489": "https://assets.mixkit.co/active_storage/sfx/1489/1489-preview.mp3"}.items():
    get(url, H / f"assets/sfx/{name}.mp3")
SVGL = {"chatgpt": "openai.svg", "gemini": "gemini.svg", "perplexity": "perplexity.svg", "google": "google.svg", "claude": "claude-ai-icon.svg",
        "youtube": "youtube.svg", "reddit": "reddit.svg", "trustpilot": "trustpilot.svg", "linkedin": "linkedin.svg", "shopify": "shopify.svg",
        "wordpress": "wordpress.svg", "webflow": "webflow.svg", "framer": "framer.svg", "nextjs": "nextjs_icon_dark.svg"}
for n, f in SVGL.items(): get("https://svgl.app/library/" + f, H / f"assets/svg/{n}.svg")
for n in ["wix", "wikipedia", "ghost", "bigcommerce"]: get(f"https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{n}.svg", H / f"assets/svg/{n}.svg")
get("https://cdn.jsdelivr.net/npm/simple-icons@13/icons/wordpress.svg", H / "assets/wordpress.svg")
get("https://cdn.jsdelivr.net/npm/simple-icons@13/icons/shopify.svg", H / "assets/shopify.svg")
get("https://cdn.jsdelivr.net/npm/simple-icons@13/icons/ghost.svg", H / "assets/ghost.svg")
get("https://fonts.gstatic.com/s/geist/v5/gyByhwUxId8gMEwcGFWNOITd.woff2", H / "fonts/geist-latin.woff2")
print("done")
