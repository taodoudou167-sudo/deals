"""Télécharge tous les sets LEGO depuis Brickset et réécrit data.js.
Lancé chaque jour par GitHub Actions (clé dans le secret BRICKSET_KEY)."""
import json, os, sys, datetime, urllib.parse, urllib.request

KEY = os.environ["BRICKSET_KEY"]
rows = []
for year in range(2000, datetime.date.today().year + 2):
    page = 1
    while True:
        params = json.dumps({"year": str(year), "pageSize": 500, "pageNumber": page})
        url = ("https://brickset.com/api/v3.asmx/getSets?apiKey=" + urllib.parse.quote(KEY)
               + "&userHash=&params=" + urllib.parse.quote(params))
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)
        if d.get("status") != "success":
            sys.exit("Erreur API: %s" % d.get("message"))
        for s in d.get("sets", []):
            if s.get("category") != "Normal":
                continue
            lc = s.get("LEGOCom") or {}
            de = lc.get("DE") or {}
            x = None
            for c in ("DE", "US"):
                v = (lc.get(c) or {}).get("dateLastAvailable")
                if v and not x:
                    x = str(v)[:10]
            rows.append({"n": s.get("number"), "v": s.get("numberVariant"), "t": s.get("name"),
                         "y": s.get("year"), "h": s.get("theme"), "b": s.get("subtheme"),
                         "p": s.get("pieces"), "m": s.get("minifigs"), "e": de.get("retailPrice"),
                         "x": x, "r": s.get("rating"), "a": s.get("availability")})
        if page * 500 >= d.get("matches", 0):
            break
        page += 1

if len(rows) < 5000:
    sys.exit("Trop peu de sets (%d), on garde l'ancien fichier." % len(rows))
with open("data.js", "w", encoding="utf-8") as f:
    f.write("const DATA = " + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n")
    f.write('const UPDATED = "%s";\n' % datetime.date.today().isoformat())
print("OK", len(rows), "sets")
