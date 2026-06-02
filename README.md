# Grafos AV3 — Sistema de Recomendação Steam

Análise de uma rede de jogos da Steam usando BFS, DFS e Dijkstra.

## Estrutura

```
├── main.py        # Ponto de entrada
├── grafo.py       # Carregamento do dataset e construção do grafo
├── bfs.py         # Busca em Largura
├── dfs.py         # Busca em Profundidade
├── dijkstra.py    # Menor caminho (Dijkstra)
└── steam-200k.csv # Dataset (necessário para execução)
```

## Pré-requisitos

- Python 3.8 ou superior
- Arquivo `steam-200k.csv` na raiz do projeto

## Como executar

```bash
python main.py
```

O programa irá:

1. Carregar o dataset e construir o grafo de jogos
2. Executar **BFS** a partir de *The Elder Scrolls V Skyrim* e listar os 10 jogos com maior afinidade
3. Executar **DFS** a partir do mesmo jogo e exibir a ordem de visita
4. Executar **Dijkstra** encontrando o menor caminho até *Left 4 Dead 2*
