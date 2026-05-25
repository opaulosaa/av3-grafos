#!/usr/bin/env python3
"""
steam_recomendacao.py — Entry point CLI
========================================
Executa as quatro análises no terminal (sem interface gráfica).

Uso
---
    python steam_recomendacao.py            # threshold padrão = 15
    python steam_recomendacao.py 20         # threshold customizado
"""

from __future__ import annotations

import io
import os
import sys
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from core.dados import carregar_dados
from core.bfs import bfs, componentes_conexas
from core.dfs import dfs
from core.dijkstra import dijkstra
from core.comunidades import grafo_knn, label_propagation, agrupar_usuarios, perfil_comunidades
from core.grafo import GrafoPonderado

_LINHA = "═" * 70


def _cabecalho(titulo: str) -> None:
    print(f"\n{_LINHA}\n  {titulo}\n{_LINHA}")


# ══════════════════════════════════════════════════════════════════════════════

def analise_hubs(grafo: GrafoPonderado, top: int = 15) -> None:
    """Análise 1 — Grau dos vértices e maiores hubs."""
    _cabecalho("ANÁLISE 1 — HUBS: Jogos com mais conexões na rede")

    graus = sorted(((grafo.grau(n), n) for n in grafo.nos), reverse=True)
    total = len(graus)

    print(f"\n  {'Rank':<5} {'Grau':>6}  Jogo")
    print(f"  {'─'*5} {'─'*6}  {'─'*50}")
    for rank, (grau, jogo) in enumerate(graus[:top], start=1):
        print(f"  {rank:<5} {grau:>6}  {jogo}  {'█' * min(grau, 40)}")

    media = sum(g for g, _ in graus) / total if total else 0
    print(f"\n  Total: {total} jogos  |  Grau médio: {media:.2f}")
    print(f"  Máximo: {graus[0][0]}  ←  '{graus[0][1]}'")
    print(f"  Mínimo: {graus[-1][0]}  ←  '{graus[-1][1]}'")
    print("\n  Percentis:")
    for p in [25, 50, 75, 90]:
        print(f"    P{p:>2}: {graus[int(total * p / 100)][0]:>4} conexões")


def analise_conectividade(grafo: GrafoPonderado) -> None:
    """Análise 2 — Componentes conexas, diâmetro BFS e ciclos DFS."""
    _cabecalho("ANÁLISE 2 — CONECTIVIDADE: Estrutura e separação da rede")

    comps = sorted(componentes_conexas(grafo), key=len, reverse=True)
    print(f"\n  Componentes conexas : {len(comps)}")
    print(f"  Componente gigante  : {len(comps[0])} jogos")
    if len(comps) > 1:
        print(f"  2ª componente       : {len(comps[1])} jogos")

    hub = max(comps[0], key=lambda n: grafo.grau(n))
    dist_bfs = bfs(grafo, hub)
    diametro = max(dist_bfs.values())
    mais_dist = max(dist_bfs, key=dist_bfs.get)

    print(f"\n  BFS a partir de '{hub}':")
    print(f"    Nós alcançados  : {len(dist_bfs)}")
    print(f"    Diâmetro (hops) : {diametro}")
    print(f"    Mais afastado   : '{mais_dist}'  ({dist_bfs[mais_dist]} saltos)")

    hist: dict[int, int] = defaultdict(int)
    for d in dist_bfs.values():
        hist[d] += 1
    for k in sorted(hist):
        print(f"      {k} salto(s): {hist[k]:>5} jogos  {'▪' * min(hist[k], 50)}")

    ordem_dfs, tem_ciclo = dfs(grafo, hub)
    print(f"\n  DFS — {len(ordem_dfs)} nós visitados  |  "
          f"Ciclos: {'SIM' if tem_ciclo else 'NÃO'}")


def analise_recomendacao(grafo: GrafoPonderado) -> None:
    """Análise 3 — Caminho Dijkstra entre dois jogos de nicho."""
    _cabecalho("ANÁLISE 3 — RECOMENDAÇÃO: Caminho de menor distância de gosto")

    comps = sorted(componentes_conexas(grafo), key=len, reverse=True)
    gigante = comps[0]

    nicho = sorted(
        [n for n in gigante if 5 <= grafo.grau(n) <= 50],
        key=lambda n: grafo.grau(n), reverse=True,
    )
    origem = nicho[0]
    vizinhos_origem = {v for v, _ in grafo.vizinhos(origem)}
    destino = next(
        (c for c in nicho[1:] if c not in vizinhos_origem), nicho[-1]
    )

    peso_total, caminho = dijkstra(grafo, origem, destino)

    print(f"\n  Origem  : {origem}")
    print(f"  Destino : {destino}")
    print(f"  Peso total (distância de gosto) : {peso_total:.8f}")
    print(f"  Afinidade inversa (1/peso)      : {1/peso_total:.2f}")
    print(f"  Saltos                          : {len(caminho) - 1}")
    print(f"\n  {'─'*60}")
    for i, jogo in enumerate(caminho):
        if i == 0:
            print(f"  ▶  [{i}] {jogo}  [INÍCIO]")
        else:
            peso_aresta = grafo._adj[caminho[i - 1]][jogo]
            afinidade   = round(1 / peso_aresta, 1) if peso_aresta else 0
            tag = "  [DESTINO]" if i == len(caminho) - 1 else ""
            print(f"  ➜  [{i}] {jogo}{tag}  (afinidade ≈ {afinidade})")
    print(f"  {'─'*60}")


def analise_agrupamento(
    grafo: GrafoPonderado,
    usuario_jogos: dict[str, dict[str, float]],
) -> None:
    """Análise 4 — Grupos de usuários por perfil de jogo."""
    _cabecalho("ANÁLISE 4 — GRUPOS: Perfis de usuários por tipo de jogo")

    print("\n  Detectando comunidades (k-NN + Label Propagation)...")
    knn = grafo_knn(grafo, k=3)
    comunidade_jogo = label_propagation(knn)
    grupos  = agrupar_usuarios(usuario_jogos, comunidade_jogo)
    perfis  = perfil_comunidades(comunidade_jogo, usuario_jogos, grafo)

    grupos_ord = sorted(grupos.items(), key=lambda kv: len(kv[1]), reverse=True)
    print(f"  {len(grupos_ord)} grupos detectados\n")

    for cid, membros in grupos_ord:
        perfil = perfis.get(cid, {})
        hub    = perfil.get("hub", "—")
        total_h = perfil.get("total_horas", 0)
        top_jogos = perfil.get("jogos_top", [])

        print(f"  ┌─ Grupo {cid + 1}  ({len(membros)} usuários  |  {total_h:,.0f} h totais)")
        print(f"  │  Hub: {hub}")
        print("  │  Top jogos:")
        for jogo, h in top_jogos[:5]:
            print(f"  │    • {jogo:<45} {h:>8,.0f} h")
        print("  └" + "─" * 55)
        print()


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 15

    CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "steam-200k.csv")
    if not os.path.exists(CSV):
        print(f"Erro: '{CSV}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║   SISTEMA DE RECOMENDAÇÃO DE JOGOS STEAM — TEORIA DOS GRAFOS    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    grafo, usuario_jogos = carregar_dados(CSV, minimo_usuarios=threshold)

    analise_hubs(grafo)
    analise_conectividade(grafo)
    analise_recomendacao(grafo)
    analise_agrupamento(grafo, usuario_jogos)

    print(f"\n{_LINHA}")
    print(f"  Concluído. Grafo: {grafo.total_nos()} vértices × {grafo.total_arestas()} arestas")
    print(_LINHA + "\n")
