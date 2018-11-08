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


def csv_args(unix=False):
    if unix:
        return dict(sep=',', decimal='.')
    else:
        return dict(sep=';', decimal=',')


def check_path(pth=None):
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

    :param export_path: path where file will be stored
    :type export_path: str

    :param filename: name of the file
    :type filename: str

    :type series: pd.Series

    :param save_as: export format
    :type save_as: str

    :param unix: whether to use "," or ";" for the csv
    :type unix: bool
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

    :param filename:
    :param series_label:
    :param index_label:
    :param unix: whether to use "," or ";" for the csv
    :type unix: bool
    :return:
    """
    if filename.endswith('csv'):
        try:
            ts = pd.read_csv(filename, index_col=0, header=None, squeeze=True, names=[series_label], **csv_args(unix))
            ts.index = pd.to_datetime(ts.index)
            ts.index.name = index_label
            return ts
        except ParserError:
            return _parse(filename)
    elif filename.endswith('parquet'):
        return pd.read_parquet(filename).iloc[:, 0].copy()
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

    :param id_:
    :return:
    """
    url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=2'.format(id=id_)
    r = requests.get(url, allow_redirects=True)
    c = r.content
    if c != b'':
        z = ZipFile(BytesIO(c))
        filename = z.namelist()[0]
        csv_file = TextIOWrapper(z.open(filename), encoding='iso8859')
        return csv_file


def _parse(filepath_or_buffer, series_label='precipitation', index_label='datetime', with_meta=False):
    """

    :param filepath_or_buffer:
    :param series_label:
    :param index_label:
    :return:
    """
    if isinstance(filepath_or_buffer, str):
        csv_file = codecs.open(filepath_or_buffer, 'r', encoding='iso8859')
    elif isinstance(filepath_or_buffer, IOBase):
        csv_file = filepath_or_buffer
    else:
        raise NotImplementedError()

    if with_meta:
        meta = []
    for line in csv_file:
        if line.startswith('Werte:'):
            break
        elif with_meta:
            meta.append(line)
    if with_meta:
        meta = pd.Series(meta).str.replace('\n', '').str.split(';', expand=True).fillna('').apply(lambda x: x.str.strip())
        # meta = ''.join(meta)

    f = csv_file.read().replace(' ', '').replace(',', '.')
    csv_file.close()
    ts = pd.read_csv(StringIO(f), sep=';', header=None, index_col=0, squeeze=True, names=[series_label],
                     na_values=['Lücke'], date_parser=lambda s: pd.to_datetime(s, format='%d.%m.%Y%H:%M:%S'))
    ts = ts.rename_axis(index_label, axis='index')
    ts = ts.resample('1T').ffill()

    if with_meta:
        return ts, meta
    else:
        return ts


def get_station(id_):
    """

    :param id_:
    :return:
    """
    return ehyd_stations[id_]


def get_all_stations():
    """

    :return:
    """
    for id, location in ehyd_stations:
        print(id, ':', location)


def get_series(id_, with_meta=False):
    """

    :param id_:
    :type id_: int

    :param with_meta: whether to return meta data or not
    :type with_meta: bool

    :return: data or data with the meta-data
    :rtype:  pd.Series | list[pd.Series, str]
    """
    if id_ in ehyd_stations:
        print('You choose the station: "{}" with the id: "{}".'.format(get_station(id_), id_))
    return _parse(_get_file(id_), with_meta=with_meta)


def get_station_meta(id_):
    """

    :param id_:
    :return:
    """
    url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=1'.format(id=id_)
    r = requests.get(url, allow_redirects=True)
    c = r.content
    if c != b'':
        file = TextIOWrapper(BytesIO(c), encoding='iso8859')
        return file.read()

# if __name__ == '__main__':
#     print(pd.Series(ehyd_stations).to_string())
#     NOW = time.time()
#     print('{:0.0f}'.format(time.time() - NOW))
#     get_series(105445)
#     print('{:0.0f}'.format(time.time() - NOW))
