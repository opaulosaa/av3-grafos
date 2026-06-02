from collections import deque


def bfs(adj, inicio):
    distancia = {inicio: 0}
    fila = deque([inicio])
    while fila:
        atual = fila.popleft()
        for vizinho in adj[atual]:
            if vizinho not in distancia:
                distancia[vizinho] = distancia[atual] + 1
                fila.append(vizinho)
    return distancia
