# coding: utf-8
from __future__ import unicode_literals
"""
The 'mojibakery' cooks up some relevant examples of mojibake in several
languages, from which we can learn a heuristic that detects certain subtle
forms of mojibake, especially those that map single bytes to other single
bytes.

Why do we use synthetic examples? Because there's no good test corpus of real
mojibake, and if there were one there would probably be mojibake in the
"correct" data too. Realistically, every sufficiently large data set that
hasn't been smashed to ASCII has unintended mojibake in it.

Also, when the answer 'False' is correct 99.8% of the time and false positives
are the worst case, the best thing a typical machine learning algorithm could
do is learn to always output 'False'.

Instead of relying on insufficiently-labeled real data, then, we will use
lists of common words (from the wordfreq package) to create examples of likely
mojibake. Trigrams that frequently appear in these examples and never appear in
clean text (with some added safeguards against weird typography) will be used
to detect mojibake.
"""

import wordfreq
from collections import defaultdict
from operator import itemgetter
import ftfy
from ftfy.chardata import chars_to_classes
from unicodedata import normalize
import re
import json
import pprint
import sys


LANGUAGE_ENCODINGS = {
    'ar': ['iso-8859-6', 'sloppy-windows-1256'],
    'de': ['macroman', 'iso-8859-2', 'cp437', 'cp850'],
    'el': ['sloppy-windows-1253'],
    'en': ['macroman', 'cp437', 'cp850'],
    'es': ['macroman', 'cp437', 'cp850'],
    'fr': ['macroman', 'cp437', 'cp850'],
    'id': ['macroman', 'cp437', 'cp850'],
    'ja': ['shift-jis', 'euc-jp'],
    'ko': ['euc-kr'],
    'ms': ['macroman', 'cp437'],
    'nl': ['macroman', 'cp437', 'cp850'],
    'pl': ['iso-8859-2', 'windows-1250'],
    'pt': ['macroman', 'cp437', 'cp850'],
    'ru': ['sloppy-windows-1251', 'koi8-r', 'iso-8859-5', 'cp866'],
    'sv': ['macroman', 'iso-8859-2', 'cp437', 'cp850'],
    'tr': ['macroman', 'cp850', 'iso-8859-9', 'sloppy-windows-1254'],
    #'zh': ['euc-cn', 'gbk', 'big5']
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

            for enc1 in COMMON_ENCODINGS + LANGUAGE_ENCODINGS[language]:
                for enc2 in COMMON_ENCODINGS + LANGUAGE_ENCODINGS[language]:
                    if enc1 != enc2 and (enc1 not in COMMON_ENCODINGS or enc2 not in COMMON_ENCODINGS):
                        try:
                            mojibaked = word.encode(enc1).decode(enc2)
                            if mojibaked != word:
                                for trigram in get_trigrams(mojibaked):
                                    baked_freqs[(trigram, enc2, enc1)] += freq
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
    return mojibake_items[:25000]


DETECTING_CODE = """
import re

HEURISTIC_LOOKUP = {0}
HEURISTIC_RE = re.compile({1!r})
"""

def write_detector(found):
    if sys.hexversion < 0x03020000 and not do_it_anyway:
        raise RuntimeError(
            "This function should be run in Python 3.2 or later."
        )
    mojidict = defaultdict(list)
    for freq, trigram, encoder, decoder in found:
        mojidict[trigram].append((encoder, decoder))
    regex_text = '|'.join(sorted(mojidict))
    with open('_heuristic.py', 'w', encoding='utf-8') as out:
        mojidict_format = pprint.pformat(dict(mojidict))
        print(DETECTING_CODE.format(mojidict_format, regex_text), file=out)


if __name__ == '__main__':
    found = find_mojibake(normal_freqs, baked_freqs)
    write_detector(found)

