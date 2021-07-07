import requests
from flask import current_app
from lxml import etree, html
from ...db.services import LexemeService
from ..languages.utils import serializable_language

__all__ = [
    'serializable_token', 'serializable_word', 'serializable_lexeme',
    'get_token', 'parse_loegion'
]

ALLOW_AUTOLOAD = False


def serializable_token(token):
    if not token:
        return None
    s = {
        'identifier': token.identifier,
        'form': token.form,
        'gloss': token.gloss,
        'words': [serializable_word(w) for w in token.words]
    }
    return s


def serializable_word(word):
    if not word:
        return None
    s = {
        'id': word.id,
        'form': word.form,
        'parsing': word.parsing,
        'lexeme': serializable_lexeme(word.lexeme)
    }
    return s


def serializable_lexeme(lex):
    if not lex:
        return None
    s = {
        'id': lex.id,
        'lemma': lex.lemma,
        'gloss': lex.gloss,
        'language': serializable_language(lex.language)
    }
    return s


def get_token(document, identifier):
    fname = document.file_url
    parser = etree.XMLParser(remove_blank_text=True)
    if not fname.startswith('http'):
        fname = current_app.static_path('data/' + fname)
        root = etree.parse(fname, parser)
    else:
        r = requests.get(fname)
        root = html.fromstring(r.text)

    t = root.xpath(f'//*[@id="{identifier}"]')
    if not t:
        return None
    return t[0].text


def parse_loegion(document, identifier):
    from ...workbench.parsing.loegion import LoegionParser, norm_word
    t = get_token(document, identifier)

    lang = document.collection.language

    words = {}
    existing = LexemeService.Tokens.get_all(form=t)
    for tok in existing:
        for w in tok.words:
            words[w.id] = w

    word_form = norm_word(t)
    existing = LexemeService.Words.get_all(form=word_form)
    for w in existing:
        words[w.id] = w

    words = list(words.values())

    if not words:
        if not ALLOW_AUTOLOAD:
            return None

        parsed = LoegionParser().parse_word(t)
        for lem, parsings in parsed.items():
            lex = LexemeService.get_or_create(
                lemma=lem,
                language_id=lang.id
            )

            if not lex.gloss:
                gloss = gloss_loegion(lex.lemma)
                if gloss:
                    lex.gloss = gloss

            w = LexemeService.Words.get_or_create(
                form=word_form,
                lexeme_id=lex.id
            )
            words.append(w)

    token = LexemeService.Tokens.get_or_create(
        identifier=identifier,
        form=t,
        document_id=document.id,
        no_commit=True
    )
    token.words = words

    LexemeService.commit()

    return token


def gloss_loegion(lemma):
    from ...workbench.glossing.loegion import LoegionGlosser

    gloss = LoegionGlosser().gloss(lemma)
    return gloss
