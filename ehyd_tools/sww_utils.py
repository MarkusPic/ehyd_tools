from pandas.tseries.frequencies import to_offset

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
    :type timedelta: pd.Timedelta

    :param monotonic: whether to look for time gaps or time setbacks
    :type monotonic: bool

    :return: start-time [start], end-time [end], duration of the gap [delta]
    :rtype: pd.DataFrame[start, end, delta]
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

    :param index: index of the bool series
    :type index: DatetimeIndex

    :param span_bool: len(span_bool)=len(index); "True"=Event
    :type span_bool: Series[bool] | list[bool]

    :param min_span: minimum time range of an event
    :type min_span: Timedelta

    :return: start-time [start], end-time [end], duration of the gap [delta]
    :rtype: DataFrame[start, end, delta]
    """
    span_bool[index[0]] = False
    span_bool[index[-1]] = False
    return time_delta_table(index[~span_bool[index]], timedelta=min_span, monotonic=False)


def guess_freq(date_time_index, default=pd.Timedelta(minutes=1)):
    """
    guess the frequency by evaluating the most often frequency

    Args:
        date_time_index (pandas.DatetimeIndex): index of a time-series
        default (pandas.Timedelta):

    Returns:
        DateOffset: frequency of the date-time-index
    """
    freq = date_time_index.freq
    if pd.notnull(freq):
        return to_offset(freq)

    if not len(date_time_index) <= 3:
        freq = pd.infer_freq(date_time_index)  # 'T'

        if pd.notnull(freq):
            return to_offset(freq)

        delta_series = date_time_index.to_series().diff(periods=1).fillna(method='backfill')
        counts = delta_series.value_counts()
        counts.drop(pd.Timedelta(minutes=0), errors='ignore')

        if counts.empty:
            delta = default
        else:
            delta = counts.index[0]
            if delta == pd.Timedelta(minutes=0):
                delta = default
    else:
        delta = default

    return to_offset(delta)