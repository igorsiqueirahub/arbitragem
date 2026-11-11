"""Gera as páginas do site a partir dos modelos e dos dados calculados.

Uso: python build_site.py <modelo> <dados.json> <saida.html> <link_da_outra_pagina>
"""
import sys, re

modelo, dados, saida, outro = sys.argv[1:5]
t = open(modelo, encoding="utf-8").read()
d = open(dados, encoding="utf-8").read()
t = t.replace("__DATA__", d)

# links entre as duas páginas: no site, apontam para o arquivo vizinho
t = re.sub(r'<a href="https://claude\.ai/artifact/[A-Za-z0-9]+" target="_blank" rel="noopener"', f'<a href="{outro}"', t)

# separa o que vai no <head> (título, metas, fontes, estilo) do corpo
i = t.index('<div class="wrap">')
head, corpo = t[:i], t[i:]
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")

reset = """<style>
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}
img{max-width:100%}
[hidden]{display:none!important}
</style>
"""
html = ("<!doctype html>\n<html lang=\"pt-BR\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        + reset + head.strip() + "\n</head>\n<body>\n" + corpo.strip() + "\n</body>\n</html>\n")
open(saida, "w", encoding="utf-8").write(html)
print(saida, len(html))
