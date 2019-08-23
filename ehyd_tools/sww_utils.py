__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2018, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

from pandas.tseries.frequencies import to_offset
import pandas as pd

START = 'start'
END = 'end'


def _index_series(date_time_index):
    """create a time series from a datetime index without loosing the timezone info"""
    if isinstance(date_time_index, pd.DatetimeIndex) and date_time_index.tzinfo is not None:
        return pd.Series(data=date_time_index, index=date_time_index)
    else:
        return date_time_index.to_series()


def span_table(span_bool, min_span=None):
    """
    time span with consist "True" with a minimum span of <min_span> are the resulting events

    Args:
        span_bool (pandas.Series[bool]): "True"=Event
        min_span (pandas.Timedelta): minimum time range of an event (default=freq of index)

    Returns:
        pandas.DataFrame: with the columns:
            'start' = start-time,
            'end' = end-time,
    """
    index = span_bool.index

    # minimum duration which is considered as one event
    if min_span is None:
        min_span = guess_freq(index).delta  # TODO: Will not work on monthly or yearly data steps

    # pandas.Series with DatetimeIndex as index AND data
    temp = _index_series(index[span_bool])

    # first value in diff will default to NaN
    # fill value is set to double the value of the greater than operation = fixed true value
    start_bool = temp.diff().gt(min_span, fill_value=min_span * 2)
    end_bool = start_bool.shift(-1).fillna(True)

    events = pd.DataFrame()

    events[START] = temp[start_bool].index
    events[END] = temp[end_bool].index

    return events


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
