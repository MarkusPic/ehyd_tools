import codecs
import datetime
import requests
from io import BytesIO, IOBase, StringIO
from pandas import DataFrame
from zipfile import ZipFile, is_zipfile
from numpy import NaN
import pandas as pd


def get_all_ehyd_stations_online():
    # 1456s / 975s last
    url_ = 'https://ehyd.gv.at/eHYD/MessstellenExtraData/nlv?id={id}&file=2'

    import dask.bag as db

    def t(i):
        url = url_.format(id=i)
        r = requests.get(url, allow_redirects=True)
        c = r.content
        if c != b'':
            b = BytesIO(c)
            if is_zipfile(b):
                # print(time.time() - NOW)
                z = ZipFile(b)
                filename = z.namelist()[0]
                # print(i, ':', filename)
                if filename.startswith('N-Minutensummen'):
                    # print('check')
                    return i
                    # print(i)
                # z = BytesIO(c).read()
                # print('_'*100, '\n', 'id =',i, '\n', c, '\n', z)

    id_range = range(100000, 130000)

    if 1:
        b = db.from_sequence(id_range, npartitions=8).map(t)
        b.compute(scheduler='processes')
    else:
        for i in id_range:
            t(i)


def _parse_time(x):
    return datetime.datetime.strptime(x, '%d.%m.%Y %H:%M:%S')


def _parse2(filepath_or_buffer, series_label='precipitation', index_label='datetime', **args):
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
        eol = '\r\n'
    elif isinstance(filepath_or_buffer, IOBase):
        eol = '\n'
        csv_file = filepath_or_buffer
    else:
        raise NotImplementedError()

    # print('start read')
    lines = list(map(lambda x: x.split(';'), csv_file.read().split(eol)))
    csv_file.close()
    tuples = []

    # l = len(lines)
    # pct = int(l / 100)
    # pct = 8000
    # print('_' + '_'*int(l / pct) + '_')
    # print('[', end='')

    # print('start parse')
    # i = 0
    for line in lines:
        # if i < pct:
        #     i += 1
        # else:
        #     print('#', end='')
        #     i = 0
        parsed = read_line(line)
        if parsed is not None:
            tuples.append(parsed)
    # print('] end parse')
    ts = DataFrame.from_records(tuples, columns=[index_label, series_label], index=index_label)[series_label]
    # last_minute=str(year)+"-12-31 23:59:00"
    # try:
    #     df.loc[last_minute]
    # except KeyError:
    #     df.loc[datetime.datetime(year,12,31,23,59,00)]=df.tail(1)
    ts = ts.resample('1T').ffill()
    return ts


def parse_meta_data(meta_info):
    meta_data = dict()
    subtable = False
    for line in meta_info:
        # if line.count(':') == 1:

        if subtable and line.startswith(' '):
            subtable_data.append(line)

        else:
            if subtable:
                subtable = False
                # d = [[i.strip().replace(':', '') for i in line.split(';')] for line in subtable_data]
                # d = pd.DataFrame(data=d[1:], columns=d[0]).infer_objects()
                d = pd.read_csv(StringIO(''.join(subtable_data)), sep=';')
                meta_data[head] = d

            d = [i.strip() for i in line.split(';')]
            l = len(d)

            if l == 1:
                head = d[0].replace(':', '')
                meta_data[head] = None
                subtable = True
                subtable_data = []
            elif l == 2:
                head = d[0].replace(':', '')
                if head in meta_data:
                    meta_data[head] = meta_data[head] + [d[1]] if isinstance(meta_data[head], list) else [
                        meta_data[head], d[1]]
                else:
                    if head == '':
                        head = list(meta_data.keys())[-1]
                        meta_data[head] = [meta_data[head], d[1]]
                    else:
                        meta_data[head] = d[1]
            else:
                meta_data[d[0].replace(':', '')] = d[1:]
