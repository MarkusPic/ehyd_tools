__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"


import pandas as pd
from .data_processing import import_series, export_series, data_validation, data_availability, max_10a
from .arg_parser import ehyd_parser
from .io import get_series
from .sww_utils import span_table


def execute_tool():
    args = ehyd_parser.parse_args()

    for i, e in vars(args).items():
        print(i, ':', e)

    if args.id is not None:
        id_number = args.id
        series = get_series(id_number)

    elif args.input is not None:
        fn = args.input
        series = import_series(fn)
    else:
        raise UserWarning('No data selected. Use either a input file or a id. See help menu.')

    if args.start is not None:
        start = pd.to_datetime(args.start)
        series = series[start:].copy()

    if args.end is not None:
        end = pd.to_datetime(args.end)
        series = series[:end].copy()

    if args.max10a:
        tags = data_validation(series)
        availability = data_availability(tags)
        start, end = max_10a(availability)
        series = series.loc[start:end].copy()
    else:
        tags = pd.DataFrame()
        availability = pd.Series()

    print('Data was clipped to start="{:%Y-%m-%d}" and end="{:%Y-%m-%d}".'.format(*series.iloc[[0, -1]].values))

    if args.export is not None:
        out_dir = args.export
        export_series(series, out_dir)

    if args.add_gaps:
        if tags.empty:
            tags = data_validation(series)
        if availability.empty:
            availability = data_availability(tags)

        gaps = span_table(~availability)
        gaps.to_csv('gaps.csv')

    if args.to_csv:
        series.to_csv('series.csv')

    if args.plot:
        ax = series.resample('AM').sum().plot()
        fig = ax.get_figure()
        # fig.set_size_inches()
        fig.tight_figure()
        fig.savefig('plot.pdf')
