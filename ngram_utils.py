import operator
import constants
from collections import defaultdict


def range_ngrams(ngrams):
    zipf = sorted(ngrams.items(), key=operator.itemgetter(1), reverse=True)[:constants.TOP_NGRAMS]
    return zipf


def compactify(ngrams):
    return defaultdict(int, {k: v for k, v in ngrams.items() if v > 100})


def compute_distance(text_model, lang_model):
    sum_distance = 0

    for i in range(5):
        for text_rank, (ngram, _freq) in enumerate(text_model.grams[i].contents):
            match = next((lang_rank for lang_rank, lang_gram in enumerate(lang_model.grams[i].contents)
                          if lang_gram[0] == ngram), None)
            if match is not None:
                sum_distance += abs(match - text_rank)
            else:
                sum_distance += constants.MAX_PROB_VALUE
    return sum_distance
