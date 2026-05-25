"""core/dijkstra.py — Caminho de menor peso via heap mínimo (Dijkstra)."""

from __future__ import annotations

import math
import heapq

from .grafo import GrafoPonderado


def dijkstra(
    grafo: GrafoPonderado,
    inicio: str,
    destino: str,
) -> tuple[float, list[str]]:
    """
    Retorna ``(peso_total, caminho)`` ou ``(inf, [])`` se inalcançável.

    Extrai o vértice de menor distância acumulada do heap a cada passo;
    entradas obsoletas (d > dist[u]) são descartadas.
    Quando *destino* é extraído, sua distância é definitiva (pesos ≥ 0).
    O((V + E) log V).
    """
    if inicio not in grafo:
        raise ValueError(f"Vértice '{inicio}' não existe no grafo.")
    if destino not in grafo:
        raise ValueError(f"Vértice '{destino}' não existe no grafo.")

    INF = math.inf
    dist: dict[str, float] = {no: INF for no in grafo.nos}
    anterior: dict[str, str | None] = {no: None for no in grafo.nos}
    dist[inicio] = 0.0

    heap: list[tuple[float, str]] = [(0.0, inicio)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == destino:
            break
        for vizinho, peso in grafo.vizinhos(u):
            nova = dist[u] + peso
            if nova < dist[vizinho]:
                dist[vizinho] = nova
                anterior[vizinho] = u
                heapq.heappush(heap, (nova, vizinho))

    if dist[destino] == INF:
        return INF, []

    caminho: list[str] = []
    cursor: str | None = destino
    while cursor is not None:
        caminho.append(cursor)
        cursor = anterior[cursor]
    caminho.reverse()
    return dist[destino], caminho
