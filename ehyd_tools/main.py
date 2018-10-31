__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from .data_processing import *
from .arg_parser import ehyd_parser
from .io import get_series


def execute_tool():
    args = ehyd_parser.parse_args()

    for i, e in vars(args).items():
        print(i, ':', e)

    if args.id_number is not None:
        id = args.id_number
        series = get_series(id)
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
        print('max10a')

    if args.export is not None:
        out_dir = args.export
        export_series(series, out_dir)

    if args.add_gaps:
        print('add_gaps')

    if args.to_csv:
        print('to_csv')

    if args.plot:
        print('plot')
