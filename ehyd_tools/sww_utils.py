__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2018, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import pandas as pd


def time_delta_table(date_time_index, timedelta=pd.Timedelta(minutes=1), monotonic=False):
    """
    get the timedelta of data gaps in a dataframe

    :type date_time_index: pd.DatetimeIndex

    :param timedelta: at witch delta a gap is defined
    :type timedelta: Timedelta

    :param bool monotonic: whether to look for time gaps or time setbacks
    :return: start-time [start], end-time [end], duration of the gap [delta]
    :rtype: DataFrame[start, end, delta]
    """
    if isinstance(date_time_index, pd.DatetimeIndex) and date_time_index.tzinfo is not None:
        temp = pd.Series(data=date_time_index, index=date_time_index)
    else:
        temp = date_time_index.to_series()

    if monotonic:
        timedelta = pd.Timedelta(minutes=0)
        start = temp[temp.diff(periods=-1) > -timedelta]
        end = temp[temp.diff() < timedelta]

    else:
        start = temp[temp.diff(periods=-1) < -timedelta]
        end = temp[temp.diff() > timedelta]

    check = pd.concat([start.reset_index(drop=True), end.reset_index(drop=True)], axis=1, ignore_index=True)

    if monotonic:
        check.columns = ['time_of_reset', 'reset_to']
        check['delta'] = check['time_of_reset'] - check['reset_to']

    else:
        check.columns = ['start', 'end']
        check['delta'] = check['end'] - check['start']

    return check


def span_table(index, span_bool, min_span=pd.Timedelta(minutes=1)):
    """
    time span with consist "True" with a minimum span of <min_span> are the resulting events

    :type index: DatetimeIndex
    :param Series[bool]| list[bool] span_bool: len(span_bool)=len(index); "True"=Event
    :param Timedelta min_span: minimum time range of an event

    :return: start-time [start], end-time [end], duration of the gap [delta]
    :rtype: DataFrame[start, end, delta]
    """
    span_bool[0] = False
    span_bool[-1] = False
    return time_delta_table(index[~span_bool], timedelta=min_span, monotonic=False)

#
# def gap_table(data, min_gap=pd.Timedelta(minutes=1)):
#     """
#     time gaps with consist 'NaN' with a minimum span of <min_gap> are the resulting events
#
#     :type data: DataFrame | Series
#     :param Timedelta min_gap: minimum time range of an event
#
#     :return: start-time [start], end-time [end], duration of the gap [delta]
#     :rtype: DataFrame[start, end, delta]
#     """
#     if isinstance(data, pd.DataFrame):
#         index = data.dropna(axis=0, how='any').index.copy()
#     elif isinstance(data, pd.Series):
#         index = data.dropna().index.copy()
#     else:
#         raise NotImplementedError('Wrong data used in <gap_table>: DataFrame or Series - used "{}"'.format(type(data)))
#
#     # to see NaN gaps at the start and the end of the data
#     for i in data.index[[0, -1]]:
#         if i not in index:
#             index = index.append(pd.DatetimeIndex([i]))
#     index = index.sort_values()
#
#     return time_delta_table(index, timedelta=min_gap, monotonic=False)
