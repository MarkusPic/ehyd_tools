__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import codecs
import json
import warnings
from io import BytesIO, TextIOWrapper, IOBase, StringIO
from os import path
from zipfile import ZipFile

import pandas as pd
import requests
from pandas.errors import ParserError

from .sww_utils import guess_freq

# import numba
# warnings.filterwarnings("ignore", category=numba.NumbaDeprecationWarning)


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


PARQUET_ERROR = ModuleNotFoundError("""Error: Unable to find a usable engine to read or write parquet files.
A suitable version of pyarrow (recommended) or fastparquet (alternative) is required for parquet support.
Use pip or conda to install:
- pyarrow (https://pypi.org/project/pyarrow/) or 
- fastparquet (https://pypi.org/project/fastparquet/).""")


def export_series(series, filename, export_path=None, save_as='csv', unix=False):
    """
    export the series to a given format
    may be extended

    Args:
        series (pandas.Series):
        filename (str): name of the file
        export_path (str): path where the file will be stored.
        save_as (str): export format
        unix (bool): whether to use "," or ";" for the csv

    Returns:
        str: path to created file
    """
    fn = path.join(check_path(export_path), '{}.{}'.format(filename, save_as))

    if save_as == 'csv':
        series.to_csv(fn, **csv_args(unix))

    elif save_as == 'parquet':
        try:
            series.to_frame().to_parquet(fn)
        except ImportError:
            raise PARQUET_ERROR

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
            ts = pd.read_csv(filename, index_col=0, header=0, squeeze=True, **csv_args(unix))
            ts.index = pd.to_datetime(ts.index)
            ts.name = series_label
            ts.index.name = index_label
            return ts
        except (ParserError, UnicodeDecodeError):
            return _parse(filename)
    elif filename.endswith('parquet'):
        try:
            return pd.read_parquet(filename).iloc[:, 0].asfreq('T').copy()
        except ImportError:
            raise PARQUET_ERROR
    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')


ehyd_stations = json.load(open(path.join(path.dirname(__file__), 'ehyd_stations.json'), 'r', encoding='utf-8'))


class DATA_KIND:
    MEASUREMENT = 'MessstellenExtraData'
    DESIGN_PRECIPITATION = 'BemessungsniederschlagExtraData'


class FIELDS:
    NIEDERSCHLAG = 'nlv'
    QUELLEN = 'qu'
    GRUNDWASSER = 'gw'
    OBERFLAECHENWASSER = 'ofw'
    PDF = 'pdf'


def get_url(identifier, data_kind=DATA_KIND.MEASUREMENT, field=FIELDS.NIEDERSCHLAG, file_number=2):
    """
    data_kind = MessstellenExtraData; BemessungsniederschlagExtraData
    field = nlv; qu; gw; owf
    file_number = 1

    https://ehyd.gv.at/eHYD/MessstellenExtraData/qu?id=395293&file=1
    https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id=101063&file=1
    https://ehyd.gv.at/eHYD/MessstellenExtraData/gw?id=325274&file=1
    https://ehyd.gv.at/eHYD/MessstellenExtraData/owf?id=211912&file=2
    https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData?id=4108
    https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData/pdf?id=3499
    """
    url = f'https://ehyd.gv.at/eHYD/{data_kind}'
    if field:
        url += f'/{field}'
    url += f'?id={identifier}'
    if file_number:
        url += f'&file={file_number}'
    return url


def _get_file(id_):
    """
    get the file of the series of the station

    Args:
        id_ (int): Gitterpunktnummer (id number) of the station

    Returns:
        TextIOWrapper | IOBase:
    """
    url = get_url(identifier=id_, field=FIELDS.NIEDERSCHLAG, file_number=2, data_kind=DATA_KIND.MEASUREMENT)
    # url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=2'.format(id=id_)
    r = requests.get(url, allow_redirects=True)
    h = r.headers
    if 'content-disposition' in h:
        # h['content-disposition'] = 'attachment; filename=N-Minutensummen-112086.zip'
        filename = h['content-disposition'].split('filename=')[1]
        if ('N-Minutensummen' not in filename) or ('.zip' not in filename):
            raise NotImplementedError('This kind of request is not implemented yet. Sorry!')
        c = r.content
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
    url = get_url(identifier=id_, field=FIELDS.NIEDERSCHLAG, file_number=1, data_kind=DATA_KIND.MEASUREMENT)
    # url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=1'.format(id=id_)
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
