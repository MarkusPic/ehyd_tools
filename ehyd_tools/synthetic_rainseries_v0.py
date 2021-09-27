import numpy as np
import pandas as pd
from math import floor
from abc import ABC, abstractmethod

from scipy.interpolate import interp2d


def block_rain(idf_table, return_period, duration, interval=5):
    if duration not in idf_table.index:
        idf_table = idf_table.append(pd.Series(index=idf_table.columns, name=duration)).sort_index()

    if isinstance(return_period, float):
        idf_table.columns = idf_table.columns.astype(float)
    if return_period not in idf_table.columns:
        idf_table[return_period] = np.NaN
        idf_table = idf_table.sort_index(axis=1)

    if any(idf_table.isna()):
        idf_table = idf_table.interpolate().T.interpolate().T

    height = idf_table.loc[duration, return_period]
    index = range(interval, duration + interval, interval)
    intensity = height / len(index)
    r = pd.Series(index=index, data=intensity)

    r = r.append(pd.Series({0: 0})).sort_index()
    return r


def euler_model_rain(idf_table, return_period, duration, interval=5, occurrence_highest_intensity=1 / 3):
    return_period_series = idf_table[return_period]

    index = range(interval, duration + interval, interval)
    filtered_series = pd.Series(data=np.interp(index, return_period_series.index, return_period_series),
                                index=index)

    d = filtered_series.diff()
    d.iloc[0] = filtered_series.iloc[0]

    # max_index = floor((occurrence_highest_intensity * duration) / interval) * interval
    max_index = floor(round((occurrence_highest_intensity * duration) / interval, 3)) * interval

    # sort differences and reset index
    r = d.sort_values(ascending=False)
    r.index = sorted(r.index.values)

    # reverse first <occurrence_highest_intensity> values
    r.loc[:max_index] = r.loc[max_index::-1].values

    # add Zero value at first posiotion (for SWMM ?)
    r = r.append(pd.Series({0: 0})).sort_index()

    # ---------------
    if 0:
        _res = pd.DataFrame(index=filtered_series.index)
        _res['basis'] = return_period_series
        _res['gefüllt'] = filtered_series
        _res['diff'] = d
        _res['spitze'] = False
        _res.loc[max_index, 'spitze'] = True
        _res['fertig'] = r
    return r


def euler_model_rain_type2(idf_table, return_period, duration, interval=5):
    return euler_model_rain(idf_table, return_period, duration, interval=interval, occurrence_highest_intensity=1 / 3)


def euler_model_rain_type1(idf_table, return_period, duration, interval=5):
    return euler_model_rain(idf_table, return_period, duration, interval=interval, occurrence_highest_intensity=0)


def rain_series(start_time, kind, idf_table, return_period, duration, interval=5):
    rain = kind(idf_table, return_period=return_period, duration=duration, interval=interval)
    rain.index = start_time + pd.to_timedelta(rain.index, unit='m')
    return rain


if __name__ == '__main__':
    from ehyd_tools.design_rainfall import get_ehyd_design_rainfall_file, read_ehyd_design_rainfall, get_max_calculation_method

    grid_point = 5214
    idf_table = read_ehyd_design_rainfall(get_ehyd_design_rainfall_file(grid_point_number=grid_point))
    idf_table = get_max_calculation_method(idf_table)
    print(block_rain(idf_table, return_period=2, duration=60, interval=5))
    print(euler_model_rain_type2(idf_table, return_period=2, duration=60, interval=5))
    print(euler_model_rain_type2(idf_table, return_period=3, duration=60, interval=5))
