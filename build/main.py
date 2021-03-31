from nltk.tokenize import sent_tokenize
from pathlib import Path

from text_analysis import search_sentence
from WordSequence import WordSequence
from Construction import Construction

# читаем корпус
with open('corpus.txt', 'r', encoding='utf-8') as corpus_file:
    text = corpus_file.read()

# text = """Вот встречь семенит тетка Авдотья, бабушкина свояченица.
# Глава восьмая Александр Дмитриевич Кузнецов, бабушкин пасынок, по окончании войны,
# также вернулся в Николаев и поселился в том малом флигеле, рядом с нашим, где пожил недолго «генерал-ополченец».
# Необратимость умирания Дома усугубилась и человеческой смертью:
# умерла моя прабабка, а дедова мать и свекровь моей бабушки.
# Ближайшей родственницей оказалась дедушкина племянница, дочь его родной сестры, пожилая женщина, жена кузнеца,
# между прочим, первоклассного, потомственного кузнеца, даже фамилия его была Кузнецов."""

# разбиваем текст на предложения
text = sent_tokenize(text, language='russian')
word_sequences = []

# ищем конструкции
for i in range(len(text)):
    sent = text[i]
    search_results = search_sentence(sent)
    for seq in search_results:
        word_sequences.append(WordSequence(seq_original=seq, sentence=sent, sent_id=i + 1))

# обрабатываем конструкции
for ws in word_sequences:
    ws.clear()
    ws.normalize()
    ws.get_basic()
    ws.check_correct()

    # print(ws.seq_original)
    # print(ws.seq_clear)
    # print(ws.seq_normal)
    # print()

# записываем их в файл
# with open('corpus_search_results.txt', 'w', encoding='utf-8') as fout:
#     for sent in text:
#         fout.write(sent + '\n')
#         flag = False
#         for ws in word_sequences:
#             if ws.sentence == sent:
#                 flag = True
#                 ws.show(fout=fout)
#                 fout.write('\n')
#         if not flag:
#             fout.write('-\n')
#         fout.write('\n')

# таблица для оценки качества
# with open('evaluation_table.tsv', 'w', encoding='utf-8') as table:
#     table.write('\t'.join(['', '', '']) + '\n')
#     for i in range(len(text)):
#         sent = text[i]
#         flag = False
#         for ws in word_sequences:
#             if sent == ws.sentence:
#                 flag = True
#                 sent_print = ' '.join(ws.sentence.split('\n'))
#                 arr = [str(ws.sent_id), sent_print, ' '.join(ws.seq_clear)]
#                 table.write('\t'.join(arr) + '\n')
#         if not flag:
#             sent_print = ' '.join(sent.split('\n'))
#             arr = [str(i + 1), sent_print, '-']
#             table.write('\t'.join(arr) + '\n')

# создаем и рисуем деревья
for ws in word_sequences:
    print(ws.sent_id)
    # создаем директорию данного предложения
<<<<<<< HEAD
    folder_path = 'graphs/' + str(ws.sent_id)
=======
    folder_path = '/cs_projects/relatives_to_trees/graphs/' + str(ws.sent_id)
>>>>>>> 9ada933a1d05f2a59978bf283cb7b0428b774e37
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    txt_file_path = folder_path + '/sentence.txt'
    with open(txt_file_path, 'w', encoding='utf-8') as sent_file:
        sent_file.write(ws.sentence)

    if not ws.correct:
        print('word sequence skipped - incorrect')
        print(ws.seq_original)
        print(ws.seq_basic)
        print()
    else:
        construction = Construction(word_sequence=ws)
        print(ws.seq_original)
        print(ws.seq_clear)
        print(ws.seq_normal)
        print()
        construction.create_trees()
