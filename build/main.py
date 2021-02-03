from nltk.tokenize import sent_tokenize
from pathlib import Path

from text_analysis import search_sentence
from WordSequence import WordSequence
from Construction import Construction

# читаем корпус
# with open('corpus.txt', 'r', encoding='utf-8') as corpus_file:
#     text = corpus_file.read()

text = """У жены сестра, а вы ее муж. Ладно? Вы ее муж. Вошли две дамы, обе девицы, 
одна ― падчерица одного двоюродного брата покойной жены князя, 
или что-то в этом роде, воспитанница его, которой он уже выделил приданое и которая (замечу для будущего) 
и сама была с деньгами; вторая ― Анна Андреевна Версилова, дочь Версилова, старше меня тремя годами, 
жившая с своим братом у Фанариотовой и которую я видел до этого времени всего только раз в моей жизни, 
мельком на улице, хотя с братом ее, тоже мельком, уже имел в Москве стычку 
(очень может быть, и упомяну об этой стычке впоследствии, если место будет, потому что в сущности не стоит)."""

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
#     # table.write('\t'.join(['', '', '']) + '\n')
#
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
    folder_path = '/cs_projects/relatives_to_trees/graphs/' + str(ws.sent_id)
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
        construction.create_trees()
