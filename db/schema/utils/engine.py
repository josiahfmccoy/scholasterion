import sqlalchemy as sa
from .base import Model

__all__ = [
    'DataBase'
]


class DataBase:
    def __init__(self, uri, model_base=Model):
        self.uri = uri
        self.engine = sa.create_engine(
            self.uri, connect_args={'check_same_thread': False}
        )
        print("Created new database connection")
        self._session = None

        if model_base:
            self._init_model_base(model_base)

    def _make_session(self):
        s = sa.orm.Session(bind=self.engine)
        return s

    def _init_model_base(self, model_base):
        class _QueryProperty:
            def __init__(self, db):
                self.db = db

            def __get__(self, obj, cls):
                return self.db.session.query(cls)
        model_base.query = _QueryProperty(self)
        self.Model = model_base

    @property
    def session(self):
        if self._session is None:
            self._session = self._make_session()
        return self._session
