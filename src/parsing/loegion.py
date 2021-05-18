import json
import re
import requests
import time
from .base import Parser
try:
    from ..utils import *
except ValueError:
    from utils import *


class LoegionParser(Parser):
    base_url = 'https://api-v2.logeion.org/morpho'

    accent_map = {
        'των': 'τῶν',
        'αγιων': 'ἁγίων',
        'αποστολων': 'ἀποστόλων'
    }

    def parse_word(self, word):
        n = norm_word(word)
        n = self.accent_map.get(n, n)
        while True:
            try:
                r = requests.get(f'{self.base_url}/wordwheel/{n}')
                r = r.json()
                break
            except json.JSONDecodeError:
                print(r)
                print(r.text)
                raise
            except requests.exceptions.ConnectionError:
                time.sleep(10)

        parses = r.get('parses', [])
        if not isinstance(parses, list):
            parses = [parses]

        desc = r.get('description', '')
        if 'Could not find the search term' in desc:
            if 'Found the closest form' in desc:
                wd = r.get('word')
                for hw in r.get('headwords', []):
                    if strip_accents(norm_word(hw)) == strip_accents(norm_word(word)):
                        if wd != hw:
                            return self.parse_word(hw)

        vals = {}
        for info in parses:
            lem = info['lemma']
            lem = re.split('\d+', lem)  # noqa
            if len(lem) > 1:
                lem = ''.join(lem[0:-1])
            else:
                lem = lem[0]

            parsed = []
            ps = info['parse']
            ps = ps.replace('<br/>', '<br>')
            ps = ps.replace('&#x2713', '<br>')
            for p in ps.split('<br>'):
                parse = self.normalize_parsing(p)
                if parse:
                    parsed.append(parse)

            vals.setdefault(lem, []).extend(parsed)

        return vals
