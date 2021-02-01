from text_analysis import is_kinship_term, is_definition, is_noun, \
    is_vnuch_dvoiur, is_pronoun, is_poss_adj, \
    check_case_gender, get_normal_form, get_basic_term, sequence_correct, search_sentence
from nltk.tokenize import sent_tokenize


class WordSequence:
    def __init__(self, seq_original: [str], sentence: str, sent_id: int):
        self.sentence = sentence
        self.sent_id = sent_id
        self.seq_original = seq_original
        self.seq_clear = []
        self.seq_normal = []
        self.seq_basic = []
        self.type = -1
        self.correct = None

    def show(self, fout):  # печать в файл
        fout.write(' '.join(self.seq_original) + '\n' +
                   ' '.join(self.seq_clear) + '\n' +
                   ' '.join(self.seq_normal) + ' (type = ' + str(self.type) + ')\n' +
                   # ' '.join(self.seq_basic) + '\n' +
                   'correct = ' + str(self.correct) + '\n')

    def clear(self):  # очистка конструкции
        # удаляем все опред. - не прит. прил. / местоим. / внуч. / двоюр.
        seq_temp = []
        for word in self.seq_original:
            if is_definition(word) and not is_vnuch_dvoiur(word) \
                    and not is_poss_adj(word) and not is_pronoun(word):
                continue
            seq_temp.append(word)

        if len(seq_temp) == 1:  # тип 0
            self.type = 0
            self.seq_clear = seq_temp
            return

        # тип 1
        first_word = seq_temp[0]
        if (is_pronoun(first_word) or is_poss_adj(first_word)) and \
                check_case_gender(first_word, seq_temp[1]):
            for i in range(1, len(seq_temp)):
                if is_kinship_term(seq_temp[i]):
                    self.seq_clear = [first_word, seq_temp[i]]
                    break
            self.type = 1
            return

        # тип 2
        sec_last_word = seq_temp[len(seq_temp) - 2]
        last_word = seq_temp[-1]
        if (is_pronoun(sec_last_word) or is_poss_adj(sec_last_word)) and is_kinship_term(last_word):
            for word in seq_temp:
                if is_kinship_term(word) or is_vnuch_dvoiur(word) or word == sec_last_word:
                    self.seq_clear.append(word)
            self.type = 2
            return

        # тип 4
        last_word = seq_temp[len(seq_temp) - 1]
        if not is_kinship_term(last_word) and is_noun(last_word, case='gent'):
            for word in seq_temp:
                if is_kinship_term(word) or is_vnuch_dvoiur(word):
                    self.seq_clear.append(word)
            self.seq_clear.append(last_word)
            self.type = 4
            return

        # тип 3
        if (is_pronoun(last_word) or is_poss_adj(last_word)) and \
                check_case_gender(last_word, seq_temp[len(seq_temp) - 2]):
            for word in seq_temp:
                if is_kinship_term(word) or is_vnuch_dvoiur(word):
                    self.seq_clear.append(word)
            self.seq_clear.append(last_word)
            self.type = 3
            return

        # тип 5
        for word in seq_temp:
            if is_kinship_term(word) or is_vnuch_dvoiur(word):
                self.seq_clear.append(word)
        self.type = 5

    # приведение к конструкций к нормальному виду (начальные формы, переворачивание)
    def normalize(self):
        self.seq_normal = [''] * len(self.seq_clear)
        for i in range(len(self.seq_clear) - 1, -1, -1):
            # получаем нормальную форму
            word = self.seq_clear[i]
            if i == len(self.seq_clear) - 1:
                word = get_normal_form(word)
            else:
                next_word = self.seq_normal[i + 1]
                word = get_normal_form(word, next_word=next_word)
            self.seq_normal[i] = word

        # склеиваем внуч. / двоюр. со след. словом
        i = 0
        while i < len(self.seq_normal):
            word = self.seq_normal[i]
            if word in ('внучатый', 'внучатая', 'двоюродный', 'двоюродная'):
                self.seq_normal[i] += ' ' + self.seq_normal[i + 1]
                del self.seq_normal[i + 1]
            else:
                i += 1

        # для типов констр. 1, 2 меняем местами два посл. слова
        if self.type in (1, 2):
            self.seq_normal[len(self.seq_normal) - 1], self.seq_normal[len(self.seq_normal) - 2] = \
                self.seq_normal[len(self.seq_normal) - 2], self.seq_normal[len(self.seq_normal) - 1]
        # для типа констр. 0, 5 добавляем корень "я"
        if self.type in (0, 5):
            self.seq_normal.append('я')

        # переворачиваем последов.
        self.seq_normal.reverse()

    # создаем последов. с базов. терминами родства
    def get_basic(self):
        self.seq_basic = [get_basic_term(word) for word in self.seq_normal]

    # проверка корректности
    def check_correct(self):
        self.correct = sequence_correct(self.seq_basic)


if __name__ == '__main__':
    # text = """От бывшей жены ее племянника Михаила.
    # Через пару дней бабушка моего друга вышла в туалет ранним утром.
    # Еще раз взглянув на дядю моего друга, поняла, что знакомиться будем завтра, сегодня он точно не в теме."""

    with open('corpus.txt', 'r', encoding='utf-8') as corpus_file:
        text = corpus_file.read()

    text = sent_tokenize(text, language='russian')  # разбиваем текст на предложения
    word_sequences = []

    # ищем конструкции
    for i in range(len(text)):
        sent = text[i]
        search_results = search_sentence(sent)
        for seq in search_results:
            word_sequences.append(WordSequence(seq_original=seq, sentence=sent, sent_id=i))

    for ws in word_sequences:
        ws.clear()
        ws.normalize()
        ws.get_basic()
        ws.check_correct()

    with open('new_try.txt', 'w', encoding='utf-8') as fout:
        for sent in text:
            fout.write(sent + '\n')
            flag = False
            for ws in word_sequences:
                if ws.sentence == sent:
                    flag = True
                    ws.show(fout=fout)
                    fout.write('\n')
            if not flag:
                fout.write('-\n')
            fout.write('\n')
