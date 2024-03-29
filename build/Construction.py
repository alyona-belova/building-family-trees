import copy
import os

from TreeVersion import TreeVersion
from WordSequence import WordSequence
from Graph import create_graph
from Template import Template, get_template_info_by_word


class Construction:
    def __init__(self, word_sequence: WordSequence):
        self.word_sequence = word_sequence
        self.tree_versions = []

    def process_word(self, tree_id: int, this_word_ind: int, root_id: int):
        # если слова закончились
        if this_word_ind == len(self.word_sequence.seq_basic):
            return

        # первое слово пропускаем
        if this_word_ind == 0:
            this_word_ind += 1

        tree = self.tree_versions[tree_id]
        word_basic = self.word_sequence.seq_basic[this_word_ind]
        word = self.word_sequence.seq_normal[this_word_ind]
        prev_word_basic = self.word_sequence.seq_basic[this_word_ind - 1]
        template_info_arr = get_template_info_by_word(word_basic, prev_word=prev_word_basic)
        # print(word + ' -> ' + word_basic + ':', str(len(template_info_arr)), 'options')

        for template_info in template_info_arr:
            # если это второе слово, у корня шаблончика color=1, name=root_name, если нужно
            if this_word_ind == 1:
                template_info['relatives'][0][1] = self.word_sequence.seq_normal[0]
                template_info['relatives'][0][2] = 1

            # если это последнее слово, у целевого слова в шаблончике color=1
            if this_word_ind == len(self.word_sequence.seq_basic) - 1:
                template_info['relatives'][len(template_info['relatives']) - 1][2] = 1

        # добавляем остальные варианты
        for template_info in template_info_arr[1:]:
            new_tree = TreeVersion(id=len(self.tree_versions))
            new_tree.relatives = copy.deepcopy(tree.relatives)

            template = Template(template_info, word)
            new_tree.add_template(template, root_id)
            new_root_id = template.get_target_word_id()

            self.tree_versions.append(new_tree)
            self.process_word(new_tree.id, this_word_ind + 1, new_root_id)

        # добавляем первый вариант шаблончика
        template = Template(template_info_arr[0], word)
        tree.add_template(template, root_id)
        new_root_id = template.get_target_word_id()
        self.process_word(tree_id, this_word_ind + 1, new_root_id)

    def build_trees(self):  # строим графы
        first_tree_version = TreeVersion(id=0)
        self.tree_versions.append(first_tree_version)
        self.process_word(tree_id=0, this_word_ind=0, root_id=0)

        for tree in self.tree_versions:
            # удаляем дубликаты родственников
            while True:
                id_duplicates = tree.find_duplicates()
                if id_duplicates:
                    tree.clear_out_duplicates(id_duplicates)
                else:
                    break
            tree.reclaim_id()  # переназначаем id, чтобы они шли по порядку
            tree.rename_relatives()  # переименовываем родственников, чтобы избежать повторения имен

    def draw(self):  # отрисовка
        current_directory = os.getcwd()
        folder_path = os.path.join(current_directory, 'graphs', str(self.word_sequence.sent_id),
                                   ' '.join(self.word_sequence.seq_clear))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for tree in self.tree_versions:
            tree.pic_name = os.path.join(folder_path, str(tree.id + 1) + '.png')
            create_graph(tree=tree, seq=self.word_sequence.seq_clear, sentence=self.word_sequence.sentence)
