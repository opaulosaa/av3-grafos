"""core/bfs.py — Busca em Largura e identificação de componentes conexas."""

from __future__ import annotations
from collections import deque

from .grafo import GrafoPonderado


def bfs(grafo: GrafoPonderado, inicio: str) -> dict[str, int]:
    """
    Retorna ``{nó: distância_em_hops}`` para todos os nós alcançáveis.
    Garante menor número de saltos por ser FIFO.  O(V + E).
    """
    if inicio not in grafo:
        raise ValueError(f"Vértice '{inicio}' não existe no grafo.")

    distancia: dict[str, int] = {inicio: 0}
    fila: deque[str] = deque([inicio])

    while fila:
        atual = fila.popleft()
        for vizinho, _ in grafo.vizinhos(atual):
            if vizinho not in distancia:
                distancia[vizinho] = distancia[atual] + 1
                fila.append(vizinho)

    return distancia


def componentes_conexas(grafo: GrafoPonderado) -> list[set[str]]:
    """
    Retorna lista de conjuntos, cada um sendo uma componente conexa.
    Um BFS por componente; cada vértice e aresta visitados no máximo uma vez.
    O(V + E).
    """
    visitados: set[str] = set()
    componentes: list[set[str]] = []

    for no in grafo.nos:
        if no not in visitados:
            componente: set[str] = set()
            fila: deque[str] = deque([no])
            visitados.add(no)
            while fila:
                atual = fila.popleft()
                componente.add(atual)
                for vizinho, _ in grafo.vizinhos(atual):
                    if vizinho not in visitados:
                        visitados.add(vizinho)
                        fila.append(vizinho)
            componentes.append(componente)

    return componentes
