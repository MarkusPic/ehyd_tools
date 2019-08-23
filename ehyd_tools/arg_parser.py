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

    parser.add_argument('--add_gaps',
                        help='get the gaps in the series as a csv table',
                        required=False, action='store_true')

    parser.add_argument('--to_csv',
                        help='save the data to the current directory',
                        required=False, action='store_true')

    parser.add_argument('--to_parquet',
                        help='save the data to the current directory',
                        required=False, action='store_true')

    parser.add_argument('--max10a',
                        help='consider only 10 years with the most availability',
                        required=False, action='store_true')

    parser.add_argument('--start',
                        help='custom start time, Format="YYYY-MM-DD"',
                        required=False)

    parser.add_argument('--end',
                        help='custom end time, Format="YYYY-MM-DD"',
                        required=False)

    parser.add_argument('--plot',
                        help='plot the data',
                        required=False, action='store_true')

    parser.add_argument('--statistics',
                        help='creates a txt file with basic statistics (sum, max & min)',
                        required=False, action='store_true')

    parser.add_argument('--meta',
                        help='add the txt file with the meta data of the ehyd data',
                        required=False, action='store_true')

    parser.add_argument('--unix',
                        help='export the csv files with a "," as separator and a "." as decimal sign.',
                        required=False, action='store_true')

    return parser.parse_args()
