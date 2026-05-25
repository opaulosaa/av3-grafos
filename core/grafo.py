"""core/grafo.py — Grafo não-dirigido ponderado via lista de adjacência."""

from __future__ import annotations
from collections import defaultdict


class GrafoPonderado:
    """
    Lista de adjacência: ``_adj[u][v] = peso`` em ambas as direções.
    Consulta de peso: O(1).  Iteração de vizinhos: O(grau(u)).
    """

    def __init__(self) -> None:
        self._adj: dict[str, dict[str, float]] = defaultdict(dict)
        self._nos: set[str] = set()

    def adicionar_no(self, no: str) -> None:
        self._nos.add(no)
        if no not in self._adj:
            self._adj[no] = {}

    def adicionar_aresta(self, u: str, v: str, peso: float) -> None:
        self._nos.add(u)
        self._nos.add(v)
        self._adj[u][v] = peso
        self._adj[v][u] = peso

    @property
    def nos(self) -> frozenset[str]:
        return frozenset(self._nos)

    def vizinhos(self, no: str):
        return self._adj[no].items()

    def tem_aresta(self, u: str, v: str) -> bool:
        return v in self._adj.get(u, {})

    def grau(self, no: str) -> int:
        return len(self._adj[no])

    def total_nos(self) -> int:
        return len(self._nos)

    def total_arestas(self) -> int:
        return sum(len(viz) for viz in self._adj.values()) // 2

    def __contains__(self, no: str) -> bool:
        return no in self._nos

    def __repr__(self) -> str:
        return f"GrafoPonderado(V={self.total_nos()}, E={self.total_arestas()})"
