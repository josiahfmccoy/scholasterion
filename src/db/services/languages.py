from ..schema.languages.models import *
from .generic import GenericService

__all__ = ['LanguageService']


class LanguageService(GenericService):
    __model__ = Language
