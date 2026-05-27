import csv
import math
import heapq
from collections import defaultdict, deque

# ── Carrega dataset ───────────────────────────────────────────────────────────
# Formato: user_id, jogo, acao, valor, flag
# Mantém apenas linhas "play" (horas jogadas > 0)

def carregar_dados(caminho):
    usuarios = defaultdict(dict)  # {user_id: {jogo: horas}}
    with open(caminho, encoding='utf-8') as f:
        for row in csv.reader(f):
            user_id, jogo, acao, valor = row[0], row[1], row[2], float(row[3])
            if acao == 'play' and valor > 0:
                usuarios[user_id][jogo] = valor
    return usuarios


# ── Constrói grafo de jogos ───────────────────────────────────────────────────
# Nós: jogos. Aresta entre dois jogos se pelo menos um usuário jogou ambos.
# Peso: número de usuários que jogaram os dois jogos (afinidade).

def construir_grafo(usuarios):
    adj = defaultdict(lambda: defaultdict(int))  # {jogo: {vizinho: peso}}
    for jogos in usuarios.values():
        lista = list(jogos.keys())
        for i in range(len(lista)):
            for j in range(i + 1, len(lista)):
                a, b = lista[i], lista[j]
                adj[a][b] += 1
                adj[b][a] += 1
    return adj


# ── BFS ───────────────────────────────────────────────────────────────────────
# Explora camada por camada. Retorna {nó: distância_em_hops}.

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


# ── DFS ───────────────────────────────────────────────────────────────────────
# Explora fundo antes de voltar. Iterativo para evitar estouro de recursão.
# Retorna lista de nós na ordem de visita.

def dfs(adj, inicio):
    visitados = set()
    ordem = []
    pilha = [inicio]
    while pilha:
        no = pilha.pop()
        if no in visitados:
            continue
        visitados.add(no)
        ordem.append(no)
        for vizinho in adj[no]:
            if vizinho not in visitados:
                pilha.append(vizinho)
    return ordem


# ── Dijkstra ──────────────────────────────────────────────────────────────────
# Menor custo entre dois jogos. Usa 1/peso como custo (peso maior = mais afim).
# Retorna (custo_total, [caminho]).

def dijkstra(adj, inicio, destino):
    dist = defaultdict(lambda: math.inf)
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

    if dist[destino] == math.inf:
        return math.inf, []

    caminho = []
    cursor = destino
    while cursor is not None:
        caminho.append(cursor)
        cursor = anterior.get(cursor)
    caminho.reverse()
    return dist[destino], caminho


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("Carregando dados...")
    usuarios = carregar_dados('steam-200k.csv')
    print(f"Usuarios carregados: {len(usuarios)}")

    print("\nConstruindo grafo...")
    adj = construir_grafo(usuarios)
    total_nos = len(adj)
    total_arestas = sum(len(v) for v in adj.values()) // 2
    print(f"Grafo: {total_nos} jogos, {total_arestas} arestas")

    jogo_a = "The Elder Scrolls V Skyrim"
    jogo_b = "Left 4 Dead 2"

    # ── BFS ──────────────────────────────────────────────────────────────────
    print(f"\n=== BFS a partir de '{jogo_a}' ===")
    dist_bfs = bfs(adj, jogo_a)
    vizinhos_diretos = sorted(
        [(j, adj[jogo_a][j]) for j in adj[jogo_a]],
        key=lambda x: x[1], reverse=True
    )[:10]
    print(f"Jogos alcancaveis: {len(dist_bfs)}")
    print("Top 10 vizinhos diretos (por afinidade):")
    for jogo, peso in vizinhos_diretos:
        print(f"  {jogo} (usuarios em comum: {peso})")

    # ── DFS ──────────────────────────────────────────────────────────────────
    print(f"\n=== DFS a partir de '{jogo_a}' ===")
    ordem_dfs = dfs(adj, jogo_a)
    print(f"Jogos visitados: {len(ordem_dfs)}")
    print(f"Primeiros 10 na ordem DFS: {ordem_dfs[:10]}")

    # ── Dijkstra ─────────────────────────────────────────────────────────────
    print(f"\n=== Dijkstra: '{jogo_a}' -> '{jogo_b}' ===")
    custo, caminho = dijkstra(adj, jogo_a, jogo_b)
    if caminho:
        print(f"Custo acumulado: {custo:.4f}")
        print(f"Caminho: {' -> '.join(caminho)}")
    else:
        print("Sem caminho encontrado.")
