import os
from lxml import etree
from .utils import make_uid
try:
    from ..utils import *
except ValueError:
    from utils import *


class TextProcessor:
    def __init__(self, logger=None):
        if logger is None:
            logger = make_logger(self.__class__.__name__)
        self.logger = logger

    def has_multiple_words(self, txt):
        return (' ' in txt)

    def split_words(self, txt):
        for word in txt.split(' '):
            yield word

    def process_file(self, filepath):
        self.logger.debug(f'Processing {os.path.basename(filepath)} ...')
        if filepath.endswith('.xml') or filepath.endswith('.html'):
            parser = etree.XMLParser(remove_blank_text=True)
            text = etree.parse(filepath, parser)
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = '\n'.join(f.readlines()).strip()
            if not text.strip():
                return None
            root = etree.Element('section')
            root.text = text.strip()
            text = etree.ElementTree(root)

        self.process_tag(text.getroot())

        self._uids = {}
        for w in text.xpath('//span[@class="word"]'):
            if 'id' in w.attrib:
                continue
            uid = make_uid()
            while uid in self._uids:
                uid = make_uid()
            self._uids[uid] = 0
            w.set('id', f'a.{uid}')

        return text

    def process_tag(self, tag):
        txt = (tag.text or '') + (tag.tail or '')
        tag.text = None
        tag.tail = None
        if txt:
            if len(list(self.split_words(txt))) > 1:
                self.process_text_string(txt, tag)
            else:
                tag.text = txt
                return

        for child in tag:
            self.process_tag(child)

    def process_text_string(self, text, parent):
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
                # f = etree.SubElement(w, 'span')
                # f.set('class', 'word-form')
                w.text = norm_accents(word.strip())
