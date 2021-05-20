import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Text', 'Volume'
]


class Text(Model):
    name = sa.Column(sa.Unicode(), nullable=False)

    language_id = sa.Column(
        sa.Integer(), sa.ForeignKey('language.id'), nullable=False
    )
    language = sa.orm.relationship(
        'Language',
        backref=sa.orm.backref('texts', cascade='all, delete-orphan')
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'name', 'language_id'
        ),
    )

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self.name}')"


class Volume(Model):
    order = sa.Column(sa.Integer(), nullable=False)
    name = sa.Column(sa.Unicode(), nullable=False)
    file_url = sa.Column(sa.Unicode(), nullable=False, unique=True)

    text_id = sa.Column(
        sa.Integer(), sa.ForeignKey('text.id'), nullable=False
    )
    text = sa.orm.relationship(
        'Text',
        backref=sa.orm.backref('volumes', cascade='all, delete-orphan')
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'name', 'text_id'
        ),
    )

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self.text.name}', '{self.file_url}')"
