__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"


from pandas import to_datetime, DataFrame, Series
from os import path
from .data_processing import data_validation, data_availability, max_10a, check_period, rain_plot
from .arg_parser import ehyd_parser
from .in_out import get_series, import_series, export_series, csv_args
from .sww_utils import span_table


def execute_tool():
    args = ehyd_parser()

    # for i, e in vars(args).items():
    #     print(i, ':', e)

    if args.start is not None:
        try:
            start = to_datetime(args.start)
        except ValueError():
            raise UserWarning('Wrong time format for the start time. Use the format="YYYY-MM-DD"')
    else:
        start = None

    if args.end is not None:
        try:
            end = to_datetime(args.end)
        except ValueError():
            raise UserWarning('Wrong time format for the end time. Use the format="YYYY-MM-DD"')
    else:
        end = None

    if args.id is not None:
        id_number = args.id
        name = 'ehyd_{}'.format(id_number)

        if args.meta:
            series, meta = get_series(id_number, with_meta=args.meta)
            meta_fn = '{}_meta.txt'.format(name)
            stats_f = open(meta_fn, 'w+')
            stats_f.write(meta)
            stats_f.close()
            print('Meta-data written in "{}".'.format(meta_fn))

        else:
            series = get_series(id_number)

    elif args.input is not None:
        fn = args.input
        series = import_series(fn, args.unix)
        name = path.basename(fn).split('.')[0]

        print('Series "{}" was imported. The filename basis of the output files is "{}".'.format(fn, name))

    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    print('The original time series has the start at "{:%Y-%m-%d}" and the end at "{:%Y-%m-%d}".'
          ''.format(*series.index[[0, -1]].tolist())
          )

    if start is not None:
        series = series[start:].copy()
        check_period(series)

    if end is not None:
        series = series[:end].copy()
        check_period(series)

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

    if args.add_gaps:
        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        gaps = span_table(availability.index, ~availability)
        gaps['delta'] = gaps['delta'].dt.total_seconds() / (60*60*24)
        gaps = gaps.sort_values('delta', ascending=False)
        gaps.columns = ['start', 'end', 'gaps in days']

        gaps_fn ='{}_gaps.csv'.format(name)

        gaps.to_csv(gaps_fn, float_format='%0.3f', **csv_args(args.unix))
        print('The gaps table was written in "{}".'.format(gaps_fn))

    if args.statistics:
        stats_fn = '{}_stats.txt'.format(name)
        with open(stats_fn, 'w+') as f:

            sums = series.resample('Y').sum()
            max_ = sums.max()
            max_at = sums.idxmax()
            min_ = sums.min()
            min_at = sums.idxmin()
            mean_ = sums.mean()

            rain_fmt = '{:0.0f} mm'
            date_fmt = '{:%Y}'

            f.write(
                'The annual totals of the data series serve as the data basis.\n'
                'The following statistics were analyzed:\n'
                '\n'
                'The maximum is {rain} and was in the year {date}.\n'
                'The minimum is {rain} and was in the year {date}.\n'
                'The mean is {rain}.'.format(rain=rain_fmt, date=date_fmt).format(max_, max_at, min_, min_at, mean_)
            )
            f.close()
        print('The statistics was written in the file "{}".'.format(stats_fn))

    if args.to_csv:
        out_fn = name + '.csv'
        export_series(series, filename=name, save_as='csv', unix=args.unix)
        print('The time series was saved in the file "{}".'.format(out_fn))

    if args.plot:
        plot_fn = '{}_plot.png'.format(name)
        rain_plot(series, plot_fn)
        print('The plot was saved in the file "{}".'.format(plot_fn))


if __name__ == '__main__':
    execute_tool()
