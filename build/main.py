from TreeVersion import TreeVersion, tree_versions
from to_root_form import get_root_form_string
from Graph import create_graph

# считываем входную конструкцию и преобразуем для построения дерева
input_str = input()
root_form_arr = get_root_form_string(input_str).split()

# строим деревья
first_tree_version = TreeVersion(id=0)
tree_versions.append(first_tree_version)
first_tree_version.process_word(word_arr=root_form_arr, this_word_ind=0, root_id=0)

for tree in tree_versions:
    # удаляем дубликаты родственников
    while True:
        id_duplicates = tree.find_duplicates()
        if id_duplicates:
            tree.clear_out_duplicates(id_duplicates)
        else:
            break

    tree.reclaim_id()  # переназначаем id, чтобы они шли по порядку
    tree.rename_relatives()  # переименовываем родственников, чтобы избежать повторения имен

    if len(tree_versions) > 1:
        tree.pic_name += '_' + str(tree.id + 1)
    tree.pic_name += '.png'
    create_graph(tree=tree)  # рисуем картинку

print()
print('graphs created:', str(len(tree_versions)))
