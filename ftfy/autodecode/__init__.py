# notes on the relationship between ftfy and autodecode:
# autodecode contains a big huge classifier. It shouldn't really be a
# dependency.
#
# Thus autodecode should be its own repository.
#
# ftfy.bad_codecs didn't even turn out to have much to do with autodecode.
# (We could benefit from a full ftfy.bad_codecs.cesu8.)
#
# Learn condensed heuristics from autodecode for 1252 <-> MacRoman mojibake,
# and include their results in a future version of ftfy.

from ftfy.chardata import possible_encoding


def try_multibyte_encoding(bstring, encoding, weight=1.):
    try:
        decoded = bstring.decode(encoding)
        return [(decoded, encoding, weight)]
    except UnicodeDecodeError:
        return []


def decode_level0(bstring):
    return try_multibyte_encoding(bstring, 'ascii')


def decode_level1(bstring):
    decodings = decode_level0(bstring)
    if bstring.startswith(b'\xfe\xff') or bstring.startswith(b'\xff\xfe'):
        decodings += try_multibyte_encoding(bstring, 'utf-16')
    else:
        fixed = fix_java_encoding(bstring)
        if fixed != bstring:
            possible_decoding = try_multibyte_encoding(bstring, 'utf-8')
            if possible_decoding:
                decoded, encoding, weight = possible_decoding[0]
                decodings.append((decoded, 'cesu-8', 1.))
        else:
            decodings += try_multibyte_encoding(bstring, 'utf-8')
    return decodings



