import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Collection', 'Document'
]


class Collection(Model):
    title = sa.Column(sa.Unicode(255), nullable=False)
    author = sa.Column(sa.Unicode())

    _long_title = sa.Column('long_title', sa.Unicode())

    @property
    def long_title(self):
        return self._long_title or self.title

    order = sa.Column(sa.Integer(), nullable=True)

    language_id = sa.Column(
        sa.Integer(), sa.ForeignKey('language.id'), nullable=False
    )
    language = sa.orm.relationship(
        'Language',
        backref=sa.orm.backref('documents', cascade='all, delete-orphan')
    )

    parent_id = sa.Column(
        sa.Integer(), sa.ForeignKey('collection.id'), nullable=True
    )
    parent = sa.orm.relationship(
        'Collection',
        remote_side='Collection.id',
        backref=sa.orm.backref('sections', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self.title}')"


class Document(Model):
    title = sa.Column(sa.Unicode(255), nullable=False)
    author = sa.Column(sa.Unicode())

    _long_title = sa.Column('long_title', sa.Unicode())

    @property
    def long_title(self):
        return self._long_title or self.title

    order = sa.Column(sa.Integer(), nullable=False)

    file_url = sa.Column(sa.Unicode(), nullable=False, unique=True)

    collection_id = sa.Column(
        sa.Integer(), sa.ForeignKey('collection.id'), nullable=False
    )
    collection = sa.orm.relationship(
        'Collection',
        backref=sa.orm.backref('documents', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f"{self.__class__.__qualname__}('{self.title}')"
