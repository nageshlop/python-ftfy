# coding: utf-8
import wordfreq
from collections import defaultdict
from operator import itemgetter
import ftfy
from ftfy.chardata import chars_to_classes
from unicodedata import normalize
import re
import json
import pprint


LANGUAGE_ENCODINGS = {
    'ar': ['iso-8859-6', 'sloppy-windows-1256'],
    'de': ['macroman', 'iso-8859-2', 'cp437'],
    'el': ['sloppy-windows-1253'],
    'en': ['macroman', 'cp437'],
    'es': ['macroman', 'cp437'],
    'fr': ['macroman', 'cp437'],
    'id': ['macroman', 'cp437'],
    'ja': ['shift-jis', 'euc-jp'],
    'ko': ['euc-kr'],
    'ms': ['macroman', 'cp437'],
    'nl': ['macroman', 'cp437'],
    'pt': ['macroman', 'cp437'],
    'ru': ['sloppy-windows-1251', 'koi8-r'],
    'zh': ['euc-cn', 'gbk', 'big5']
}
COMMON_ENCODINGS = ['iso-8859-1', 'sloppy-windows-1252', 'utf-8']


def get_trigrams(text):
    for pos in range(0, len(text) - 2):
        trigram = text[pos:pos+3]
        yield trigram


def add_language_trigrams(normal_freqs, baked_freqs, language):
    for baseword in wordfreq.iter_wordlist(language):
        freq = wordfreq.word_frequency(baseword, language)
        for word in set([baseword, baseword.upper()]):
            padded = ' %s ' % word
            for trigram in get_trigrams(padded):
                normal_freqs[trigram] += freq

            for enc1 in LANGUAGE_ENCODINGS[language]:
                for enc2 in COMMON_ENCODINGS + LANGUAGE_ENCODINGS[language]:
                    if enc1 != enc2:
                        try:
                            mojibaked = word.encode(enc1).decode(enc2)
                            if mojibaked != word:
                                for trigram in get_trigrams(mojibaked):
                                    baked_freqs[(trigram, enc2, enc1)] += freq
                        except UnicodeError:
                            pass
                        try:
                            mojibaked = word.encode(enc2).decode(enc1)
                            if mojibaked != word:
                                for trigram in get_trigrams(mojibaked):
                                    baked_freqs[(trigram, enc1, enc2)] += freq
                        except UnicodeError:
                            pass


def build_trigrams():
    normal_freqs = defaultdict(float)
    baked_freqs = defaultdict(float)
    for language in LANGUAGE_ENCODINGS:
        print(language)
        add_language_trigrams(normal_freqs, baked_freqs, language)
    return normal_freqs, baked_freqs


normal_freqs, baked_freqs = build_trigrams()


EXCLUDE_CLASSES = {'LLL', 'Lll', 'lLl', 'llL', 'lll', 'AAA', 'Aaa', 'aAa', 'aaA', 'aaa', 'CCC', 'CCM', 'CMC', 'MCC', 'CMM', 'MCM', 'MMC'}


def exclude_trigram(trigram):
    if trigram[0] == trigram[1] and trigram[1] == trigram[2]:
        # Repeated letters might not be mojibake
        return True
    if set(trigram) & set("'’\x92\xa0\\|()[]{}.+*"):
        return True
    # Exclude trigrams that follow one of the patterns above of capital
    # and lowercase Latin letters (Ll), non-Latin letters (Aa), and
    # uncased characters and combining marks (CM), as long as they contain
    # no more than 2 accents or combining marks.
    #
    # Trigrams of this form are too likely to appear in normal,
    # unusually-spelled text, even if they don't appear in wordfreq's
    # vocabulary.
    return chars_to_classes(trigram) in EXCLUDE_CLASSES and len(normalize('NFD', trigram)) <= 5


def find_mojibake(normal_freqs, baked_freqs):
    mojibake_items = []
    for (trigram, encoder, decoder), freq in baked_freqs.items():
        if trigram not in normal_freqs and trigram.lower() not in normal_freqs and not exclude_trigram(trigram):
            tokenized = ' '.join(wordfreq.simple_tokenize(trigram))
            if len(tokenized) == len(trigram):
                mojibake_items.append((int(freq * 1e6), trigram, encoder, decoder))
    mojibake_items.sort(reverse=True)
    return mojibake_items[:20000]


DETECTING_CODE = """
import re

HEURISTIC_LOOKUP = {0}
HEURISTIC_RE = re.compile({1!r})
"""

def write_detector(found):
    mojidict = defaultdict(list)
    for freq, trigram, encoder, decoder in found:
        mojidict[trigram].append((encoder, decoder))
    regex_text = '|'.join(sorted(mojidict))
    with open('tricky_mojibake.py', 'w', encoding='utf-8') as out:
        mojidict_format = pprint.pformat(dict(mojidict))
        print(DETECTING_CODE.format(mojidict_format, regex_text), file=out)


if __name__ == '__main__':
    found = find_mojibake(normal_freqs, baked_freqs)
    write_detector(found)

