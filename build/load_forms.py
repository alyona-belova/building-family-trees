def load_forms():
    with open('kinship_term_list.txt', 'r', encoding='utf-8') as data_file:
        for s in data_file:
            s = s.strip()
            if s == '':
                continue
            s = s.split(',')
            kinship_term_list.extend(s)
            for term in s:
                kinship_term_dict[term] = s[0]

    with open('pronouns.txt', 'r', encoding='utf-8') as data_file:
        lines = data_file.readlines()
        i = 0
        prev_empty = True
        while i < len(lines):
            s = lines[i].strip()
            if s == '':
                prev_empty = True
                i += 1
            elif prev_empty:
                pronouns_list.extend(s.split(', '))
                pronouns_dict[tuple(s.split(', '))] = lines[i + 1].strip()
                prev_empty = False
                i += 2

    with open('poss_adj_list.txt', 'r', encoding='utf-8') as data_file:
        for s in data_file:
            s = s.strip().split()
            poss_adj_stem[s[0]] = s[1]

    with open('kinship_term_gender.txt', 'r', encoding='utf-8') as data_file:
        for s in data_file:
            s = s.strip().split()
            word, gender = s[0], s[1]
            for term in kinship_term_dict:
                if kinship_term_dict[term] == word:
                    kinship_gender[term] = gender


kinship_term_list = []  # термины родства
kinship_term_dict = dict()  # термины родства - соотв. базовым терминам
kinship_gender = dict()  # пол родственников
kinship_gendered_exceptions = {'female': [], 'male': []}  # такие родственни_цы м. б. только у м / ж

pronouns_list = []  # местоимения
pronouns_dict = dict()  # местоимения - соотв. нач. формам
poss_adj_stem = dict()  # прит. прил. + сущ., от кот. образованы

load_forms()
