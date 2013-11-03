# Ways to do this classifier better:
# - train on cesu-8
# - do the hashing right away

import numpy as np
import codecs
from ftfy.chardata import possible_encoding
from ftfy.autodecode.classifier import ENCODINGS

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
            try:
                linebytes = line.encode(encoding)
                for pos in range(1, len(linebytes) - 1):
                    if linebytes[pos] >= 0x80:
                        trigram = linebytes[pos-1:pos+2]
                        assert len(trigram) == 3
                        row = trigram_to_row(trigram)
                        matrix[row, i] += 1
            except UnicodeEncodeError:
                pass

    norms = np.sum(matrix * matrix, axis=1)[:, np.newaxis]
    return matrix / norms

if __name__ == '__main__':
    matrix = learn_matrix('../../testdata/all.txt')
    np.save('data/_new_classifier.npy', matrix)
