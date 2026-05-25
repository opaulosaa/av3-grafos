#!/usr/bin/env python3
"""
steam_gui.py — Entry point da interface gráfica
================================================
Carrega os dados, detecta comunidades e abre a janela principal.

Uso
---
    python steam_gui.py
    python steam_gui.py 20      # threshold customizado
"""

from __future__ import annotations

import os
import sys

from core.dados import carregar_dados
from gui.app import SteamApp


def main() -> None:
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 15

    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "steam-200k.csv")
    if not os.path.exists(csv_path):
        print(f"Erro: '{csv_path}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    print("Carregando dados...")
    grafo, usuario_jogos = carregar_dados(csv_path, minimo_usuarios=threshold)

    print("Iniciando interface gráfica...")
    app = SteamApp(grafo, usuario_jogos)
    app.mainloop()


if __name__ == "__main__":
    main()
