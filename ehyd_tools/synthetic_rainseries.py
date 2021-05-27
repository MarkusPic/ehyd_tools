import numpy as np
import pandas as pd
from math import floor
from abc import ABC, abstractmethod

from scipy.interpolate import interp2d

from ehyd_tools.design_rainfall import (get_ehyd_file, ehyd_design_rainfall_ascii_reader,
                                        get_max_calculation_method, get_calculation_method, )


class _AbstractModelRain(ABC):
    def __init__(self, return_period, duration, interval=5, idf_table=None):
        self.return_period = return_period
        self.duration = duration
        self.interval = interval
        self.idf_table = idf_table

    @property
    def index(self):
        return range(self.interval, self.duration + self.interval, self.interval)

    def get_idf_value(self, duration, return_period):
        f = interp2d(x=self.idf_table.columns.values, y=self.idf_table.index.values, z=self.idf_table.values,
                     kind='linear')
        return float(f(return_period, duration)[0])

    @abstractmethod
    def get_series(self):
        pass

    def get_time_series(self, start_time):
        if isinstance(start_time, str):
            start_time = pd.to_datetime(start_time)
        rain = self.get_series()
        rain.index = start_time + pd.to_timedelta(rain.index, unit='m')
        return rain

    def set_idf_table(self, grid_point, kind='maxBemessung'):
        """
        set idf table of ehyd database

        Args:
            grid_point (int): 4 digit id number (Gitterpunktnummer)
            kind (str): which row to use. one of ['ÖKOSTRA', 'Bemessung', 'maxBemessung']
        """
        self.idf_table = ehyd_design_rainfall_ascii_reader(get_ehyd_file(grid_point_number=grid_point))
        if kind == 'maxBemessung':
            self.idf_table = get_max_calculation_method(self.idf_table)
        else:
            self.idf_table = get_calculation_method(self.idf_table, method=kind)


class BlockRain(_AbstractModelRain):
    def __init__(self, return_period, duration, interval=5, idf_table=None):
        _AbstractModelRain.__init__(self, return_period, duration, interval, idf_table)

    def get_series(self):
        height = self.get_idf_value(self.duration, self.return_period)
        intensity = height / len(self.index)
        r = pd.Series(index=self.index, data=intensity)
        r = r.append(pd.Series({0: 0})).sort_index()
        return r


class EulerRain(_AbstractModelRain):
    def __init__(self, return_period, duration, interval=5, idf_table=None, kind=2):
        _AbstractModelRain.__init__(self, return_period, duration, interval, idf_table)
        self.kind = kind

    @property
    def occurrence_highest_intensity(self):
        if self.kind == 1:
            return 0
        elif self.kind == 2:
            return 1 / 3

    def get_series(self):
        return_period_series = self.idf_table[self.return_period]

        filtered_series = pd.Series(data=np.interp(self.index, return_period_series.index, return_period_series),
                                    index=self.index)

        d = filtered_series.diff()
        d.iloc[0] = filtered_series.iloc[0]

        # max_index = floor((occurrence_highest_intensity * duration) / interval) * interval
        max_index = floor(round((self.occurrence_highest_intensity * self.duration) / self.interval, 3)) * self.interval

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
    def __init__(self, grid_point, return_period, duration, interval=5, kind='maxBemessung'):
        """
        object to create block and euler model rain series

        Args:
            grid_point (int): 4 digit id number (Gitterpunktnummer)
            return_period (int): in years
            duration (int): in minutes
            interval (int): in minutes
            kind (str): which row to use of the idf table. one of ['ÖKOSTRA', 'Bemessung', 'maxBemessung']
        """
        self.return_period = return_period
        self.duration = duration
        self.interval = interval
        self.grid_point = grid_point
        self.idf_table = None
        self.set_idf_table(kind)

    def set_idf_table(self, kind='maxBemessung'):
        """
        set idf table of ehyd database

        Args:
            kind (str): which row to use. one of ['ÖKOSTRA', 'Bemessung', 'maxBemessung']
        """
        self.idf_table = ehyd_design_rainfall_ascii_reader(get_ehyd_file(grid_point_number=self.grid_point))
        if kind == 'maxBemessung':
            self.idf_table = get_max_calculation_method(self.idf_table)
        else:
            self.idf_table = get_calculation_method(self.idf_table, method=kind)

    def block(self) -> BlockRain:
        return BlockRain(return_period=self.return_period, duration=self.duration, interval=self.interval,
                         idf_table=self.idf_table)

    def euler(self, kind=2) -> EulerRain:
        return EulerRain(return_period=self.return_period, duration=self.duration, interval=self.interval,
                         idf_table=self.idf_table, kind=kind)


if __name__ == '__main__':
    model_rain = BlockRain(return_period=2, duration=60, interval=5)
    model_rain.set_idf_table(5214, kind='Bemessung')
    print(model_rain.get_series())

    model_rain = RainModeller(grid_point=5214, return_period=2, duration=60, interval=5, kind='maxBemessung')
    print(model_rain.block().get_series())
    print(model_rain.euler(2).get_series())
    print(model_rain.euler(2).get_time_series('2021-05-27 16:00'))
