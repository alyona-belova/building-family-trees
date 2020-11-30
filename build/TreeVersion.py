import copy

from Relative import Relative
from Template import Template, get_template_info_by_word

tree_versions = []


class TreeVersion:
    def __init__(self, id):
        self.id = id
        self.relatives = []
        self.pic_name = 'graph'

    def add_template(self, template: Template, root_id):
        # если это первый обрабатываемый шаблончик, просто добавляем всех родственников в relatives
        if not self.relatives:
            self.relatives.extend(template.template_relatives)
            return

        # иначе: заменяем id остальных персонажей шаблончика на root_id + их текущий id
        for rel in template.template_relatives:
            rel.id += root_id
            for rel_type in rel.relations:
                for i in range(len(rel.relations[rel_type])):
                    rel.relations[rel_type][i] += root_id

        # находим корень_осн в relatives (запоминаем индекс)
        for i in range(len(self.relatives)):
            if self.relatives[i].id == root_id:
                real_root_ind = i
                break

        # добавляем relations корня_ш в relations корня_осн
        template_root_relations = template.template_relatives[0].relations
        for rel_type in self.relatives[real_root_ind].relations:
            self.relatives[real_root_ind].relations[rel_type].extend(template_root_relations[rel_type])

        # добавляем в основной массив relatives родственников из шаблончика, кроме корня_ш
        for rel in template.template_relatives[1:]:
            self.relatives.append(rel)

    def clear_relative_duplicates(self):
        max_rel_number = {'mother': 1, 'father': 1, 'daughter': 10, 'son': 10, 'husband': 1, 'wife': 1}

        # сделаем табличку: в каждой строчке список id, которые на самом деле относятся к одному персонажу
        id_duplicates = []

        for rel in self.relatives:
            for rel_type in rel.relations:
                # если родственник связан данным типом связи с большим числом родственников, чем разрешено
                if len(rel.relations[rel_type]) > max_rel_number[rel_type]:
                    num = -1
                    # ищем, вдруг строчка про этого персонажа уже есть в таблице
                    for v in rel.relations[rel_type]:
                        for i in range(len(id_duplicates)):
                            if v in id_duplicates[i]:
                                num = i  # сохраняем номер строки в таблице в num
                                break

                    # если еще нет, записываем в новую строку
                    if num == -1:
                        id_duplicates.append(rel.relations[rel_type])
                    # если есть, дописываем в нее
                    else:
                        for v in rel.relations[rel_type]:
                            if v not in id_duplicates[num]:
                                id_duplicates.append(v)

        for i in range(len(id_duplicates)):
            id_duplicates[i] = tuple(id_duplicates[i])

        new_relatives = []
        for lst in id_duplicates:
            # создадим нового родственника и сохраним в спец. массив
            final_id = min(lst)  # id - минимальный в строке
            final_color = -1  # color - максимальный в строке
            for rel in self.relatives:  # ищем родственника с таким id - от него возьмем name
                if rel.id == final_id:
                    final_name = rel.name
                if rel.id in lst and rel.color > final_color:
                    final_color = rel.color

            new_rel = Relative(id=final_id, name=final_name, color=final_color)

            # relations - соберем ото всех, чьи id указаны в строке
            for rel in self.relatives:
                if rel.id in lst:
                    for rel_type in rel.relations:
                        for v in rel.relations[rel_type]:
                            if v not in new_rel.relations[rel_type]:
                                new_rel.relations[rel_type].append(v)
            new_relatives.append(new_rel)

            # найдем, у кого персонаж числится в relations, и заменим id на final_id + удалим лишние записи
            for rel in self.relatives:
                for rel_type in rel.relations:
                    for i in range(len(rel.relations[rel_type])):
                        if rel.relations[rel_type][i] in lst:
                            rel.relations[rel_type][i] = final_id

            for rel in self.relatives:
                for rel_type in rel.relations:
                    rel.relations[rel_type] = list(set(rel.relations[rel_type]))

        # удалим всех родственников, кот. записаны > 1 раза
        for lst in id_duplicates:
            ind = 0
            while self.relatives and ind < len(self.relatives):
                if self.relatives[ind].id in lst:
                    del self.relatives[ind]
                else:
                    ind += 1

        # добавим новосозданных родственников (массив new_relatives)
        self.relatives.extend(new_relatives)

    def reclaim_id(self):
        self.relatives.sort(key=lambda relative: relative.id)

        # перезадаем id самим родственникам
        old_new_id_dict = {}
        for i in range(len(self.relatives)):
            old_new_id_dict[self.relatives[i].id] = i
            self.relatives[i].id = i

        # перезадаем id в relations
        for rel in self.relatives:
            for rel_type in rel.relations:
                for i in range(len(rel.relations[rel_type])):
                    rel.relations[rel_type][i] = old_new_id_dict[rel.relations[rel_type][i]]

    def rename_relatives(self):
        name_id_dict = {}
        for rel in self.relatives:
            if rel.name not in name_id_dict:
                name_id_dict[rel.name] = 1
            else:
                name_id_dict[rel.name] += 1
                rel.name = rel.name + '_' + str(name_id_dict[rel.name])

    def process_word(self, word_arr: [str], this_word_ind: int, root_id):
        # если слова закончились
        if this_word_ind == len(word_arr):
            return

        # первое слово пропускаем
        if this_word_ind == 0:
            this_word_ind += 1

        word = word_arr[this_word_ind]
        template_info_arr = get_template_info_by_word(word, word_arr[this_word_ind - 1])
        print(word + ':', str(len(template_info_arr)), 'options')

        for template_info in template_info_arr:
            # если это второе слово, у корня шаблончика color=1, name=root_name, если нужно
            if this_word_ind == 1:
                template_info['relatives'][0][1] = word_arr[0]
                template_info['relatives'][0][2] = 1

            # если это последнее слово, у целевого слова в шаблончике color=1
            if this_word_ind == len(word_arr) - 1:
                template_info['relatives'][len(template_info['relatives']) - 1][2] = 1

        # добавляем остальные варианты
        for template_info in template_info_arr[1:]:
            new_tree = TreeVersion(id=len(tree_versions))
            new_tree.relatives = copy.deepcopy(self.relatives)

            template = Template(template_info)
            new_tree.add_template(template, root_id)
            new_root_id = template.get_target_word_id()

            tree_versions.append(new_tree)
            new_tree.process_word(word_arr, this_word_ind + 1, new_root_id)

        # добавляем первый вариант шаблончика
        template = Template(template_info_arr[0])
        self.add_template(template, root_id)
        new_root_id = template.get_target_word_id()
        self.process_word(word_arr, this_word_ind + 1, new_root_id)
