__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import codecs
import datetime
import requests
from io import BytesIO, TextIOWrapper, IOBase
from pandas import DataFrame
from zipfile import ZipFile
from numpy import NaN
from os import path
import pandas as pd
from pandas.errors import ParserError


def export_series(series, export_path=None, save_as='csv'):
    """
    export the series to a given format
    may be extended

    :param export_path: path where file will be stored
    :type export_path: str

    :type series: pd.Series
    :param save_as: export format
    :type save_as: str
    """
    if save_as is 'csv':
        if path.isdir(export_path):
            pass
        else:
            raise UserWarning('Path is not available')

        series.to_csv(path.join(export_path, '{}.csv'.format(series.name)))
    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')


def import_series(filename, series_label='precipitation', index_label='datetime'):
    if filename.endswith('csv'):
        try:
            ts = pd.read_csv(filename, index_col=0, header=None, squeeze=True, names=[series_label])
            ts.index = pd.to_datetime(ts.index)
            ts.index.name = index_label
            return ts
        except ParserError:
            return _parse(filename)
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


def _get_file(id):
    url = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=2'.format(id=id)
    r = requests.get(url, allow_redirects=True)
    z = ZipFile(BytesIO(r.content))
    csv_file = TextIOWrapper(z.open(z.namelist()[0]), encoding='iso8859')
    return csv_file


def _parse_time(x):
    return datetime.datetime.strptime(x, '%d.%m.%Y %H:%M:%S')


def _parse(filepath_or_buffer, series_label='precipitation', index_label='datetime', **args):
    # bn = os.path.basename(path)

    # print(path)
    # year=int(bn[bn.find('_')+1:bn.rfind('-')])
    def read_line(line):
        try:
            time = _parse_time(line[0].strip())
            # if time.year !=year:
            #    return None
            val = line[1].strip()
            if val == 'Lücke':
                value = NaN
            else:
                value = float(val.replace(',', '.'))
            return time, value
        except ValueError as e:
            if str(e).startswith("time data"):
                return None
            else:
                raise e

    if isinstance(filepath_or_buffer, str):
        csv_file = codecs.open(filepath_or_buffer, 'r', encoding='iso8859')
        eof = '\r\n'
    elif isinstance(filepath_or_buffer, IOBase):
        eof = '\n'
        csv_file = filepath_or_buffer
    else:
        raise NotImplementedError()

    print('start read')
    lines = list(map(lambda x: x.split(';'), csv_file.read().split(eof)))
    csv_file.close()
    tuples = []

    l = len(lines)
    pct = int(l / 100)
    # pct = 8000
    print('_' + '_'*int(l / pct) + '_')
    print('[', end='')

    # print('start parse')
    i = 0
    for line in lines:
        if i < pct:
            i += 1
        else:
            print('#', end='')
            i = 0
        parsed = read_line(line)
        if parsed is not None:
            tuples.append(parsed)
    print('] end parse')
    ts = DataFrame.from_records(tuples, columns=[index_label, series_label], index=index_label)[series_label]
    # last_minute=str(year)+"-12-31 23:59:00"
    # try:
    #     df.loc[last_minute]
    # except KeyError:
    #     df.loc[datetime.datetime(year,12,31,23,59,00)]=df.tail(1)
    ts = ts.resample('1T').ffill()
    return ts


def get_station(id):
    return ehyd_stations[id]


def get_all_stations():
    for id, location in ehyd_stations:
        print(id, ':', location)


def get_series(id):
    if id in ehyd_stations:
        print('You choose the station: "{}" with the id: "{}".'.format(get_station(id), id))
    return _parse(_get_file(id))


# if __name__ == '__main__':
#     get_series(105445)
