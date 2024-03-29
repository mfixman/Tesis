from __future__ import print_function, division

from argparse import ArgumentParser

import logging
import pandas
import sys

# Iterates through a csv file read by chunks from pandas.read_csv that's
# orderedby its index
class OrderedDF(object):
    def extract(self):
        try:
            ch = pandas.concat([self.rest, next(self.it)])

            self.body = ch[ch.index != ch.index[-1]]
            self.rest = ch[ch.index == ch.index[-1]]
        except StopIteration:
            self.body = self.rest
            self.rest = pandas.DataFrame()

    def done(self):
        return self.body.empty and self.rest.empty

    # Iterate through the DataFrame and make sure there aren't any
    # incomplete blocks in the body.
    def __iter__(self):
        self.extract()
        while not self.done():
            yield self.body
            self.extract()

    def __init__(self, it):
        self.it = it
        self.body = pandas.DataFrame()
        self.rest = pandas.DataFrame()

def parse_args():
    parser = ArgumentParser(
        description = (
            'Partition a big ordered file against a certain columns, merge it'
            'with another file, and accumulate the results'
        ),
        epilog = 'The first row fill always be partitioned, and should be ordered.'
    )
    parser.add_argument('-f', '--filterrows', help = 'Only rows processed ar the ones in this file.')
    parser.add_argument('-c', '--columns', nargs = '*', default = [], help = 'Columns to partition the file by, other than the first.')
    parser.add_argument('-a', '--categories', help = 'Also separate the columns depending on these categories')
    parser.add_argument('merge_col', help = 'Column in the standard imput to do the merging.')
    parser.add_argument('merge_file', help = 'File to do the merging with.')
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s|\t%(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')
    args = parse_args()

    logging.debug('Reading merge file.')
    extra = []
    for e, chunk in enumerate(pandas.read_csv(args.merge_file, sep = '|', index_col = [0], chunksize = 1000000)):
        if e & (e - 1) == 0:
            logging.debug('Parsing chunk {}. Last datum is {}.'.format(e, chunk.index[-1]))

        extra.append(chunk)
    extra = pandas.concat(extra)

    if args.categories:
        logging.debug('Reading categories file')
        categories = pandas.read_csv(args.categories, sep = '|', index_col = [0], squeeze = True)

        logging.debug('Merging with merge file')
        extra = extra.merge(categories.to_frame(), left_index = True, right_index = True)

        args.columns.append(categories.name)

    filterrows = None
    if args.filterrows:
        logging.debug('Reading filter file.')
        filterrows = pandas.read_csv(args.filterrows, sep = '|', usecols = [0], squeeze = True).values

    columns = None
    data = OrderedDF(pandas.read_csv(sys.stdin, sep = '|', index_col = [0], chunksize = 1000000))
    for e, chunk in enumerate(data):
        if e & (e - 1) == 0:
            logging.debug('Parsing chunk {}. Last datum is {}.'.format(e, None if chunk.empty else chunk.index[-1]))

        if filterrows is not None:
            chunk = chunk[chunk.index.isin(filterrows)]

        full = chunk.merge(extra, left_on = args.merge_col, right_index = True).drop(args.merge_col, axis = 1)
        accum = full.groupby([full.index] + args.columns).sum().unstack(level = range(1, len(args.columns) + 1)).fillna(0, downcast = 'infer')

        accum.columns = ['_'.join('{}{}'.format('' if type(y) == str else 'd', y) for y in x) for x in accum.columns]
        accum.index.rename(extra.index.name, inplace = True)

        if columns is None:
            columns = accum.columns
        else:
            assert accum.columns.difference(columns).size == 0, "First chunk doesn't contain all columns"
            accum = accum.reindex(columns = columns, fill_value = 0)

        accum.to_csv(sys.stdout, sep = '|', index = True, header = e == 0)
