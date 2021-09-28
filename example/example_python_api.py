from ehyd_tools.data_processing import (start_end_date, data_validation, data_availability, max_10a, check_period,
                                        rain_figure, create_statistics, )
from ehyd_tools.in_out import (get_ehyd_data, import_series, FIELDS, DATA_KIND, available_files, get_basic_station_meta,
                               get_ehyd_stations, get_ehyd_files, get_station_reference_data)
from ehyd_tools.sww_utils import span_table

# %%
# a1 = get_station_reference_data(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)
# a2 = get_ehyd_data(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT, file_number=2)

a = get_ehyd_files(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)

b = get_ehyd_files(identifier=205641, field=FIELDS.OBERFLAECHENWASSER, data_kind=DATA_KIND.MEASUREMENT)

c = get_ehyd_files(identifier=356980, field=FIELDS.GRUNDWASSER, data_kind=DATA_KIND.MEASUREMENT)

d = get_ehyd_files(identifier=395855, field=FIELDS.QUELLEN, data_kind=DATA_KIND.MEASUREMENT)
exit()

field = FIELDS.NIEDERSCHLAG
get_ehyd_stations(field)

id_number = 106559
# f = _get_files(id_number, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)
print(get_basic_station_meta(id_number, field=field))
# print(available_files(id_number, field=field, data_kind=DATA_KIND.MEASUREMENT))

# f = _get_files(210641, field=FIELDS.OBERFLAECHENWASSER, data_kind=DATA_KIND.MEASUREMENT)
series = get_ehyd_data(id_number, field=field, file_number=2, data_kind=DATA_KIND.MEASUREMENT, with_meta=False)
print(series)
exit()
# __________________________________________________________________________________________________________________
id_number = 112086

# series = get_series(id_number)


start = '2007-01-01'
end = '2016-12-31'
# series = series[start:end].copy()
# check_period(series)

# __________________________________________________________________________________________________________________
label = 'ehyd_{}'.format(id_number)
# export_series(series, filename=label, save_as='csv')
# export_series(series, filename=label, save_as='parquet')
# exit()
# __________________________________________________________________________________________________________________
series = import_series(label + '.parquet')
# series = import_series(r'C:\Users\mp\PycharmProjects\ehyd_tools\example\112086_graz\N-Minutensummen-112086.csv')
# export_series(series, 'test', export_path=None, save_as='parquet', unix=False)


# __________________________________________________________________________________________________________________
tags = data_validation(series)
availability = data_availability(tags)
start, end = max_10a(availability)
series = series.loc[start:end].copy()
check_period(series)

print('The time-series is clipped to '
      'start at "{:%Y-%m-%d}" and end at "{:%Y-%m-%d}".'.format(*start_end_date(series)))

# __________________________________________________________________________________________________________________
gaps = span_table(~availability)
gaps['delta'] = (gaps['end'] - gaps['start']).dt.total_seconds() / (60 * 60 * 24)
gaps = gaps.sort_values('delta', ascending=False)
gaps.columns = ['start', 'end', 'gaps in days']
gaps

# __________________________________________________________________________________________________________________
availability_cut = 0.9

stats = create_statistics(series, availability, availability_cut=availability_cut)

rain_fmt = '{:0.0f} mm'
date_fmt = '{:%Y}'
avail_fmt = '{:0.0%}'

print(
    'The annual totals of the data series serve as the data basis.\n'
    'The following statistics were analyzed:\n'
    'Only years with a availability of {avail} will be evaluated.\n'
    '\n'
    'The maximum is {rain} and was in the year {date} (with {avail} Data available).\n'
    'The minimum is {rain} and was in the year {date} (with {avail} Data available).\n'
    'The mean is {rain} (with {avail} Data available in average).'
    ''.format(rain=rain_fmt, date=date_fmt, avail=avail_fmt).format(availability_cut,
                                                                    *stats['maximum'],
                                                                    *stats['minimum'],
                                                                    *stats['mean'])
    )

# __________________________________________________________________________________________________________________
fig, ax = rain_figure(series, availability, freq='Y')
fig.show()

