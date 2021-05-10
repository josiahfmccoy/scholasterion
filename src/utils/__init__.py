import string
import unicodedata
from .loggers import *

__all__ = ['norm_word', 'norm_accents', 'strip_accents', 'make_logger']


punctuation = ''.join([
    string.punctuation,
    '—',
    '·'
])


def norm_word(word):
    n = norm_accents(word.strip().lower().translate(
        str.maketrans(dict.fromkeys(punctuation))
    ))
    return n


def norm_accents(word):
    had_spaces = (' ' in word)
    n = unicodedata.normalize('NFC', word)
    if not had_spaces:
        n = n.replace(' ', '')
    return n


def strip_accents(word):
    separated = unicodedata.normalize('NFD', word)
    normed = ''.join([c for c in separated if not unicodedata.combining(c)])
    return normed
