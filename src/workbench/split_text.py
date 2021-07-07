import argparse
import os
import time
from lxml import etree
from utils import *


def split_text(
    filename, level, subname, start_at=1, logger=None, overwrite=False
):
    outpath = os.path.abspath(filename.rsplit('.', 1)[0])
    if not os.path.isdir(outpath):
        os.makedirs(outpath)

    with open(filename, 'r', encoding='utf-8') as f:
        data = '\n'.join(f.readlines())

    delim = f'<section class="sc-level-{level}">'

    data = [
        delim + x
        for x in data.split(delim)
        if x.strip()
    ]

    logger = logger or make_logger('splitter')
    parser = etree.XMLParser(remove_blank_text=True)

    for i, txt in enumerate(data, start=int(start_at)):
        fname = os.path.join(outpath, f'{subname}-{i}.xml')

        if not overwrite and os.path.isfile(fname):
            raise AssertionError(f'File "{os.path.basename(fname)}" exists!')

        try:
            tree = etree.fromstring(txt, parser=parser)
            with open(fname, 'wb') as f:
                f.write(etree.tostring(tree, encoding='utf-8', pretty_print=True))
        except Exception:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(txt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filepath')
    parser.add_argument('-l', '--level', default='1')
    parser.add_argument('-n', '--name', default='book')
    parser.add_argument('-s', '--start', default='1')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--overwrite', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('splitter', level=('debug' if args.verbose else 'info'))

    start = time.time()
    try:
        split_text(
            args.filepath, args.level, args.name,
            start_at=args.start,
            logger=logger, overwrite=args.overwrite
        )
    except AssertionError:
        pass
    end = time.time()

    logger.info(f'Ran in {end - start} s')
