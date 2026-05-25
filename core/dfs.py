"""core/dfs.py — Busca em Profundidade iterativa com detecção de ciclos."""

from __future__ import annotations

from .grafo import GrafoPonderado


def dfs(grafo: GrafoPonderado, inicio: str) -> tuple[list[str], bool]:
    """
    Retorna ``(ordem_de_visita, tem_ciclo)``.

    Ciclo detectado via contagem de arestas na componente:
    grafo conexo é acíclico sse |E| == |V| - 1.
    Pilha explícita evita estouro de recursão.  O(V + E).
    """
    if inicio not in grafo:
        raise ValueError(f"Vértice '{inicio}' não existe no grafo.")

    visitados: set[str] = set()
    ordem: list[str] = []
    pilha: list[str] = [inicio]

    while pilha:
        no = pilha.pop()
        if no in visitados:
            continue
        visitados.add(no)
        ordem.append(no)
        for vizinho, _ in grafo.vizinhos(no):
            if vizinho not in visitados:
                pilha.append(vizinho)

    arestas = sum(
        1 for no in visitados
        for viz, _ in grafo.vizinhos(no)
        if viz in visitados
    ) // 2

    return ordem, arestas >= len(ordem)
