import requests
from .base import Parser
try:
    from ..utils import *
except ValueError:
    from utils import *


class CalParser(Parser):
    base_url = 'http://cal.huc.edu/browseheaders.php'

    character_map = {
        ')': {
            'transcribed': 'ˀ',
            'hebrew': 'א',
            'syriac': 'ܐ'
        },
        'b': {
            'transcribed': 'b',
            'hebrew': 'ב',
            'syriac': 'ܒ'
        },
        'g': {
            'transcribed': 'g',
            'hebrew': 'ג',
            'syriac': 'ܓ'
        },
        'd': {
            'transcribed': 'd',
            'hebrew': 'ד',
            'syriac': 'ܕ'
        },
        'h': {
            'transcribed': 'h',
            'hebrew': 'ה',
            'syriac': 'ܗ'
        },
        'w': {
            'transcribed': 'w',
            'hebrew': 'ו',
            'syriac': 'ܘ'
        },
        'z': {
            'transcribed': 'z',
            'hebrew': 'ז',
            'syriac': 'ܙ'
        },
        'x': {
            'transcribed': 'ḥ',
            'hebrew': 'ח',
            'syriac': 'ܚ'
        },
        'T': {
            'transcribed': 'ṭ',
            'hebrew': 'ט',
            'syriac': 'ܛ'
        },
        'y': {
            'transcribed': 'y',
            'hebrew': 'י',
            'syriac': 'ܝ'
        },
        'k': {
            'transcribed': 'k',
            'hebrew': 'כ',
            'syriac': 'ܟ'
        },
        'l': {
            'transcribed': 'l',
            'hebrew': 'ל',
            'syriac': 'ܠ'
        },
        'm': {
            'transcribed': 'm',
            'hebrew': 'מ',
            'syriac': 'ܡ'
        },
        'n': {
            'transcribed': 'n',
            'hebrew': 'נ',
            'syriac': 'ܢ'
        },
        's': {
            'transcribed': 's',
            'hebrew': 'ס',
            'syriac': 'ܣ'
        },
        '(': {
            'transcribed': 'ˁ',
            'hebrew': 'ע',
            'syriac': 'ܥ'
        },
        'p': {
            'transcribed': 'p',
            'hebrew': 'פ',
            'syriac': 'ܦ'
        },
        'P': {
            'transcribed': 'ṗ',
            'hebrew': 'פ',
            'syriac': 'ܧ'
        },
        'c': {
            'transcribed': 'ṣ',
            'hebrew': 'צ',
            'syriac': 'ܨ'
        },
        'q': {
            'transcribed': 'q',
            'hebrew': 'ק',
            'syriac': 'ܩ'
        },
        'r': {
            'transcribed': 'r',
            'hebrew': 'ר',
            'syriac': 'ܪ'
        },
        '$': {
            'transcribed': 'š',
            'hebrew': 'ש',
            'syriac': 'ܫ'
        },
        '&': {
            'transcribed': 'ś',
            'hebrew': 'שׂ'
        },
        't': {
            'transcribed': 't',
            'hebrew': 'ת',
            'syriac': 'ܬ'
        },
        '@': {
            'transcribed': ' ',
            'hebrew': ' ',
            'syriac': ' '
        }
    }

    def __init__(self, script='syriac'):
        self.script = script
        self._full_map = {
            v: {'cal': c, **m} for c, m in self.character_map.items()
            for k, v in m.items()
        }

    def transliterate(self, word, script=None):
        script = script or self.script
        t = ''.join([
            self._full_map.get(c, {}).get(script, c)
            for c in norm_accents(word)
        ])
        return t

    def parse_word(self, word):
        n = word  # norm_word(word)

        while True:
            try:
                r = requests.post(self.base_url, data={'first3': n})
                break
            except requests.exceptions.ConnectionError:
                time.sleep(10)
        root = html.fromstring(r.text)

        lemmas = root.findall(f'.//span[@class="lem"]')
        if not lemmas:
            if self.transliterate(n, 'cal')[0] in ['d', 'w', 'b']:
                x = n[1:]
                r = requests.post(self.base_url, data={'first3': x})
                root = html.fromstring(r.text)
                lemmas = root.findall(f'.//span[@class="lem"]')

        pos = root.findall(f'.//pos')
        glosses = root.findall(f'.//span[@class="gloss"]')

        vals = {}
        for lem, pos, gls in zip(lemmas, pos, glosses):
            lem = self.transliterate(lem.text_content()).strip()
            pos = pos.text_content().strip()
            gls = gls.text_content().strip()

            vals.setdefault(lem, []).append(self.normalize_parsing({
                'pos': pos.strip(),
                'gloss': gls
            }))

        return vals

    def normalize_parsing(self, parsing):
        pos = parsing['pos']

        if pos == 'n.m.':
            parsing['pos'] = 'noun'
            parsing['gender'] = 'masculine'

        elif pos == 'n.f.':
            parsing['pos'] = 'noun'
            parsing['gender'] = 'feminine'

        elif pos == 'adj.':
            parsing['pos'] = 'adjective'

        elif pos == 'vb.':
            parsing['pos'] = 'verb'

        elif pos == 'adv.':
            parsing['pos'] = 'adverb'

        elif pos == 'prep.':
            parsing['pos'] = 'preposition'

        return parsing
