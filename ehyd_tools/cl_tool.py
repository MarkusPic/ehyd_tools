__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from pandas import to_datetime, DataFrame, Series
from os import path
from webbrowser import open as show_file
from .data_processing import data_validation, data_availability, max_10a, check_period, rain_plot, create_statistics
from .arg_parser import ehyd_arg_parser
from .in_out import get_series, import_series, export_series, csv_args, get_station_meta
from .sww_utils import span_table


def convert_time(time=None, helper=''):
    try:
        return to_datetime(time)
    except ValueError():
        raise UserWarning('Wrong time format for the {} time. Use the format="YYYY-MM-DD"'.format(helper))


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
    if id_ is not None:
        id_number = id_
        name = 'ehyd_{}'.format(id_number)

        if meta:
            with open('{}_meta.txt'.format(name), 'w') as f:
                f.write(get_station_meta(id_number))
                print('Meta-data written in "{}".'.format(f.name))

        series = get_series(id_number)

    # __________________________________________________________________________________________________________________
    elif input_ is not None:
        fn = input_
        series = import_series(fn, unix)
        print('Series "{}" was imported.'.format(fn))
        name = path.basename(fn).split('.')[0]
        print('The filename basis of the output files is "{}".'.format(name))

    # __________________________________________________________________________________________________________________
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    print('The original time series has the start at "{:%Y-%m-%d}"'
          ' and the end at "{:%Y-%m-%d}".'.format(*series.index[[0, -1]].tolist())
          )

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
    if start is not None:
        series = series[start:].copy()
        check_period(series)

    if end is not None:
        series = series[:end].copy()
        check_period(series)

    # __________________________________________________________________________________________________________________
    if max10a:
        tags = data_validation(series)
        availability = data_availability(tags)
        start, end = max_10a(availability)
        series = series.loc[start:end].copy()
        check_period(series)
    else:
        tags = DataFrame()
        availability = Series()

    print('Data was clipped to start="{:%Y-%m-%d}" and end="{:%Y-%m-%d}".'
          ''.format(*series.index[[0, -1]].tolist())
          )

    # __________________________________________________________________________________________________________________
    if add_gaps:
        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        gaps = span_table(~availability)
        gaps['delta'] = (gaps['end'] - gaps['start']).dt.total_seconds() / (60 * 60 * 24)
        gaps = gaps.sort_values('delta', ascending=False)
        gaps.columns = ['start', 'end', 'gaps in days']

        gaps_fn = '{}_gaps.csv'.format(name)

        gaps.to_csv(gaps_fn, float_format='%0.3f', **csv_args(unix))
        print('The gaps table was written in "{}".'.format(gaps_fn))

    # __________________________________________________________________________________________________________________
    if statistics:
        with open('{}_stats.txt'.format(name), 'w+') as f:

            if tags.empty:
                tags = data_validation(series)
            if availability.empty:
                availability = data_availability(tags)

            availability_cut = 0.9

            stats = create_statistics(series, availability, availability_cut=availability_cut)

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
            print('The statistics was written in the file "{}".'.format(f.name))

    # __________________________________________________________________________________________________________________
    if to_csv:
        out_fn = export_series(series, filename=name, save_as='csv', unix=unix)
        print('The time series was saved in the file "{}".'.format(out_fn))

    # __________________________________________________________________________________________________________________
    if to_parquet:
        out_fn = export_series(series, filename=name, save_as='parquet')
        print('The time series was saved in the file "{}".'.format(out_fn))

    # __________________________________________________________________________________________________________________
    if plot:

        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        plot_fn = '{}_plot.png'.format(name)
        rain_plot(series, availability, plot_fn)
        print('The plot was saved in the file "{}".'.format(plot_fn))
        show = True
        if show:
            show_file(plot_fn)
