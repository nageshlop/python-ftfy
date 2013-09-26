My notes on encodings, which eventually may turn into documentation.
Keep in mind that the software being documented doesn't exist yet.

Encodings
=========

Level 0 (fundamental)
---------------------
ASCII takes priority over all other encodings. Any text that is pure 7-bit
ASCII will never be interpreted as anything else.

This means that autodecode will not decode 7-bit encodings such as HZ, UTF-7,
or MIME quoted-printable, and does not intend to.

Level 1 (preferred)
-------------------
These encodings can easily be distinguished with each other in all cases, and
are in common use.

If you use ``autodecode(bytestring, level=1)``, you will get one of these three
encodings (or ASCII).  Text that isn't in any of the encodings below will
default to UTF-8, using replacement characters for the parts that don't decode.

UTF-8
`````
UTF-8 is the current standard for text. Most Web sites and Web APIs use it.
It's compatible with ASCII.

You should use UTF-8 for text in any language, and generally assume other
people are using it and expecting it, unless you find out otherwise.

The rest of this page supposes that you found out otherwise.

UTF-16 (with a byte order mark)
```````````````````````````````
UTF-16 is the in-memory format of Unicode for many programming languages, so it
sometimes saves some programming effort to export text in it. It's incompatible
with ASCII, which makes it incompatible with many protocols, and the large
number of null bytes make it incompatible with many data structures.

Microsoft Office often calls UTF-16 "Unicode", and provides it as the only
option for arbitrary Unicode text.

UTF-16 should include a byte order mark, and to send UTF-16 text without one is
just mean. Because any sequence of bytes could technically be UTF-16, in either
of two completely different byte orders, the BOM is often the only solid
indication that we should try decoding as UTF-16. autodecode will only decode
UTF-16 when it begins with a BOM.

CESU-8
``````
CESU-8 is a very popular mistake.

It's what happens when you take the 16-bit values in UTF-16 and encode them
each as UTF-8, without decoding them first. It is equivalent to UTF-8 except on
astral characters, such as emoji. Those turn into incorrect six-byte sequences
that require multiple decoding steps.

Python 3's standard library will not decode CESU-8. autodecode therefore
adds a codec for it.

CESU-8 continues to be popularized by Java and MySQL. Analyzing mojibake on
Twitter shows that CESU-8 may be more common than real UTF-8. This, and the
fact that detecting UTF-8 does most of the work to detect CESU-8, is why it's a
level 1 encoding.

Level 2 (Common)
----------------
These encodings are less preferable than Unicode standards, but are still
extremely common.

If you use ``autodecode(bytestring, level=2)``, you will get one of these
encodings. Many of these encodings can decode anything, but the one you are
most likely to get for arbitrary bytes is windows-1252.

Latin-1 and Windows-1252
````````````````````````
These encodings are *everywhere*. If a programmer thinks there are only 256
possible characters, the characters that they think are possible are probably
Windows-1252.

Latin-1 (more formally but less commonly called ISO-8859-1) is an ISO standard
for encoding Western European text with one byte per character. Standards were
made to be broken, so Windows 3.1 added 27 more characters in positions that
are assigned to terribly obsolete control characters in Latin-1.

Latin-1 is now the simplest encoding, because it is represented by the first
256 code points of Unicode. However, most software assumes you couldn't
possibly mean to use the C1 control characters in Latin-1, and that assumption
is reasonable, so these encodings are widely considered equivalent. Web
browsers replace C1 control characters with Windows-1252 characters whenever
possible.

So the actual commonly used encoding is an encoding that contains 27 characters
from Windows-1252, five useless characters from Latin-1, and the other 224 that
they agree on.  We'll call this "Sloppy 1252", which autodecode implements as
the ``sloppy-1252`` codec. Other Windows-style encodings will have similar
Python codecs, such as ``sloppy-1251``.


Windows-1251 (Cyrillic)
```````````````````````
Windows-1251 is the most popular single-byte encoding of Cyrillic. In my
experience, it is commonly used by Russian spambots, but that's evidence that
it's used for other reasons as well. It's also used in the UDHR corpus.


GB18030 (Simplified Chinese)
````````````````````````````
Mainland China's newest official encoding. Like UTF-8, it can encode all of
Unicode, but it favors Chinese characters (including ones in the Supplementary
Ideographic Plane) with shorter encodings than characters in other languages.

Chinese standards prefer it over UTF-8, unfortunately, and mapping it to
Unicode generally involves an ugly lookup table.

Big5 (Traditional Chinese)
``````````````````````````
Commonly used in Taiwan and Hong Kong.

Wikipedia dithers a lot about what single-byte characters mean in Big5. In
practice, they are ASCII.


Shift JIS and cp932 (Japanese)
``````````````````````````````
Commonly used in Japan. Many Japanese programmers explicitly prefer Shift-JIS
to UTF-8.

You guessed it: Windows has a version with more characters that's commonly
confused with the standard. Everything that's valid Shift-JIS is also valid
cp932 (also known as Windows-31J).


EUC-KR and Windows-949 (Korean)
```````````````````````````````
EUC-KR is the widely used legacy encoding of Korean, and Windows's extension of
it is called Windows-949.


Level 3 (Alternative)
---------------------
These encodings are both deprecated in favor of Unicode *and* less common than
another encoding for the same language. This does not, of course, stop them
from being used. If you have a need for autodecode, you probably do need to
detect them.


