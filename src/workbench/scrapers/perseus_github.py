from lxml import etree
from .base import WebScraper

__all__ = ['PerseusGithubClient']


class PerseusGithubClient(WebScraper):
    base_url = 'https://raw.githubusercontent.com/PerseusDL'

    def _load(self, urn, excerpt=None, filename=None):

        urn = urn.lstrip('urn:cts:')

        urn = urn.split(':')
        urn_path = urn[1].split('.')

        url = (
            f'{self.base_url}/canonical-{urn[0]}/master/data'
            f'/{urn_path[0]}/{urn_path[1]}/{urn[1]}.xml'
        )

        self.logger.debug(f'Loading {url}')
        r = self.session.get(url)

        parser = etree.XMLParser(remove_blank_text=True)
        html = etree.fromstring(r.content, parser=parser)

        body = html.findall(f'.//text//body')[0]

        def get_child_text(block, rank=1):
            ret = []

            blocks = block.xpath(f'child::div{rank}')
            if not blocks:
                ret.append(' '.join(t for t in block.itertext()))
                return ret

            for b in blocks:
                t = (b.attrib.get('type') or '').strip()
                n = (b.attrib.get('n') or '').strip()
                name = ' '.join([x for x in [t, n] if x]).strip().title()

                child_txt = get_child_text(b, rank=(rank + 1))
                if child_txt and name:
                    child_txt = [name] + child_txt

                txt = '\n\n'.join(child_txt)
                ret.append(txt)

            return ret

        text = get_child_text(body)

        text = '\n\n'.join(text)

        return text
