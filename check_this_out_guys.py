def get_available_nodes(start_node):
    if graph.get(start_node):
        for node in graph.get(start_node):
            if node not in available_nodes:
                available_nodes.append(node)
                get_available_nodes(node)


available_nodes = [(24, 18)]
depth = 0
graph = {
    (24, 17): [(1020120, 2994)],
    (24, 18): [(24, 19), (23, 18)],
    (24, 19): [(24, 18), (24, 20), (23, 19)],
    (23, 19): []
}
get_available_nodes((24, 18), depth)
print(available_nodes)
