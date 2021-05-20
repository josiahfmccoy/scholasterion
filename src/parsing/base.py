import json
import os
from processing.processor import TextProcessor
try:
    from ..utils import *
except ValueError:
    from utils import *

__all__ = ['Parser']


with open(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
) as f:
    PARSER_CONFIG = json.load(f)


class Parser:
    config = PARSER_CONFIG

    _lemma_cache = {}

    def __init__(self, logger=None):
        if logger is None:
            logger = make_logger(self.__class__.__name__)
        self.logger = logger

    def parse_file(self, filepath):
        text = TextProcessor(self.logger).process_file(filepath)
        if not text:
            return None

        words = text.xpath('//span[@class="word"]')

        normed = {}

        for w in words:
            try:
                normalized = norm_word(w.text)
            except Exception:
                import traceback
                traceback.print_exc()
                raise
                normalized = None
            if not normalized:
                continue
            normed.setdefault(normalized, []).append(w.attrib['id'])

        lemmas = {}

        total = len(list(normed))
        for i, (normed, ids) in enumerate(normed.items(), start=1):
            self.logger.debug(f'Parsing word {i}/{total} ...')

            if normed not in self._lemma_cache:
                lems = self.parse_word(normed)
                self._lemma_cache[normed] = lems

            lems = self._lemma_cache[normed]
            for lem, parsings in lems.items():
                lemma_info = lemmas.setdefault(lem, {}).setdefault(
                    normed, {}
                )
                lemma_info.setdefault('tokens', []).append(ids)
                lemma_info.setdefault('parsings', []).extend(parsings)

        return {
            'formatted_text': text,
            'lemma_mapping': lemmas
        }

    def parse_word(self, word):
        raise NotImplementedError()

    def normalize_parsing(self, parsing):
        p = parsing.strip()
        if not p:
            return None

        if p.startswith('ronoun'):
            p = 'p' + p

        notes = []
        while '(' in p:
            p = p.split('(', 1)
            note = p[-1].split(')', 1)
            p = (p[0] + ' ' + note[-1]).strip()
            notes.append(note[0].strip())

        parse = {}
        for pos, mapped in self.config['parts_of_speech'].items():
            if p.startswith(pos):
                parse['pos'] = mapped
                p = p[len(pos):].strip()
                break

        for x in p.split(' '):
            x = x.strip()
            for cat, mapping in self.config['categories'].items():
                if x in mapping:
                    parse[cat] = mapping[x]
                    break

            if ('pos' not in parse) and (x in self.config['parts_of_speech']):
                parse['pos'] = self.config['parts_of_speech'][x]

        if 'pos' not in parse:
            if 'case' in parse:
                if 'tense' in parse:
                    parse['pos'] = 'participle'
                else:
                    parse['pos'] = 'noun'
            elif 'tense' in parse:
                parse['pos'] = 'verb'

        if notes:
            parse['notes'] = '; '.join(notes)

        return parse
