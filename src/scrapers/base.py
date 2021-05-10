import requests
try:
    from ..utils import *
except ValueError:
    from utils import *

__all__ = ['WebScraper']


class WebScraper:
    _session = None

    base_url = None

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            self.init_session()
        return self._session

    def __init__(self, logger=None):
        if logger is None:
            logger = make_logger(self.__class__.__name__)
        self.logger = logger

    def init_session(self):
        return True

    def load_text(self, *args, **kwargs):
        raise NotImplementedError()
