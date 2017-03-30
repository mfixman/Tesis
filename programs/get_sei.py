from __future__ import division, print_function

import logging
import pandas
import sys

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s|\t%(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')

    logging.debug('Reading data')
    cols = ['NUM_CLIENTE', 'IM_DISP_MES_01', 'IM_DISP_MES_02', 'IM_DISP_MES_03']
    data = pandas.read_csv(sys.stdin, sep = '|', index_col = 'NUM_CLIENTE', decimal = ',', usecols = cols)

    logging.debug('Unstacking data')
    data = data.unstack().reset_index(level = 0, drop = True)

    logging.debug('Averaging data')
    data = data.groupby(level = 0).mean()
    data.rename('income', inplace = True)

    logging.debug('Writing data, with only {} NaNs'.format(data.isnull().sum()))
    data.dropna().to_csv(sys.stdout, sep = '|', index = True, header = True)
