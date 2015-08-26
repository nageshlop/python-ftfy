# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ftfy import fix_text
from ftfy.fixes import fix_encoding_and_explain, apply_plan
from nose.tools import eq_


TEST_CASES = [
    ## These are excerpts from tweets actually seen on the public Twitter
    ## stream. Usernames and links have been removed.
    ("He's Justinâ¤", "He's Justin❤"),
    ("Le Schtroumpf Docteur conseille g√¢teaux et baies schtroumpfantes pour un r√©gime √©quilibr√©.",
     "Le Schtroumpf Docteur conseille gâteaux et baies schtroumpfantes pour un régime équilibré."),
    ("âœ” No problems", "✔ No problems"),
    ('4288×…', '4288×…'),
    ('RETWEET SE VOCÊ…', 'RETWEET SE VOCÊ…'),
    ('PARCE QUE SUR LEURS PLAQUES IL Y MARQUÉ…', 'PARCE QUE SUR LEURS PLAQUES IL Y MARQUÉ…'),
    ('TEM QUE SEGUIR, SDV SÓ…', 'TEM QUE SEGUIR, SDV SÓ…'),
    ('Join ZZAJÉ’s Official Fan List and receive news, events, and more!', "Join ZZAJÉ's Official Fan List and receive news, events, and more!"),
    ('L’épisode 8 est trop fou ouahh', "L'épisode 8 est trop fou ouahh"),
    ("РґРѕСЂРѕРіРµ РР·-РїРѕРґ #С„СѓС‚Р±РѕР»",
     "дороге Из-под #футбол"),
    ("\x84Handwerk bringt dich \xfcberall hin\x93: Von der YOU bis nach Monaco",
     '"Handwerk bringt dich überall hin": Von der YOU bis nach Monaco'),
    ("Hi guys í ½í¸", "Hi guys 😍"),
    ("hihi RT username: âºí ½í¸",
     "hihi RT username: ☺😘"),
    ("Beta Haber: HÄ±rsÄ±zÄ± BÃ¼yÃ¼ Korkuttu",
     "Beta Haber: Hırsızı Büyü Korkuttu"),
    ("Ôôô VIDA MINHA", "Ôôô VIDA MINHA"),
    ('[x]\xa0©', '[x]\xa0©'),
    ('2012—∞', '2012—∞'),
    ('Con il corpo e lo spirito ammaccato,\xa0è come se nel cuore avessi un vetro conficcato.',
     'Con il corpo e lo spirito ammaccato,\xa0è come se nel cuore avessi un vetro conficcato.'),
    ('Р С—РЎР‚Р С‘РЎРЏРЎвЂљР Р…Р С•РЎРѓРЎвЂљР С‘. РІСњВ¤', 'приятности. ❤'),
    ('Kayanya laptopku error deh, soalnya tiap mau ngetik deket-deket kamu font yg keluar selalu Times New Ã¢â‚¬Å“ RomanceÃ¢â‚¬Â.',
     'Kayanya laptopku error deh, soalnya tiap mau ngetik deket-deket kamu font yg keluar selalu Times New " Romance".'),
    ("``toda produzida pronta pra assa aí´´", "``toda produzida pronta pra assa aí´´"),
    ('HUHLL Õ…', 'HUHLL Õ…'),
    ('Iggy Pop (nÃƒÂ© Jim Osterberg)', 'Iggy Pop (né Jim Osterberg)'),
    ('eres mía, mía, mía, no te hagas la loca eso muy bien ya lo sabías',
     'eres mía, mía, mía, no te hagas la loca eso muy bien ya lo sabías'),
    ("Direzione Pd, ok âsenza modifiche all'Italicum.",
     "Direzione Pd, ok \"senza modifiche\" all'Italicum."),
    ('Engkau masih yg terindah, indah di dalam hatikuâ™«~',
     'Engkau masih yg terindah, indah di dalam hatiku♫~'),
    ('SENSЕ - Oleg Tsedryk', 'SENSЕ - Oleg Tsedryk'),   # this Е is a Ukrainian letter
    ('OK??:(   `¬´    ):', 'OK??:(   `¬´    ):'),
    ("selamat berpuasa sob (Ã\xa0Â¸â€¡'ÃŒâ‚¬Ã¢Å’Â£'ÃŒÂ\x81)Ã\xa0Â¸â€¡",
     "selamat berpuasa sob (ง'̀⌣'́)ง"),

    # Looks like UTF-8/Windows-1252, but it should be left alone
    ("SELKÄ\xa0EDELLÄ\xa0MAAHAN via @YouTube", "SELKÄ\xa0EDELLÄ\xa0MAAHAN via @YouTube"),

    # This one has two differently-broken layers of Windows-1252 <=> UTF-8,
    # and it's kind of amazing that we solve it.
    ('Arsenal v Wolfsburg: pre-season friendly â\x80â\x80\x9c live!',
     'Arsenal v Wolfsburg: pre-season friendly – live!'),

    # Test that we can mostly decode this face when the nonprintable
    # character \x9d is lost
    ('Ã¢â€\x9dâ€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€\x9dÅ½', '┒(⌣˛⌣)┎'),
    ('Ã¢â€�â€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€�Å½', '�(⌣˛⌣)�'),

    # You tried
    ('I just figured out how to tweet emojis! â\x9a½í\xa0½í¸\x80í\xa0½í¸\x81í\xa0½í¸\x82í\xa0½í¸\x86í\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8e',
     'I just figured out how to tweet emojis! ⚽😀😁😂😆😎😎😎😎'),

    # Fix single-byte encoding mixups
    ('Inglaterra: Es un lugar que nunca te aburrir‡s',
     'Inglaterra: Es un lugar que nunca te aburrirás'),
    ('Inundaciones y da\x96os materiales en Tamaulipas por lluvias',
     'Inundaciones y daños materiales en Tamaulipas por lluvias'),
    ('èíñòðóêöèÿ', 'инструкция'),

    # Examples from martinblech
    ('ÖÉËÁ ÌÅ - ÂÏÓÊÏÐÏÕËÏÓ - ×ÉÙÔÇÓ', 'ΦΙΛΑ ΜΕ - ΒΟΣΚΟΠΟΥΛΟΣ - ΧΙΩΤΗΣ'),
    ('ÑÅÊÐÅÒ - Áåñïå÷íûé Åçäîê - 0:00', 'СЕКРЕТ - Беспечный Ездок - 0:00'),
    ('¼Ò¸®¿¤ - »ç¶ûÇÏ´Â ÀÚ¿©', '소리엘 - 사랑하는 자여'),

    # Windows-1252/EUC-JP mojibake
    ('49Ç¯Á°½Ð¾ì¡¢Ê¡¸¶¤µ¤ó¤â´î¤Ó Åìµþ¸ÞÎØ ¡Ê¤ï¤«¤ä¤Þ¿·Êó¡Ë',
     '49年前出場、福原さんも喜び 東京五輪 (わかやま新報)'),

    # Latin-1/Shift-JIS mojibake
    ('\x83o\x83{\x82¿\x82á\x82ñ\x83l\x83b\x83g\x83j\x83\x85\x81[\x83X',
     'バボちゃんネットニュース'),

    # ISO-8859-1(?) / cp437 mojibake on top of Romanized Urdu leetspeak.
    # This is such a crazy solution that I won't even mind if it regresses.
    ('""" JUMMA """"    ,M\x97B\x84R\x84K ,   " H\x94"AP"K\x94 D\x97\x84 h\x84i \x8ds M\x97b\x84r\x84k D\x8dn k S\x84dq\x8a A\x84p k\x8d H\x84r p\x84r\x8ash\x84n\x8d A\x97r H\x84r M\x97sib\x84t d\x94\x94r H\x94 J\x84y\x8a    =AAMEEn=',
     '""" JUMMA """"    ,MùBäRäK ,   " Hö"AP"Kö Dùä häi ìs Mùbäräk Dìn k Sädqè Aäp kì Här pärèshänì Aùr Här Mùsibät döör Hö Jäyè    =AAMEEn='),

    # Only fix character width; this looks like Shift-JIS/EUC-JP mojibake
    # but isn't
    ('(|| * m *)ｳ､ｳｯﾌﾟ･･', '(|| * m *)ウ、ウップ・・'),

    ## Current false positives:
    #('Feijoada do Rio Othon Palace no Bossa Café\x80\x80', 'Feijoada do Rio Othon Palace no Bossa Café\x80\x80')
    #("├┤a┼┐a┼┐a┼┐a┼┐a", "├┤a┼┐a┼┐a┼┐a┼┐a"),
    #("ESSE CARA AI QUEM É¿", "ESSE CARA AI QUEM É¿"),
    #("``hogwarts nao existe, voce nao vai pegar o trem pra lá´´", "``hogwarts nao existe, voce nao vai pegar o trem pra lá´´"),
    #('P I R Ê™', 'P I R Ê™),
    #('WELCΘME HΘME THETAS!', 'WELCΘME HΘME THETAS!'),

    ## This kind of tweet can't be fixed without a full-blown encoding detector.
    #("Deja dos heridos hundimiento de barco tur\x92stico en Acapulco.",
    # "Deja dos heridos hundimiento de barco turístico en Acapulco."),

    ## The heuristics aren't confident enough to fix this text and its weird encoding.
    #("Blog Traffic Tip 2 вЂ“ Broadcast Email Your Blog",
    # "Blog Traffic Tip 2 – Broadcast Email Your Blog"),

    ## Can't fix this because we're cautious about false positives involving \xa0.
    #('CÃ\xa0nan nan GÃ\xa0idheal', 'Cànan nan Gàidheal'),
]


def test_real_tweets():
    """
    Test with text actually found on Twitter.

    I collected these test cases by listening to the Twitter streaming API for
    a million or so tweets, picking out examples with high weirdness according
    to ftfy version 2, and seeing what ftfy decoded them to. There are some
    impressive things that can happen to text, even in an ecosystem that is
    supposedly entirely UTF-8.

    The tweets that appear in TEST_CASES are the most interesting examples of
    these, with some trickiness of how to decode them into the actually intended
    text.
    """
    for orig, target in TEST_CASES:
        # make sure that the fix_encoding step outputs a plan that we can
        # successfully run to reproduce its result
        encoding_fix, plan = fix_encoding_and_explain(orig)
        eq_(apply_plan(orig, plan), encoding_fix)

        # make sure we can decode the text as intended
        eq_(fix_text(orig), target)

        # make sure we can decode as intended even with an extra layer of badness
        extra_bad = orig.encode('utf-8').decode('latin-1')
        eq_(fix_text(extra_bad), target)
