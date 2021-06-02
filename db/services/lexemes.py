from ..schema.lexemes.models import *
from .generic import GenericService

__all__ = ['TokenService', 'WordService', 'LexemeService']


class TokenService(GenericService):
    __model__ = Token


class WordService(GenericService):
    __model__ = Word


class LexemeService(GenericService):
    __model__ = Lexeme

    class Words(WordService):
        pass

    class Tokens(TokenService):
        pass
