import re, sys, json, glob, os
out=[]
for f in sorted(glob.glob(os.path.join(sys.argv[1], "2026_Copa_*.txt"))):
    comp = "Libertadores" if "Libertadores" in f else "Sul-Americana"
    stage = os.path.basename(f)[:-4].split("_",3)[-1].replace("_"," ")
    t = open(f, encoding="utf-8").read()
    sec = ""
    for m in re.finditer(r"(^==+[^=\n]+==+\s*$)|(\{\{\s*[Ff]ootball ?box(?:[^{}]|\{\{[^{}]*\}\})*\}\})", t, re.M):
        if m.group(1): sec = m.group(1).strip("= \n"); continue
        b = m.group(2)
        g = lambda k: (re.search(r"\|\s*"+k+r"\s*=\s*([^\n]*)", b) or [None,""])[1]
        ref = g("referee")
        if not re.search(r"Brazil", ref): continue
        clean = lambda s: re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", re.sub(r"\{\{[^{}]*?\|([^{}|]*)\}\}", r"\1", s)).strip()
        dm = re.search(r"(\d{4})\|(\d{1,2})\|(\d{1,2})", g("date"))
        out.append({"comp": comp, "fase": sec, "pagina": stage, "data": f"{dm[1]}-{int(dm[2]):02d}-{int(dm[3]):02d}" if dm else g("date"),
                    "jogo": f'{clean(g("team1"))} x {clean(g("team2"))}', "arbitro": clean(ref).replace(" (Brazil)","")})
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=0)
for x in sorted(out, key=lambda x: x["data"]): print(x["data"], x["comp"][:4], x["fase"][:22].ljust(22), x["arbitro"].ljust(28), x["jogo"])
