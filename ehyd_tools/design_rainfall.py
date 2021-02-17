__author__ = "Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Markus Pichler"

from pandas import read_fwf, IndexSlice as idx
import os

import requests
from io import BytesIO, TextIOWrapper


def get_ehyd_file(grid_point_number=5214):
    url = 'https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData?id={no}'.format(no=grid_point_number)
    r = requests.get(url, allow_redirects=True)
    fwf_file = TextIOWrapper(BytesIO(r.content), encoding='ISO-8859-1')
    return fwf_file


def save_ehyd_pdf_file(grid_point_number, fn):
    from os import path
    fn = path.join(fn, 'Bemessungsniederschlag_Gitterpunkt_{no}.pdf'.format(no=grid_point_number))
    if not path.isfile(fn):
        url = 'https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData/pdf?id={no}'.format(no=grid_point_number)
        r = requests.get(url, allow_redirects=True)
        open(fn, 'wb').write(r.content)


# https://ehyd.gv.at/#
def ehyd_design_rainfall_ascii_reader(filepath_or_buffer):
    if isinstance(filepath_or_buffer, str):
        txt_file = open(filepath_or_buffer, 'r', encoding='ISO-8859-1')
    else:
        txt_file = filepath_or_buffer

    # The first three lines are purely informal and do not belong to the table.
    first_three_lines = [txt_file.readlines(1) for _ in range(3)]
    # print(*first_three_lines, sep='\n')

    df = read_fwf(txt_file, header=0, skiprows=0, index_col=[0, 1, 2],
                  encoding='ISO-8859-1',
                  comment='-',
                  skip_blank_lines=True)
    txt_file.close()

    # drop empty rows
    df = df.dropna(axis=0, how='all')

    # convert string column names to integers
    df.columns = [int(c.replace('T', '')) for c in df.columns]
    # df.columns.name = 'Jährlichkeit'
    df.columns.name = 'return period'

    # index "0" (="DAUER") is just the string representative of the index "duration"
    df.index = df.index.droplevel(0)
    # originally named ["DAUERMIN", "TYP"]
    # df.index.names = ['Dauerstufe', 'Berechnungstyp']
    df.index.names = ['duration', 'calculation method']

    # set duration index as integer
    df.index = df.index.set_levels([df.index.levels[0].astype(int), df.index.levels[1]])

    return df


def get_max_calculation_method(df, methods=None):
    if methods is None:
        methods = ['ÖKOSTRA', 'Bemessung']

    return df.loc[idx[:, methods], :].max(axis=0, level=0).copy()


def get_calculation_method(df, method='Bemessung'):
    return df.xs(method, axis=0, level='calculation method', drop_level=True).copy()


if __name__ == '__main__':
    df = ehyd_design_rainfall_ascii_reader(get_ehyd_file(grid_point_number=5214))

    max_df = get_max_calculation_method(df)

    # max_df.to_csv(os.path.join('V:', 'DATA', 'OPENSDM', 'INBOX', 'STRATUS', 'shared', 'hydras', 'events',
    #                            'events_whole', 'ehyd_table.csv'))

    df.loc[idx[1:100, 'Bemessung'], 5]

    max_df.loc[1:100, 5]

    print(get_max_calculation_method(df))
    print(get_calculation_method(df))

    print(df)
