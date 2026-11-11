# Árbitros na geladeira

Quanto tempo cada árbitro do quadro PRO da CBF ficou sem trabalhar em jogos da elite em 2026, contado em rodadas da Série A.

- `index.html`: árbitros centrais (categorias FIFA-PRO, AB-PRO e MASTER-PRO)
- `var.html`: VARs (categoria VAR-FIFA-PRO)

Cada nome abre um perfil com todos os jogos, o maior hiato e o que o árbitro fez nesse período (Série B, VAR, AVAR, quarto árbitro).

## Regras do levantamento

- O hiato é contado em rodadas da Série A entre dois jogos da elite. A data de cada rodada é a mediana das datas dos seus jogos, então jogos adiados não distorcem a conta, e a pausa da Copa do Mundo e as datas Fifa não inflam o número.
- Na contagem em dias, a pausa da Copa do Mundo (1/6 a 15/7, sem Série A nem Copa do Brasil) é descontada.
- Contam como jogos da elite: Série A, Copa do Brasil, Copa do Mundo (Wilton Sampaio, Raphael Claus e Ramon Abatti), Libertadores e Sul-Americana.
- Charly Deretti, Daiane Muniz e Edina Alves aparecem fora da comparação: seguem trilha paralela no futebol feminino, rumo à Copa do Mundo Feminina de 2027.
- Cada hiato é marcado como "sob Cintra", "sob Ricci" ou "atravessa a troca", pela troca na Comissão de Arbitragem em 9/6/2026.

## Fontes

- Escalas da CBF: `https://www.cbf.com.br/api/cbf/jogos/campeonato/{id}/rodada/{n}/fase` (Série A 1260611, Série B 1260612, Copa do Brasil 1260615 com `/fase/{id_da_fase}`).
- Libertadores e Sul-Americana: páginas da Wikipédia em inglês de cada fase (árbitro central) e planilhas de designação da Conmebol (demais funções). Faltam algumas planilhas; nessas rodadas só o árbitro central está coberto.
- Jogos da Copa do Mundo: Wikipédia ("Árbitros brasileiros em Copas do Mundo FIFA").

## Como atualizar

Os scripts ficam em `scripts/` e recebem os caminhos como argumentos. A ordem é:

1. `baixar.py <pasta_raw>`: baixa Série A e Copa do Brasil da CBF.
2. Série B: mesma API com o id 1260612 (rodadas 1 a 38), salvando como `B_<rodada>.json` em outra pasta.
3. `parse.py <pasta_raw> games.json`: extrai o árbitro central de cada jogo.
4. Conmebol: `wiki_conmebol.py`, `parse_pdf.py`, `build_conmebol.py` e `limpa_jogo.py` geram `dados/conmebol.json`.
5. `calc.py games.json result.json dados/conmebol.json` e `annot.py result.json <raw> <rawb> dados/arbitros.json dados/conmebol.json`.
6. `calc_var.py <raw> <rawb> dados/arbitros.json dados/var.json dados/conmebol.json`.
7. Monta as páginas:

```
python scripts/build_site.py modelos/arbitros.html dados/arbitros.json index.html var.html
python scripts/build_site.py modelos/var.html dados/var.json var.html index.html
```

A data de referência ("hoje") fica em `calc.py`, na constante `HOJE`.
