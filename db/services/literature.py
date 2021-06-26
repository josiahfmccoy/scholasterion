from ..schema.literature.models import *
from .generic import GenericService

__all__ = ['CollectionService', 'DocumentService']


class DocumentService(GenericService):
    __model__ = Document


class CollectionService(GenericService):
    __model__ = Collection

    class Documents(DocumentService):
        pass
