__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

from pandas import Timedelta, DataFrame, isna
from numpy import NaN
from pandas.tseries.offsets import _delta_to_tick as delta_to_freq
from warnings import warn
from matplotlib.pyplot import subplots


def year_delta(years):
    """
    return a timedelta object for a given number of years

    :type years: float
    :param years: number of years

    :return: time period
    :rtype: pd.Timedelta
    """
    return Timedelta(days=365.25) * years


def data_validation(series):
    """
    add gaps sum & nan sum to the time series

    :type series: pd.Series
    :param series:

    :return: tags with columns 'nans', 'gaps', ...
    :rtype: pd.DataFrame
    """
    tags = DataFrame(index=series.index)
    tags['nans'] = isna(series).astype(int)
    tags['gaps'] = isna(series.fillna(0).resample('T').sum()).astype(int)
    return tags


def data_availability(tags):
    """

    :param tags: errors tagged as true
    :type tags: pd.DataFrame

    :return: availability
    :rtype: pd.Series
    """
    return ~tags.any(axis=1)


def max_10a(availability):
    """
    get the minimal gaps and minimal nan
    and take the latest possible time span

    :param availability: series with available data tagged as True
    :type availability: pd.Series[True]

    :rtype: list[pd.datetime]
    :return: start & end time of most available time span
    """
    window = delta_to_freq(year_delta(years=10))
    avail_sum = availability.rolling(window).sum()

    maximums = avail_sum == avail_sum.max()

    end = maximums.index[-1]
    start = end.replace(year=end.year - 10)
    return start, end


def check_period(series):
    """
    calculate the period of the series

    :param series: data
    :type series: pd.Series

    :return: period of the series
    :rtype: pd.Timedelta
    """
    if not is_longer(series, years=9.99):
        warn('Series not longer than 10 years!')


def is_longer(series, years):
    """
    calculate the period of the series

    :param series: data
    :type series: pd.Series

    :param years: number of years
    :type years: float

    :return: whether the series is longer
    :rtype: bool
    """
    return (series.index[-1] - series.index[0]) > year_delta(years=years)


def rain_plot(series, fn):
    """
    monthly sum bar plot

    :param series: data
    :type series: pd.Series

    :param fn: path + filename of the resulting plot
    :type fn: str
    """

    if is_longer(series, years=15):
        freq = 'Y'
        freq_long = 'Year'
    else:
        freq = 'M'
        freq_long = 'Month'

    sums = series.resample(freq).sum()
    index = series.index.to_series().resample(freq).apply(lambda s: s.min() + abs(s.min() - s.max()) / 2).values

    dummy = sums.rename('dummy').copy()
    dummy.loc[:] = 0

    fig, ax = subplots()
    fig.set_size_inches(w=29.7 / 2.54, h=21. / 2.54)

    ax = dummy.plot(ax=ax, lw=0)
    ax.bar(index, sums.values, color='b')

    ax.set_ylabel('Niederschlag (mm/{})'.format(freq_long))
    ax.set_xlabel('Zeit')
    fig.tight_layout()
    fig.savefig(fn)


def statistics(series, availability, availability_cut=0.2):
    sums = series.resample('Y').sum()
    avail = availability.resample('Y').sum() / (year_delta(1) / series.index.freq)

    sums[avail < availability_cut] = NaN

    stats = dict()
    stats['max'] = (sums.max(), sums.idxmax(), avail.loc[sums.idxmax()])
    stats['min'] = (sums.min(), sums.idxmin(), avail.loc[sums.idxmin()])
    stats['mean'] = (sums.mean(), avail.mean())
    return stats
