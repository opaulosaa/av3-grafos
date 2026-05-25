"""core/comunidades.py — Agrupamento de usuários por perfil de jogo."""

from __future__ import annotations

import random
from collections import defaultdict

from .grafo import GrafoPonderado


def grafo_knn(grafo: GrafoPonderado, k: int = 3) -> GrafoPonderado:
    """
    Retorna versão esparsa mantendo as *k* arestas de menor peso por vértice.

    O grafo original é quase-completo (diâmetro 2), o que colapsa o Label
    Propagation em uma única comunidade. Com k-NN, fronteiras entre nichos
    ficam nítidas e o LP converge para grupos coerentes.
    """
    sparse = GrafoPonderado()
    for no in grafo.nos:
        for viz, peso in sorted(grafo.vizinhos(no), key=lambda p: p[1])[:k]:
            sparse.adicionar_aresta(no, viz, peso)
    return sparse


def label_propagation(
    grafo: GrafoPonderado,
    max_iter: int = 60,
    semente: int = 42,
) -> dict[str, int]:
    """
    Detecta comunidades sem fixar k a priori.

    Cada vértice adota o rótulo com maior soma de votos ponderados pela
    afinidade (1/peso) dos vizinhos. Ordem aleatória por iteração evita
    viés. Para quando nenhum rótulo muda.  O(V + E) por iteração.

    Retorna ``{jogo: id_comunidade}`` com IDs consecutivos a partir de 0.
    """
    random.seed(semente)
    nos = list(grafo.nos)
    rotulos: dict[str, int] = {no: i for i, no in enumerate(nos)}

    for _ in range(max_iter):
        random.shuffle(nos)
        mudou = False
        for no in nos:
            votos: dict[int, float] = defaultdict(float)
            for viz, peso in grafo.vizinhos(no):
                votos[rotulos[viz]] += 1.0 / peso if peso > 0 else 1.0
            if not votos:
                continue
            max_v = max(votos.values())
            vencedor = random.choice([r for r, v in votos.items() if v == max_v])
            if vencedor != rotulos[no]:
                rotulos[no] = vencedor
                mudou = True
        if not mudou:
            break

    ids = sorted(set(rotulos.values()))
    remap = {old: new for new, old in enumerate(ids)}
    return {no: remap[rotulos[no]] for no in nos}


def agrupar_usuarios(
    usuario_jogos: dict[str, dict[str, float]],
    comunidade_jogo: dict[str, int],
    min_horas: float = 0.5,
) -> dict[int, list[tuple[str, float]]]:
    """
    Atribui cada usuário à comunidade onde acumulou mais horas.

    Retorna ``{id_comunidade: [(user_id, horas), ...]}`` por horas desc.
    """
    grupos: dict[int, list] = defaultdict(list)

    for user, jogos in usuario_jogos.items():
        h_por_com: dict[int, float] = defaultdict(float)
        for jogo, h in jogos.items():
            if jogo in comunidade_jogo:
                h_por_com[comunidade_jogo[jogo]] += h
        if not h_por_com or sum(h_por_com.values()) < min_horas:
            continue
        melhor = max(h_por_com, key=h_por_com.get)
        grupos[melhor].append((user, h_por_com[melhor]))

    return {cid: sorted(m, key=lambda x: x[1], reverse=True)
            for cid, m in grupos.items()}


def perfil_comunidades(
    comunidade_jogo: dict[str, int],
    usuario_jogos: dict[str, dict[str, float]],
    grafo_original: GrafoPonderado,
    top_jogos: int = 8,
) -> dict[int, dict]:
    """
    Retorna ``{id_comunidade: {"jogos_top", "hub", "total_horas"}}``.

    ``hub`` é o jogo de maior grau no grafo original dentro da comunidade.
    """
    horas_cj: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for user, jogos in usuario_jogos.items():
        for jogo, h in jogos.items():
            if jogo in comunidade_jogo:
                horas_cj[comunidade_jogo[jogo]][jogo] += h

    perfis: dict[int, dict] = {}
    for cid, jogos_h in horas_cj.items():
        top = sorted(jogos_h.items(), key=lambda x: x[1], reverse=True)[:top_jogos]
        hub = max(
            (j for j in jogos_h if j in grafo_original.nos),
            key=lambda j: grafo_original.grau(j),
            default="—",
        )
        perfis[cid] = {"jogos_top": top, "hub": hub, "total_horas": sum(jogos_h.values())}
    return perfis
