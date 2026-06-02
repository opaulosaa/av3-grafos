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
