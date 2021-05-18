from ..schema.lexemes.models import *
from .generic import GenericService

__all__ = ['WordService', 'LexemeService']


class WordService(GenericService):
    __model__ = Word


class LexemeService(GenericService):
    __model__ = Lexeme

    class Words(WordService):
        pass
