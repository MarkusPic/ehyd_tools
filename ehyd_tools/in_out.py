__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import codecs
import requests
from io import BytesIO, TextIOWrapper, IOBase, StringIO
from zipfile import ZipFile
from os import path
import pandas as pd
from pandas.errors import ParserError

from .sww_utils import guess_freq


def csv_args(unix=False):
    """
    how to read and write csv file
    differs between windows and unix (mac+linux)

    Args:
        unix (bool): if it is a unix computer

    Returns:
        dict: arguments to read and write csv files
    """
    if unix:
        return dict(sep=',', decimal='.')
    else:
        return dict(sep=';', decimal=',')


def check_path(pth=None):
    """
    use the local directory if not path is give

    Args:
        pth (str): path to directory

    Returns:
        str: path to directory
    """
    if pth == '':
        return pth
    elif pth is None:
        return ''
    elif path.isdir(pth):
        return pth
    else:
        raise UserWarning('Path is not available')


def export_series(series, filename, export_path=None, save_as='csv', unix=False):
    """
    export the series to a given format
    may be extended

    Args:
        series (pandas.Series):
        filename (str): name of the file
        export_path (str): path where file will be stored
        save_as (str): export format
        unix (bool): whether to use "," or ";" for the csv

    Returns:
        str: path to created file
    """
    fn = path.join(check_path(export_path), '{}.{}'.format(filename, save_as))

    if save_as is 'csv':
        series.to_csv(fn, **csv_args(unix))

    elif save_as is 'parquet':
        series.to_frame().to_parquet(fn)

    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')

    return fn


def import_series(filename, series_label='precipitation', index_label='datetime', unix=False):
    """

    Args:
        filename (str):
        series_label (str):
        index_label (str):
        unix (bool): whether to use "," or ";" for the csv

    Returns:
        pandas.Series: rain series
    """
    if filename.endswith('csv'):
        try:
            ts = pd.read_csv(filename, index_col=0, header=None, squeeze=True, names=[series_label], **csv_args(unix))
            ts.index = pd.to_datetime(ts.index)
            ts.index.name = index_label
            return ts
        except (ParserError, UnicodeDecodeError):
            return _parse(filename)
    elif filename.endswith('parquet'):
        return pd.read_parquet(filename).iloc[:, 0].asfreq('T').copy()
    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')


ehyd_stations = {100180: 'Tschagguns',
                 100370: 'Thüringen',
                 100446: 'Lustenau',
                 100479: 'Dornbirn',
                 100776: 'Bregenz',
                 101303: 'Leutasch-Kirchplatzl',
                 101816: 'Ladis-Neuegg',
                 102772: 'Kelchsau',
                 103143: 'St. Johann in Tirol-Almdorf',
                 103895: 'Eugendorf',
                 104604: 'Schlägl',
                 104877: 'Linz-Urfahr',
                 105445: 'Vöcklabruck',
                 105528: 'Wels',
                 105908: 'Flachau',
                 106112: 'Liezen',
                 106252: 'Wildalpen',
                 106435: 'Klaus an der Pyhrnbahn',
                 106559: 'Steyr',
                 106856: 'Weitersfelden-Ritzenedt',
                 107029: 'Lunz am See',
                 107284: 'Melk',
                 107854: 'Hollabrunn',
                 108118: 'Wien (Botanischer Garten)',
                 108456: 'Gutenstein',
                 108563: 'Naglern',
                 109280: 'Waidhofen an der Thaya',
                 109918: 'Neunkirchen',
                 110064: 'Gattendorf',
                 110312: 'Karl',
                 110734: 'Eisenstadt',
                 111112: 'Oberwart',
                 111435: 'Alpl',
                 111716: 'Judenburg',
                 112086: 'Graz-Andritz',
                 112391: 'St.Peter am Ottersbach',
                 112995: 'Ried im Innkreis',
                 113001: 'Sillian',
                 113050: 'Matrei in Osttirol',
                 113548: 'Afritz',
                 113670: 'Waidegg',
                 114561: 'Klagenfurt',
                 114702: 'Wolfsberg',
                 115055: 'Kendlbruck',
                 115642: 'St.Pölten',
                 120022: 'Hall in Tirol'}


