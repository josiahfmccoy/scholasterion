from ..languages.utils import serializable_language

__all__ = [
    'serializable_word', 'serializable_lexeme'
]


def serializable_word(word):
    s = {
        'id': word.id,
        'form': word.form,
        'lexeme': serializable_lexeme(word.lexeme)
    }
    return s


def serializable_lexeme(lex):
    s = {
        'id': lex.id,
        'lemma': lex.lemma,
        'language': serializable_language(lex.language)
    }
    return s
