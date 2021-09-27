__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import codecs
import json
import warnings
import io
import os
from zipfile import ZipFile

import pandas as pd
import requests
from pandas.errors import ParserError

from .sww_utils import guess_freq
from .deprecated import parse_meta_data

ENCODING = 'iso8859'


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
    elif os.path.isdir(pth):
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
    fn = os.path.join(check_path(export_path), '{}.{}'.format(filename, save_as))

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


# ######################################################################################################################
STATIONS_PRECIPITATION_HIGH_RES = json.load(open(os.path.join(os.path.dirname(__file__), 'ehyd_stations.json'), 'r', encoding='utf-8'))
"""Niederschlagsstationen mit Langzeitserie mit Minutensummen"""


def get_high_res_station(identifier):
    """
    get the name of the station based on the id number

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station

    Returns:
        str: name of the station
    """
    return STATIONS_PRECIPITATION_HIGH_RES[identifier]


class DATA_KIND:
    MEASUREMENT = 'MessstellenExtraData'
    DESIGN_PRECIPITATION = 'BemessungsniederschlagExtraData'


class FIELDS:
    NIEDERSCHLAG = 'nlv'
    QUELLEN = 'qu'
    GRUNDWASSER = 'gw'
    OBERFLAECHENWASSER = 'owf'
    PDF = 'pdf'


_path_file = os.path.dirname(__file__)
_stations_files = {FIELDS.NIEDERSCHLAG: 'niederschl_lufttemp_verdunst.csv',
                   FIELDS.QUELLEN: 'unteririsches_wasser.csv',
                   FIELDS.OBERFLAECHENWASSER: 'oberflaechenwasser.csv'}

EHYD_STATIONS = {k: pd.read_csv(os.path.join(_path_file, v), index_col=0, header=0).to_dict(orient='index') for k, v in _stations_files.items()}


def get_ehyd_stations(field=FIELDS.NIEDERSCHLAG):
    """
    Stationsinformationen wie: Mst. ID,Messstellen Name,Jahr,Bundesland,Flussgebiet,Seehöhe

    Args:
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)

    Returns:
        dict: Stationsinformationen
    """
    return EHYD_STATIONS[field]


def get_basic_station_meta(identifier, field=FIELDS.NIEDERSCHLAG):
    """
    Stationsinformationen wie: Mst. ID,Messstellen Name,Jahr,Bundesland,Flussgebiet,Seehöhe

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)

    Returns:
        dict: Stationsinformationen
    """
    return get_ehyd_stations(field)[identifier]


def _get_url(identifier, data_kind=DATA_KIND.MEASUREMENT, field=FIELDS.NIEDERSCHLAG, file_number=2):
    """
    get the URL to the specific file

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)
        file_number: 1 - ... (see available files with function `available_files`)

    Example-URLS:
        - https://ehyd.gv.at/eHYD/MessstellenExtraData/qu?id=395293&file=1
        - https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id=101063&file=1
        - https://ehyd.gv.at/eHYD/MessstellenExtraData/gw?id=325274&file=1
        - https://ehyd.gv.at/eHYD/MessstellenExtraData/owf?id=211912&file=2
        - https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData?id=4108
        - https://ehyd.gv.at/eHYD/BemessungsniederschlagExtraData/pdf?id=3499

    Returns:
        str: url to the file
    """
    url = f'https://ehyd.gv.at/eHYD/{data_kind}'
    if field:
        url += f'/{field}'
    url += f'?id={identifier}'
    if file_number:
        url += f'&file={file_number}'
    return url


_REQUESTS = dict()


def _get_request(identifier, data_kind=DATA_KIND.MEASUREMENT, field=FIELDS.NIEDERSCHLAG, file_number=1) -> requests.Response:
    """get request of website"""
    url = _get_url(identifier=identifier, field=field, file_number=file_number, data_kind=data_kind)
    if url not in _REQUESTS:
        _REQUESTS[url] = requests.get(url, allow_redirects=True)
    return _REQUESTS[url]


def _file_available(r: requests.Response) -> bool:
    """if any file is available in give request"""
    return 'content-disposition' in r.headers


def _get_filename(r: requests.Response) -> str:
    """get filename of request"""
    # h['content-disposition'] = 'attachment; filename=N-Minutensummen-112086.zip'
    return r.headers['content-disposition'].split('filename=')[1]


def available_files(identifier, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT):
    """
    get the file of the series of the station

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)

    Returns:
        dict[int, str]: dictionary of {file-number: file-name}
    """
    files = dict()
    for file_number in range(1, 15):
        r = _get_request(identifier=identifier, field=field, file_number=file_number, data_kind=data_kind)
        if _file_available(r):
            files[file_number] = _get_filename(r)
        else:
            break
    return files


def _get_file_from_request(r: requests.Response) -> (io.TextIOWrapper or io.IOBase):
    filename = _get_filename(r)
    if ('N-Minutensummen' in filename) and ('.zip' in filename):
        c = r.content
        z = ZipFile(io.BytesIO(c))
        filename = z.namelist()[0]
        csv_file = io.TextIOWrapper(z.open(filename), encoding=ENCODING)
        return csv_file
    elif ('.csv' in filename) or ('.txt' in filename):
        csv_file = io.TextIOWrapper(io.BytesIO(r.content), encoding=ENCODING)
        return csv_file


