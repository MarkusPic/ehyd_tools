from ehyd_tools.data_processing import (data_validation, data_availability, max_10a, check_period,
                                        agg_data_figure, create_statistics, )
from ehyd_tools.in_out import (get_ehyd_data, import_series, FIELDS, DATA_KIND, available_files, get_basic_station_meta,
                               get_ehyd_stations, get_ehyd_files, get_station_reference_data, translate_meta_dict, )
from ehyd_tools.sww_utils import span_table

def main2():
    a1 = get_station_reference_data(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)
    # a1t = translate_meta_dict(a1)
    # a2 = get_ehyd_data(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT, file_number=2)

    a = get_ehyd_files(identifier=106559, field=FIELDS.NIEDERSCHLAG, data_kind=DATA_KIND.MEASUREMENT)

    b = get_ehyd_files(identifier=205641, field=FIELDS.OBERFLAECHENWASSER, data_kind=DATA_KIND.MEASUREMENT)

    c = get_ehyd_files(identifier=356980, field=FIELDS.GRUNDWASSER, data_kind=DATA_KIND.MEASUREMENT)

    d = get_ehyd_files(identifier=395855, field=FIELDS.QUELLEN, data_kind=DATA_KIND.MEASUREMENT)


def main():
    field = FIELDS.NIEDERSCHLAG
    get_ehyd_stations(field)

    # __________________________________________________________________________________________________________________
    identifier = 112086

    # print(get_basic_station_meta(identifier, field=field))
    # series = get_ehyd_data(identifier, field=field, file_number=2, data_kind=DATA_KIND.MEASUREMENT)
    # print(series)

    start = '2007-01-01'
    end = '2016-12-31'
    # series = series[start:end].copy()
    # check_period(series)

    # __________________________________________________________________________________________________________________
    label = 'ehyd_{}'.format(identifier)
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

    print(f'The time-series is clipped to start at "{series.index[0]:%Y-%m-%d}" and end at "{series.index[0]:%Y-%m-%d}".')

    # __________________________________________________________________________________________________________________
    gaps = span_table(~availability)
    gaps['delta'] = (gaps['end'] - gaps['start']).dt.total_seconds() / (60 * 60 * 24)
    gaps = gaps.sort_values('delta', ascending=False)
    gaps.columns = ['start', 'end', 'gaps in days']
    print(gaps)

    # __________________________________________________________________________________________________________________
    availability_cut = 0.9

    stats = create_statistics(series, availability, availability_cut=availability_cut)

    rain_fmt = '{:0.0f} mm'
    date_fmt = '{:%Y}'
    avail_fmt = '{:0.0%}'

    print(
        f'The annual totals of the data series serve as the data basis.\n'
        f'The following statistics were analyzed:\n'
        f'Only years with a availability of {availability_cut:{avail_fmt}} will be evaluated.\n'
        f'\n'
        f'The maximum is {stats["maximum"]:{rain_fmt}} and was in the year {stats["maximum_date"]:{date_fmt}} '
        f'(with {stats["maximum_avail"]:{avail_fmt}} Data available).\n'
        f'The minimum is {stats["minimum"]:{rain_fmt}} and was in the year {stats["minimum_date"]:{date_fmt}} '
        f'(with {stats["minimum_avail"]:{avail_fmt}} Data available).\n'
        f'The mean is {stats["mean"]:{rain_fmt}} '
        f'(with {stats["mean_avail"]:{avail_fmt}} Data available in average).')

    # __________________________________________________________________________________________________________________
    fig, ax = agg_data_figure(series, availability, freq='Y')
    fig.show()


if __name__ == '__main__':
    main()
