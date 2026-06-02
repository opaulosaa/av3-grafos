import math
import heapq


def dijkstra(adj, inicio, destino):
    dist = {no: math.inf for no in adj}
    dist[inicio] = 0.0
    anterior = {}
    heap = [(0.0, inicio)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == destino:
            break
        for vizinho, peso in adj[u].items():
            nova_dist = dist[u] + (1.0 / peso)
            if nova_dist < dist[vizinho]:
                dist[vizinho] = nova_dist
                anterior[vizinho] = u
                heapq.heappush(heap, (nova_dist, vizinho))

    if dist.get(destino, math.inf) == math.inf:
        return math.inf, []

    caminho = []
    cursor = destino
    while cursor is not None:
        caminho.append(cursor)
        cursor = anterior.get(cursor)
    caminho.reverse()
    return dist[destino], caminho
