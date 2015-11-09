"""
This file defines a general method for evaluating ftfy using data that arrives
in a stream. A concrete implementation of it is found in `twitter_tester.py`.
"""
from __future__ import print_function, unicode_literals
from ftfy import fix_text
from ftfy.fixes import fix_encoding, unescape_html
from ftfy.chardata import possible_encoding
import sys


class StreamTester:
    """
    Take in a sequence of texts, and show the ones that will be changed by
    ftfy. This will also periodically show updates, such as the proportion of
    texts that changed.
    """
    def __init__(self):
        self.num_fixed = 0
        self.count = 0

    def check_ftfy(self, text, encoding_only=True):
        """
        Given a single text input, check whether `ftfy.fix_text_encoding`
        would change it. If so, display the change.
        """
        self.count += 1
        text = unescape_html(text)
        if not possible_encoding(text, 'ascii'):
            if encoding_only:
                fixed = fix_encoding(text, cleverness=2)
            else:
                fixed = fix_text(text, uncurl_quotes=False, fix_character_width=False, cleverness=2)
            if text != fixed:
                # possibly filter common bots before printing
                print(u'\nText:\t{text!r}\nFixed:\t{fixed!r}\n'.format(
                    text=text, fixed=fixed
                ))
                self.num_fixed += 1

        # Print status updates once in a while
        if self.count % 100 == 0:
            print('.', end='', flush=True)
        if self.count % 10000 == 0:
            print('\n%d/%d fixed' % (self.num_fixed, self.count))


def main():
    """
    When run from the command line, this script runs on a saved text file,
    one line at a time. It uses the last value (presumed to be the actual text)
    of tab-separated lines.
    """
    if len(sys.argv) <= 1:
        print("Specify a filename containing the text to check.")
        sys.exit(0)
    tester = StreamTester()
    for line in open(sys.argv[1]):
        text = line.rstrip().split('\t')[-1]
        tester.check_ftfy(text)


if __name__ == '__main__':
    main()

