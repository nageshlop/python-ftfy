from __future__ import unicode_literals
import codecs

REPLACEMENT_CHAR = '\ufffd'

def make_sloppy_codec(encoding):
    decoding_list = []
    for byte in range(0x100):
        char = chr(byte).encode('latin-1').decode(encoding, errors='replace')
        if char == REPLACEMENT_CHAR:
            char = chr(byte)
        decoding_list.append(char)
    decoding_table = ''.join(decoding_list)
    encoding_table = codecs.charmap_build(decoding_table)

    class Codec(codecs.Codec):
        def encode(self,input,errors='strict'):
            return codecs.charmap_encode(input,errors,encoding_table)

        def decode(self,input,errors='strict'):
            return codecs.charmap_decode(input,errors,decoding_table)

    class IncrementalEncoder(codecs.IncrementalEncoder):
        def encode(self, input, final=False):
            return codecs.charmap_encode(input,self.errors,encoding_table)[0]

    class IncrementalDecoder(codecs.IncrementalDecoder):
        def decode(self, input, final=False):
            return codecs.charmap_decode(input,self.errors,decoding_table)[0]

    class StreamWriter(Codec,codecs.StreamWriter):
        pass

    class StreamReader(Codec,codecs.StreamReader):
        pass

    return codecs.CodecInfo(
        name='cp1252',
        encode=Codec().encode,
        decode=Codec().decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=StreamWriter,
    )

CODECS = {}
for codepage in range(1250, 1259):
    codec_info = make_sloppy_codec('windows-%s' % codepage)
    CODECS['sloppy%s' % codepage] = codec_info
