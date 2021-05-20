import argparse
import json
import os
import time
from parsing.loegion import LoegionParser
from utils import *


def parse_loegion(filename, outpath=None, logger=None):
    outname = outpath or os.path.dirname(filename)
    if outname.endswith('formatted') or outname.endswith('processed'):
        outname = os.path.dirname(outname)
    outname = os.path.join(outname, 'parsings', os.path.basename(filename))

    if not outname.endswith('.xml'):
        if '.' in outname:
            outname = outname.rsplit('.', 1)[0]
        outname += '.xml'

    if os.path.isfile(outname):
        raise AssertionError('File exists!')

    logger = logger or make_logger('parser')
    parser = LoegionParser(logger=logger)
    parsed_data = parser.parse_file(filename)

    lem_file = outname.rsplit('.', 1)[0] + '-lemmas.json'
    with open(lem_file, 'w', encoding='utf-8') as f:
        json.dump(parsed_data['lemma_mapping'], f, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename')
    parser.add_argument('-o', '--outpath', default=None)
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    args = parser.parse_args()

    logger = make_logger('parser', level=('debug' if args.verbose else 'info'))

    start = time.time()
    parse_loegion(args.filename, outpath=args.outpath, logger=logger)
    end = time.time()

    logger.info(f'Ran in {end - start} s')
