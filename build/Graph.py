from TreeVersion import TreeVersion
from load_forms import kinship_gender
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


def plot_graph(nodes, edges, pos, node_color, node_shape, name, sentence, size_x, size_y, right, top, bottom):
    G = nx.Graph()

    f_list = []
    m_list = []
    n_list = []

    f_color = []
    m_color = []
    n_color = []

    f_pos = {}
    m_pos = {}
    n_pos = {}

    for node, sex, color in zip(nodes, node_shape, node_color):
            if sex == "f":
                f_list.append(node)
                f_color.append(color)
                f_pos.update({node: pos.get(node)})
            elif sex == "m":
                m_list.append(node)
                m_color.append(color)
                m_pos.update({node: pos.get(node)})
            else:
                n_list.append(node)
                n_color.append(color)
                n_pos.update({node: pos.get(node)})

    fig = plt.figure(figsize=(size_x + 19, size_y + 19))
    ax = fig.add_subplot(111)

    fig.set(facecolor='white')
    ax.set(facecolor='white')
    ax.set_title(name, fontsize=40, fontweight='bold')

    img = plt.imread("image.png")
    ax.imshow(img, extent=[-0.5, right+0.5, bottom-0.5, top+0.5])

    plt.figtext(0.5, 0.01, sentence, ha="center", fontsize=22,
                bbox={"facecolor": "blue", "alpha": 0.1, "pad": 5}, wrap=True)

    nx.draw_networkx_nodes(G, f_pos, f_list, node_shape='o', node_size=7000, node_color=f_color, alpha=0.9)
    nx.draw_networkx_nodes(G, m_pos, m_list, node_shape='s', node_size=7000, node_color=m_color, alpha=0.9)
    nx.draw_networkx_nodes(G, n_pos, n_list, node_shape='d', node_size=7000, node_color=n_color, alpha=0.9)

    G.add_edges_from(edges)
    nx.draw_networkx_edges(G, pos)

    names = []
    for node in nodes:
        names.append(node.partition("_")[0])

    nx.draw_networkx_labels(G, pos, font_size=18, font_weight='bold', labels=dict(zip(nodes, names)))


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


def create_graph(tree: TreeVersion, seq: [str], sentence: str):
    relatives = tree.relatives
    word_seq_original = ' '.join(seq)
    for relative in relatives:
        if " " in relative.name:
            relative.name = "\n".join(relative.name.split())

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
            color_map.append('cornflowerblue')
        else:
            color_map.append('skyblue')

    # задаем пол
    sex_map = []
    for node in relatives:
        if node.id == 0:
            sex_map.append('both')
        else:
            name = ''.join(c for c in node.name if c not in '_0123456789')
            if "\n" in name:
                sex_map.append(kinship_gender.get(name[name.index('\n') + 1:]))
            else:
                sex_map.append(kinship_gender.get(name))

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
    plot_graph(nodes=nodes,
               edges=[tuple(row) for row in connections.values],
               pos=fixed_positions,
               node_color=color_map,
               node_shape=sex_map,
               name=word_seq_original,
               sentence=sentence,
               size_x=size_x,
               size_y=size_y,
               right=max_x,
               top=max_y,
               bottom=min_y)
    plt.savefig(tree.pic_name)
    plt.close()
