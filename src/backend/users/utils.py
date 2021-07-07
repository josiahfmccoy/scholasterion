
__all__ = [
    'serializable_user'
]


def serializable_user(user):
    if not user:
        return None
    s = {
        'email': user.email,
        'username': user.username
    }
    return s
