import datetime
import jwt
import os
from flask import request
from functools import wraps
from werkzeug.security import check_password_hash
from ...db.services import UserService
from .. import api

__all__ = ['AuthManager', 'require_auth']


class AuthManager:
    @classmethod
    def get_token(cls, user):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow(),
            'sub': user.username
        }
        token = jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )
        return token

    @classmethod
    def decode_token(cls, auth_token):
        try:
            payload = jwt.decode(
                auth_token,
                os.getenv('SECRET_KEY'),
                algorithms='HS256'
            )
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Expired Signature')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid Token')

    @classmethod
    def check_token(cls, auth_token):
        sub = cls.decode_token(auth_token)
        current_user = UserService.get(username=sub)
        if not current_user:
            raise ValueError(f'Unknown User: {sub}')
        return current_user

    @classmethod
    def login(cls, auth):
        if not auth or not auth.username or not auth.password:
            raise ValueError('Invalid Login')

        u = UserService.get(username=auth.username)
        if not u:
            u = UserService.get(email=auth.username)
        if not u:
            raise ValueError(f'Unknown User: {auth.username}')

        if check_password_hash(u.password, auth.password):
            return u


def require_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('X-Access-Token')
        if not token:
            raise api.Exception('Unauthorized', 401)

        try:
            current_user = AuthManager.check_token(token)
        except Exception as e:
            raise api.Exception(str(e), 401)

        return f(current_user, *args, **kwargs)
    return decorator
