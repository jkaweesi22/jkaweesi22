"""Generate assets/stats.svg (repo counts + top languages) from the GitHub API."""
import json, os, sys, urllib.request
from html import escape

USER = os.environ.get("GH_USER", "jkaweesi22")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

COLORS = {"JavaScript": "#F1E05A", "TypeScript": "#3178C6", "HTML": "#E34C26", "CSS": "#8E5BD9",
          "Python": "#3572A5", "Shell": "#89E051", "Swift": "#F05138", "Java": "#B07219"}
FALLBACK = ["#FB8C00", "#2E86C1", "#43A047", "#8E24AA", "#E53935"]


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "stats-card",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100&type=owner")
own = [r for r in repos if not r["fork"]]
stars = sum(r["stargazers_count"] for r in own)
langs = {}
for r in own:
    try:
        for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
            langs[k] = langs.get(k, 0) + v
    except Exception as e:
        print("skip", r["name"], e, file=sys.stderr)
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]

tiles = [("📦", "Public repos", user["public_repos"]), ("⭐", "Stars earned", stars),
         ("👥", "Followers", user["followers"])]

o = ['''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 928 250" width="928" height="250" role="img" aria-label="GitHub stats and top languages">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1f2937"/><stop offset="1" stop-color="#0f172a"/></linearGradient>
<linearGradient id="or" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FB8C00"/><stop offset="1" stop-color="#FFB74D"/></linearGradient>
<filter id="s" x="-5%" y="-5%" width="110%" height="120%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000" flood-opacity=".25"/></filter></defs>
<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}.b{transform-origin:0 0;animation:g 1.2s ease-out both}@keyframes g{from{transform:scaleX(0)}}</style>
<g filter="url(#s)"><rect x="12" y="8" width="904" height="226" rx="20" fill="url(#bg)"/></g>
<text x="44" y="46" font-size="16" font-weight="700" fill="#FB8C00">GITHUB SNAPSHOT</text>
<text x="884" y="46" text-anchor="end" font-size="11" fill="#94a3b8">public repos · auto-updated daily</text>
<line x1="470" y1="66" x2="470" y2="212" stroke="#334155"/>''']
for i, (ic, lab, val) in enumerate(tiles):
    y = 70 + i * 50
    o.append(f'<text x="44" y="{y+30}" font-size="26">{ic}</text>'
             f'<text x="92" y="{y+22}" font-size="26" font-weight="800" fill="#fff">{val}</text>'
             f'<text x="92" y="{y+40}" font-size="12" fill="#94a3b8">{lab}</text>')
o.append('<text x="504" y="80" font-size="13" font-weight="700" fill="#e2e8f0">Top languages</text>')
for i, (name, n) in enumerate(top):
    y = 100 + i * 24
    pct = n / total * 100
    col = COLORS.get(name, FALLBACK[i % len(FALLBACK)])
    w = max(6, 250 * n / top[0][1])
    o.append(f'<text x="504" y="{y+12}" font-size="12" fill="#cbd5e1">{escape(name)}</text>'
             f'<rect x="604" y="{y+2}" width="250" height="12" rx="6" fill="#334155"/>'
             f'<rect class="b" x="604" y="{y+2}" width="{w:.0f}" height="12" rx="6" fill="{col}" style="animation-delay:{i*.15}s"/>'
             f'<text x="884" y="{y+12}" text-anchor="end" font-size="12" font-weight="600" fill="#fff">{pct:.1f}%</text>')
o.append('</svg>')
os.makedirs("assets", exist_ok=True)
open("assets/stats.svg", "w").write("\n".join(o))
print("ok", user["public_repos"], stars, top)
