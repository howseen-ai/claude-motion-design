"""Minimal MCP client for 21st.dev (streamable HTTP + x-api-key). usage: mcp21.py tools | mcp21.py call <tool> '<json>'"""
import json, os, sys, urllib.request
KEY = os.environ.get("API_KEY_21ST") or open(os.path.expanduser("~/.config/21st.key")).read().strip()
URL = "https://21st.dev/api/mcp"
SID = None


def rpc(method, params=None, id_=1):
    global SID
    body = {"jsonrpc": "2.0", "method": method}
    if id_ is not None: body["id"] = id_
    if params is not None: body["params"] = params
    h = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "x-api-key": KEY, "User-Agent": "claude-code-mcp-client/1.0"}
    if SID: h["Mcp-Session-Id"] = SID
    try:
        r = urllib.request.urlopen(urllib.request.Request(URL, data=json.dumps(body).encode(), headers=h), timeout=90)
    except urllib.error.HTTPError as e:
        print("HTTP", e.code, e.read().decode()[:600]); sys.exit(1)
    SID = r.headers.get("Mcp-Session-Id") or SID
    raw = r.read().decode()
    if not raw.strip(): return None
    if raw.lstrip().startswith("{"): return json.loads(raw)
    for line in raw.splitlines():
        if line.startswith("data:"):
            d = json.loads(line[5:].strip())
            if d.get("id") == id_: return d
    return raw


rpc("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "claude-code-raph", "version": "1"}})
rpc("notifications/initialized", None, None)
if sys.argv[1] == "tools":
    for t in rpc("tools/list", {}, 2)["result"]["tools"]:
        props = list((t.get("inputSchema") or {}).get("properties", {}).keys())
        print(f"- {t['name']}({', '.join(props)}): {(t.get('description') or '')[:260]}")
else:
    res = rpc("tools/call", {"name": sys.argv[2], "arguments": json.loads(sys.argv[3] if len(sys.argv) > 3 else "{}")}, 3)
    r = res.get("result", res) if isinstance(res, dict) else res
    if isinstance(r, dict) and "content" in r:
        for c in r["content"]: print(c.get("text", c)[:12000] if isinstance(c.get("text"), str) else c)
    else: print(json.dumps(r, ensure_ascii=False)[:12000])
