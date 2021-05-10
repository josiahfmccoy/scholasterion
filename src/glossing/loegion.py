import requests
try:
    from ..utils import *
except ValueError:
    from utils import *


class LoegionGlosser:
    base_url = 'https://api-v2.logeion.org/morpho'

    def gloss(self, lemma):
        n = norm_word(lemma)
        while True:
            try:
                r = requests.get(f'{self.base_url}/detail/{n}?dicos=all').json()
                break
            except requests.exceptions.ConnectionError:
                time.sleep(10)

        shortdef = [
            x.replace(' ronoun', 'pronoun')
            for x in r['shortdef']
            if f'{lemma},' in x
        ]
        shortdef = shortdef[0] if shortdef else None

        return shortdef
