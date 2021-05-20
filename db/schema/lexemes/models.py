import sqlalchemy as sa
from ..utils.base import Model


__all__ = [
    'Word', 'Lexeme'
]


class Word(Model):
    form = sa.Column(sa.Unicode(), nullable=False)
    parsing = sa.Column(sa.Unicode(255), nullable=True)

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

    language_id = sa.Column(
        sa.Integer(), sa.ForeignKey('language.id'), nullable=True
    )
    language = sa.orm.relationship(
        'Language',
        backref=sa.orm.backref('lexemes', cascade='all, delete-orphan')
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'lemma', 'language_id'
        ),
    )

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}('{self.lemma}')"
        )
