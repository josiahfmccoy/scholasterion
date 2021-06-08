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
    if '/texts/processed' not in outname:
        outname = os.path.join(outname, 'texts/processed')

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
    parser.add_argument('-f', '--folderpath')
    parser.add_argument('-o', '--outpath', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('processor', level=('debug' if args.verbose else 'info'))

    def recursive_listdir(folderpath):
        ret = []
        for x in os.listdir(folderpath):
            fpath = os.path.join(folderpath, x)
            if os.path.isfile(fpath):
                ret.append(fpath)
            else:
                ret.extend(recursive_listdir(fpath))
        return ret

    start = time.time()
    for fname in recursive_listdir(os.path.abspath(args.folderpath)):
        try:
            process_text(
                fname, outpath=args.outpath, logger=logger, overwrite=args.overwrite
            )
        except AssertionError:
            continue
    end = time.time()

    logger.info(f'Ran in {end - start} s')
