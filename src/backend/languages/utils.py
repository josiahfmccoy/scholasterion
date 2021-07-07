
__all__ = [
    'serializable_language'
]


def serializable_language(lang):
    s = {
        'id': lang.id,
        'iso_code': lang.iso_code,
        'name': lang.name
    }
    return s
