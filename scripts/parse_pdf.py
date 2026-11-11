import re, sys, glob, os, json, collections
C = r"(?:BRA|ARG|URU|PAR|CHI|COL|PER|ECU|BOL|VEN|MEX|USA)"
TOK = r"(?!" + C + r"\b)[A-ZÁÉÍÓÚÑÃÕÇÜ][A-ZÁÉÍÓÚÑÃÕÇÜ'.\-]*"
NAME = TOK + r"(?: " + TOK + r")*"
out = []
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.txt"))):
    comp = "Libertadores" if ("Libertadores" in f or "IND.-DEL-VALLE" in f) else "Sul-Americana"
    lines = open(f, encoding="utf-8").read().splitlines()
    for i, l in enumerate(lines):
        m = re.match(r"\s*\d{1,3}\s+(\d{1,2})/(\d{1,2})(?:/\d{4})?\s", l)
        if not m: continue
        parens = list(re.finditer(r"\(" + C + r"\)", l))
        if parens:
            tail = l[parens[-1].end():]
        elif re.search(r"\svs\.?\s", l, re.I):
            tail = re.split(r"\svs\.?\s", l, maxsplit=1, flags=re.I)[1]
        else:
            continue
        pairs = [[(n or "").strip(), c] for n, c in re.findall(r"(" + NAME + r")?\s*\b(" + C + r")\b", tail)]
        if pairs and not pairs[0][0]:
            if parens:
                prev = re.sub(r"\(" + C + r"\)", "", lines[i-1]).strip() if i else ""
                seg = re.split(r"\s{2,}", prev)[-1] if prev else ""
                if re.fullmatch(NAME, seg) and not re.fullmatch(C, seg): pairs[0][0] = seg
                else: pairs = pairs[1:]
            else:
                pairs = pairs[1:]
        if pairs: pairs[0][0] = re.split(r"\s{2,}", pairs[0][0])[-1]
        jogo = l[:parens[-1].end()] if parens else re.split(r"\s{2,}(?=" + NAME + r"\s+" + C + r"\b)", l)[0]
        jogo = re.sub(r"\s{2,}", " ", re.sub(r"^.*?\d{1,2}:\d{2}\s+(?:Grupo\s+\w+\s+|[A-H]\s+|C\d+\s+)?", "", jogo, count=1)).strip()
        ctx = " vs " not in jogo.lower()
        if ctx:
            viz = (lines[i-1] if i else "") + "  " + (lines[i+1] if i + 1 < len(lines) else "")
            v = re.search(r"vs\.? [^()]*\(" + C + r"\)", viz)
            if v: jogo = jogo + " " + re.sub(r"\s{2,}", " ", v.group(0)).strip()
        out.append({"comp": comp, "arq": os.path.basename(f), "data": f"2026-{int(m[2]):02d}-{int(m[1]):02d}", "jogo": jogo, "ctx": ctx or bool(parens), "pairs": pairs})
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
print(collections.Counter(len(x["pairs"]) for x in out))
c = collections.Counter(x["arq"] for x in out)
for k in sorted(c): print(c[k], k)
