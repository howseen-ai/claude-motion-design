"""List Mixkit SFX (id + title): each card's title is searched between its own id marker and the next one, and before it."""
import re, sys, urllib.request
for q in sys.argv[1:]:
    html = urllib.request.urlopen(urllib.request.Request(f"https://mixkit.co/free-sound-effects/{q}/", headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read().decode("utf8", "ignore")
    marks = [(m.start(), m.group(1)) for m in re.finditer(r'data-audio-player-item-id-value="(\d+)"', html)]
    titles = [(m.start(), m.group(1).strip()) for m in re.finditer(r'item-grid-card__title">\s*(?:<[^>]+>\s*)*([^<]+?)\s*<', html)]
    print("==", q, len(marks), "ids", len(titles), "titles")
    for i, (p, sid) in enumerate(marks[:14]):
        nxt = marks[i + 1][0] if i + 1 < len(marks) else len(html)
        prv = marks[i - 1][0] if i else 0
        after = [t for pos, t in titles if p < pos < nxt]
        before = [t for pos, t in titles if prv < pos < p]
        print(f"   {sid:>5}  after={after[:1]}  before={before[-1:]}")
