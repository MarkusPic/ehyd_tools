__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

from pandas import Timedelta, DataFrame, isna, Series, DateOffset
from numpy import NaN
from warnings import warn
from matplotlib.pyplot import subplots


def start_end_date(series):
    return series.index[[0, -1]].tolist()


def year_delta(years):
    """
    return a timedelta object for a given number of years

    Args:
        years (float): number of years

    Returns:
        pandas.Timedelta: time period
    """
    return Timedelta(days=365.25) * years


def data_validation(series):
    """
    add gaps sum & nan sum to the time series

    Args:
        series (pandas.Series): time-series

    Returns:
        pandas.DataFrame: tags with columns 'nans', 'gaps', ...
    """
    ts = series.copy()

    first_index = ts.index[0].replace(day=1, month=1, hour=0, minute=0)
    if first_index not in series.index:
        ts = Series(index=[first_index]).append(ts)

    last_index = ts.index[-1].replace(day=31, month=12, hour=23, minute=59)
    if last_index not in ts.index:
        ts = ts.append(Series(index=[last_index]))

    if ts.index.has_duplicates:  # very slow an large data sets
        ts = ts[~ts.index.duplicated()].copy()

    if not ts.index.is_monotonic_increasing:
        raise UserWarning('Series has not monotonic increasing of the timestamps.')
        ts = ts.sort_index()

    tags = DataFrame(index=ts.index)
    tags['nans'] = isna(ts).astype(int)
    tags = tags.reindex(tags.asfreq('T').index)
    tags['gaps'] = isna(ts.fillna(0).reindex(tags.index)).astype(int)
    return tags


def data_availability(tags):
    """
    get availability based on the validation tags

    Args:
        tags (pandas.DataFrame): errors tagged as true (see function data_validation)

    Returns:
        pandas.Series: availability
    """
    return ~tags.any(axis=1)


def max_10a(availability):
    """
    get the minimal gaps and minimal nan
    and take the latest possible time span

    Args:
        availability (pandas.Series[bool]): series with available data tagged as True

    Returns:
        tuple[pandas.Timestamp, pandas.Timestamp]: start & end time of most available time span
    """

    window = year_delta(years=10)
    avail_sum = availability.rolling(window).sum()

    end = avail_sum[::-1].idxmax()
    start = end - DateOffset(years=10)
    return start, end


def check_period(series):
    """
    check if the period of the series is at least 10 years long

    Warnings:
        UserWarning - if the series is shorter

    Args:
        series (pandas.Series): time-series
    """
    if not is_longer(series, years=10):
        print('WARNING: The Series is only {:.1f} < 10 years long!'.format(
            (series.index[-1] - series.index[0]) / Timedelta(days=365)))


def is_longer(series, years):
    """
    check if the period of the series is at least x years long

    Args:
        series (pandas.Series): time-series
        years (int): number of years to compare with

    Returns:
        bool: whether the series is longer
    """
    return series.index[0] + DateOffset(years=years) <= series.index[-1]
    # return (series.index[-1] - series.index[0]) > year_delta(years=years)


def rain_figure(series, availability, freq=None, add_mean_line=False):
    """
    creates a monthly sum bar plot

    Args:
        series (pandas.Series): time-series
        availability (pandas.Series): availability
        fn (str): path + filename of the resulting plot
    """

    freq_long = {
        'Y': 'Jahr',
        'M': 'Monat'
    }

    if freq is None:
        if is_longer(series, years=15):
            freq = 'Y'
            # base_delta = year_delta(1)
        else:
            freq = 'M'
            # base_delta = year_delta(1) / 12

    sums = series.resample(freq).sum()

    if freq == 'Y':
        index = sums.index.year.values
    else:
        # monthly
        index = sums.index.year.values + sums.index.month.values / 12

    # index = series.index.to_series().resample(freq).apply(lambda s: s.min() + abs(s.min() - s.max()) / 2).dt.date.values
    freq_avail = availability.resample(freq)
    avail = (freq_avail.sum() / freq_avail.count())[sums.index]

    # dummy = sums.rename('dummy').copy()
    # dummy.loc[:] = 0

    height_ratios = [1, 10]

    fig, (ax1, ax) = subplots(2, gridspec_kw=dict(height_ratios=height_ratios), sharex=True)

    # ax = dummy.plot(ax=ax, lw=0)
    fig.set_size_inches(w=29.7 / 2.54, h=21. / 2.54)

    ax1.set_ylim(0, 100)
    ax1.set_ylabel('% Verfügbar')
    ax1.set_yticks(range(0, 110, 10), minor=True)
    ax1.grid(axis='y', which='minor', color='lightgrey', linestyle=':', linewidth=0.5)  # , zorder=-10000000)
    # ax1 = dummy.plot(ax=ax1, lw=0)
    # ax1.scatter(x=index, y=avail.values * 100, color='grey', clip_on=False, marker='_')
    ax1.bar(x=index, height=avail.values * 100, color='grey')
    ax1.set_axisbelow(True)

    if add_mean_line:
        mean = sums[avail > 0.5].mean()
        ax.text(ax.get_xlim()[0] + 1, mean + 15, f'Mittelwert: {mean:0.0f} (mm/{freq_long[freq]})',
                bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 2, 'linewidth': '0'})
        ax.axhline(mean, ls='--', color='darkgray', linewidth=0.7)

    ax.bar(x=index, height=sums.values, color='k')
    ax.set_ylabel('Niederschlag (mm/{})'.format(freq_long[freq]))
    ax.set_xlabel('Zeit')
    # ax.set_xlim(left=ax.get_xlim()[0] - 0.5)
    # ax.set_xlim(right=ax.get_xlim()[1] + 0.5)
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    return fig, ax


def rain_plot(series, availability, fn):
    """
    creates a monthly sum bar plot

    Args:
        series (pandas.Series): time-series
        availability (pandas.Series): availability
        fn (str): path + filename of the resulting plot
    """
    fig, ax = rain_figure(series, availability)
    # fig.show()
    fig.savefig(fn)


def create_statistics(series, availability, availability_cut=0.2):
    """
    creates basic (maximum, minimum and mean) yearly statistics of the time-series

    Args:
        series (pandas.Series): time-series
        availability (pandas.Series): availability
        availability_cut (float): minimal availability for creating a yearly statistic

    Returns:
        dict: of the yearly statistics
    """
    sums = series.resample('Y').sum()
    avail_sum = availability.resample('Y').sum()

    base_freq = series.index.freq
    yearly_index = avail_sum.index
    delta_per_year = yearly_index - (yearly_index - DateOffset(years=1))
    avail_full = delta_per_year / base_freq
    avail = avail_sum / avail_full  # type: Series
    if (avail < availability_cut).all():
        print('ATTENTION: only very small data availability! The statistic may be not very meaningful.')
        if (avail < 0.1).all():
            return dict()
        sums[avail < 0.1] = NaN
    else:
        sums[avail < availability_cut] = NaN

    stats = dict()
    stats['maximum'] = (sums.max(), sums.idxmax(), avail.loc[sums.idxmax()])
    stats['minimum'] = (sums.min(), sums.idxmin(), avail.loc[sums.idxmin()])
    stats['mean'] = (sums.mean(), avail.mean())
    return stats
