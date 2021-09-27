import pandas as pd

from ehyd_tools.in_out import STATIONS_PRECIPITATION_HIGH_RES

df = pd.read_csv('../ehyd_tools/niederschl_lufttemp_verdunst.csv', index_col=0, header=0)

df = pd.read_csv('../ehyd_tools/oberflaechenwasser.csv', index_col=0, header=0)

df = pd.read_csv('../ehyd_tools/unteririsches_wasser.csv', index_col=0, header=0)

df.dtypes

df.describe()

STATIONS_PRECIPITATION_HIGH_RES

df.index.to_series()

pd.Index(STATIONS_PRECIPITATION_HIGH_RES.keys()).astype(int).difference(df.index)
