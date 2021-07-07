import argparse
import os
import time
from processing.processor import TextProcessor
from lxml import etree
from utils import *


def process_text(filename, outpath=None, logger=None, overwrite=False):
    outname = os.path.abspath(outpath or os.path.dirname(filename))
    outname = outname.replace('\\', '/')
    if '/texts/formatted' in outname:
        outname = outname.replace('/texts/formatted', '/texts/processed')

    outname = os.path.join(outname, os.path.basename(filename))
    if not outname.endswith('.xml'):
        if '.' in outname:
            outname = outname.rsplit('.', 1)[0]
        outname += '.xml'

    logger = logger or make_logger('processor')
    logger.info(f'Processing {os.path.relpath(filename)} ...')

    if not overwrite and os.path.isfile(outname):
        raise AssertionError('File exists!')

    processor = TextProcessor(logger=logger)
    tree = processor.process_file(filename)

    if not os.path.isdir(os.path.dirname(outname)):
        os.makedirs(os.path.dirname(outname))

    with open(outname, 'wb') as f:
        f.write(etree.tostring(tree, encoding='utf-8', pretty_print=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath')
    parser.add_argument('-o', '--outpath', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('processor', level=('debug' if args.verbose else 'info'))

    start = time.time()
    try:
        process_text(
            args.filepath, outpath=args.outpath,
            logger=logger, overwrite=args.overwrite
        )
    except AssertionError:
        pass
    end = time.time()

    logger.info(f'Ran in {end - start} s')
