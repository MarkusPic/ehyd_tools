from matplotlib.gridspec import GridSpec

__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

from pandas import Timedelta, DataFrame, isna, DatetimeIndex, Series
from numpy import NaN
from pandas.tseries.offsets import _delta_to_tick as delta_to_freq
from warnings import warn
from matplotlib.pyplot import subplots, subplot


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
    ts = series.copy()
    ts = ts.append(Series(index=[ts.index[0].replace(day=1, month=1, hour=0, minute=0),
                                 ts.index[-1].replace(day=31, month=12, hour=23, minute=59)],
                          data=[NaN, NaN])).sort_index()

    tags = DataFrame(index=ts.index)
    tags['nans'] = isna(ts).astype(int)
    tags = tags.reindex(tags.asfreq('T').index)
    tags['gaps'] = isna(ts.fillna(0).reindex(tags.index)).astype(int)
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


def rain_plot(series, availability, fn):
    """
    monthly sum bar plot

    :param series: data
    :type series: pd.Series

    :param fn: path + filename of the resulting plot
    :type fn: str
    """

    if is_longer(series, years=15):
        freq = 'Y'
        freq_long = 'Jahr'
        # base_delta = year_delta(1)
    else:
        freq = 'M'
        freq_long = 'Monat'
        # base_delta = year_delta(1) / 12

    sums = series.resample(freq).sum()
    index = series.index.to_series().resample(freq).apply(lambda s: s.min() + abs(s.min() - s.max()) / 2).dt.date.values
    freq_avail = availability.resample(freq)
    avail = (freq_avail.sum()/ freq_avail.count())[sums.index]

    dummy = sums.rename('dummy').copy()
    dummy.loc[:] = 0

    height_ratios = [1, 10]

    fig, (ax1, ax) = subplots(2, gridspec_kw=dict(height_ratios=height_ratios), sharex=True)

    ax = dummy.plot(ax=ax, lw=0)
    fig.set_size_inches(w=29.7 / 2.54, h=21. / 2.54)

    ax1.set_ylim(0, 100)
    ax1.set_ylabel('% Verfügbar')
    ax1.set_yticks(range(0,110,10), minor=True)
    ax1.grid(axis='y', which='minor', color='lightgrey', linestyle=':', linewidth=0.5)  # , zorder=-10000000)
    ax1 = dummy.plot(ax=ax1, lw=0)
    # ax1.scatter(x=index, y=avail.values * 100, color='grey', clip_on=False, marker='_')
    ax1.bar(x=index, height=avail.values*100, color='grey')
    ax1.set_axisbelow(True)

    ax.bar(x=index, height=sums.values, color='k')
    ax.set_ylabel('Niederschlag (mm/{})'.format(freq_long))
    ax.set_xlabel('Zeit')
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    # fig.show()
    fig.savefig(fn)


def statistics(series, availability, availability_cut=0.2):
    sums = series.resample('Y').sum()
    avail = availability.resample('Y').sum() / (year_delta(1) / series.index.freq)

    sums[avail < availability_cut] = NaN

    stats = dict()
    stats['maximum'] = (sums.max(), sums.idxmax(), avail.loc[sums.idxmax()])
    stats['minimum'] = (sums.min(), sums.idxmin(), avail.loc[sums.idxmin()])
    stats['mean'] = (sums.mean(), avail.mean())
    return stats
