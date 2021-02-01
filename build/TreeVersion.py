from Relative import Relative
from Template import Template, get_template_info_by_word


class TreeVersion:
    def __init__(self, id):
        self.id = id
        self.relatives = []
        self.pic_name = ''

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

    def find_duplicates(self):
        max_rel_number = {'mother': 1, 'father': 1, 'daughter': 10, 'son': 10, 'husband': 2, 'wife': 2}

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
        return id_duplicates

    def clear_out_duplicates(self, id_duplicates):
        # создадим словарь старый id : новый id
        final_ids = {}
        for lst in id_duplicates:
            for v in lst:
                final_ids[v] = min(lst)  # для дупликатов берем минимум строки
        for rel in self.relatives:
            if rel.id not in final_ids:
                final_ids[rel.id] = rel.id  # для остальных - оставляем старый id

        new_relatives = []
        for lst in id_duplicates:
            # создадим нового родственника и сохраним в спец. массив
            final_color = -1  # color - максимальный в строке
            for rel in self.relatives:  # ищем родственника с соотв. final_id - от него возьмем name и name_basic
                if rel.id == final_ids[lst[0]]:
                    final_name = rel.name
                    final_name_basic = rel.name_basic
                if rel.id in lst and rel.color > final_color:
                    final_color = rel.color

            new_rel = Relative(id=final_ids[lst[0]], name=final_name,
                               name_basic=final_name_basic, color=final_color)

            # relations - соберем ото всех, чьи id указаны в строке
            for rel in self.relatives:
                if rel.id in lst:
                    for rel_type in rel.relations:
                        for v in rel.relations[rel_type]:
                            if v not in new_rel.relations[rel_type]:
                                new_rel.relations[rel_type].append(final_ids[v])
            new_relatives.append(new_rel)

            # найдем, у кого персонаж числится в relations, и заменим id на final_id + удалим лишние записи
            for rel in self.relatives:
                for rel_type in rel.relations:
                    for i in range(len(rel.relations[rel_type])):
                        if rel.relations[rel_type][i] in lst:
                            rel.relations[rel_type][i] = final_ids[lst[0]]

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
