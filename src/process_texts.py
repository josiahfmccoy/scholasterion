import argparse
import os
import time
from processing.processor import TextProcessor
from lxml import etree
from utils import *


def process_text(filename, outpath=None, logger=None, overwrite=False):
    outname = outpath or os.path.dirname(filename)
    if outname.endswith('formatted'):
        outname = os.path.dirname(outname)
    if not outname.endswith('processed'):
        outname = os.path.join(outname, 'processed')

    outname = os.path.join(outname, os.path.basename(filename))
    if not outname.endswith('.xml'):
        if '.' in outname:
            outname = outname.rsplit('.', 1)[0]
        outname += '.xml'

    if not overwrite and os.path.isfile(outname):
        raise AssertionError('File exists!')

    logger = logger or make_logger('scraper')
    processor = TextProcessor(logger=logger)
    tree = processor.process_file(filename)

    with open(outname, 'wb') as f:
        f.write(etree.tostring(tree, encoding='utf-8', pretty_print=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folderpath')
    parser.add_argument('-o', '--outpath', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('processor', level=('debug' if args.verbose else 'info'))

    start = time.time()
    for filename in os.listdir(args.folderpath):
        fname = os.path.join(args.folderpath, filename)
        try:
            process_text(
                fname, outpath=args.outpath, logger=logger, overwrite=args.overwrite
            )
        except AssertionError:
            continue
    end = time.time()

    logger.info(f'Ran in {end - start} s')
