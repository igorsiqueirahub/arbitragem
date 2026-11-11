import re, json, sys
CODES = r"(?:BRA|ARG|URU|PAR|CHI|COL|PER|ECU|BOL|VEN)"
def limpa(j):
    j = re.sub(r"^\s*\d{1,3}\s+\d{1,2}/\d{1,2}(?:/\d{4})?\s+", "", j)          # nº e data no começo
    j = re.sub(r"^.*?\b[CG]\d+\s+", "", j) if re.search(r"\b[CG]\d+\s", j) else j  # cidade + chave (C1, G3)
    j = re.sub(r"\s*\(" + CODES + r"\)", "", j)                                   # (ARG)
    j = re.sub(r"\b" + CODES + r"\b", "", j)                                      # ARG solto (Wikipédia)
    j = re.sub(r"\s+", " ", j).strip()
    j = re.sub(r"\s+vs\.?\s+", " x ", j, flags=re.I)
    if j.replace(" x ", " ").isupper(): j = " ".join(w if len(w) <= 3 and "." in w else w.capitalize() for w in j.lower().split()).replace(" X ", " x ")
    j = re.sub(r"\bDel\b", "del", j).replace(" De ", " de ").replace(" Da ", " da ")
    return j
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
for x in d: x["jogo"] = limpa(x["jogo"])
json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for x in d[:40]: print(x["data"], x["jogo"])
