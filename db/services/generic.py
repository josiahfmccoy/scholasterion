import os
from ..schema.utils.engine import DataBase

__all__ = ['db', 'GenericService', 'PermissionsMixin']


db_path = os.getenv('DATABASE_URI')
db = DataBase(db_path)


def make_key(**opts):
    key = '-'.join([
        f'{k}={v}'
        for k, v in dict(opts).items()
    ])
    return key


# Caching is currently disabled; too buggy.
# If this ends up being inefficient
# we should return to caching and fix it
class ServiceMetaClass(type):
    @property
    def db(cls):
        return db

    def cache(cls, key, value):
        try:
            cls.__cache
        except AttributeError:
            cls.__cache = {}
        cls.__cache[key] = value

    def cached(cls, key):
        try:
            cls.__cache
        except AttributeError:
            cls.__cache = {}
        # Using 'get' instead of 'pop' here would enable caching
        return cls.__cache.pop(key, None)

    def clear_cache(cls):
        cls.__cache = {}


class GenericService(metaclass=ServiceMetaClass):
    __model__ = None
    __unique_on__ = []

    auto_commit = True

    @classmethod
    def commit(cls):
        cls.clear_cache()
        cls.db.session.commit()

    @classmethod
    def rollback(cls):
        cls.clear_cache()
        cls.db.session.rollback()

    @classmethod
    def create(cls, *, no_commit=False, check_unique=True, **kwargs):
        opts = dict(kwargs)

        for k in list(opts):
            opt = opts.pop(k)
            if hasattr(opt, 'id') and hasattr(cls.__model__, f'{k}_id'):
                opts[f'{k}_id'] = opt.id
            else:
                opts[k] = opt

        if check_unique and cls.__unique_on__:
            check = {k: opts.get(k) for k in cls.__unique_on__}
            existing_term = cls.get(**check)

            if existing_term:
                for k, v in kwargs.items():
                    if hasattr(existing_term, k):
                        setattr(existing_term, k, v)
                cls.db.session.add(existing_term)
                if not no_commit and cls.auto_commit:
                    cls.commit()
                return existing_term

        with cls.db.session.no_autoflush:
            model = cls.__model__(**opts)
            cls.db.session.add(model)
            cls.cache(make_key(**opts), model)

        if not no_commit and cls.auto_commit:
            cls.commit()
        return model

    @classmethod
    def get_all(cls, **kwargs):
        key = make_key(**kwargs)
        if not cls.cached(key):
            with cls.db.session.no_autoflush:
                model_query = cls.db.session.query(cls.__model__)
                if kwargs:
                    model_query = model_query.filter_by(**kwargs)
                models = model_query.all()
                cls.cache(key, models)
        ret = cls.cached(key) or []

        if isinstance(ret, cls.__model__):
            ret = [ret]

        with cls.db.session.no_autoflush:
            ret = [
                x if (x in cls.db.session) else cls.db.session.merge(x)
                for x in ret
            ]
        return ret

    @classmethod
    def get(cls, model_id=None, **kwargs):
        ret = None
        query_options = kwargs.pop('query_options', None)
        if model_id is not None:
            if not isinstance(model_id, int):
                raise TypeError(
                    '"model_id" must be of type int,'
                    f' not {model_id.__class__.__name__}'
                )
            if model_id > 0:
                if not cls.cached(model_id):
                    with cls.db.session.no_autoflush:
                        q = cls.db.session.query(cls.__model__)
                        if query_options is not None:
                            q = q.options(query_options)
                        model = q.get(
                            model_id
                        )
                        cls.cache(model_id, model)
                ret = cls.cached(model_id)
        elif kwargs:
            models = cls.get_all(**kwargs)
            models.append(None)
            ret = models[0]

        if ret:
            with cls.db.session.no_autoflush:
                if ret not in cls.db.session:
                    ret = cls.db.session.merge(ret)
        return ret

    @classmethod
    def get_or_create(cls, model_id=None, no_commit=False, **kwargs):
        model = cls.get(model_id=model_id, **kwargs)
        if model is None:
            check_unique = kwargs.pop('check_unique', False)
            model = cls.create(
                no_commit=no_commit, check_unique=check_unique, **kwargs
            )
        with cls.db.session.no_autoflush:
            if model not in cls.db.session:
                model = cls.db.session.merge(model)
        return model

    @classmethod
    def update(cls, model):
        if isinstance(model, list):
            models = model
        else:
            models = [model]

        for model in models:
            if not isinstance(model, cls.__model__):
                raise TypeError(
                    '"model" must be of type'
                    f' {cls.__model__.__class__.__name__},'
                    f' not {model.__class__.__name__}'
                )
            if model in cls.db.session:
                cls.db.session.expunge(model)
        cls.db.session.add_all(models)
        cls.commit()

    @classmethod
    def delete(cls, model_or_id, no_commit=False):
        if isinstance(model_or_id, int):
            model = cls.get(model_or_id)
        elif isinstance(model_or_id, cls.__model__):
            model = model_or_id
            if model not in cls.db.session:
                model = cls.db.session.merge(model)
        else:
            raise TypeError(
                '"model_or_id" must be of type int'
                f' or {cls.__model__.__class__.__name__},'
                f' not {model_or_id.__class__.__name__}'
            )

        cls.db.session.delete(model)
        if not no_commit and cls.auto_commit:
            cls.commit()

    def __init__(self, model, *args, **kwargs):
        self.__instance = model


class PermissionsMixin:
    @classmethod
    def grant(cls, model, user, permission, no_commit=False):
        if not hasattr(model, 'grant'):
            raise TypeError(
                f'{model.__class__.__qualname__} does not support permissions'
            )
        model.grant(user, permission)
        cls.db.session.add(model)
        if not no_commit and cls.auto_commit:
            cls.commit()

    @classmethod
    def clear_permissions(cls, model, except_for=[]):
        model._permissions = [  # Clear existing permissions
            x for x in model._permissions if x.user_id in except_for
        ]
