import json, sys, urllib.request, os, time
out = sys.argv[1]
B = "https://www.cbf.com.br/api/cbf/jogos/campeonato/"
def get(path):
    req = urllib.request.Request(B + path, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    for i in range(3):
        try:
            return urllib.request.urlopen(req, timeout=60).read()
        except Exception as e:
            err = e; time.sleep(2)
    print("FALHA", path, err); return None
jobs = [("A", r, f"1260611/rodada/{r}/fase") for r in range(1, 39)]
fases = {1995:1,1996:1,1997:1,1998:1,1999:2,2000:2,2001:2,2002:2,2003:2}
for f, n in fases.items():
    for r in range(1, n + 1):
        jobs.append(("CDB", f"{f}-{r}", f"1260615/rodada/{r}/fase/{f}"))
for comp, key, path in jobs:
    b = get(path)
    if b:
        open(os.path.join(out, f"{comp}_{key}.json"), "wb").write(b)
        print(comp, key, len(b))
