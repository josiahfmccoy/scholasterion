from flask import request, session
from ...db.services import UserService
from .. import api
from .auth import *
from .utils import *


user_api = api.Blueprint('user_api', __name__)


@user_api.route('/api/user/login', methods=['POST'])
def login():
    try:
        if session.get('current_user'):
            current_user = UserService.get(session['current_user'])
        else:
            current_user = AuthManager.login(request.authorization)
        token = AuthManager.get_token(current_user)
        session['current_user'] = current_user.id
    except ValueError:
        raise api.Exception('Invalid Login', 401)
    return api.Result({'user': serializable_user(current_user), 'token': token})


@user_api.route('/api/user/logout', methods=['GET', 'POST'])
def logout():
    session['current_user'] = None
    return api.Result({'user': None})


@user_api.route('/api/user/check-status', methods=['GET'])
def check_status():
    current_user = UserService.get(session.get('current_user'))
    if current_user:
        token = AuthManager.get_token(current_user)
    else:
        token = None
    return api.Result({'user': serializable_user(current_user), 'token': token})
