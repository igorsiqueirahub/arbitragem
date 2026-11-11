import json, sys, os, glob, collections
raw = sys.argv[1]; out = sys.argv[2]
FASE = {"1995":"1ª fase","1996":"2ª fase","1997":"3ª fase","1998":"4ª fase","1999":"5ª fase","2000":"Oitavas","2001":"Quartas","2002":"Semifinal"}
games = []
for f in sorted(glob.glob(os.path.join(raw, "*.json"))):
    name = os.path.basename(f)[:-5]
    comp, key = name.split("_")
    d = json.load(open(f, encoding="utf-8"))
    for g in d.get("jogos", []):
        for j in g["jogo"]:
            arb = [a for a in j.get("arbitros", []) if a.get("funcao","").strip().lower() == "arbitro"]
            if comp == "A": etapa = f"Rodada {key}"
            else:
                fid, r = key.split("-"); etapa = FASE[fid] + (f" (jogo {r})" if fid >= "1999" else "")
            games.append({
                "comp": "Série A" if comp == "A" else "Copa do Brasil",
                "etapa": etapa, "rodada": int(key) if comp == "A" else None,
                "id": j["id_jogo"], "num": j["num_jogo"],
                "data": j["data"].strip(), "hora": j.get("hora","").strip(),
                "mandante": j["mandante"]["nome"], "visitante": j["visitante"]["nome"],
                "gm": j["mandante"].get("gols"), "gv": j["visitante"].get("gols"),
                "local": j.get("local","").strip(),
                "arbitro": arb[0] if arb else None,
            })
json.dump(games, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("jogos", len(games), "sem arbitro", sum(1 for g in games if not g["arbitro"]))
c = collections.Counter((g["arbitro"]["categoria"]) for g in games if g["arbitro"])
print(c)
print(collections.Counter(g["comp"] for g in games))
for r in range(33, 39):
    gs = [g for g in games if g["rodada"] == r]
    print(r, len(gs), sum(1 for g in gs if g["arbitro"]), sorted(set(g["data"] for g in gs)))
