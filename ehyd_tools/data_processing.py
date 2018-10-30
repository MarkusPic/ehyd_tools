__author__ = "David Camhy, Markus Pichler"
__copyright__ = "Copyright 2017, University of Technology Graz"
__credits__ = ["David Camhy", "Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "David Camhy, Markus Pichler"

import pandas as pd
from pandas.tseries.offsets import _delta_to_tick as delta_to_freq


def export_series(series, save_as='csv'):
    """
    export the series to a given format
    may be extended

    :type series: pd.Series
    :param save_as: export format
    :type save_as: str
    """
    if save_as is 'csv':
        series.to_csv('{}.csv'.format(series.name))


def year_delta(years):
    """
    return a timedelta object for a given number of years

    :type years: float
    :param years: number of years

    :return: time period
    :rtype: pd.Timedelta
    """
    return pd.Timedelta(days=365.2425 * years)


def max_10a(frame, name):
    """
    get the minimal gaps and minimal nan

    :param frame: dataframe with columns 'nans', 'gaps' and <name>
    :type frame: pd.DataFrame

    :param name: name of the data of interest in the dataframe
    :type name: str

    :rtype: pd.Series
    :return: 10 years of the time series of interest
    """
    df = frame.copy()
    avail = ~(df['nans'] | df['gaps'])
    avail_sum = avail.rolling(delta_to_freq(year_delta(years=10))).sum()
    max_avail_end = avail_sum.idxmax()
    max_avail_start = max_avail_end - year_delta(years=10)
    return df.loc[max_avail_start:max_avail_end, name].copy()


def data_analysis(series):
    """
    add gaps sum & nan sum to the time series

    :type series: pd.Series
    :param series:

    :return: dataframe with columns 'nans', 'gaps' and <name>
    :rtype: pd.DataFrame
    """
    df = series.to_frame()
    df['nans'] = pd.isna(series).astype(int)
    df['gaps'] = pd.isna(series.fillna(0).resample('T').sum()).astype(int)
    return df
