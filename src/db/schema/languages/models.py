import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Language'
]


class Language(Model):
    iso_code = sa.Column(sa.Unicode(120), nullable=False, unique=True)
    name = sa.Column(sa.Unicode(), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.iso_code}, '{self.name}')"
