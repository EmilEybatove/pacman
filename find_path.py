import datetime
from pprint import pp
from random import random
from collections import deque


def get_next_nodes(x, y):
    check_next_node = lambda x, y: True if (0 <= x < cols) and (0 <= y < rows) and (grid[y][x] in allowed) else False
    return [(x + dx, y + dy) for dx, dy in ways if check_next_node(x + dx, y + dy)]


# MAIN SETTINGS. DO NOT TOUCH!!
SIZE = cols, rows = 25, 15

not_allowed = ["|", "-", "1", "2", "3", "4", 1, 2, 3, 4]
allowed = ["0", 0, "."]
ways = [0, -1], [0, 1], [1, 0], [-1, 0]

grid = [[0 if random() < 0.2 else 0 for col in range(cols)] for row in range(rows)]
for el in grid:
    print(el)

graph = {}
for y, row in enumerate(grid):
    for x, col in enumerate(row):
        if col in allowed:
            graph[(x, y)] = graph.get((x, y), []) + get_next_nodes(x, y)
pp(graph)
print("\n" * 3)


def bfs(graph, start_point, end_point):
    parent, queue = {start_point: None}, deque([start_point])

    if start_point not in graph:
        raise ValueError("Start point is not in graph")
    if end_point not in graph:
        raise ValueError("End point is not in graph")
    while queue:
        node = queue.popleft()
        for neighbour in graph[node]:
            if node == end_point:
                path = [node]
                n = parent.get(node)
                while n is not None:
                    path.append(n)
                    n = parent.get(n)
                return path[::-1]
            if neighbour not in parent:
                queue.append(neighbour)
                parent[neighbour] = node
    return None


print(bfs(graph, (5, 0), (24, 14)))
