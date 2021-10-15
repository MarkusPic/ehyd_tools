__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

import json
from os import path
from webbrowser import open as show_file

from argh import arg
from pandas import to_datetime

from .data_processing import (data_validation, data_availability, max_10a, check_period, agg_data_plot,
                              create_statistics, )
from .in_out import (get_ehyd_data, import_series, export_series, csv_args, get_station_reference_data, FIELDS,
                     get_basic_station_meta, DATA_KIND, )
from .sww_utils import span_table


def _convert_time(time=None, helper=''):
    try:
        return to_datetime(time)
    except ValueError():
        raise UserWarning('Wrong time format for the {} time. Use the format="YYYY-MM-DD"'.format(helper))


def _output_filename(fn):
    if '/' in fn or '\\' in fn:
        return f'in the file "{fn}"'
    else:
        return f'in the current working directory as "{fn}"'


@arg('--identifier', '-id', help='the id number for the station from the ehyd.gv.at platform')
@arg('--filename', '-fn', help='path to the rain input file including the filename')
@arg('--start', help='custom start time (Format="YYYY-MM-DD") for clipping the data')
@arg('--end', help='custom end time (Format="YYYY-MM-DD") for clipping the data')
@arg('--max10a', help='consider only 10 years with the most availability (for clipping the data)')
@arg('--add_gaps', help='save a gaps-table as a csv-file')
@arg('--to_csv', help='save the time-series as csv-file '
                      '(to the current directory if the id is used or in the directory of the input-file)')
@arg('--to_parquet', help='save the time-series as parquet-file '
                          '(to the current directory if the id is used or in the directory of the input-file)'
                          ' - parquet is a much faster as csv to read and write')
@arg('--plot', help='save a bar-plot with monthly sums and availability as a png-file')
@arg('--statistics', help='save the basic statistics (sum, max & min) as a txt-file')
@arg('--meta', help='save the meta-data presented in ehyd as a txt-file')
@arg('--unix', help='export the csv files with a "," as separator and a "." as decimal sign '
                    '(otherwise ";" as separator and a "," as decimal sign will be used)')
@arg('--availability_cut', help='minimum percentage of availability of data to take account in the aggregations '
                                'in the statistics')
@arg('--agg', help='aggregation for the plot i.e.: "sum", "mean", "median", ...')
@arg('--field', help='field of the observation [NIEDERSCHLAG, QUELLEN, GRUNDWASSER, OBERFLAECHENWASSER]',
     choices=[FIELDS.NIEDERSCHLAG, FIELDS.QUELLEN, FIELDS.GRUNDWASSER, FIELDS.OBERFLAECHENWASSER])
def run_script(identifier=None, filename=None, start=None, end=None, max10a=False, add_gaps=True,
               to_csv=False, to_parquet=False, plot=False, statistics=False, meta=False, unix=False,
               availability_cut=0.9, agg='sum', field=FIELDS.NIEDERSCHLAG):
    """
    get eHYD.gv.at data and run simple analysis on it and finally save the data to a local file.
    """
    # __________________________________________________________________________________________________________________
    if start is not None:
        start = _convert_time(start, 'start')

    # __________________________________________________________________________________________________________________
    if end is not None:
        end = _convert_time(end, 'end')

    # __________________________________________________________________________________________________________________
    if identifier is not None:
        name = f'ehyd_{field}_{identifier}'

        print(
            f'You choose the id: "{identifier}" with the meta-data: '
            f'{get_basic_station_meta(identifier, field=field)}.')

        if meta:
            with open('{}_meta.json'.format(name), 'w') as f:
                json.dump(
                    get_station_reference_data(identifier, field=field, data_kind=DATA_KIND.MEASUREMENT),
                    f, indent=4)
                print('The meta-data are saved in {}.'.format(_output_filename(f.name)))

        series = get_ehyd_data(identifier, field=field, data_kind=DATA_KIND.MEASUREMENT)

    # __________________________________________________________________________________________________________________
    elif filename is not None:
        series = import_series(filename, unix=unix)
        print(f'The data in "{filename}" were imported and are used as the precipitation time-series.')
        name = path.basename(filename).split('.')[0]

    # __________________________________________________________________________________________________________________
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    print(f'The selected time-series start at "{series.index[0]:%Y-%m-%d}" and ends at "{series.index[0]:%Y-%m-%d}".')

    # __________________________________________________________________________________________________________________
    series = series[start:end].copy()
    check_period(series)

    # ______________________________________________________
    tags = None
    availability = None

    # __________________________________________________________________________________________________________________
    if max10a:
        tags = data_validation(series)
        availability = data_availability(tags)
        start, end = max_10a(availability)
        series = series.loc[start:end].copy()
        check_period(series)

    if start or end or max10a:
        print(
            f'The time-series is clipped to start at "{series.index[0]:%Y-%m-%d}" and end at "'
            f'{series.index[0]:%Y-%m-%d}".')

    # __________________________________________________________________________________________________________________
    if add_gaps:
        if tags is None:
            tags = data_validation(series)
        if availability is None:
            availability = data_availability(tags)

        gaps = span_table(~availability)
        gaps['delta'] = (gaps['end'] - gaps['start']).dt.total_seconds() / (60 * 60 * 24)
        gaps = gaps.sort_values('delta', ascending=False)
        gaps.columns = ['start', 'end', 'gaps in days']

        gaps_fn = f'{name}_gaps.csv'

        gaps.to_csv(gaps_fn, float_format='%0.3f', **csv_args(unix))

        print(f'The gaps table is saved {_output_filename(gaps_fn)}.')

    # __________________________________________________________________________________________________________________
    if statistics:
        if tags is None:
            tags = data_validation(series)
        if availability is None:
            availability = data_availability(tags)

        stats = create_statistics(series, availability, availability_cut=availability_cut)

        with open('{}_stats.txt'.format(name), 'w+') as f:
            rain_fmt = '{:0.0f} mm'
            date_fmt = '{:%Y}'
            avail_fmt = '{:0.0%}'

            f.write(
                f'The annual totals of the data series serve as the data basis.\n'
                f'The following statistics were analyzed:\n'
                f'Only years with a availability of {availability_cut:{avail_fmt}} will be evaluated.\n'
                f'\n'
                f'The maximum is {stats["maximum"]:{rain_fmt}} and was in the year {stats["maximum_date"]:{date_fmt}} '
                f'(with {stats["maximum_avail"]:{avail_fmt}} Data available).\n'
                f'The minimum is {stats["minimum"]:{rain_fmt}} and was in the year {stats["minimum_date"]:{date_fmt}} '
                f'(with {stats["minimum_avail"]:{avail_fmt}} Data available).\n'
                f'The mean is {stats["mean"]:{rain_fmt}} '
                f'(with {stats["mean_avail"]:{avail_fmt}} Data available in average).')

            print(f'The statistics are saved {_output_filename(f.name)}.')

    # __________________________________________________________________________________________________________________
    save_formats = list()
    if to_csv:
        save_formats.append('csv')
    if to_parquet:
        save_formats.append('parquet')

    for save_as in save_formats:
        out_fn = export_series(series, filename=name, save_as=save_as, unix=unix)
        print(f'The time-series is saved {_output_filename(out_fn)}.')

    # __________________________________________________________________________________________________________________
    if plot:
        if tags is None:
            tags = data_validation(series)
        if availability is None:
            availability = data_availability(tags)

        plot_fn = f'{name}_plot.png'
        agg_data_plot(series, availability, plot_fn, agg=agg)
        print(f'The plot is saved {_output_filename(plot_fn)}.')
        show = True
        if show:
            show_file(plot_fn)
