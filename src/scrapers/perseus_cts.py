import re
from lxml import etree
from .base import WebScraper

__all__ = ['PerseusCtsClient']


class PerseusCtsClient(WebScraper):
    hopper = 'http://www.perseus.tufts.edu/hopper/CTS'
    cts = 'http://cts.perseids.org'

    def load_metadata(self, urn):
        self.logger.debug(f'Loading metadata for {urn} ...')
        r = self.session.get(self.hopper, params={
            'request': 'GetCapabilities'
        })

        html = etree.fromstring(r.content)
        ns = html.tag.split('}')[0] + '}'

        textgroups = html.findall(f'.//{ns}textgroup')

        def get_sections(citeMap):
            sections = []
            for sec in citeMap.findall(f'.//{ns}citation'):
                sections.append({
                    'name': sec.get('label'),
                    'subsections': get_sections(sec)
                })
            return sections

        for tg in textgroups:
            for wk in tg.findall(f'.//{ns}work'):
                for ed in wk.findall(f'.//{ns}edition'):
                    if urn == ed.get('urn'):
                        metadata = {
                            'title': wk.find(f'.//{ns}title').text,
                            'label': ed.find(f'.//{ns}label').text,
                            'description': ed.find(f'.//{ns}description').text
                        }
                        citeMap = ed.find(f'.//{ns}online')
                        if citeMap is not None:
                            citeMap = citeMap.find(f'.//{ns}citationMapping')
                            metadata['section_types'] = get_sections(citeMap)
                        return metadata
        return None

    def _load(self, urn, excerpt=None, filename=None):
        metadata = self.load_metadata(urn)
        if metadata is None:
            raise ValueError(f'No text exists with URN {urn}')

        def get_excerpt(urn):
            self.logger.debug(f'Determining full-text bounds ...')
            read_urn = re.sub('urn:cts:|urn.cts.', '', urn)
            read_urn = re.sub('[:.]', '/', read_urn)
            read_url = f'{self.cts}/read/{read_urn}'
            r = self.session.get(read_url)
            while r.status_code != 200:
                try:
                    i = int(read_url[-1])
                    if i > 8:
                        return urn, ''
                    read_url = read_url[:-1] + str(i + 1)
                    urn = urn[:-1] + str(i + 1)
                    r = self.session.get(read_url)
                except ValueError:
                    return urn, ''

            html = etree.HTML(r.content)
            start_passage = None
            end_passage = None
            for btn in html.findall('.//*[@class="col-md-1"]'):
                data = ''.join(btn.itertext()).strip()
                txt = data.split('-')
                if start_passage is None:
                    start_passage = txt[0].strip()
                end_passage = txt[-1].strip()
            return urn, f'{start_passage}-{end_passage}'

        if excerpt is None:
            urn, excerpt = get_excerpt(urn)

        if excerpt:
            excerpt = ':' + excerpt

        self.logger.debug(f'Loading {urn}{excerpt}')
        r = self.session.get(f'{self.cts}/api/cts', params={
            'request': 'GetPassage',
            'urn': f'{urn}{excerpt}'
        })

        parser = etree.XMLParser(remove_blank_text=True)
        html = etree.fromstring(r.content, parser=parser)
        ns = html.tag.split('}')[0] + '}'

        passage = html.findall(f'.//{ns}passage')[0]

        tei = list(passage)[0]
        ns = tei.tag.split('}')[0] + '}'

        blocks = tei.xpath(
            './/ns:l|.//ns:p',
            namespaces={'ns': re.sub('[{}]', '', ns)}
        )

        if not blocks:
            return

        text = []

        for i, block in enumerate(blocks):
            s = ' '.join(t for t in block.itertext())
            text.append(s)
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(text))

        text = '\n'.join(text)

        # Perseus does weird things with paragraphs sometimes;
        # try to clean that up a bit
        # (in this case, hanging indents of 7 tabs each 3 spaces wide)
        text = text.replace('\n' + (' ' * 3 * 7), ' ')

        return text
