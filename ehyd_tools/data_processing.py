__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import pandas as pd
from pandas.tseries.offsets import _delta_to_tick as delta_to_freq
from os import path
from warnings import warn


def year_delta(years):
    """
    return a timedelta object for a given number of years

    :type years: float
    :param years: number of years

    :return: time period
    :rtype: pd.Timedelta
    """
    return pd.Timedelta(days=365.25) * years


def data_validation(series):
    """
    add gaps sum & nan sum to the time series

    :type series: pd.Series
    :param series:

    :return: tags with columns 'nans', 'gaps', ...
    :rtype: pd.DataFrame
    """
    tags = pd.DataFrame(index=series.index)
    tags['nans'] = pd.isna(series).astype(int)
    tags['gaps'] = pd.isna(series.fillna(0).resample('T').sum()).astype(int)
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

    :param availability: series with available data tagged as True
    :type availability: pd.Series[True]

    :rtype: list[pd.datetime]
    :return: start & end time of most available time span
    """
    window = delta_to_freq(year_delta(years=10))
    avail_sum = availability.rolling(window).sum()

    end = avail_sum.idxmax()
    start = end.replace(year=end.year - 10)
    return start, end


def check_period(series):
    if (series.index[-1] - series.index[0]) < year_delta(years=9.99):
        warn('Series not longer than 10 years!')


def rain_plot(series, fn):
    msum = series.resample('M').sum()
    ax = msum.plot(kind='bar', color='b')
    # ax.set_ylim(msum.max(), 0)

    ax.set_xlabel('Zeit - Monat/Jahr')
    ax.set_ylabel('Niederschlag (mm/Monat)')

    months = msum.index.strftime('%m').tolist()
    years = msum.index.strftime('\n%Y').unique().tolist()

    mticks = list(range(0, len(months), 4))
    yticks = list(range(0, len(months), 12))

    ax.set_xticks(mticks, minor=True)
    ax.set_xticks(yticks)

    ax.set_xticklabels(months[::4], minor=True)
    ax.set_xticklabels(years, rotation='horizontal')

    ax.get_xticklabels(minor=True)

    fig = ax.get_figure()
    fig.set_size_inches(w=29.7 / 2.54, h=21. / 2.54)
    fig.tight_layout()
    fig.savefig(fn)