import argparse
import time
from parsing.loegion import LoegionParser
from lxml import etree
from utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    parser.add_argument('-o', '--outname', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('scraper', level=('debug' if args.verbose else 'info'))

    start = time.time()

    if args.filename.endswith('.xml'):
        parser = etree.XMLParser(remove_blank_text=True)
        text = etree.parse(args.filename, parser)
    else:
        with open(args.filename, 'r', encoding='utf-8') as f:
            text = '\n'.join(f.readlines()).strip()

    parser = LoegionParser(logger=logger)
    tree = parser.parse_text(text)

    end = time.time()
    fname = args.outname or args.filename
    if not fname.endswith('.xml'):
        if '.' in fname:
            fname = fname.rsplit('.', 1)[0]
        fname += '.xml'
    with open(fname, 'wb') as f:
        f.write(etree.tostring(tree, encoding='utf-8', pretty_print=True))

    logger.info(f'Ran in {end - start} s')