def _get_file(identifier, field=FIELDS.NIEDERSCHLAG, file_number=1, data_kind=DATA_KIND.MEASUREMENT):
    """
    get the file of the series of the station

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)
        file_number (int): file-number (>= 1)

    Returns:
        io.TextIOWrapper | io.IOBase:
    """
    r = _get_request(identifier=identifier, field=field, file_number=file_number, data_kind=data_kind)
    if _file_available(r):
        csv_file = _get_file_from_request(r)
        if csv_file is None:
            raise NotImplementedError('This kind of request is not implemented yet. Sorry!')
        return csv_file


def get_ehyd_files(identifier, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT):
    """
    get the files of the series of one station

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)

    Returns:
        dict: with key=filename and value=tuple(meta_data, timeseries_data)
    """
    files = dict()
    for file_number, filename in available_files(identifier, field=field, data_kind=data_kind).items():
        if file_number == 1:
            files[filename] = get_meta_data(identifier, field=field, data_kind=data_kind)
        else:
            r = _get_request(identifier=identifier, field=field, file_number=file_number, data_kind=data_kind)
            files[filename] = read_ehyd_file(_get_file_from_request(r))
    return files


def get_meta_data(identifier, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT):
    """
    get the station meta data

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)

    Returns:
        dict: meta data of station
    """
    # parse_meta_data(_get_file(identifier=identifier, field=field, file_number=1, data_kind=data_kind).read())
    return _get_file(identifier=identifier, field=field, file_number=1, data_kind=data_kind).read()


def _split_file(file):
    """
    split the file in meta-data and time-series-data

    Args:
        file (io.IOBase): file of the series

    Returns:
        (list, list): meta-data and time-series-data
    """
    lines = file.readlines()
    file.close()

    # items = {':': [2, ],
    #          '.': [2, ],
    #          ';': [1, ],
    #          ',': [0, 1]}
    # i = 0
    # for i, line in enumerate(lines):
    #     if all([line.count(s) in n for s, n in items.items()]):
    #         break

    i = lines.index('Werte:\n')

    meta = lines[:i]
    data = lines[i+1:]
    return meta, data


def read_ehyd_file(filepath_or_buffer, with_meta=False):
    """

    Args:
        filepath_or_buffer (io.IOBase | str):
        series_label (str):
        index_label (str):
        with_meta (bool): whether to return meta data or not

    Returns:
        (list, pandas.Series): meta-data and time-series
    """
    if isinstance(filepath_or_buffer, str):
        csv_file = codecs.open(filepath_or_buffer, 'r', encoding=ENCODING)
    elif isinstance(filepath_or_buffer, io.IOBase):
        csv_file = filepath_or_buffer
    else:
        raise NotImplementedError()

    # ___________________________
    meta, data = _split_file(csv_file)

    # ___________________________
    ts = pd.read_csv(io.StringIO('\n'.join(data).replace(' ', '')), sep=';', decimal=',', index_col=0,
                     na_values='Lücke', header=None, squeeze=True, # names=[series_label],
                     date_parser=lambda s: pd.to_datetime(s, format='%d.%m.%Y%H:%M:%S')
                     )

    if isinstance(ts, pd.DataFrame):
        ts = ts.dropna(axis=1, how='all')
        if ts.columns.size == 1:
            ts = ts.iloc[:, 0].copy()

    # ___________________________
    ts.index.name = 'datetime'
    # ts = ts.rename_axis(index_label, axis='index')

    freq = guess_freq(ts.index)
    ts = ts.resample(freq).ffill()

    # ___________________________
    if with_meta:
        # meta = '\n'.join(meta)
        meta = pd.Series(meta).str.replace('\n', '').str.split(';', expand=True).fillna('').apply(lambda x: x.str.strip())
        return ts, meta

    else:
        return ts


def get_ehyd_data(identifier, field=FIELDS.NIEDERSCHLAG, file_number=2, data_kind=DATA_KIND.MEASUREMENT, with_meta=False):
    """
    get the series from the ehyd platform

    Args:
        identifier (int): Gitterpunktnummer or HZBNR of the station
        field (str): nlv; qu; gw; owf (use constant struct: `FIELDS`)
        data_kind (str): MessstellenExtraData; BemessungsniederschlagExtraData (use constant struct: `DATA_KIND`)
        file_number (int): file-number (>= 1)
        with_meta (bool): whether to return meta data or not

    Returns:
        pandas.Series | list[pandas.Series, str]: mata or data with the meta-data
    """
    if identifier not in get_ehyd_stations(field):
        raise ValueError(f'Identifier "{identifier}" not in ehyd!')

    print(f'You choose the id: "{identifier}" with the meta-data: {get_basic_station_meta(identifier, field)}.')

    return read_ehyd_file(_get_file(identifier=identifier, field=field, file_number=file_number, data_kind=data_kind),
                          with_meta=with_meta)
