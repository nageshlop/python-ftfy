import codecs
from encodings import normalize_encoding

_cache = {}


def search_function(encoding):
    if encoding in _cache:
        return _cache[encoding]

    norm_encoding = normalize_encoding(encoding).replace('_', '')
    codec = None
    if norm_encoding in ('utf8variants', 'utf8variant', 'utf8var'):
        from ftfy.bad_codecs.utf8_variants import CODEC_INFO
        codec = CODEC_INFO

    if codec is not None:
        _cache[encoding] = codec

    return codec


codecs.register(search_function)
