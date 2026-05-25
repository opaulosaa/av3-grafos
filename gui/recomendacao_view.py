"""gui/recomendacao_view.py — Aba de recomendação via Dijkstra."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.grafo import GrafoPonderado
from core.dijkstra import dijkstra


class RecomendacaoView(ttk.Frame):
    """
    Painel com formulário de origem/destino e exibição do caminho Dijkstra.
    Chama *on_path_found* com a lista de nós para que a aba do grafo
    possa destacar o caminho visualmente.
    """

    def __init__(
        self,
        master,
        grafo: GrafoPonderado,
        on_path_found=None,   # callback: lista[str] → None
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._grafo = grafo
        self._on_path_found = on_path_found
        self._jogos = sorted(grafo.nos)
        self._build_ui()

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        form = ttk.LabelFrame(self, text="Parâmetros da recomendação", padding=10)
        form.pack(fill=tk.X, padx=12, pady=12)

        ttk.Label(form, text="Jogo de origem:").grid(row=0, column=0, sticky="w", padx=4)
        self._cb_origem = ttk.Combobox(form, values=self._jogos, width=40, state="readonly")
        self._cb_origem.grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(form, text="Jogo de destino:").grid(row=1, column=0, sticky="w", padx=4)
        self._cb_destino = ttk.Combobox(form, values=self._jogos, width=40, state="readonly")
        self._cb_destino.grid(row=1, column=1, padx=8, pady=4)

        ttk.Button(form, text="Recomendar", command=self._recomendar).grid(
            row=2, column=0, columnspan=2, pady=8
        )

        # Área de resultado
        resultado_frame = ttk.LabelFrame(self, text="Caminho encontrado", padding=10)
        resultado_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self._resultado_text = tk.Text(
            resultado_frame, wrap=tk.WORD, font=("Courier", 10),
            state=tk.DISABLED, height=16, relief=tk.FLAT,
        )
        sb = ttk.Scrollbar(resultado_frame, command=self._resultado_text.yview)
        self._resultado_text.configure(yscrollcommand=sb.set)
        self._resultado_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.LEFT, fill=tk.Y)

    # ── Lógica de recomendação ────────────────────────────────────────────────

    def _recomendar(self) -> None:
        origem  = self._cb_origem.get()
        destino = self._cb_destino.get()

        self._escrever("")

        if not origem or not destino:
            self._escrever("Selecione origem e destino.")
            return
        if origem == destino:
            self._escrever("Origem e destino devem ser jogos diferentes.")
            return

        peso_total, caminho = dijkstra(self._grafo, origem, destino)

        if not caminho:
            self._escrever(f"Nenhum caminho encontrado entre\n'{origem}'\ne '{destino}'.")
            return

        linhas = [
            f"{'─'*55}",
            f"  Origem  : {origem}",
            f"  Destino : {destino}",
            f"  Saltos  : {len(caminho) - 1}",
            f"  Peso total (distância de gosto): {peso_total:.8f}",
            f"  Afinidade acumulada (1/peso)   : {1/peso_total:.2f}",
            f"{'─'*55}",
            "",
            "  Rota passo a passo:",
        ]

        for i, jogo in enumerate(caminho):
            if i == 0:
                linhas.append(f"\n  ▶  {jogo}  [INÍCIO]")
            else:
                peso_aresta = self._grafo._adj[caminho[i - 1]][jogo]
                afinidade   = round(1 / peso_aresta, 1) if peso_aresta else 0
                tag = "  [DESTINO]" if i == len(caminho) - 1 else ""
                linhas.append(f"  ➜  {jogo}{tag}")
                linhas.append(f"       afinidade ≈ {afinidade}")

        self._escrever("\n".join(linhas))

        if self._on_path_found:
            self._on_path_found(caminho)

    def _escrever(self, texto: str) -> None:
        self._resultado_text.config(state=tk.NORMAL)
        self._resultado_text.delete("1.0", tk.END)
        self._resultado_text.insert(tk.END, texto)
        self._resultado_text.config(state=tk.DISABLED)
