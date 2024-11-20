import io
from pandas import read_csv
from ehyd_tools.synthetic_rainseries import RainModeller

# language=csv
rain = """duration,1,2,5,10,20
5,12.9,14.7,17.2,19.0,20.9
10,18.9,21.9,25.6,28.8,31.9
15,24.6,28.2,34.4,37.9,43.0
30,34.4,40.9,49.5,55.6,62.3
60,45.4,55.0,69.8,79.2,88.8
90,47.4,56.8,68.9,78.6,88.6
120,50.0,59.3,71.5,81.5,91.3
240,55.9,66.6,81.1,91.5,102.2
720,61.9,72.9,87.9,100.5,111.9
1440,66.1,78.1,92.3,104.8,115.9
"""

kostra = read_csv(io.StringIO(rain), index_col=0)
model_rain = RainModeller()
model_rain.idf_table = kostra
model_rain.idf_table.columns = model_rain.idf_table.columns.astype(int)
ts = model_rain.euler.get_time_series(return_period=20, duration=1440, interval=5, kind=2, start_time='2021-01-01 00:00')
print(ts.tail(10))
