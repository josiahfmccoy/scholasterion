import argparse
import os
import time
from lxml import etree
from utils import *


def split_text(filename, logger=None, overwrite=False):
    outpath = os.path.abspath(filename.rsplit('.', 1)[0])
    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    with open(filename, 'r', encoding='utf-8') as f:
        data = '\n'.join(f.readlines())

    delim = '<section class="sc-level-1">'

    data = [
        delim + x
        for x in data.split(delim)
        if x.strip()
    ]

    logger = logger or make_logger('splitter')
    parser = etree.XMLParser(remove_blank_text=True)

    i = 0
    for i, txt in enumerate(data, start=1):
        fname = os.path.join(outpath, f'book-{i}.xml')

        if not overwrite and os.path.isfile(fname):
            raise AssertionError(f'File "{os.path.basename(fname)}" exists!')

        tree = etree.fromstring(txt, parser=parser)
        with open(fname, 'wb') as f:
            f.write(etree.tostring(tree, encoding='utf-8', pretty_print=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('splitter', level=('debug' if args.verbose else 'info'))

    start = time.time()
    try:
        split_text(
            args.filepath, logger=logger, overwrite=args.overwrite
        )
    except AssertionError:
        pass
    end = time.time()

    logger.info(f'Ran in {end - start} s')
