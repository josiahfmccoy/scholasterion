import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Token', 'Word', 'Lexeme'
]


token_words = sa.Table(
    'token_words', Model.metadata,
    sa.Column('token_id', sa.Integer(), sa.ForeignKey('token.id'), nullable=False),
    sa.Column('word_id', sa.Integer(), sa.ForeignKey('word.id'), nullable=False)
)


class Token(Model):
    identifier = sa.Column(sa.Unicode(60), nullable=False)
    gloss = sa.Column(sa.Unicode(), nullable=True)

    document_id = sa.Column(
        sa.Integer(), sa.ForeignKey('document.id'), nullable=True
    )
    document = sa.orm.relationship(
        'Document', backref=sa.orm.backref('tokens', cascade='all, delete-orphan')
    )

    words = sa.orm.relationship(
        'Word', secondary=token_words, backref=sa.orm.backref('tokens')
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'identifier', 'document_id'
        ),
    )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}"
            f"('{self.document.title}', '{self.identifier}')"
        )


class Word(Model):
    form = sa.Column(sa.Unicode(), nullable=False)
    parsing = sa.Column(sa.Unicode(255), nullable=True)
    gloss = sa.Column(sa.Unicode(), nullable=True)

    lexeme_id = sa.Column(
        sa.Integer(), sa.ForeignKey('lexeme.id'), nullable=True
    )
    lexeme = sa.orm.relationship(
        'Lexeme', backref=sa.orm.backref('forms', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}('{self.form}')"
        )


class Lexeme(Model):
    lemma = sa.Column(sa.Unicode(), nullable=False)
    gloss = sa.Column(sa.Unicode(), nullable=True)

    subscript = sa.Column(sa.Integer(), nullable=True)

    language_id = sa.Column(
        sa.Integer(), sa.ForeignKey('language.id'), nullable=True
    )
    language = sa.orm.relationship(
        'Language',
        backref=sa.orm.backref('lexemes', cascade='all, delete-orphan')
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'lemma', 'gloss', 'language_id'
        ),
    )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}('{self.lemma}')"
        )
