"""gui/app.py — Janela principal da interface gráfica."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.grafo import GrafoPonderado
from core.comunidades import grafo_knn, label_propagation, agrupar_usuarios, perfil_comunidades

from gui.grafo_view import GraphView
from gui.grupos_view import GruposView
from gui.recomendacao_view import RecomendacaoView


class SteamApp(tk.Tk):
    """
    Janela principal com três abas:
      1. Rede de Jogos     — grafo colorido por comunidade
      2. Grupos de Usuários — comunidades e jogos representativos
      3. Recomendação       — caminho Dijkstra com destaque no grafo
    """

    def __init__(
        self,
        grafo: GrafoPonderado,
        usuario_jogos: dict[str, dict[str, float]],
    ) -> None:
        super().__init__()
        self.title("Steam Game Recommender — Teoria dos Grafos")
        self.geometry("1280x800")
        self.minsize(900, 600)

        # Detectar comunidades (k-NN + Label Propagation)
        print("  Detectando comunidades de jogos (k-NN + Label Propagation)...")
        knn = grafo_knn(grafo, k=3)
        comunidade_jogo = label_propagation(knn)
        grupos  = agrupar_usuarios(usuario_jogos, comunidade_jogo)
        perfis  = perfil_comunidades(comunidade_jogo, usuario_jogos, grafo)
        n_com   = len(set(comunidade_jogo.values()))
        print(f"  {n_com} comunidades detectadas, {len(grupos)} grupos de usuários.")

        self._construir_ui(grafo, comunidade_jogo, grupos, perfis)

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _construir_ui(
        self,
        grafo: GrafoPonderado,
        comunidade_jogo: dict[str, int],
        grupos: dict,
        perfis: dict,
    ) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Aba 1 — Grafo
        frame_grafo = ttk.Frame(notebook)
        notebook.add(frame_grafo, text="  Rede de Jogos  ")
        self._graph_view = GraphView(frame_grafo, grafo, comunidade_jogo)
        self._graph_view.pack(fill=tk.BOTH, expand=True)

        # Aba 2 — Grupos
        frame_grupos = ttk.Frame(notebook)
        notebook.add(frame_grupos, text="  Grupos de Usuários  ")
        GruposView(frame_grupos, grupos, perfis).pack(fill=tk.BOTH, expand=True)

        # Aba 3 — Recomendação
        frame_rec = ttk.Frame(notebook)
        notebook.add(frame_rec, text="  Recomendação  ")
        RecomendacaoView(
            frame_rec, grafo,
            on_path_found=self._ao_encontrar_caminho,
        ).pack(fill=tk.BOTH, expand=True)

        # Renderizar grafo ao exibir a aba 1
        notebook.bind("<<NotebookTabChanged>>", self._ao_trocar_aba)
        self._grafo_renderizado = False
        self._notebook = notebook

    def _ao_trocar_aba(self, _event) -> None:
        idx = self._notebook.index(self._notebook.select())
        if idx == 0 and not self._grafo_renderizado:
            self._graph_view.render()
            self._grafo_renderizado = True

    def _ao_encontrar_caminho(self, caminho: list[str]) -> None:
        """Muda para a aba do grafo e destaca o caminho."""
        self._notebook.select(0)
        self._graph_view.destacar_caminho(caminho)
        self._grafo_renderizado = True
