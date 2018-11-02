__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import pandas as pd
from pandas.tseries.offsets import _delta_to_tick as delta_to_freq
from os import path


def export_series(series, export_path=None, save_as='csv'):
    """
    export the series to a given format
    may be extended

    :param export_path: path where file will be stored
    :type export_path: str

    :type series: pd.Series
    :param save_as: export format
    :type save_as: str
    """
    if save_as is 'csv':
        if path.isdir(export_path):
            pass
        else:
            raise UserWarning('Path is not available')

        series.to_csv(path.join(export_path, '{}.csv'.format(series.name)))
    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')


def import_series(filename):
    if filename.endswith('csv'):
        return pd.read_csv(filename, index_col=0, header=None, squeeze=True)
    else:
        raise NotImplementedError('Sorry, but only csv files are implemented. Maybe there will be more options soon.')


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
    return ~tags.any()


def max_10a(availability):
    """
    get the minimal gaps and minimal nan

    :param availability: series with available data tagged as True
    :type availability: pd.Series[True]

    :rtype: list[pd.datetime]
    :return: start & end time of most available time span
    """
    avail_sum = availability.rolling(delta_to_freq(year_delta(years=10))).sum()

    end = avail_sum.idxmax()
    start = end.replace(year=end.year - 10)
    return start, end
