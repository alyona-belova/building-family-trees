import pymorphy2
from nltk.tokenize import word_tokenize
from load_forms import kinship_term_list, kinship_term_dict, kinship_gender, kinship_gendered_exceptions, \
    pronouns_list, pronouns_dict, poss_adj_stem

morph = pymorphy2.MorphAnalyzer()  # морфологический анализатор pymorphy2


def is_kinship_term(s, case=None):  # термин родства?
    s_parse = morph.parse(s)
    if case is None:
        for v in s_parse:
            if v.normal_form in kinship_term_list:
                return True
    else:
        for v in s_parse:
            if v.normal_form in kinship_term_list and v.tag.case == case:
                return True
    return False


def is_definition(s):  # определение?
    s_parse = morph.parse(s)
    for v in s_parse:
        if v.tag.POS in ['ADJF', 'ADJS', 'PRTF', 'PRTS']:
            return True
    return False


def is_noun(s, case=None):  # существительное?
    s_parse = morph.parse(s)
    for v in s_parse:
        if v.tag.POS == 'NOUN' and (case is None or v.tag.case == case):
            return True
    return False


def is_poss_adj(s):  # притяжательное прилагательное?
    p = morph.parse(s)
    for v in p:
        ending = v.normal_form[len(v.normal_form) - 2:]
        if ending in ('ов', 'ев', 'ёв', 'ин', 'ын'):
            return True
    return False


def is_pronoun(s):  # местоимение из нашего списка?
    p = morph.parse(s)
    for v in p:
        if v.normal_form in pronouns_list:
            return True
    return False


def is_vnuch_dvoiur(s):  # форма слова внучатый / двоюродный ?
    p = morph.parse(s)
    for v in p:
        if v.normal_form in ('внучатый', 'двоюродный'):
            return True
    return False


# проверка, что слово согласовано по роду и падежу с предыд. / след.
def check_case_gender(kinship_term, definition):
    kinship_parse = morph.parse(kinship_term)
    def_parse = morph.parse(definition)
    for p1 in kinship_parse:
        for p2 in def_parse:
            if p1.tag.case == p2.tag.case and p1.tag.gender == p2.tag.gender:
                return True
    return False


# получение начальной формы
def get_normal_form(s: str, is_first: bool, next_word=None):
    s_capitalized = s
    s = s.lower()
    s_normal = ''

    if is_kinship_term(s):  # термин родства
        s_parse = morph.parse(s)
        for v in s_parse:
            if v.normal_form in kinship_term_list:
                s_normal = v.normal_form
                break

    elif is_vnuch_dvoiur(s):  # форма внучатый / двоюродный
        if s[0] == 'в':
            if kinship_gender[next_word] == 'f':
                s_normal = 'внучатая'
            else:
                s_normal = 'внучатый'
        if s[0] == 'д':
            if kinship_gender[next_word] == 'f':
                s_normal = 'двоюродная'
            else:
                s_normal = 'двоюродный'

    elif is_pronoun(s):  # местоимение
        s_parse = morph.parse(s)
        for v in s_parse:
            if v.tag.POS == 'ADJF':
                s_normal = v.normal_form
                break
        for item in pronouns_dict:
            if s_normal in item:
                s_normal = pronouns_dict[item]
                break

    elif is_noun(s, case='gent'):  # существит. (не термин родства)
        s_parse = morph.parse(s)[0]
        if s_parse.tag.number == 'plur':
            s_normal = s_parse.inflect({'nomn', 'plur'}).word
        else:
            s_normal = morph.parse(s)[0].normal_form

    elif is_poss_adj(s):  # притяжательные прилагательные
        s_parse = morph.parse(s)
        for v in s_parse:
            if v.normal_form in poss_adj_stem:
                s_normal = poss_adj_stem[v.normal_form]
                break

    if s_normal == '':
        raise Exception("Can't get normal form: " + s)
    return capitalize(s_capitalized, s_normal, is_first)


def get_basic_term(s: str):  # базовая форма терминов родства
    s = s.lower()
    if s in kinship_term_dict:
        return kinship_term_dict[s]
    return s


def cut_dots(s):  # удаление многоточий и точек, приклеенных к словам
    if len(s) == 1:
        return s
    if s[len(s) - 1] == '…' or s[len(s) - 1] == '.':
        return s[:len(s) - 1]
    return s


def capitalize(s_old: str, s_new: str, is_first: bool):
    if not is_first and not s_old.isupper() and s_old[0].isupper():
        s_new = s_new[0].upper() + s_new[1:]
    return s_new


def sequence_correct(seq: [str]):  # проверка конструкции на корректность
    # все слова, кроме, возм., первого, должны быть терм. родства в И. п. или их сочет. с внуч. / двоюр.
    for word in seq[1:]:
        if ' ' in word:
            first, second = word.split()
            if not (first in ('внучатый', 'внучатая', 'двоюродный', 'двоюродная')
                    and second in kinship_term_list):
                return False
        elif word not in kinship_term_list:
            return False

    # проверка, что такие сочетания родств. связь + пол возможны
    for i in range(2, len(seq)):
        word = seq[i]
        prev_word = seq[i - 1]
        if (word in kinship_gendered_exceptions['female'] and kinship_gender[prev_word] == 'm') or \
                (word in kinship_gendered_exceptions['male'] and kinship_gender[prev_word] == 'f'):
            return False
    return True


# поиск конструкций в предложении
def search_sentence(sent):
    sent = word_tokenize(sent, language='russian')  # разбиваем предложение на слова
    sent = [cut_dots(word) for word in sent]
    sent_capitalized = tuple(sent)
    sent = [word.lower() for word in sent]

    results = []

    prev_kin, prev_def = False, False
    i = 0
    while i < len(sent):
        word = sent[i]

        if not prev_kin and not prev_def and is_kinship_term(word):  # найдено первое слово
            start = i
            prev_kin = True
            if i > 0 and is_definition(sent[i - 1]):  # берем предыд. слово
                start = i - 1
            i += 1

        elif prev_kin or prev_def:  # мы внутри конструкции
            # текущ. слово - определение
            if is_definition(word):
                prev_def = True
                prev_kin = False
                i += 1
            # текущ. слово - термин родства в Р. п.
            elif is_kinship_term(word, case='gent'):
                prev_kin = True
                prev_def = False
                i += 1
            else:
                # текущ. слово - существительное в Р. п.
                if is_noun(word, case='gent'):
                    results.append(sent_capitalized[start:i + 1])
                else:
                    results.append(sent_capitalized[start:i])
                prev_kin = False
                prev_def = False

        else:  # мы вне конструкции
            i += 1
    return results
