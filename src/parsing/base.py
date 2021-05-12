import json
import os
from lxml import etree
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

    def has_multiple_words(self, txt):
        return (' ' in txt)

    def split_words(self, txt):
        for word in txt.split(' '):
            yield word

    def parse_text(self, text):
        if not text:
            return None

        if isinstance(text, str):
            if not text.strip():
                return None
            root = etree.Element('section')
            root.text = text.strip()
            text = etree.ElementTree(root)

        def format_text(tag):
            txt = (tag.text or '') + (tag.tail or '')
            tag.text = None
            tag.tail = None
            if txt:
                if self.has_multiple_words(txt):
                    self._process(txt, tag)
                else:
                    tag.text = txt
                    return

            for child in tag:
                format_text(child)

        format_text(text.getroot())

        words = text.xpath('//span[@class="word"]')

        normed = {}

        for w in words:
            lem = w.xpath('.//span[@class="lemma"]')
            if lem:
                continue
            try:
                normalized = norm_word(w.xpath('.//span[@class="word-form"]')[0].text)
            except Exception:
                import traceback
                traceback.print_exc()
                raise
                normalized = None
            if not normalized:
                continue
            normed.setdefault(normalized, []).append(w)

        total = len(list(normed))
        for i, (n, words) in enumerate(normed.items(), start=1):
            self.logger.debug(f'Parsing token {i}/{total} ...')

            if n not in self._lemma_cache:
                lemmas = self.parse_word(n)
                for lemma in lemmas:
                    lemmas[lemma] = {
                        'parsings': lemmas[lemma]
                    }
                self._lemma_cache[n] = lemmas

            lemmas = self._lemma_cache[n]
            for w in words:
                for i, lemma in enumerate(lemmas, start=1):
                    lem = etree.SubElement(w, 'span')
                    lem.set('class', 'lemma')
                    # lem.set('option', str(i))
                    # for parsing in lemmas[lemma]['parsings']:
                    #     p = etree.SubElement(lem, 'parsing')
                    #     for k, v in parsing.items():
                    #         p.set(k, v)
                    # hw = etree.SubElement(lem, 'span')
                    lem.text = lemma

        return text

    def _process(self, text, parent):
        paragraphs = text.strip().split('\n')
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            if len(paragraphs) > 1:
                para = etree.SubElement(parent, 'section')
            else:
                para = parent

            if p.startswith('[') and (']' in p):
                p = p[1:].split(']', 1)
                lbl = p[0].strip()
                h = etree.SubElement(para, 'h4')
                h.text = lbl
                p = p[-1].strip()

            for word in self.split_words(p):
                normalized = norm_word(word)
                if not normalized:
                    continue
                w = etree.SubElement(para, 'span')
                w.set('class', 'word')
                f = etree.SubElement(w, 'span')
                f.set('class', 'word-form')
                f.text = norm_accents(word.strip())

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
