import json, sys, glob, os, datetime as dt, collections
res_p, raw, rawb, out = sys.argv[1:5]
R = json.load(open(res_p, encoding="utf-8")); HOJE = dt.date.fromisoformat(R["hoje"])
FASE = {"1995":"1ª fase","1996":"2ª fase","1997":"3ª fase","1998":"4ª fase","1999":"5ª fase","2000":"Oitavas","2001":"Quartas","2002":"Semifinal"}
FUN = {"arbitro":"Árbitro","var":"VAR","avar":"AVAR","avar2":"AVAR 2","quarto arbitro":"Quarto árbitro","arbitro assistente 1":"Assistente","arbitro assistente 2":"Assistente"}
esc = collections.defaultdict(list)
files = [(f, "A") for f in glob.glob(os.path.join(raw, "A_*.json"))] + [(f, "CDB") for f in glob.glob(os.path.join(raw, "CDB_*.json"))] + [(f, "B") for f in glob.glob(os.path.join(rawb, "B_*.json"))]
for f, c in files:
    key = os.path.basename(f)[:-5].split("_")[1]
    comp = {"A":"Série A","B":"Série B","CDB":"Copa do Brasil"}[c]
    etapa = f"Rodada {key}" if c != "CDB" else FASE[key.split("-")[0]]
    for g in json.load(open(f, encoding="utf-8")).get("jogos", []):
        for j in g["jogo"]:
            d = dt.datetime.strptime(j["data"].strip(), "%d/%m/%Y").date()
            if d > HOJE: continue
            for a in j.get("arbitros", []):
                fn = a.get("funcao","").strip().lower()
                if fn not in FUN: continue
                esc[a["id"]].append({"comp": comp, "etapa": etapa, "data": str(d), "funcao": FUN[fn], "jogo": f'{j["mandante"]["nome"]} x {j["visitante"]["nome"]}'})
EXT = json.load(open(sys.argv[5], encoding="utf-8")) if len(sys.argv) > 5 else []
for x in EXT:
    if x["funcao"] == "Árbitro": continue
    esc[x["pid"]].append({"comp": x["comp"], "etapa": x["fase"], "data": x["data"], "funcao": x["funcao"], "jogo": x["jogo"]})
for a in R["arbitros"]:
    E = sorted(esc[a["id"]], key=lambda x: x["data"])
    for g in a["gaps"]:
        ini = dt.date.fromisoformat(g["ini"]); fim = dt.date.fromisoformat(g["fim"])
        lo = (lambda d: d >= ini) if g["tipo"] == "inicio" else (lambda d: d > ini)
        hi = (lambda d: d <= fim) if g["tipo"] == "aberto" else (lambda d: d < fim)
        g["outros"] = [x for x in E if lo(dt.date.fromisoformat(x["data"])) and hi(dt.date.fromisoformat(x["data"]))]
    b = a["gaps"][a["best"]]
    c = collections.Counter(f'{x["comp"]}/{x["funcao"]}' for x in b["outros"])
    print(f'{a["nome"][:30]:30} rod={len(b["rodadas"]):2} {b["ini"]}->{b["fim"]} | {dict(c) or "SEM ESCALA"}')
json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False)
