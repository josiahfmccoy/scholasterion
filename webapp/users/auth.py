import datetime
import flask
import jwt
import os
from functools import wraps
from werkzeug.security import check_password_hash
from db.services import UserService
from .. import api

__all__ = ['AuthManager', 'require_auth']


class AuthManager:
    @classmethod
    def get_token(cls, user):
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user.username
        }
        return jwt.encode(
            payload,
            os.getenv('SECRET_KEY'),
            algorithm='HS256'
        )

    @classmethod
    def decode_token(cls, auth_token):
        try:
            payload = jwt.decode(auth_token, os.getenv('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise ValueError('Expired Signature')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid Token')


def require_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = flask.request.headers.get('X-Access-Token')
        if not token:
            raise api.Exception('Unauthorized', 403)

        try:
            sub = AuthManager.decode_token(token)
            flask.current_user = UserService.get(username=sub)
        except Exception as e:
            raise api.Exception(str(e), 403)

        return f(*args, **kwargs)
    return decorator
