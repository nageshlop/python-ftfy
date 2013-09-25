from __future__ import unicode_literals
from ftfy.compatibility import PYTHON2, bytes_to_ints, unichr
from encodings.utf_8 import IncrementalDecoder as UTF8IncrementalDecoder
import re

CESU8_RE = re.compile(b'\xed[\xa0-\xaf][\x80-\xbf]\xed[\xb0-\xbf][\x80-\xbf]')


class JavaCESU8Decoder(UTF8IncrementalDecoder):
    def _buffer_decode(self, input, errors, final):
        sup = UTF8IncrementalDecoder._buffer_decode
        cutoff1 = input.find(b'\xed')
        cutoff2 = input.find(b'\xc0')
        if cutoff1 != -1 and cutoff2 != -1:
            cutoff = min(cutoff1, cutoff2)
        elif cutoff1 != -1:
            cutoff = cutoff1
        elif cutoff2 != -1:
            cutoff = cutoff2
        else:
            return sup(input, errors, final)

        if input.startswith(b'\xc0'):
            return self._buffer_decode_null(sup, input, errors, final)
        elif input.startswith(b'\xed'):
            return self._buffer_decode_surrogates(sup, input, errors, final)
        else:
            # at this point, we know cutoff > 0
            return sup(input[:cutoff], errors, False)

    @staticmethod
    def _buffer_decode_null(sup, input, errors, final):
        nextchar = input[1:2]
        if nextchar == '':
            return '', 0
        elif nextchar == b'\x80':
            return '\u0000', 2
        else:
            return sup('\xc0', errors, True)

    @staticmethod
    def _buffer_decode_surrogates(sup, input, errors, final):
        """
        When we have improperly encoded surrogates, we can still see the
        bits that they were meant to represent.
        
        The surrogates were meant to encode a 20-bit number, to which we
        add 0x10000 to get a codepoint. That 20-bit number now appears in
        this form:
        
          11101101 1010abcd 10efghij 11101101 1011klmn 10opqrst
        
        The CESU8_RE above matches byte sequences of this form. Then we need
        to extract the bits and assemble a codepoint number from them.
        """
        if len(input) < 6:
            if final:
                return sup(input, errors, True)
            else:
                return '', 0
        else:
            if CESU8_RE.match(input):
                bytenums = bytes_to_ints(input[:6])
                codepoint = (
                    ((bytenums[1] & 0x0f) << 16) +
                    ((bytenums[2] & 0x3f) << 10) +
                    ((bytenums[4] & 0x0f) << 6) +
                    (bytenums[5] & 0x3f) +
                    0x10000
                )
                return unichr(codepoint), 6
            else:
                return sup(input[:3], errors, False)
