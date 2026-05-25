"""gui/grupos_view.py — Aba de grupos de usuários por perfil de jogo."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class GruposView(ttk.Frame):
    """
    Painel com dois painéis lado a lado:
    - Esquerda: lista de comunidades (grupo, nº usuários, hub).
    - Direita: top jogos da comunidade selecionada.
    """

    def __init__(
        self,
        master,
        grupos: dict[int, list[tuple[str, float]]],
        perfis: dict[int, dict],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._grupos = grupos
        self._perfis = perfis
        self._build_ui()
        self._popular_lista()

    # ── Construção da UI ─────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Painel esquerdo — lista de grupos
        esq = ttk.Frame(self)
        esq.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(8, 4), pady=8)

        ttk.Label(esq, text="Comunidades detectadas", font=("", 10, "bold")).pack(anchor="w")

        colunas = ("grupo", "usuarios", "hub")
        self._tree = ttk.Treeview(
            esq, columns=colunas, show="headings", height=20, selectmode="browse"
        )
        self._tree.heading("grupo",    text="Grupo")
        self._tree.heading("usuarios", text="Usuários")
        self._tree.heading("hub",      text="Jogo principal")
        self._tree.column("grupo",    width=60,  anchor="center")
        self._tree.column("usuarios", width=80,  anchor="center")
        self._tree.column("hub",      width=220, anchor="w")

        scrollbar = ttk.Scrollbar(esq, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)

        self._tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # Painel direito — detalhes do grupo selecionado
        dir_ = ttk.Frame(self, relief=tk.GROOVE, borderwidth=1)
        dir_.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 8), pady=8)

        self._titulo_detalhe = ttk.Label(dir_, text="Selecione um grupo", font=("", 10, "bold"))
        self._titulo_detalhe.pack(anchor="w", padx=8, pady=(8, 4))

        self._detalhe_tree = ttk.Treeview(
            dir_, columns=("jogo", "horas"), show="headings", height=10
        )
        self._detalhe_tree.heading("jogo",  text="Jogo")
        self._detalhe_tree.heading("horas", text="Horas totais")
        self._detalhe_tree.column("jogo",  width=300, anchor="w")
        self._detalhe_tree.column("horas", width=120, anchor="center")
        self._detalhe_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        ttk.Separator(dir_).pack(fill=tk.X, padx=8)
        self._info_usuarios = ttk.Label(dir_, text="")
        self._info_usuarios.pack(anchor="w", padx=8, pady=6)

    # ── População dos dados ──────────────────────────────────────────────────

    def _popular_lista(self) -> None:
        grupos_ordenados = sorted(
            self._grupos.items(),
            key=lambda kv: len(kv[1]),
            reverse=True,
        )
        for cid, membros in grupos_ordenados:
            perfil = self._perfis.get(cid, {})
            hub = perfil.get("hub", "—")
            self._tree.insert(
                "", tk.END,
                iid=str(cid),
                values=(f"Grupo {cid + 1}", len(membros), hub),
            )

    def _ao_selecionar(self, _event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        perfil = self._perfis.get(cid, {})
        membros = self._grupos.get(cid, [])

        self._titulo_detalhe.config(text=f"Grupo {cid + 1} — Top jogos por horas jogadas")

        for row in self._detalhe_tree.get_children():
            self._detalhe_tree.delete(row)

        for jogo, horas in perfil.get("jogos_top", []):
            self._detalhe_tree.insert("", tk.END, values=(jogo, f"{horas:,.0f} h"))

        total_h = perfil.get("total_horas", 0)
        self._info_usuarios.config(
            text=f"{len(membros)} usuários  |  {total_h:,.0f} horas totais na comunidade"
        )