EUC-JP (Japanese)
`````````````````
Given the popularity of Shift JIS, I was surprised that EUC-JP sees any
widespread use. However, it turns out to be the encoding preferred by Japanese
UNIX utilities (even now), where plain text matters a lot.


EUC-CN (Simplified Chinese)
```````````````````````````
A relatively common encoding of mainland China's former standard character set,
GB2312, plus ASCII, preferred by UNIX utilities.


MacRoman (Mac OS Roman)
```````````````````````

A single-byte, Western European encoding with a different layout from
Windows-1252. Mac OS Classic used this as its default encoding. Microsoft
Office thinks Macs *still* use this encoding, although that's not true; Mac OS
X has always used UTF-8.

This encoding is still common in the wild in 2013, and is a common source of
mojibake, particularly in Spanish text. It's been going strong for decades,
because it's also the second most common encoding in the 20 Newsgroups corpus.


Level 4 (Declining)
-------------------
Most people would expect you to use UTF-8 instead of these encodings, but you
can still find them in old software or old documents. If your input is modern,
you can stop before this level.


cp437 (code page 437)
`````````````````````

This encoding is hard-coded into the display hardware of most PC motherboards.
When most people used DOS, most people used cp437. It's the most common
encoding in the 20 Newsgroups corpus, and Microsoft Office will still export
text in it if you ask for "DOS text".

Some Twitter users who tweet in romanized Hindi are still using cp437, except
it's reinterpreted as Latin-1 and encoded as UTF-8. I have no idea what their
computers are doing to make this show up correctly.


Windows-1250 and ISO-8859-2 (Eastern European)
``````````````````````````````````````````````
The Eastern European answers to Windows-1252 and Latin-1.  However,
Windows-1250 and ISO-8859-2 are not completely compatible with each other.

The name "Latin-2" is used for both of these encodings, plus at least one
other. The UDHR corpus in particular uses Windows-1250 and calls it "Latin-2".

I've never seen real ISO-8859-2 myself, but Wikipedia tells me that there's a
common confusion between it and Windows-1250. I'll believe it, even though
Wikipedia often says encodings are common when they aren't.

In the last "official" version of chardet, multiple bugs conspired to
misclassify many single-byte encodings as ISO-8859-2. By Bayesian inference, if
you are also checking your text with chardet, and it tells you it's ISO-8859-2,
it is overwhelmingly likely that something has gone wrong.


Windows-1253 (Greek)
````````````````````
Windows-1253 is the corresponding Windows encoding for Greek. It is used in
the UDHR corpus.

ISO-8859-7 is a very similar encoding, but it is probably always confused for
Windows-1253 in practice.


Windows-1254 and Latin-5 (Turkish)
``````````````````````````````````
These largely compatible encodings are used to write Turkish, and appear in the
UDHR corpus.


Windows-1255 and ISO-8859-8 (Hebrew)
````````````````````````````````````
These largely compatible encodings are used to write Hebrew, and appear in the
UDHR corpus.

autodecode will not detect whether the Hebrew text is written in visual order
(where every line is spelled backwards and displayed from left to right).
You should probably assume it is in logical, right-to-left order.


Windows-1256 (Arabic)
`````````````````````
This encoding is used to write Arabic, and appears in the UDHR corpus.

autodecode will not detect whether the Arabic text is written in visual order
(where every line is spelled backwards and displayed from left to right).
You should probably assume it is in logical, right-to-left order.

ISO-8859-6 is not compatible with it.


Windows-1257 (Baltic)
`````````````````````

Windows-1258 (Vietnamese)
`````````````````````````

ISO-8859-11 (Thai)
``````````````````

Other encodings to consider
```````````````````````````

- ISO-8859-6 (Arabic)
- ISO-8859-7 (Greek)
- ISO-8859-10 (Baltic)
- ISO-8859-16 (Romanian)
- KOI8-R
- KOI8-U

Encodings to probably not consider
----------------------------------

- ISO-8859-3 (Maltese, obsolete Turkish, Esperanto?)
- ISO-8859-4 (also Baltic)
- ISO-8859-5 (Cyrillic, generally ignored)
- ISO-8859-13 (still Baltic)
- ISO-8859-14 (Celtic)
- EBCDIC


Non-supported encodings
=======================

autodecode does not aim to decode:

- Any 7-bit encoding, including UTF-7, the original JIS, HZ, MIME
  quoted-printable, and any of the variants of ISO 2022. Even if they might
  still be found, the risk to reward ratio of messing with pure ASCII text
  is too high.

- UCS-4. A four-byte encoding where most bytes are null, and one byte in four
  is completely useless. It's intended and used as a byte-aligned, completely
  general encoding for in-memory Unicode strings, but nobody really transmits
  text in UCS-4. If anyone had a reason to put a byte-order mark on it, it
  would likely look like a UTF-16 BOM.

- ISO-8859-15, which is too easily confused with Windows-1252, which is
  millions of times more common and incompatible.

- cp863 (Quebecois weirdified cp437)
- Mazovia (Polish)
- Kamenický, cp895 (Czech)
- cp737 (Greek)
- cp866 (Cyrillic)
- cp850 (Brazilian, Western European)
- cp857 (Turkish)
- MacCyrillic
- MacArabic
- MacCentralEurRoman
- MacUkrainian

