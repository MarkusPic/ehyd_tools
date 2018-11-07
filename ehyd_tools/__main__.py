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
from .in_out import get_series, import_series, export_series
from .sww_utils import span_table


def execute_tool():
    args = ehyd_parser()

    # for i, e in vars(args).items():
    #     print(i, ':', e)

    if args.id is not None:
        id_number = args.id
        series = get_series(id_number)
        name = 'ehyd_{}'.format(id_number)

    elif args.input is not None:
        fn = args.input
        series = import_series(fn)
        name = path.basename(fn).split('.')[0]
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    if args.start is not None:
        start = to_datetime(args.start)
        series = series[start:].copy()
        check_period(series)

    if args.end is not None:
        end = to_datetime(args.end)
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

    print('Data was clipped to start="{:%Y-%m-%d}" and end="{:%Y-%m-%d}".'.format(*series.index[[0, -1]].tolist()))

    if args.export is not None:
        out_dir = args.export
        export_series(series, out_dir)

    if args.add_gaps:
        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        gaps = span_table(availability.index, ~availability)
        gaps.to_csv('{}_gaps.csv'.format(name))

    if args.to_csv:
        series.to_csv('{}.csv'.format(name))

    if args.plot:
        rain_plot(series, '{}_plot.pdf'.format(name))


if __name__ == '__main__':
    execute_tool()