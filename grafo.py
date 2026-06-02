import csv
from collections import defaultdict


def carregar_dados(caminho):
    usuarios = defaultdict(dict)
    with open(caminho, encoding='utf-8') as f:
        for row in csv.reader(f):
            user_id, jogo, acao, valor = row[0], row[1], row[2], float(row[3])
            if acao == 'play' and valor > 0:
                usuarios[user_id][jogo] = valor
    return usuarios


def construir_grafo(usuarios):
    adj = defaultdict(lambda: defaultdict(int))
    for jogos in usuarios.values():
        lista = list(jogos.keys())
        for i in range(len(lista)):
            for j in range(i + 1, len(lista)):
                a, b = lista[i], lista[j]
                adj[a][b] += 1
                adj[b][a] += 1
    return adj
