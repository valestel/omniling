import ngram_utils
import json
import os
from typing import List, Tuple
from collections import defaultdict
from io import StringIO


class GramCollection:
    def __init__(self, description, contents, total):
        self.description: str = description
        self.contents: List[Tuple[str, int]] = contents
        self.total: int = total


class LanguageModel:
    def __init__(self, iso: str):
        self.lang_id: str = iso
        self.grams = None

    def load_grams_from_string(self, text: str):
        text = StringIO(text)
        return self._load_grams(text)

    def load_grams_from_file(self, text_path: str):
        with open(text_path, 'r') as file:
            return self._load_grams(file)

    def _load_grams(self, file):
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        all_ngrams = [defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)]
        total = 0

        prev_chars = " " * 5
        end = 0
        while True:
            char = file.read(1)
            if not char or end > 0:
                char = " "
                end += 1
            if end == 4:
                break

            if (not (char.isalpha() or char.isspace())) or (not char.isprintable()):
                continue
            prev_chars = prev_chars[1:] + char
            for n in range(5):
                all_ngrams[n][prev_chars[-(n + 1):]] += 1
            total += 1
            if total % 10000000 == 0:
                before = len(all_ngrams[4])
                for n in range(5):
                    all_ngrams[n] = ngram_utils.compactify(all_ngrams[n])
                print(f'[{self.lang_id}] {(total * 100 / size):.2f}%, total 5grams: {before} -> {len(all_ngrams[4])}')

        # removing single whitespaces from all_grams
        all_ngrams[0].pop(" ", None)
        all_ngrams[1].pop("  ", None)
        all_ngrams[2].pop("   ", None)

        def to_gram_collection(i, gram_dict, total):
            gram_dict = ngram_utils.range_ngrams(gram_dict)
            return GramCollection(str(i + 1) + 'grams', gram_dict, total)

        self.grams = list(map(lambda t: to_gram_collection(t[0], t[1], total), enumerate(all_ngrams)))

    def to_json(self):
        with open('models_json/' + self.lang_id + '.json', 'w', encoding='utf8') as fp:
            json.dump(self.__dict__, fp, default=lambda o: o.__dict__, ensure_ascii=False)


def load_model(jsonpath):
    with open(jsonpath) as f:
        json_data = json.load(f)
        model = LanguageModel(json_data['lang_id'])
        model.grams = list(
            map(lambda t: GramCollection(t['description'], t['contents'], t['total']), json_data['grams']))
        return model


def load_language_models():
    json_dir = os.fsencode('./models_json/')
    for file in os.listdir(json_dir):
        yield load_model(os.path.join(json_dir, file))


def detect_language(text: str):
    text_model = LanguageModel('n/a')
    text_model.load_grams_from_string(text)
    all_languages = load_language_models()
    res_distance = []
    for language in all_languages:
        distance = ngram_utils.compute_distance(text_model, language)
        res_distance.append((distance, language.lang_id))
    return sorted(res_distance)[:3]
