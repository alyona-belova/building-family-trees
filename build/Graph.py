from TreeVersion import TreeVersion

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


def plot_graph(nodes, edges, pos, labels=False, node_size=False, node_color='r',
               arrows=False, alpha=0.8, font_size=18, font_weight='normal'):
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.draw(G, with_labels=labels, node_color=node_color,
            node_size=node_size, arrows=arrows, alpha=alpha,
            pos=pos, font_size=font_size, font_weight=font_weight)


def get_connections(relatives):
    connections = []
    for relative in relatives:
        for relation in relative.relations:
            if relative.relations.get(relation) != []:
                first = relative.name
                second = relatives[relative.relations.get(relation)[0]].name
                no_duplicates = True
                for i in connections:
                    if i == [first, second] or i == [second, first]:
                        no_duplicates = False
                if no_duplicates:
                    connections.append([first, second])
    connections = pd.DataFrame(connections, columns=['start', 'end'])
    return connections


def get_coordinates(relatives, relative, fixed_positions):
    for relation in relative.relations:
        for rel_id in relative.relations[relation]:
            if fixed_positions[relatives[rel_id].name] is None:

                if relation == 'mother' or relation == 'father':
                    x = fixed_positions[relative.name][0]
                    y = fixed_positions[relative.name][1] + 1
                    unique_values = set(fixed_positions.values())
                    while (x, y) in unique_values:
                        x += 1
                    fixed_positions[relatives[rel_id].name] = (x, y)

                elif relation == 'daughter' or relation == 'son':
                    x = fixed_positions[relative.name][0]
                    y = fixed_positions[relative.name][1] - 1
                    unique_values = set(fixed_positions.values())
                    while (x, y) in unique_values:
                        x += 1
                    fixed_positions[relatives[rel_id].name] = (x, y)

                elif relation == 'husband' or relation == 'wife':
                    x = fixed_positions[relative.name][0] + 1
                    y = fixed_positions[relative.name][1]
                    fixed_positions[relatives[rel_id].name] = (x, y)

    return fixed_positions


def create_graph(tree: TreeVersion):
    relatives = tree.relatives
    connections = get_connections(relatives)  # список ребер

    nodes = []  # создаем вершины
    for i in relatives:
        nodes.append(i.name)

    # задаем цвета (записываем в отедльный массив)
    color_map = []
    for node in relatives:
        if node.color == -1:
            color_map.append('lightgrey')
        elif node.color == 1:
            color_map.append('lightcoral')
        else:
            color_map.append('skyblue')

    # задаем координаты
    fixed_positions = dict.fromkeys(nodes)
    for relative in relatives:
        if relative.id == 0:
            fixed_positions[relative.name] = (0, 0)
    for relative in relatives:
        fixed_positions = get_coordinates(relatives, relative, fixed_positions)

    # рассчитываем размер окна
    min_x = max_x = min_y = max_y = 0
    for i in fixed_positions.values():
        if i[0] < min_x:
            min_x = i[0]
        elif i[0] > max_x:
            max_x = i[0]
        elif i[1] < min_y:
            min_y = i[1]
        elif i[1] > max_y:
            max_y = i[1]

    if min_x < 0:
        size_x = abs(min_x) + max_x
    else:
        size_x = max_x
    if min_y < 0:
        size_y = abs(min_y) + max_y
    else:
        size_y = max_y

    # рисуем график
    plt.figure(figsize=(size_x + 20, size_y + 15))
    plot_graph(nodes=nodes,
               edges=[tuple(row) for row in connections.values],
               labels=True,
               node_color=color_map,
               node_size=7000,
               alpha=1,
               pos=fixed_positions,
               font_size=18,
               font_weight='bold')
    plt.savefig(tree.pic_name)
