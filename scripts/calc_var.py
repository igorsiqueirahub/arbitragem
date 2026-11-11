import json, sys, glob, os, re, datetime as dt, collections
raw, rawb, base_p, out = sys.argv[1:5]
EXT = json.load(open(sys.argv[5], encoding="utf-8")) if len(sys.argv) > 5 else []
BASE = json.load(open(base_p, encoding="utf-8"))
HOJE = dt.date.fromisoformat(BASE["hoje"])
rd = {int(k): dt.date.fromisoformat(v) for k, v in BASE["rodadas"].items()}
CAT = "VAR-FIFA-PRO"
PAUSA_INI, PAUSA_FIM = dt.date(2026, 6, 1), dt.date(2026, 7, 16)
def util(a, b):
    return (b - a).days - max(0, (min(b, PAUSA_FIM) - max(a, PAUSA_INI)).days)
FASE = {"1995":"1ª fase","1996":"2ª fase","1997":"3ª fase","1998":"4ª fase","1999":"5ª fase","2000":"Oitavas","2001":"Quartas","2002":"Semifinal"}
FUN = {"arbitro":"Árbitro","var":"VAR","avar":"AVAR","avar2":"AVAR 2","quarto arbitro":"Quarto árbitro","arbitro assistente 1":"Assistente","arbitro assistente 2":"Assistente"}
P = lambda s: dt.datetime.strptime(s.strip(), "%d/%m/%Y").date()
elite = collections.defaultdict(list); info = {}; esc = collections.defaultdict(list)
files = [(f, "A") for f in glob.glob(os.path.join(raw, "A_*.json"))] + [(f, "CDB") for f in glob.glob(os.path.join(raw, "CDB_*.json"))] + [(f, "B") for f in glob.glob(os.path.join(rawb, "B_*.json"))]
for f, c in files:
    key = os.path.basename(f)[:-5].split("_")[1]
    comp = {"A":"Série A","B":"Série B","CDB":"Copa do Brasil"}[c]
    if c == "CDB":
        fid, r = key.split("-"); etapa = FASE[fid] + (f" (jogo {r})" if fid >= "1999" else "")
    else: etapa = f"Rodada {key}"
    for g in json.load(open(f, encoding="utf-8")).get("jogos", []):
        for j in g["jogo"]:
            d = P(j["data"])
            if d > HOJE: continue
            central = next((a["nome"] for a in j.get("arbitros", []) if a["funcao"].strip().lower() == "arbitro"), "")
            for a in j.get("arbitros", []):
                fn = a["funcao"].strip().lower()
                if fn not in FUN: continue
                if fn == "var" and c in ("A", "CDB") and a["categoria"] == CAT:
                    info[a["id"]] = a
                    elite[a["id"]].append({"id": j["id_jogo"], "comp": comp, "etapa": etapa, "data": j["data"].strip(), "hora": j.get("hora","").strip(),
                        "mandante": j["mandante"]["nome"], "visitante": j["visitante"]["nome"], "gm": j["mandante"].get("gols"), "gv": j["visitante"].get("gols"),
                        "local": j.get("local","").strip(), "central": central})
                else:
                    esc[a["id"]].append({"comp": comp, "etapa": etapa, "data": str(d), "funcao": FUN[fn], "jogo": f'{j["mandante"]["nome"]} x {j["visitante"]["nome"]}'})
for i, x in enumerate(EXT):
    if x["pid"] not in info: continue
    if x["funcao"] == "VAR":
        y, mo, d = x["data"].split("-"); p_ = re.split(r"\s+(?:vs\.?|x)\s+", x["jogo"], maxsplit=1, flags=re.I)
        elite[x["pid"]].append({"id": f"cm{i}", "comp": x["comp"], "etapa": x["fase"], "data": f"{d}/{mo}/{y}", "hora": "", "mandante": p_[0], "visitante": p_[1] if len(p_) > 1 else "", "gm": None, "gv": None, "local": "", "central": ""})
    else:
        esc[x["pid"]].append({"comp": x["comp"], "etapa": x["fase"], "data": x["data"], "funcao": x["funcao"], "jogo": x["jogo"]})
def entre(a, b, incl=False):
    return [r for r in range(1, 39) if a < rd[r] and (rd[r] <= b if incl else rd[r] < b)]
res = []
for rid, js in elite.items():
    js.sort(key=lambda x: (P(x["data"]), x["hora"]))
    gaps = []; ini = dt.date(2026, 1, 28); d0 = P(js[0]["data"])
    gaps.append({"tipo": "inicio", "ini": str(ini), "fim": str(d0), "dias": (d0-ini).days, "util": util(ini, d0), "rodadas": entre(ini - dt.timedelta(days=1), d0)})
    for a, b in zip(js, js[1:]):
        da, db = P(a["data"]), P(b["data"])
        gaps.append({"tipo": "entre", "ini": str(da), "fim": str(db), "dias": (db-da).days, "util": util(da, db), "rodadas": entre(da, db)})
    dl = P(js[-1]["data"])
    gaps.append({"tipo": "aberto", "ini": str(dl), "fim": str(HOJE), "dias": (HOJE-dl).days, "util": util(dl, HOJE), "rodadas": entre(dl, HOJE, True)})
    E = sorted(esc[rid], key=lambda x: x["data"])
    for g in gaps:
        i, f_ = dt.date.fromisoformat(g["ini"]), dt.date.fromisoformat(g["fim"])
        g["outros"] = [x for x in E if (dt.date.fromisoformat(x["data"]) >= i if g["tipo"] == "inicio" else dt.date.fromisoformat(x["data"]) > i)
                       and (dt.date.fromisoformat(x["data"]) <= f_ if g["tipo"] == "aberto" else dt.date.fromisoformat(x["data"]) < f_)]
    best = max(gaps, key=lambda z: (len(z["rodadas"]), z["util"])); bestd = max(gaps, key=lambda z: (z["util"], len(z["rodadas"])))
    a = info[rid]
    res.append({"id": rid, "nome": a["nome"], "uf": a["uf"], "cat": a["categoria"], "jogos": js, "gaps": gaps, "best": gaps.index(best), "bestDias": gaps.index(bestd)})
res.sort(key=lambda r: (-len(r["gaps"][r["best"]]["rodadas"]), -r["gaps"][r["best"]]["util"]))
for r in res:
    b = r["gaps"][r["best"]]
    c = collections.Counter(f'{x["comp"]}/{x["funcao"]}' for x in b["outros"])
    print(f'{r["nome"][:34]:34} {r["uf"]} j={len(r["jogos"]):2} | rod={len(b["rodadas"]):2} {b["tipo"]:6} {b["ini"]}->{b["fim"]} {b["util"]}d(util) {b["dias"]}d | {dict(c) or "SEM ESCALA"}')
json.dump({"hoje": BASE["hoje"], "rodadas": BASE["rodadas"], "arbitros": res}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
