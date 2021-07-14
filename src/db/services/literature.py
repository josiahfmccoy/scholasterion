from ..schema.literature.models import *
from .generic import GenericService

__all__ = ['DocumentService']


class DocumentService(GenericService):
    __model__ = Document
