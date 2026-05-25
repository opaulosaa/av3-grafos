"""gui/grafo_view.py — Aba de visualização do grafo de jogos."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from core.grafo import GrafoPonderado
from core.comunidades import grafo_knn

# Paleta de cores para comunidades
_CORES = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3",
    "#ff7f00", "#a65628", "#f781bf", "#999999",
    "#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3",
]


def _cor_comunidade(cid: int) -> str:
    return _CORES[cid % len(_CORES)]


class GraphView(ttk.Frame):
    """
    Painel com o grafo colorido por comunidade.

    Usa o grafo k-NN (mais esparso) para o layout, permitindo
    visualização clara das fronteiras entre nichos.
    """

    def __init__(
        self,
        master,
        grafo: GrafoPonderado,
        comunidade_jogo: dict[str, int],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._grafo = grafo
        self._comunidade_jogo = comunidade_jogo
        self._pos: dict | None = None          # posições dos nós (lazy)
        self._nx_graph: nx.Graph | None = None
        self._path_nodes: list[str] = []       # nós do caminho Dijkstra
        self._path_edges: list[tuple] = []     # arestas do caminho

        self._build_ui()

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._fig, self._ax = plt.subplots(figsize=(10, 7))
        self._fig.patch.set_facecolor("#1e1e2e")
        self._ax.set_facecolor("#1e1e2e")

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        toolbar_frame = ttk.Frame(self)
        toolbar_frame.pack(fill=tk.X)
        NavigationToolbar2Tk(self._canvas, toolbar_frame)

    # ── Renderização ─────────────────────────────────────────────────────────

    def _build_nx_graph(self) -> nx.Graph:
        """Constrói o grafo networkx k-NN a partir do grafo interno."""
        knn = grafo_knn(self._grafo, k=8)
        G = nx.Graph()
        for no in knn.nos:
            G.add_node(no)
        for no in knn.nos:
            for viz, peso in knn.vizinhos(no):
                if not G.has_edge(viz, no):
                    G.add_edge(no, viz, weight=peso)
        return G

    def render(self) -> None:
        """Desenha o grafo completo colorido por comunidade."""
        self._ax.clear()
        self._ax.set_facecolor("#1e1e2e")
        self._ax.axis("off")

        if self._nx_graph is None:
            self._nx_graph = self._build_nx_graph()

        G = self._nx_graph

        # Layout calculado uma única vez e reutilizado
        if self._pos is None:
            self._pos = nx.spring_layout(G, seed=42, k=0.4)

        nos = list(G.nodes())
        cores = [_cor_comunidade(self._comunidade_jogo.get(n, 0)) for n in nos]
        tamanhos = [max(20, self._grafo.grau(n) * 2) for n in nos]

        # Arestas normais (cinza claro)
        nx.draw_networkx_edges(
            G, self._pos, ax=self._ax,
            edge_color="#555577", alpha=0.3, width=0.5,
        )

        # Nós
        nx.draw_networkx_nodes(
            G, self._pos, nodelist=nos, ax=self._ax,
            node_color=cores, node_size=tamanhos, alpha=0.9,
        )

        # Rótulos apenas dos nós com alto grau
        top_nos = sorted(nos, key=lambda n: self._grafo.grau(n), reverse=True)[:20]
        labels = {n: n for n in top_nos}
        nx.draw_networkx_labels(
            G, self._pos, labels=labels, ax=self._ax,
            font_size=6, font_color="white",
        )

        # Legenda das comunidades
        ids_presentes = sorted(set(self._comunidade_jogo.values()))
        patches = [
            mpatches.Patch(color=_cor_comunidade(cid), label=f"Grupo {cid + 1}")
            for cid in ids_presentes
        ]
        self._ax.legend(
            handles=patches, loc="lower left", fontsize=7,
            facecolor="#2a2a3e", labelcolor="white", framealpha=0.8,
        )

        self._ax.set_title("Rede de Jogos — colorida por comunidade", color="white", pad=10)
        self._canvas.draw()

    def destacar_caminho(self, caminho: list[str]) -> None:
        """Redesenha o grafo com o caminho Dijkstra destacado em laranja."""
        self._path_nodes = caminho
        self._path_edges = list(zip(caminho, caminho[1:]))
        self.render()

        if not caminho or self._nx_graph is None:
            return

        G = self._nx_graph

        # Nós do caminho em laranja maior
        nos_path = [n for n in caminho if n in self._pos]
        nx.draw_networkx_nodes(
            G, self._pos, nodelist=nos_path, ax=self._ax,
            node_color="#ff8c00", node_size=200, alpha=1.0, zorder=5,
        )

        # Arestas do caminho em laranja
        arestas_path = [(u, v) for u, v in self._path_edges if G.has_edge(u, v)]
        nx.draw_networkx_edges(
            G, self._pos, edgelist=arestas_path, ax=self._ax,
            edge_color="#ff8c00", width=3, alpha=1.0, zorder=4,
        )

        # Rótulos do caminho
        labels_path = {n: n for n in nos_path}
        nx.draw_networkx_labels(
            G, self._pos, labels=labels_path, ax=self._ax,
            font_size=8, font_color="white", font_weight="bold",
        )

        self._canvas.draw()
