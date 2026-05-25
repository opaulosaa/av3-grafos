"""core/dados.py — Leitura do CSV e construção do grafo."""

from __future__ import annotations

import csv
import math
import os
from collections import defaultdict

from .grafo import GrafoPonderado


def carregar_dados(
    caminho_csv: str,
    minimo_usuarios: int = 15,
    verbose: bool = True,
) -> tuple[GrafoPonderado, dict[str, dict[str, float]]]:
    """
    Lê steam-200k.csv e devolve ``(grafo, usuario_jogos)``.

    Vértices  : jogos únicos.
    Arestas   : dois jogos se conectam quando >= *minimo_usuarios* usuários
                jogaram ambos.
    Peso      : 1 / (usuarios_comuns × ln(1 + horas_compartilhadas))
                — menor peso = maior afinidade.

    ``usuario_jogos`` = {user_id: {jogo: horas}} — necessário para
    agrupamento de usuários e para a interface gráfica.
    """
    def _log(msg: str) -> None:
        if verbose:
            print(msg)

    _log(f"  Carregando: {os.path.basename(caminho_csv)}")

    usuario_jogos: dict[str, dict[str, float]] = defaultdict(dict)

    with open(caminho_csv, encoding="utf-8", newline="") as arq:
        for linha in csv.reader(arq):
            if len(linha) < 4:
                continue
            user_id, jogo, behavior, valor = (
                linha[0].strip(), linha[1].strip(), linha[2].strip(), linha[3].strip()
            )
            if behavior == "play":
                try:
                    horas = float(valor)
                except ValueError:
                    horas = 0.0
                usuario_jogos[user_id][jogo] = horas

    _log(f"  Usuários: {len(usuario_jogos):,}  |  "
         f"Jogos únicos: {len({j for u in usuario_jogos.values() for j in u}):,}")
    _log("  Calculando co-ocorrências...")

    co_usuarios: dict[tuple, int]   = defaultdict(int)
    co_horas:    dict[tuple, float] = defaultdict(float)

    for jogos in usuario_jogos.values():
        lista = list(jogos.keys())
        for i in range(len(lista)):
            for j in range(i + 1, len(lista)):
                ga, gb = lista[i], lista[j]
                chave = (ga, gb) if ga < gb else (gb, ga)
                co_usuarios[chave] += 1
                co_horas[chave]    += jogos[ga] + jogos[gb]

    _log(f"  Construindo grafo (threshold >= {minimo_usuarios})...")

    grafo = GrafoPonderado()
    for (ga, gb), n in co_usuarios.items():
        if n >= minimo_usuarios:
            afinidade = n * math.log(1.0 + max(co_horas[(ga, gb)], 0.001))
            grafo.adicionar_aresta(ga, gb, round(1.0 / afinidade, 8))

    _log(f"  Grafo: {grafo.total_nos()} vértices, {grafo.total_arestas()} arestas")
    return grafo, dict(usuario_jogos)
