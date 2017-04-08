from __future__ import print_function, division

import logging
import pandas
import sys

from argparse import ArgumentParser

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s|\t%(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
    
    last = None
    cols = None
    for e, chunk in enumerate(pandas.read_csv(sys.stdin, sep = '|', index_col = [0, 1], chunksize = 1000000)):
        if e & (e - 1) == 0:
            logging.debug('Parsing chunk {}'.format(e))

        if last is not None:
            chunk = pandas.concat([last, chunk])
            last = None
        
        if chunk.index[-1][1] == 1:
            last = chunk.iloc[[-1]]
            chunk = chunk.iloc[:-1]

        trans = chunk.unstack(level = 1, fill_value = 0)
        trans.columns = ['{}_d{}'.format(x, y) for (x, y) in trans.columns]

        if cols is None:
            cols = trans.columns
        else:
            assert trans.columns.equals(cols)

        trans.to_csv(sys.stdout, sep = '|', index = True, header = e == 0)

    if last is not None:
        last = last.unstack(level = 1, fill_value = 0).reindex(columns = cols, fill_value = 0)
        last.to_csv(sys.stdout, sep = '|', index = True, header = False)