def _get_file(id_):
    """
    get the file of the series of the station

    Args:
        id_ (int): Gitterpunktnummer (id number) of the station

    Returns:
        TextIOWrapper | IOBase:
    """
    url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=2'.format(id=id_)
    r = requests.get(url, allow_redirects=True)
    c = r.content
    if c != b'':
        z = ZipFile(BytesIO(c))
        filename = z.namelist()[0]
        csv_file = TextIOWrapper(z.open(filename), encoding='iso8859')
        return csv_file


def _read_file(filepath_or_buffer):
    """
    read the file

    Args:
        filepath_or_buffer (IOBase | str): file of the series or path to the local file

    Returns:
        IOBase: file of the series
    """
    if isinstance(filepath_or_buffer, str):
        return codecs.open(filepath_or_buffer, 'r', encoding='iso8859')
    elif isinstance(filepath_or_buffer, IOBase):
        return filepath_or_buffer
    else:
        raise NotImplementedError()


def _split_file(file):
    """
    split the file in meta-data and series-data

    Args:
        file (IOBase): file of the series

    Returns:
        (list, list): meta-data and time-series-data
    """
    lines = file.readlines()
    file.close()

    items = {':': 2,
             '.': 2,
             ';': 1,
             ',': 1}
    i = 0
    for i, line in enumerate(lines):
        if all([line.count(s) == n for s, n in items.items()]):
            break

    meta = lines[:i]
    data = lines[i:]
    return meta, data


def parse_ehyd_file(filepath_or_buffer, series_label='precipitation', index_label='datetime'):
    """

    Args:
        filepath_or_buffer (IOBase | str):
        series_label (str):
        index_label (str):

    Returns:
        (list, pandas.Series): meta-data and time-series
    """
    csv_file = _read_file(filepath_or_buffer)

    # ___________________________
    meta, data = _split_file(csv_file)

    # ___________________________
    ts = pd.read_csv(StringIO('\n'.join(data).replace(' ', '')), sep=';', decimal=',', index_col=0, na_values='Lücke',
                     header=None, squeeze=True, names=[series_label],
                     date_parser=lambda s: pd.to_datetime(s, format='%d.%m.%Y%H:%M:%S')
                     )

    # ___________________________
    ts.index.name = index_label
    # ts = ts.rename_axis(index_label, axis='index')
    return meta, ts


def _parse(filepath_or_buffer, series_label='precipitation', index_label='datetime', with_meta=False):
    """

    Args:
        filepath_or_buffer (IOBase | str):
        series_label (str):
        index_label (str):
        with_meta (bool): whether to return meta data or not

    Returns:
        pandas.Series | (pandas.Series, pandas.Series):
    """
    meta, ts = parse_ehyd_file(filepath_or_buffer, series_label=series_label, index_label=index_label)

    freq = guess_freq(ts.index)
    ts = ts.resample(freq).ffill()

    # ___________________________
    if with_meta:
        # meta = '\n'.join(meta)
        meta = pd.Series(meta).str.replace('\n', '').str.split(';', expand=True).fillna('').apply(
            lambda x: x.str.strip())
        return ts, meta

    else:
        return ts


def get_station(id_):
    """
    get the name of the station based on the id number

    Args:
        id_ (int): number

    Returns:
        str: name of the station
    """
    return ehyd_stations[id_]


def get_all_stations():
    """
    print all station names and ids
    """
    for id, location in ehyd_stations:
        print(id, ':', location)


def get_series(id_, with_meta=False):
    """
    get the series from the ehyd platform

    Args:
        id_ (int): number
        with_meta (bool): whether to return meta data or not

    Returns:
        pandas.Series | list[pandas.Series, str]: mata or data with the meta-data
    """
    if id_ in ehyd_stations:
        print('You choose the station: "{}" with the id: "{}".'.format(get_station(id_), id_))
    return _parse(_get_file(id_), with_meta=with_meta)


def get_station_meta(id_):
    """
    get the station meta data

    Args:
        id_ (int):

    Returns:
        str:
    """
    url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=1'.format(id=id_)
    r = requests.get(url, allow_redirects=True)
    c = r.content
    if c != b'':
        file = TextIOWrapper(BytesIO(c), encoding='iso8859')
        return file.read()


# if __name__ == '__main__':
# print(pd.Series(ehyd_stations).to_string())
# import time
# NOW = time.time()
# print('{:0.0f}'.format(time.time() - NOW))
# print(get_series(105445))
# print('{:0.0f}'.format(time.time() - NOW))
