import json, sys, re, unicodedata, collections
rows_p, wiki_p, res_p, var_p, out_p = sys.argv[1:6]
ROLES = ["Árbitro", "Assistente", "Assistente", "Quarto árbitro", "VAR", "AVAR", "Assessor", "Quality manager"]
def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z ]", " ", s.replace("D'", "D").replace("D ALONSO", "DALONSO"))
pessoas = {}
for p in (res_p, var_p):
    for a in json.load(open(p, encoding="utf-8"))["arbitros"]:
        pessoas[a["id"]] = a["nome"]
import difflib
def ident(nome):
    t = [w for w in norm(nome).split() if len(w) > 1]
    if not t: return None
    def ok(w, n):
        return any(w == x or (len(w) >= 4 and difflib.SequenceMatcher(None, w, x).ratio() >= 0.8) for x in n)
    exatos = [pid for pid, n in pessoas.items() if set(t) <= set(norm(n).split())]
    if len(exatos) == 1: return exatos[0]
    if exatos: return None
    hits = [pid for pid, n in pessoas.items() if all(ok(w, norm(n).split()) for w in t)]
    return hits[0] if len(hits) == 1 else None
out = []
# Wikipédia: árbitro central em todos os jogos
for x in json.load(open(wiki_p, encoding="utf-8")):
    pid = ident(x["arbitro"])
    if not pid: print("sem par (wiki):", x["arbitro"]); continue
    fase = x["fase"] if x["fase"] != "Matches" else x["pagina"].replace("Copa Libertadores ", "").replace("Copa Sudamericana ", "")
    out.append({"pid": pid, "comp": x["comp"], "fase": fase, "data": x["data"], "jogo": x["jogo"], "funcao": "Árbitro", "fonte": "Wikipédia"})
# PDFs da Conmebol: todas as funções
for ri, r in enumerate(json.load(open(rows_p, encoding="utf-8"))):
    p = [list(q) for q in r["pairs"]]
    jogo = re.sub(r"^.*?[CG]\d\s+", "", r["jogo"]) if re.search(r"[CG]\d\s", r["jogo"]) else r["jogo"]
    for k, (n, c) in enumerate(p[:8]):
        if c != "BRA": continue
        pid = ident(n)
        if not pid: continue
        f = ROLES[k]
        out.append({"pid": pid, "comp": r["comp"], "fase": r["arq"], "data": r["data"], "jogo": jogo[:80], "funcao": f, "fonte": "Conmebol", "row": ri, "ctx": r.get("ctx", True)})
# tira duplicados (mesma pessoa, data e função); prefere Conmebol para o nome do jogo e Wikipédia para a fase
ded = {}
for x in out:
    k = (x["pid"], x["data"], x["funcao"])
    if k in ded:
        if x["fonte"] == "Wikipédia": ded[k]["fase"] = x["fase"]
        if "row" in x:
            ded[k]["row"] = x["row"]
            if not x["ctx"]: ded[k]["jogo"] = x["jogo"]   # linha da planilha oficial com o jogo completo vale mais que a Wikipédia
        ded[k]["fonte"] = "Conmebol + Wikipédia"
    else: ded[k] = dict(x)
# o nome do jogo da Wikipédia (árbitro central) vale para toda a equipe da mesma linha da planilha
jw = {x["row"]: x["jogo"] for x in ded.values() if x["fonte"] == "Conmebol + Wikipédia" and "row" in x}
for x in ded.values():
    if x.get("row") in jw: x["jogo"] = jw[x["row"]]
    x.pop("row", None)
res = sorted(ded.values(), key=lambda x: (x["data"], x["pid"]))
def fase_pt(f):
    m = re.search(r"Fecha-(\d)", f)
    if f.endswith(".txt"):
        if m: return f"Fase de grupos, rodada {m[1]}"
        m = re.search(r"Fase-(\d)", f)
        if m: return f"Fase {m[1]}"
        for k, v in (("Playoffs", "Playoffs"), ("Octavos", "Oitavas"), ("4tos", "Quartas"), ("Cuartos", "Quartas"), ("Semifinal", "Semifinal"), ("VUELTA", "Oitavas")):
            if k in f: return v
        return ""
    m = re.match(r"Group ([A-H])", f)
    if m: return f"Fase de grupos, grupo {m[1]}"
    return {"qualifying stages": "Fases preliminares", "first stage": "Primeira fase", "final stages": "Mata-mata"}.get(f, f)
for x in res:
    x["fase"] = fase_pt(x["fase"])
    x["jogo"] = re.sub(r"\s+", " ", re.sub(r"(?:BRA|ARG|URU|PAR|CHI|COL|PER|ECU|BOL|VEN)(?!\))", "", x["jogo"])).replace(" ( ", " (").strip()
    x["jogo"] = re.sub(r"\s*\((?:BRA|ARG|URU|PAR|CHI|COL|PER|ECU|BOL|VEN)\)", "", x["jogo"]).strip()
json.dump(res, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(res, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
c = collections.Counter((pessoas[x["pid"]], x["funcao"]) for x in res)
for (n, f), v in sorted(c.items()): print(f"{n[:32]:32} {f:15} {v}")
# conferência: árbitro central no PDF que a Wikipédia não tem
w = {(x["pid"], x["data"]) for x in out if x["fonte"] == "Wikipédia"}
for x in out:
    if x["fonte"] == "Conmebol" and x["funcao"] == "Árbitro" and (x["pid"], x["data"]) not in w: print("so no PDF:", pessoas[x["pid"]], x["data"], x["jogo"])
