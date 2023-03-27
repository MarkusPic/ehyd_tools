__author__ = "Markus Pichler"
__copyright__ = "Copyright 2021, University of Technology Graz"
__credits__ = ["Markus Pichler"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Markus Pichler"

import io
import os
import re

import pandas as pd

from ehyd_tools.in_out import FIELDS, DATA_KIND, _get_request


class INDICES:
    DURATION = 'duration'
    RETURN_PERIOD = 'return period'
    CALCULATION_METHOD = 'calculation method'


class INDICES_GER:
    DURATION = 'Dauerstufe'
    RETURN_PERIOD = 'Jährlichkeit'
    CALCULATION_METHOD = 'Berechnungstyp'


class NotAnEhydGridNumber(UserWarning): ...


class EhydDesignRainfall:
    def __init__(self, grid_point_number):
        self.grid_point_number = grid_point_number
        self._raw = None
        self.table = None

        self._grid_point_number_found = None
        self.coords = None
        self._bmn = None

    def _extract_info(self):
        """
        Bemessungsniederschlag mit MaxMod- und ÖKOSTRA- Niederschlag [mm]
        Gitterpunkt: 5214 (M34, R: -66_448m, H: 5215426m)
        T: Jährlichkeit
        """
        lines = self._raw.replace('\r', '').split('\n')

        # The first three lines are purely informal and do not belong to the table.
        first_three_lines = lines[:3]
        file = io.StringIO('\n'.join(lines[3:]))
        """
        UTM 33N [EPSG:32633] 534_715,1 5_213_581,62
        GK M34 [EPSG:31256] -66_452,44 215_451,6
        """
        self._grid_point_number_found, self._bmn, x, y = re.findall(r"-?\d+", first_three_lines[1])

        self.coords = (x, y)

        df = pd.read_fwf(file, header=0, skiprows=0, index_col=[0, 1, 2],
                         encoding='ISO-8859-1',
                         comment='-',
                         skip_blank_lines=True)

        # drop empty rows
        df = df.dropna(axis=0, how='all')

        # convert string column names to integers
        df.columns = [int(c.replace('T', '')) for c in df.columns]
        # df.columns.name = 'Jährlichkeit'
        df.columns.name = INDICES.RETURN_PERIOD

        # index "0" (="DAUER") is just the string representative of the index "duration"
        df.index = df.index.droplevel(0)
        # originally named ["DAUERMIN", "TYP"]
        # df.index.names = ['Dauerstufe', 'Berechnungstyp']
        df.index.names = [INDICES.DURATION, INDICES.CALCULATION_METHOD]

        # set duration index as integer
        df.index = df.index.set_levels([df.index.levels[0].astype(int), df.index.levels[1]])
        self.table = df

    @property
    def point(self):
        import shapely.geometry as shp
        return shp.Point(self.coords)

    @property
    def crs(self):
        import pyproj
        # https://de.wikipedia.org/wiki/%C3%96sterreichisches_Bundesmeldenetz
        epsg_dict = {
            '28': '31281',
            '31': '31282',
            '34': '31283',
        }
        return pyproj.CRS(f'EPSG:{epsg_dict[self._bmn]}')

    def get_coords_as_crs(self, crs):
        from pyproj import Transformer
        return Transformer.from_crs(self.crs, crs, always_xy=True).transform(*self.coords)

    def get_point_as_crs(self, crs):
        import shapely.geometry as shp
        return shp.Point(self.get_coords_as_crs(crs))

    @classmethod
    def from_ehyd(cls, grid_point_number):
        new = cls(grid_point_number)
        new._raw = new.get_online_content()
        # new._file = io.TextIOWrapper(io.BytesIO(new._raw), encoding='ISO-8859-1')
        new._extract_info()
        return new

    @classmethod
    def from_local_(cls, fn_txt, grid_point_number='???', skip_extract=False):
        new = cls(grid_point_number)
        if os.path.isfile(fn_txt):
            with open(fn_txt, 'r', encoding='ISO-8859-1') as f:
                new._raw = f.read()
        else:
            new._raw = new.get_online_content()
            with open(fn_txt, 'w', newline='') as f:
                f.write(new._raw)
        if not skip_extract:
            new._extract_info()
        return new

    @classmethod
    def from_local(cls, pth, grid_point_number, skip_extract=False):
        return cls.from_local_(os.path.join(pth, f'design_rain_ehyd_{grid_point_number}.txt'), grid_point_number=grid_point_number, skip_extract=skip_extract)

    @classmethod
    def from_csv(cls, pth, grid_point_number):
        fn_csv = os.path.join(pth, f'design_rain_ehyd_{grid_point_number}.csv')
        if os.path.isfile(fn_csv):
            df = pd.read_csv(fn_csv, index_col=[0, 1])
            df.columns = df.columns.astype(int)
            new = cls(grid_point_number)
            new.table = df
        else:
            new = cls.from_ehyd(grid_point_number)
            new.table.to_csv(fn_csv)
        return new

    def get_request(self):
        return _get_request(self.grid_point_number, data_kind=DATA_KIND.DESIGN_PRECIPITATION, field=None, file_number=None)

    def get_online_content(self):
        r = self.get_request()
        if r.content == b'':
            raise NotAnEhydGridNumber(f'Grid number: {self.grid_point_number}')
        return r.content.decode('ISO-8859-1')

    def save_pdf(self, pth):
        fn = os.path.join(pth, f'Bemessungsniederschlag_Gitterpunkt_{self.grid_point_number}.pdf')
        if not os.path.isfile(fn):
            r = _get_request(self.grid_point_number, data_kind=DATA_KIND.DESIGN_PRECIPITATION, field=FIELDS.PDF, file_number=None)
            open(fn, 'wb').write(r.content)

    def get_max_calculation_method(self, methods=None):
        if methods is None:
            methods = ['ÖKOSTRA', 'Bemessung']

        return self.table.loc[pd.IndexSlice[:, methods], :].groupby(axis=0, level=0).max().copy()

    def get_calculation_method(self, method='Bemessung'):
        return self.table.xs(method, axis=0, level=INDICES.CALCULATION_METHOD, drop_level=True).copy()

    def get_rainfall_height(self, return_period, duration):
        from scipy.interpolate import interp2d
        f = interp2d(x=self.table.columns.astype(float).values, y=self.table.index.astype(float).values, z=self.table.values, kind='linear')
        return float(f(return_period, duration)[0])


# ########################################################################################################################
def get_ehyd_design_rainfall_file(grid_point_number=5214):
    r = _get_request(grid_point_number, data_kind=DATA_KIND.DESIGN_PRECIPITATION, field=None, file_number=None)
    return io.TextIOWrapper(io.BytesIO(r.content), encoding='ISO-8859-1')


def save_ehyd_design_rainfall_pdf(grid_point_number, fn):
    fn = os.path.join(fn, f'Bemessungsniederschlag_Gitterpunkt_{grid_point_number}.pdf')
    if not os.path.isfile(fn):
        r = _get_request(grid_point_number, data_kind=DATA_KIND.DESIGN_PRECIPITATION, field=FIELDS.PDF, file_number=None)
        open(fn, 'wb').write(r.content)


def read_ehyd_design_rainfall(filepath_or_buffer):
    if isinstance(filepath_or_buffer, str):
        txt_file = open(filepath_or_buffer, 'r', encoding='ISO-8859-1')
    else:
        txt_file = filepath_or_buffer

    # The first three lines are purely informal and do not belong to the table.
    first_three_lines = [txt_file.readlines(1) for _ in range(3)]
    # print(*first_three_lines, sep='\n')

    df = pd.read_fwf(txt_file, header=0, skiprows=0, index_col=[0, 1, 2],
                     encoding='ISO-8859-1',
                     comment='-',
                     skip_blank_lines=True)
    txt_file.close()

    # drop empty rows
    df = df.dropna(axis=0, how='all')

    # convert string column names to integers
    df.columns = [int(c.replace('T', '')) for c in df.columns]
    # df.columns.name = 'Jährlichkeit'
    df.columns.name = INDICES.RETURN_PERIOD

    # index "0" (="DAUER") is just the string representative of the index "duration"
    df.index = df.index.droplevel(0)
    # originally named ["DAUERMIN", "TYP"]
    # df.index.names = ['Dauerstufe', 'Berechnungstyp']
    df.index.names = [INDICES.DURATION, INDICES.CALCULATION_METHOD]

    # set duration index as integer
    df.index = df.index.set_levels([df.index.levels[0].astype(int), df.index.levels[1]])

    return df


def get_ehyd_design_rainfall(grid_point_number):
    return read_ehyd_design_rainfall(get_ehyd_design_rainfall_file(grid_point_number))


def get_max_calculation_method(df, methods=None):
    if methods is None:
        methods = ['ÖKOSTRA', 'Bemessung']

    return df.loc[pd.IndexSlice[:, methods], :].groupby(axis=0, level=0).max().copy()


def get_calculation_method(df, method='Bemessung'):
    return df.xs(method, axis=0, level=INDICES.CALCULATION_METHOD, drop_level=True).copy()


def get_rainfall_height(table, return_period, duration):
    from scipy.interpolate import interp2d
    f = interp2d(x=table.columns.astype(float).values, y=table.index.astype(float).values, z=table.values, kind='linear')
    return float(f(return_period, duration)[0])


def get_ehyd_design_rainfall_offline(grid_point_number, pth):
    fn_csv = os.path.join(pth, f'design_rain_ehyd_{grid_point_number}.csv')
    if os.path.isfile(fn_csv):
        df = pd.read_csv(fn_csv, index_col=[0, 1])
        df.columns = df.columns.astype(int)
    else:
        df = get_ehyd_design_rainfall(grid_point_number=grid_point_number)
        df.to_csv(fn_csv)
    return df
