import json, sys, re, datetime as dt, collections, statistics
g = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
HOJE = dt.date(2026, 11, 10)
P = lambda s: dt.datetime.strptime(s, "%d/%m/%Y").date()
# data de referência de cada rodada = mediana das datas
rd = {}
for r in range(1, 39):
    ds = sorted(P(x["data"]) for x in g if x["rodada"] == r)
    rd[r] = ds[len(ds)//2]
def rodadas_entre(a, b, incl_b=False):
    return [r for r in range(1, 39) if a < rd[r] and (rd[r] <= b if incl_b else rd[r] < b)]
PAUSA_INI, PAUSA_FIM = dt.date(2026,6,1), dt.date(2026,7,16)  # sem Série A nem Copa do Brasil: 1/6 a 15/7
def util(a, b):
    ov = max(0, (min(b, PAUSA_FIM) - max(a, PAUSA_INI)).days)
    return (b - a).days - ov
WC = {"Wilton Pereira Sampaio": [("11/06/2026","México","África do Sul","Estádio Azteca - Cidade do México","Fase de grupos"),("23/06/2026","Noruega","Senegal","MetLife Stadium - East Rutherford","Fase de grupos"),("29/06/2026","Holanda","Marrocos","Estádio BBVA - Guadalupe","16 avos de final")],
      "Raphael Claus": [("21/06/2026","Espanha","Arábia Saudita","Mercedes-Benz Stadium - Atlanta","Fase de grupos"),("01/07/2026","Estados Unidos","Bósnia","Levi's Stadium - Santa Clara","16 avos de final")],
      "Ramon Abatti Abel": [("15/06/2026","Bélgica","Egito","Lumen Field - Seattle","Fase de grupos"),("24/06/2026","Suíça","Canadá","BC Place - Vancouver","Fase de grupos")]}
refs = collections.defaultdict(list); info = {}
for x in g:
    a = x["arbitro"]
    if not a or "PRO" not in a["categoria"] or P(x["data"]) > HOJE: continue
    info[a["id"]] = a
    refs[a["id"]].append(x)
for rid, a in info.items():
    for i,(d,m,v,l,e) in enumerate(WC.get(a["nome"], [])):
        refs[rid].append({"id": f"wc{rid}-{i}", "comp": "Copa do Mundo", "etapa": e, "rodada": None, "data": d, "hora": "", "mandante": m, "visitante": v, "gm": None, "gv": None, "local": l})
print("copa:", sum(1 for r in refs.values() for x in r if x["comp"]=="Copa do Mundo"))
EXT = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else []
def split_jogo(j):
    p = re.split(r"\s+(?:vs\.?|x)\s+", j, maxsplit=1, flags=re.I)
    return (p[0], p[1] if len(p) > 1 else "")
for i, x in enumerate(EXT):
    if x["funcao"] != "Árbitro" or x["pid"] not in info: continue
    y, mo, d = x["data"].split("-"); m_, v_ = split_jogo(x["jogo"])
    refs[x["pid"]].append({"id": f"cm{i}", "comp": x["comp"], "etapa": x["fase"], "rodada": None, "data": f"{d}/{mo}/{y}", "hora": "", "mandante": m_, "visitante": v_, "gm": None, "gv": None, "local": ""})
print("conmebol:", sum(1 for r in refs.values() for x in r if x["comp"] in ("Libertadores","Sul-Americana")))
res = []
for rid, js in refs.items():
    js.sort(key=lambda x: (P(x["data"]), x["hora"]))
    gaps = []
    ini = dt.date(2026, 1, 27)
    d0 = P(js[0]["data"])
    rr = rodadas_entre(ini, d0)
    gaps.append({"tipo": "inicio", "de": None, "ate": js[0]["id"], "ini": "2026-01-28", "fim": str(d0), "dias": (d0 - dt.date(2026,1,28)).days, "util": util(dt.date(2026,1,28), d0), "rodadas": rr})
    for a, b in zip(js, js[1:]):
        da, db = P(a["data"]), P(b["data"])
        gaps.append({"tipo": "entre", "de": a["id"], "ate": b["id"], "ini": str(da), "fim": str(db), "dias": (db - da).days, "util": util(da, db), "rodadas": rodadas_entre(da, db)})
    dl = P(js[-1]["data"])
    gaps.append({"tipo": "aberto", "de": js[-1]["id"], "ate": None, "ini": str(dl), "fim": str(HOJE), "dias": (HOJE - dl).days, "util": util(dl, HOJE), "rodadas": rodadas_entre(dl, HOJE, True)})
    best = max(gaps, key=lambda z: (len(z["rodadas"]), z["dias"]))
    bestd = max(gaps, key=lambda z: (z["util"], len(z["rodadas"])))
    a = info[rid]
    res.append({"id": rid, "nome": a["nome"], "uf": a["uf"], "cat": a["categoria"],
        "jogos": [{k: x[k] for k in ("id","comp","etapa","data","hora","mandante","visitante","gm","gv","local")} for x in js],
        "gaps": gaps, "best": gaps.index(best), "bestDias": gaps.index(bestd)})
res.sort(key=lambda r: (-len(r["gaps"][r["best"]]["rodadas"]), -r["gaps"][r["best"]]["dias"]))
for r in res:
    b = r["gaps"][r["best"]]; bd = r["gaps"][r["bestDias"]]
    print(f'{r["nome"][:32]:32} {r["uf"]} {r["cat"]:10} j={len(r["jogos"]):2} | rod={len(b["rodadas"]):2} {b["tipo"]:6} {b["ini"]}->{b["fim"]} {b["dias"]}d R{b["rodadas"][:1]}-{b["rodadas"][-1:]} | maxutil={bd["util"]} ({bd["dias"]}cal) {bd["tipo"]} {bd["ini"]}->{bd["fim"]}')
json.dump({"hoje": str(HOJE), "rodadas": {r: str(d) for r, d in rd.items()}, "arbitros": res}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
