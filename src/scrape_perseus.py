import argparse
import time
from parsing.loegion import LoegionParser
from scrapers.perseus_cts import PerseusCtsClient
from utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urn')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--parse', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('scraper', level=('debug' if args.verbose else 'info'))

    # ConPhil, urn:cts:latinLit:stoa0058.stoa001.perseus-lat2

    start = time.time()

    client = PerseusCtsClient(logger=logger)
    text = client.load_text(
        urn=args.urn
    )

    end = time.time()
    logger.info(f'Loaded text (length {len(text.strip())}) in {end - start} s')

    if args.parse:
        start2 = time.time()

        parser = LoegionParser(logger=logger)
        tree = parser.parse_text(text)

        end = time.time()
        logger.info(f'Lemmatized in {end - start2} s')

        fname = args.filename
        if not fname.endswith('.xml'):
            if '.' in fname:
                fname = fname.rsplit('.', 1)[0]
            fname += '.xml'
        with open(fname, 'wb') as f:
            tree.write(f, encoding='utf-8', pretty_print=True)

    else:
        with open(args.filename, 'w', encoding='utf-8') as f:
            f.write(text)

    logger.info(f'Ran in {end - start} s')
