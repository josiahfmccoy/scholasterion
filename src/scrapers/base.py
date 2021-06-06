import os
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
        self._last_text = None

    def init_session(self):
        return True

    def load_text(self, *args, **kwargs):
        text = self._load(*args, **kwargs)
        self._last_text = text
        return text

    def _load(self, *args, **kwargs):
        raise NotImplementedError()

    def save(self, filepath):
        if not self._last_text:
            return

        fname = filepath
        if not fname.endswith('.txt'):
            if '.' in fname:
                fname = fname.rsplit('.', 1)[0]
            fname += '.txt'

        if os.path.isfile(fname):
            raise IOError('File exists!')
        with open(fname, 'w', encoding='utf-8') as f:
            f.writelines([self._last_text])
