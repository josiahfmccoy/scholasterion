import sqlalchemy as sa
from werkzeug.security import generate_password_hash
from ..utils.base import Model


__all__ = [
    'User'
]


class User(Model):
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    username = sa.Column(sa.Unicode(24), unique=True, nullable=False)

    _password = sa.Column('password', sa.String(255), nullable=False)

    is_admin = sa.Column(sa.Boolean(), nullable=False, default=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value, method='sha256')

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.email})"
