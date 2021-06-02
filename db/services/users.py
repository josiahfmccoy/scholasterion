from ..schema.users.models import *
from .generic import GenericService

__all__ = ['UserService']


class UserService(GenericService):
    __model__ = User
