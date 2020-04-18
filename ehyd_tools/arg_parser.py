__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import argparse


def ehyd_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-id',
                        help='the id number for the station from the ehyd.gv.at platform',
                        required=False, type=int)
    parser.add_argument('--input',
                        help='path to the rain input file including the filename',
                        required=False)

    parser.add_argument('--max10a',
                        help='consider only 10 years with the most availability (for clipping the data)',
                        required=False, action='store_true')

    parser.add_argument('--start',
                        help='custom start time (Format="YYYY-MM-DD") for clipping the data',
                        required=False)

    parser.add_argument('--end',
                        help='custom end time (Format="YYYY-MM-DD") for clipping the data',
                        required=False)

    parser.add_argument('--add_gaps',
                        help='save a gaps-table as a csv-file',
                        required=False, action='store_true')

    parser.add_argument('--to_csv',
                        help='save the time-series as csv-file '
                             '(to the current directory if the id is used or in the directory of the input-file)',
                        required=False, action='store_true')

    parser.add_argument('--to_parquet',
                        help='save the time-series as parquet-file '
                             '(to the current directory if the id is used or in the directory of the input-file)'
                             ' - parquet is a much faster as csv to read and write',
                        required=False, action='store_true')

    parser.add_argument('--plot',
                        help='save a bar-plot with monthly sums and availability as a png-file',
                        required=False, action='store_true')

    parser.add_argument('--statistics',
                        help='save the basic statistics (sum, max & min) as a txt-file',
                        required=False, action='store_true')

    parser.add_argument('--meta',
                        help='save the meta-data presented in ehyd as a txt-file',
                        required=False, action='store_true')

    parser.add_argument('--unix',
                        help='export the csv files with a "," as separator and a "." as decimal sign '
                             '(otherwise ";" as separator and a "," as decimal sign will be used)',
                        required=False, action='store_true')

    return parser.parse_args()
