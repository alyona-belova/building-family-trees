from nltk.tokenize import sent_tokenize

from text_analysis import search_sentence
from WordSequence import WordSequence
from Construction import Construction


def find_sequences(text: str):
    text = sent_tokenize(text, language='russian')
    word_sequences = []
    for i in range(len(text)):
        sent = text[i]
        search_results = search_sentence(sent)
        for seq in search_results:
            ws = WordSequence(seq_original=seq, sentence=sent, sent_id=i + 1)
            word_sequences.append(ws)
    return word_sequences


def get_tree(seq):
    if isinstance(seq, str):
        ws = WordSequence(seq_original=seq.strip().split(),
                          sentence=seq, sent_id=0)
    elif isinstance(seq, WordSequence):
        ws = seq
    else:
        raise Exception('seq should be of type str or WordSequence')
    construction = Construction(word_sequence=ws)
    construction.build_trees()
    return construction


def visualize(text: str):
    word_sequences = find_sequences(text)
    for ws in word_sequences:
        construction = get_tree(ws)
        construction.draw()
