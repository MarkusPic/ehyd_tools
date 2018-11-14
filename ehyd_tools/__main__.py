__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from pandas import to_datetime, DataFrame, Series
from os import path
from webbrowser import open as show_file
from .data_processing import data_validation, data_availability, max_10a, check_period, rain_plot, statistics
from .arg_parser import ehyd_parser
from .in_out import get_series, import_series, export_series, csv_args, get_station_meta
from .sww_utils import span_table


def execute_tool():
    args = ehyd_parser()

    # __________________________________________________________________________________________________________________
    if args.start is not None:
        try:
            start = to_datetime(args.start)
        except ValueError():
            raise UserWarning('Wrong time format for the start time. Use the format="YYYY-MM-DD"')
    else:
        start = None

    # __________________________________________________________________________________________________________________
    if args.end is not None:
        try:
            end = to_datetime(args.end)
        except ValueError():
            raise UserWarning('Wrong time format for the end time. Use the format="YYYY-MM-DD"')
    else:
        end = None

    # __________________________________________________________________________________________________________________
    if args.id is not None:
        id_number = args.id
        name = 'ehyd_{}'.format(id_number)

        if args.meta:
            with open('{}_meta.txt'.format(name), 'w') as f:
                f.write(get_station_meta(id_number))
                print('Meta-data written in "{}".'.format(f.name))

        series = get_series(id_number)

    # __________________________________________________________________________________________________________________
    elif args.input is not None:
        fn = args.input
        series = import_series(fn, args.unix)
        print('Series "{}" was imported.'.format(fn))
        name = path.basename(fn).split('.')[0]
        print('The filename basis of the output files is "{}".'.format(name))

    # __________________________________________________________________________________________________________________
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    print('The original time series has the start at "{:%Y-%m-%d}"'
          ' and the end at "{:%Y-%m-%d}".'.format(*series.index[[0, -1]].tolist())
          )

    # __________________________________________________________________________________________________________________
    if start is not None:
        series = series[start:].copy()
        check_period(series)

    if end is not None:
        series = series[:end].copy()
        check_period(series)

    # __________________________________________________________________________________________________________________
    if args.max10a:
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
    if args.add_gaps:
        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        gaps = span_table(series.index, ~availability)
        gaps['delta'] = gaps['delta'].dt.total_seconds() / (60 * 60 * 24)
        gaps = gaps.sort_values('delta', ascending=False)
        gaps.columns = ['start', 'end', 'gaps in days']

        gaps_fn = '{}_gaps.csv'.format(name)

        gaps.to_csv(gaps_fn, float_format='%0.3f', **csv_args(args.unix))
        print('The gaps table was written in "{}".'.format(gaps_fn))

    # __________________________________________________________________________________________________________________
    if args.statistics:
        with open('{}_stats.txt'.format(name), 'w+') as f:

            if tags.empty:
                tags = data_validation(series)
            if availability.empty:
                availability = data_availability(tags)

            availability_cut = 0.9

            stats = statistics(series, availability, availability_cut=availability_cut)

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
    if args.to_csv:
        out_fn = export_series(series, filename=name, save_as='csv', unix=args.unix)
        print('The time series was saved in the file "{}".'.format(out_fn))

    # __________________________________________________________________________________________________________________
    if args.to_parquet:
        out_fn = export_series(series, filename=name, save_as='parquet')
        print('The time series was saved in the file "{}".'.format(out_fn))

    # __________________________________________________________________________________________________________________
    if args.plot:

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

# ______________________________________________________________________________________________________________________
if __name__ == '__main__':
    execute_tool()
