import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Document'
]


class Document(Model):
    title = sa.Column(sa.Unicode(255), nullable=False)
    author = sa.Column(sa.Unicode())

    file_url = sa.Column(sa.Unicode(), nullable=False, unique=True)

    language_id = sa.Column(
        sa.Integer(), sa.ForeignKey('language.id'), nullable=False
    )
    language = sa.orm.relationship(
        'Language',
        backref=sa.orm.backref('documents', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self.title}')"
