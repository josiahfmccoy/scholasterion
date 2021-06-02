import datetime
import jwt
import os
import sqlalchemy as sa
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
        self._password = value

    def get_auth_token(self):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': self.username
        }
        return jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )

    @classmethod
    def decode_auth_token(cls, auth_token):
        try:
            payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Expired Signature')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid Token')

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.email})"
