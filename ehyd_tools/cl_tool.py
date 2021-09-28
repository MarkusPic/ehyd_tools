__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from pandas import to_datetime, DataFrame, Series
from os import path
import json
from webbrowser import open as show_file
from .data_processing import (data_validation, data_availability, max_10a, check_period, rain_plot, create_statistics,
                              start_end_date, )
from .arg_parser import ehyd_arg_parser
from .in_out import (get_ehyd_data, import_series, export_series, csv_args, get_station_reference_data, FIELDS,
                     get_basic_station_meta, DATA_KIND, )
from .sww_utils import span_table


def convert_time(time=None, helper=''):
    try:
        return to_datetime(time)
    except ValueError():
        raise UserWarning('Wrong time format for the {} time. Use the format="YYYY-MM-DD"'.format(helper))


def output_filename(fn):
    if '/' in fn or '\\' in fn:
        message = 'in the file "{}"'
    else:
        message = 'in the current working directory as "{}"'

    return message.format(fn)


def execute_cl_tool():
    """execute the command line tool"""
    # parse command line arguments
    args = ehyd_arg_parser()
    # convert argparse object to dict
    args_dict = vars(args).copy()
    args_dict['id_'] = args.id
    del args_dict['id']
    args_dict['input_'] = args.input
    del args_dict['input']
    run_script(**args_dict)


def get_data(id_=None, input_=None, meta=False, unix=False):
    """
    get time-series data with its name

    Args:
        id_ (str | int): ID-number of the series to be downloaded
        input_ (str): filename of the series to be imported
        meta (bool): if the meta data should be saved as txt file
        unix (bool): if the <input_> file is a csv-file: True={sep=',', decimal='.'} False={sep=';', decimal=','}

    Returns:
        (pandas.Series, str): precipitation series and the label of the series
    """
    if id_ is not None:
        id_number = id_
        name = 'ehyd_{}'.format(id_number)

        print(f'You choose the id: "{id_number}" with the meta-data: {get_basic_station_meta(id_number, field=FIELDS.NIEDERSCHLAG)}.')

        if meta:
            with open('{}_meta.json'.format(name), 'w') as f:
                json.dump(get_station_reference_data(id_number, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT), f, indent=4)
                print('The meta-data are saved in {}.'.format(output_filename(f.name)))

        series = get_ehyd_data(id_number, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)

    # __________________________________________________________________________________________________________________
    elif input_ is not None:
        fn = input_
        series = import_series(fn, unix=unix)
        print('The data in "{}" were imported and are used as the precipitation time-series.'.format(fn))
        name = path.basename(fn).split('.')[0]

    # __________________________________________________________________________________________________________________
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    print('The selected time-series starts at "{:%Y-%m-%d}" and ends at "{:%Y-%m-%d}".'.format(*start_end_date(series)))

    return series, name


def run_script(start=None, end=None, id_=None, input_=None, meta=False, max10a=False, add_gaps=True, statistics=False,
               to_csv=False, to_parquet=False, plot=False, unix=False):
    # __________________________________________________________________________________________________________________
    if start is not None:
        start = convert_time(start, 'start')

    # __________________________________________________________________________________________________________________
    if end is not None:
        end = convert_time(end, 'end')

    # __________________________________________________________________________________________________________________
    series, name = get_data(id_, input_, meta, unix)

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
        print('The time-series is clipped to '
              'start at "{:%Y-%m-%d}" and end at "{:%Y-%m-%d}".'.format(*start_end_date(series)))

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

        gaps_fn = '{}_gaps.csv'.format(name)

        gaps.to_csv(gaps_fn, float_format='%0.3f', **csv_args(unix))

        print('The gaps table is saved {}.'.format(output_filename(gaps_fn)))

    # __________________________________________________________________________________________________________________
    if statistics:
        if tags is None:
            tags = data_validation(series)
        if availability is None:
            availability = data_availability(tags)

        availability_cut = 0.9

        stats = create_statistics(series, availability, availability_cut=availability_cut)

        with open('{}_stats.txt'.format(name), 'w+') as f:
            rain_fmt = '{:0.0f} mm'
            date_fmt = '{:%Y}'
            avail_fmt = '{:0.0%}'

            f.write(
                'The annual totals of the data series serve as the data basis.\n'
                'The following statistics were analyzed:\n'
                'Only years with a availability of {avail} will be evaluated.\n'
                '\n'
                'The maximum is {rain} and was in the year {date} (with {avail} Data available).\n'
                'The minimum is {rain} and was in the year {date} (with {avail} Data available).\n'
                'The mean is {rain} (with {avail} Data available in average).'
                ''.format(rain=rain_fmt, date=date_fmt, avail=avail_fmt).format(availability_cut,
                                                                                *stats['maximum'],
                                                                                *stats['minimum'],
                                                                                *stats['mean'])
            )
            print('The statistics are saved {}.'.format(output_filename(f.name)))

    # __________________________________________________________________________________________________________________
    save_formats = list()
    if to_csv:
        save_formats.append('csv')
    if to_parquet:
        save_formats.append('parquet')

    for save_as in save_formats:
        out_fn = export_series(series, filename=name, save_as=save_as, unix=unix)
        print('The time-series is saved {}.'.format(output_filename(out_fn)))

    # __________________________________________________________________________________________________________________
    if plot:
        if tags is None:
            tags = data_validation(series)
        if availability is None:
            availability = data_availability(tags)

        plot_fn = '{}_plot.png'.format(name)
        rain_plot(series, availability, plot_fn)
        print('The plot is saved {}.'.format(output_filename(plot_fn)))
        show = True
        if show:
            show_file(plot_fn)
