import numpy as np
import codecs
from ftfy.chardata import CHARMAPS, CHARMAP_ENCODINGS, possible_encoding
from ftfy.compatibility import PYTHON2

ENCODINGS = [
    'utf-8', 'big5+', 'gb18030', 'cp932', 'cp949', 'euc-jp'
] + CHARMAP_ENCODINGS
M = 511111  # a prime number
N = len(ENCODINGS)


def trigram_to_row(trigram):
    return (
        (trigram[0] << 15) +
        ((trigram[1] - 0x80) << 8) +
        trigram[2]
    )

def row_to_trigram(row):
    b0 = row >> 15
    b1 = ((row >> 8) % 0x80) + 0x80
    b2 = row % 0x100
    return bytes([b0, b1, b2])


def sloppy_encode(text, encoding):
    if encoding in CHARMAP_ENCODINGS:
        return text.translate(CHARMAPS[encoding]).encode('latin-1')
    else:
        return text.encode(encoding)

def sloppy_possible_encoding(text, encoding):
    if encoding in CHARMAP_ENCODINGS:
        return possible_encoding(text, encoding)
    else:
        try:
            text.encode(encoding)
            return True
        except UnicodeEncodeError:
            return False


def learn_matrix(datafile):
    matrix = np.ones((1 << 23, N), np.float32, order='F')
    count = 0
    for line in codecs.open(datafile, encoding='utf-8'):
        count += 1
        if count % 1000 == 0:
            print(count)
        if possible_encoding(line, 'ascii'):
            continue

        for i, encoding in enumerate(ENCODINGS):
            if sloppy_possible_encoding(line, encoding):
                linebytes = sloppy_encode(line, encoding)
                for pos in range(1, len(linebytes) - 1):
                    if linebytes[pos] >= 0x80:
                        trigram = linebytes[pos-1:pos+2]
                        assert len(trigram) == 3
                        row = trigram_to_row(trigram)
                        matrix[row, i] += 1

    norms = np.sum(matrix * matrix, axis=1)[:, np.newaxis]
    return matrix / norms

if __name__ == '__main__':
    matrix = learn_matrix('../../testdata/all.txt')
    np.save('classifier.npy', matrix)
