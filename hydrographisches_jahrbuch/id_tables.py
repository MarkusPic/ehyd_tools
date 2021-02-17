import pandas as pd

from ehyd_tools.in_out import ehyd_stations

df = pd.read_csv('niederschl_lufttemp_verdunst.csv', index_col=0, header=0)

df = pd.read_csv('oberflaechenwasser.csv', index_col=0, header=0)

df = pd.read_csv('unteririsches_wasser.csv', index_col=0, header=0)

df.dtypes

df.describe()

ehyd_stations

df.index.to_series()

pd.Index(ehyd_stations.keys()).astype(int).difference(df.index)

