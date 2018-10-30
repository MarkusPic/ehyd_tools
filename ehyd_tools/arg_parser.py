__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import argparse

########################################################################################################################
# class Borders():
#     def __init__(self, min_=None, max_=None, unit=''):
#         self.min_ = min_
#         self.max_ = max_
#         self.unit = unit
#
#     def __str__(self):
#         s = ''
#         if self.min_:
#             s += '>= {} {unit}'.format(self.min_, unit=self.unit)
#         if self.min_ and self.max_:
#             s += ' and '
#         if self.max_:
#             s += '<= {} {unit}'.format(self.max_, unit=self.unit)
#         return s
#
#     def __contains__(self, item):
#         b = True
#         if self.min_:
#             b &= item >= self.min_
#         if self.max_:
#             b &= item <= self.max_
#         return b
#
#     def __iter__(self):
#         return iter([str(self)])


# ------------------------------------------------------------------------------------------------------------------
ehyd_parser = argparse.ArgumentParser()
ehyd_parser.add_argument('-id', '--id_number',
                         help='the id number for the station from the ehyd.gv.at platform',
                         required=False)
ehyd_parser.add_argument('-i', '--input',
                         help='path to the rain input file including the filename',
                         required=False)

ehyd_parser.add_argument('--add_gaps',
                         help='get the gaps in the series as a csv table',
                         required=False, action='store_true')

ehyd_parser.add_argument('-ex', '--export',
                         help='path to the rain input file including the filename',
                         required=False)

ehyd_parser.add_argument('--to_csv',
                         help='save the data to the current directory',
                         required=False, action='store_true')

ehyd_parser.add_argument('--max10a',
                         help='consider only 10 years with the most availability',
                         required=False, action='store_true')

ehyd_parser.add_argument('-s', '--start',
                         help='custom start time, Format="YYYY-MM-DD"',
                         required=False)

ehyd_parser.add_argument('-e', '--end',
                         help='custom end time, Format="YYYY-MM-DD"',
                         required=False)

