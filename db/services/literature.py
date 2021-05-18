from ..schema.literature.models import *
from .generic import GenericService

__all__ = ['TextService', 'VolumeService']


class VolumeService(GenericService):
    __model__ = Volume


class TextService(GenericService):
    __model__ = Text

    class Volumes(VolumeService):
        pass
