import argparse
import time
from scrapers.perseus_cts import PerseusCtsClient
from utils import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--urn')
    parser.add_argument('-f', '--filename')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('scraper', level=('debug' if args.verbose else 'info'))

    # ConPhil, urn:cts:latinLit:stoa0058.stoa001.perseus-lat2

    start = time.time()

    client = PerseusCtsClient(logger=logger)
    text = client.load_text(
        urn=args.urn
    )
    client.save(args.filename)

    end = time.time()
    logger.info(f'Loaded text (length {len(text.strip())}) in {end - start} s')

    logger.info(f'Ran in {end - start} s')
