from grafo import carregar_dados, construir_grafo
from bfs import bfs
from dfs import dfs
from dijkstra import dijkstra


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
