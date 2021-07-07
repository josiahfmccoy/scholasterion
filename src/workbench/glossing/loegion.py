import requests
from lxml import html
try:
    from ..utils import *
except ValueError:
    from utils import *


class LoegionGlosser:
    # base_url = 'https://api-v2.logeion.org/morpho'
    base_url = 'http://www.perseus.tufts.edu/hopper/morph'

    def gloss(self, lemma):
        n = norm_word(lemma)
        while True:
            try:
                # r = requests.get(f'{self.base_url}/detail/{n}?dicos=all').json()

                lang = 'grc'
                for x in 'abcdefghijklmnopqrstuvwxyz':
                    if x in n:
                        lang = 'lat'
                        break

                r = requests.get(f'{self.base_url}?l={n}&la={lang}')
                break
            except requests.exceptions.ConnectionError:
                time.sleep(10)

        root = html.fromstring(r.text)

        shortdef = []
        lems = root.xpath('//div[@class="lemma_header"]')
        for lem in lems:
            h = lem.xpath('.//h4')
            if h[0].text.lower() != n:
                continue
            for d in lem.xpath('.//span[@class="lemma_definition"]'):
                shortdef.append(norm_word(d.text, lowercase=False))

        # shortdef = [
        #     x.replace(' ronoun', 'pronoun')
        #     for x in r['shortdef']
        #     if f'{lemma},' in x
        # ]
        # shortdef = shortdef[0] if shortdef else None

        return '; '.join(shortdef)
