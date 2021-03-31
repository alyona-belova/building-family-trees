from Relative import Relative
from load_forms import kinship_gender


# загрузка template_info из файла с описанием шаблончиков
def get_template_info_by_word(word: str, prev_word: str):
    template_info_arr = []

    with open('relatives_templates.txt', 'r', encoding='utf-8') as template_info_file:
        relatives_line, edges_line = False, False
        template_info = {'relatives': [], 'edges_list': []}

        for s in template_info_file:
            s = s.strip()
            if relatives_line:
                relatives_info = s.split('; ')
                for v in relatives_info:
                    v = v.split(', ')
                    v = [int(v[0]), v[1], int(v[2])]
                    template_info['relatives'].append(v)
                relatives_line = False
                edges_line = True

            elif edges_line:
                edges_info = s.split('; ')
                for v in edges_info:
                    v = v.split(', ')
                    v = [int(v[0]), int(v[1]), v[2]]
                    template_info['edges_list'].append(v)

                template_info_arr.append(template_info)
                relatives_line, edges_line = False, False
                template_info = {'relatives': [], 'edges_list': []}

            else:
                s = s.split('-')
                if len(s) > 0 and word == s[0]:
                    prev_word = prev_word.split()
                    if prev_word[0] in ('внучатый', 'внучатая', 'двоюродный', 'двоюродная'):
                        prev_word = prev_word[1]
                    else:
                        prev_word = prev_word[0]

                    # зять - муж золовки м. б. только у женщины
                    if len(s) > 1 and word == 'зять' and s[1] == '3' and kinship_gender[prev_word] == 'm':
                        relatives_line = False

                    # ограничения по полу бывших мужа/жены
                    elif len(s) > 1 and word in ('падчерица', 'пасынок') and s[1] == '1' \
                            and kinship_gender[prev_word] == 'f':
                        relatives_line = False
                    elif len(s) > 1 and word in ('падчерица', 'пасынок') and s[1] == '2' and \
                            kinship_gender[prev_word] == 'm':
                        relatives_line = False

                    else:
                        relatives_line = True

    return template_info_arr


# класс шаблончик
class Template:
    def __init__(self, template_info, target_rel_name: str):
        relatives_info = template_info['relatives']
        edges_list_info = template_info['edges_list']
        self.template_relatives = []

        # создаем родственников и добавляем в массив
        for r in relatives_info:
            name = r[1]
            if r[0] == len(relatives_info) - 1:
                name = target_rel_name
            self.template_relatives.append(Relative(id=r[0], name=name, name_basic=r[1], color=r[2]))
            # print(r[0], name, r[1])

        # регистрируем связи
        for edge in edges_list_info:
            id_1 = edge[0]
            id_2 = edge[1]
            rel_type = edge[2]
            for j in range(len(self.template_relatives)):
                if self.template_relatives[j].id == id_1:
                    self.template_relatives[j].relations[rel_type].append(id_2)
                    break

    def get_target_word_id(self):  # получение id последнего слова в шаблончике
        target_word_id = 0
        for rel in self.template_relatives:
            if rel.id > target_word_id:
                target_word_id = rel.id
        return target_word_id
