from warnings import warn

import numpy as np
import pandas as pd
from math import floor
from abc import ABC, abstractmethod

from scipy.interpolate import interp2d

from ehyd_tools.design_rainfall import (get_ehyd_design_rainfall_file, read_ehyd_design_rainfall,
                                        get_max_calculation_method, get_calculation_method, )


class ModelRainWarning(UserWarning):
    """For Warning during the model rain script routines."""
    pass


class _AbstractModelRain(ABC):
    def __init__(self, idf_table: pd.DataFrame=None):
        self.idf_table = idf_table

    def _get_index(self, duration, interval=5):
        return range(interval, duration + interval, interval)

    def _get_idf_value(self, duration, return_period):
        f = interp2d(x=self.idf_table.columns.values, y=self.idf_table.index.values, z=self.idf_table.values,
                     kind='linear')
        return float(f(return_period, duration)[0])

    @abstractmethod
    def _get_series(self, return_period, duration, interval=5, **kwargs):
        pass

    def get_time_series(self, return_period, duration, interval=5, start_time=None, **kwargs):
        rain = self._get_series(return_period, duration, interval, **kwargs)
        if start_time is not None:
            if isinstance(start_time, str):
                start_time = pd.to_datetime(start_time)
            rain.index = start_time + pd.to_timedelta(rain.index, unit='m')
        return rain


class _BlockRain(_AbstractModelRain):
    def __init__(self, idf_table=None):
        _AbstractModelRain.__init__(self, idf_table)

    def _get_series(self, return_period, duration, interval=5, **kwargs):
        height = self._get_idf_value(duration, return_period)
        index = self._get_index(duration, interval)
        intensity = height / len(index)
        r = pd.Series(index=index, data=intensity)
        r = r.append(pd.Series({0: 0})).sort_index()
        return r


class _EulerRain(_AbstractModelRain):
    def __init__(self, idf_table=None):
        _AbstractModelRain.__init__(self, idf_table)

    @staticmethod
    def _get_occurrence_highest_intensity(kind=2):
        if kind == 1:
            return 0
        elif kind == 2:
            return 1 / 3

    def _get_series(self, return_period, duration, interval=5, kind=2):
        return_period_series = self.idf_table[return_period]

        raising = return_period_series.diff().lt(0)
        if raising.any():
            error_from_duration = raising[raising.shift(-1).fillna(False)].index.tolist()
            error_at_duration = raising[raising].index.tolist()
            warn(f'IDF values for the return period of {return_period} a is not raising monotonically between the durations {error_from_duration} and {error_at_duration}! ', ModelRainWarning)

        index = self._get_index(duration, interval)
        filtered_series = pd.Series(data=np.interp(index, return_period_series.index, return_period_series),
                                    index=index)

        d = filtered_series.diff()
        d.iloc[0] = filtered_series.iloc[0]

        # max_index = floor((occurrence_highest_intensity * duration) / interval) * interval
        max_index = floor(round((self._get_occurrence_highest_intensity(kind) * duration) / interval, 3)) * interval

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


class RainModeller:
    def __init__(self, idf_table=None):
        """
        object to create block and euler model rain series

        Args:
            grid_point (int): 4 digit id number (Gitterpunktnummer)
            return_period (int): in years
            duration (int): in minutes
            interval (int): in minutes
            kind (str): which row to use of the idf table. one of ['ÖKOSTRA', 'Bemessung', 'maxBemessung']
        """
        self.idf_table = idf_table

    def set_idf_table_okostra(self, grid_point, kind='maxBemessung'):
        """
        set idf table of ehyd database

        Args:
            grid_point (int): 4 digit id number (Gitterpunktnummer)
            kind (str): which row to use. one of ['ÖKOSTRA', 'Bemessung', 'maxBemessung']
        """
        self.idf_table = read_ehyd_design_rainfall(get_ehyd_design_rainfall_file(grid_point_number=grid_point))
        if kind == 'maxBemessung':
            self.idf_table = get_max_calculation_method(self.idf_table)
        else:
            self.idf_table = get_calculation_method(self.idf_table, method=kind)

    @property
    def block(self) -> _BlockRain:
        return _BlockRain(idf_table=self.idf_table)

    @property
    def euler(self, ) -> _EulerRain:
        return _EulerRain(idf_table=self.idf_table)


if __name__ == '__main__':
    model_rain = RainModeller()
    model_rain.idf_table = pd.read_csv('/home/markus/PycharmProjects/ehyd_tools/example/kostra_s24z70.csv', index_col=0)
    model_rain.idf_table.columns = model_rain.idf_table.columns.astype(int)
    print(model_rain.block.get_time_series(return_period=2, duration=60, interval=5))
    exit()
    model_rain = RainModeller()
    model_rain.set_idf_table_okostra(5214, kind='Bemessung')
    print(model_rain.block.get_time_series(return_period=2, duration=60, interval=5))

    model_rain2 = RainModeller()
    model_rain2.set_idf_table_okostra(5214, kind='maxBemessung')
    print(model_rain2.block.get_time_series(return_period=2, duration=60, interval=5))
    print(model_rain2.euler.get_time_series(return_period=2, duration=60, interval=5, kind=2))
    print(model_rain2.euler.get_time_series(return_period=2, duration=60, interval=5, kind=2, start_time='2021-05-27 16:00'))
