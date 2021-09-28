# coding=UTF-8


def ehyd_reader(filename, output_type, write_csv='False',
                input_type='csv', interpolate='False'):
    """
    Reads in a CSV file containing a hydrologic time series (filename).

    Meant to be used with files obtained from ehyd.gv.at, taking into
    account the intricacies of this data (ISO 8859-15 file, use of
    german Umlauts, using the term "Lücke" for NaN, decimal comma).

    Can also read in .dat files, which get used internally in the
    governement agencies. Those follow the same format as the csv files
    but use a decimal dot and variable spaces as delimiter. Note that
    these files can have very irregular measurements, so handling these
    is still experimental!

    Use 'dict' or 'df' to specify wether you want a dict or dataframe as
    output.

    If you want a "proper" CSV file in your working directory, use
    "write_csv=True".

    Set interpolate to 'True' if you want to interpolate over missing
    data. For small gaps, this should be OK, but if 'data_error'
    indicates a lot of missing data, this is probably going to cause
    issues when further handling the data.

    Parameters
    ----------
    filename : str
        path to and name of the file to be read
    output_type : str
        can be 'df' for a dataframe as output or 'dict" for a dictionary
    write_csv : bool
    input_type : str
        can be 'csv' for a CSV file or 'dat' for a DAT file
    interpolate : bool

    Examples
    --------
    # Read in a csv file and output a dataframe:
    ehyd_df = ehyd_reader('filename.csv', output_type='df')
    # Read in a dat file and output a dictionary and a csv file:
    ehyd_dict = ehyd_reader('filename.dat', output_type='dict',
                            input_type='dat', write_csv='True')

    """

    # Import the needed modules.
    import pandas as pd
    import numpy as np
    import re
    from sklearn.metrics.pairwise import haversine_distances
    from math import radians
    # The last two imports are needed to figure out how much the station moved
    # over its lifetime. If that's not needed, the whole stuff around the
    # variable "station_move" can be removed.

    # A lot of metadata start with ';' and end with a newline.
    # Lets define a little function for that.
    def csv_splitter(tester):
        start_str = tester.find(';') + 1
        end_str = tester.find('\n')
        t_str = tester[start_str:end_str]
        return t_str

    def dat_splitter(tester):
        start_str = tester.find(':') + 1
        end_str = tester.find('\n')
        t_str = tester[start_str:end_str].lstrip()
        return t_str

    if input_type == 'dat':
        splitter = dat_splitter
    else:
        splitter = csv_splitter

    # define a long-ish function to read the coordinates,
    # needed twice, later
    def coord_calculator(raw_coords):
        nonlocal meta_error
        coord_string = str(raw_coords)
        if input_type == 'dat':
            coord_list = re.findall(r"\d{2}\s\d{2}\s\d{2}", coord_string)
            raw_longitude = coord_list[0]
            raw_latitude = coord_list[1]
        else:
            longitude_start = coord_string.find(';') + 1
            longitude_end = coord_string.rfind(';') - 1
            latitude_start = coord_string.rfind(';') + 1
            latitude_end = coord_string.find('\n')
            raw_longitude = coord_string[longitude_start:longitude_end]
            raw_latitude = coord_string[latitude_start:latitude_end]
        # Remove trailing whitespace.
        stripped_lon = raw_longitude.rstrip()
        stripped_lat = raw_latitude.rstrip()
        # There can be cases where lat and lon are missing i.e. meaning they're
        # set to 0. If that's the case, all the stuff below fails. so we gotta
        # test for that.
        if stripped_lat == '0':
            lat = np.nan
            lon = np.nan
            print('Station', HZB, 'is missing coordinates!')
            meta_error = 'missing_coords'
        else:
            # Grab the parts and turn them into floats
            s_deg_lon = stripped_lon[0:2]
            deg_lon = float(s_deg_lon)
            s_min_lon = stripped_lon[3:5]
            min_lon = float(s_min_lon)
            s_sec_lon = stripped_lon[6:8]
            sec_lon = float(s_sec_lon)
            s_deg_lat = stripped_lat[0:2]
            deg_lat = float(s_deg_lat)
            s_min_lat = stripped_lat[3:5]
            min_lat = float(s_min_lat)
            s_sec_lat = stripped_lat[6:8]
            sec_lat = float(s_sec_lat)
            # Put it all together
            lon = deg_lon + (min_lon / 60) + (sec_lon / 3600)
            lat = deg_lat + (min_lat / 60) + (sec_lat / 3600)
            lon = round(lon, 8)
            lat = round(lat, 8)
            # Should only result in 6 decimals,
            # but the division could result in a repeating decimal,
            # so let's keep that at a sane size.
        return lat, lon

    # since filename is kinda generic, change it to current_csv
    current_csv = filename

    f1 = open(current_csv, 'r', encoding='cp1252')
    table = f1.readlines(3000)
    # Reads in only 3000 characters/bytes. Most ehyd files appear to contain
    # around 1500 characters in the metadata, so this has a good margin of
    # error. Since readlines is quite fast, this limitation can also be
    # discarded without much of a penalty( ~100µs vs. 9ms for a 1MB file).
    f1.close()

    # Extract the name of the station:
    station_name_line = table[0]
    station_name = splitter(station_name_line)

    # Set metadata that might not be in every file to the 'NaN' string, to show
    # that they're not available.
    province = 'NaN'
    catchment_size = 'NaN'
    catchment_symbol = 'NaN'
    station_move = 'NaN'
    subcatchment = 'NaN'
    region_name = 'NaN'
    # set depth to not available for things that do not have it
    depth = 'NaN'
    elev = 'NaN'

    # Grab various important information from the header and find the line in
    # which the data starts.
    # Will fail when a file is smaller than 40 lines, but such short time
    # series do not make sense to work with.
    # Will also fail if the headers of the csvs get bigger than 40 lines.
    # As of now, they're around 34, so 40 leaves a bit of a margin.
    # If it fails, increase header_counter as you see fit.
    # AS of now, this can only handle groundwater levels, river levels,
    # precipitation and spring flows. If it shall be extended to other types,
    # some logic is needed to distinguish between the different possibilities
    # that one of the current 'datatype' can contain. E.g. river temperature
    # not only needs to search for 'Gew\xe4sser' as of now, but also for
    # 'WTemperatur'.
    # Thus, we set the datatype to NA at first, and change it only for files
    # that fit the rest of the Analysis:
    datatype = 'NA'
    meta_error = 'no_error'
    data_error = 'no_error'
    header_counter = 0
    while header_counter < 40:
        tester_list = table[header_counter]
        tester = str(tester_list)  # must be turned into a string,
        # otherwise we cant find strings in it.
        if 'Gew\xe4sser' in tester:
            datatype = 'Riverwater'
            catchment_name = splitter(tester)
        if 'Niederschlag' in tester:
            datatype = 'Precipitation'
            catchment_name = station_name
            # Catchment name is set to the name of the station.
        if 'Hauptquelle' in tester:
            datatype = 'Spring'
        if 'Grundwasser' in tester:
            datatype = 'Groundwater'
            catchment_name = splitter(tester)
            # Gets the written name and short symbol for the catchment, e.g.
            # 'Grazer Feld (Graz/Andritz - Wildon) [MUR]'
            # the Murdurchbruchstal is missing the [MUR] marker.
            # So we have to deal with that too.
            if '[' in catchment_name:
                name_end = catchment_name.find(']')
                name_start = name_end - 3
                catchment_symbol = catchment_name[name_start:name_end]
            else:
                catchment_symbol = 'NA'
            # Gets the short symbol for the catchment, such as
            # MUR, DRA (=Drau), DUJ (=Danube below Jochenstein) etc
            groundwaterbody_name = table[header_counter - 1]
            # Normally there are two names for the groundwater body, the larger
            # 'Grundwasserkörper' and the subregion 'PorenGW-Gebiet' which can
            # be very local (few square km).
            subcatchment = splitter(groundwaterbody_name)
        if 'Dienststelle' in tester:
            region_name = splitter(tester)
            # Who is responsible for the station. Mostly indicates which state.
            # E.g. 'HD-Steiermark'. Can overlap with 'Messstellenbetreiber' and
            # 'Bundesland', the latter being rare, however.
            # For Vienna and Lower Austria, it can also contain
            # 'HD-Wien (MA 45)' or 'Magistratsabteilung 31' with added clutter
            # or no indication of the state.
            # In this case there can also be a 'Bundesland' row:
        if 'Bundesland' in tester:
            province = splitter(tester)
            # And to complicate matters further, there can also be a
            # 'Messstellenbetreiber', i.e. who operates (or owns?) the station:
        if 'Messstellenbetreiber' in tester:
            operator = splitter(tester)
        if 'HZB-Nummer' in tester:
            # Keep the unique identifier used in ehyd
            HZB = int(splitter(tester))
            print('HZB:', HZB)
        if 'HD-Nummer' in tester:
            # Besides the HZB number, there's often also the HD number, used by
            # the state authorities. Often, this number is also included in the
            # name of the station. Can also contain letters and spaces, so
            # we'll leave that as a string.
            HD_num = splitter(tester)
        if 'DBMS-Nummer' in tester:
            # Some stations also have a DBMS number besides or instead of the
            # HD number. Seems like it's only numbers, but nothing known about
            # it, so lets keep it string.
            DBMS_num = splitter(tester)
        if 'Einzugsgebiet' in tester:
            # find the size of the catchment
            catchment_size = splitter(tester)
        if 'Koordinaten' in tester:
            # Sometimes a station gets moved and there will be all the
            # coordinates it ever had listed in the file. The lines below try
            # to find the last (=most current) coordinates by searching for the
            # term 'Exportzeitreihe' which comes after the last location.
            coord_tester = table[header_counter + 3]
            if 'Exportzeitreihe' in coord_tester:
                # This means there is only one row of Coordinates, so the
                # station didn't move.
                coord_values = header_counter + 2
                coords_changed = 'False'
            else:
                # There's more than one row of Coordinates. We need to set the
                # first one as old_coords to calculate the distance.
                print('Station got moved during its livetime.')
                coords_changed = 'True'
                meta_error = 'Station_moved'
                old_coords = table[header_counter + 2]
                old_coords = coord_calculator(old_coords)
                coord_tester = table[header_counter + 4]
                if 'Exportzeitreihe' in coord_tester:
                    coord_values = header_counter + 3
                else:
                    coord_tester = table[header_counter + 5]
                    if 'Exportzeitreihe' in coord_tester:
                        coord_values = header_counter + 4
                    else:
                        coord_values = header_counter + 5
                        print('Station', HZB, 'has been moved at least 4 times! \n',
                              'Coordinates might be of an older location, please check this station!')

            coords = coord_calculator(table[coord_values])
            lat = coords[0]
            lon = coords[1]
            if coords_changed == 'True':
                # Print info about how far the station got moved. Sometimes,
                # coordinates are missing, so we need some routine to deal with
                # missing coordinates
                if meta_error == 'missing_coords':
                    print('Station', HZB, 'was moved by an unknown distance! \n',
                          'Using the coordinates of the older location!')
                    coords = old_coords
                    lat = coords[0]
                    lon = coords[1]
                else:
                    # Uses the haversine distance from scikit learn. see
                    # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.haversine_distances.html
                    # or
                    # https://en.wikipedia.org/wiki/Haversine_formula
                    # could probably also be implemented without scikit-learn.
                    # Needs to be turned into radians to work with.
                    coords_rad = [radians(i) for i in coords]
                    old_coords_rad = [radians(i) for i in old_coords]
                    station_move = haversine_distances(
                        [coords_rad, old_coords_rad]) * 6371 * 1000
                    # Multiply with earth radius in meters to get the distance.
                    station_move = round(station_move[0, 1], 2)
                    # output is an array, this should get the distance without
                    # the rest, rounded to two decimals (=centimeters).
                    print('Sation', HZB, 'was moved by',
                          int(station_move), 'meters.')

        if 'Messpunkthöhe:' in tester:
            elev = tester.replace(",", ".")
            elev = splitter(elev)
            elev = float(elev)
        if 'Sohllage' in tester:
            depth = tester.replace(",", ".")
            depth = splitter(depth)
            depth = float(depth)
        if 'Geländehöhe-Hauptquelle' in tester:
            # can be an elevation of a spring.
            # but is this really needed? What about Pegelnullpunk?
            elev = tester.replace(",", ".")
            elev = splitter(elev)
            if elev == '':
                elev = 'NaN'
            else:
                elev = float(elev)
        if 'Pegelnullpunkt' in tester and datatype == 'Spring' and elev == 'NaN':
            elev = tester.replace(",", ".")
            elev = splitter(elev)
            elev = float(elev)
        if 'Pegelnullpunkt' in tester and datatype == 'Riverwater':
            elev = str(table[header_counter + 2])
            elev = elev.replace(",", ".")
            elev = splitter(elev)
            if elev == '':
                elev = 'NaN'
            else:
                elev = float(elev)
        if 'Höhe:' in tester:  # and datatype == 'Precipitation':
            # Should also test for datatype, but this fails.
            # Seems like 'Höhe:' only gets used in precip, but a test would
            # still be nice.
            elev = str(table[header_counter + 2])
            elev = elev.replace(",", ".")
            elev = splitter(elev)
            if elev == '':
                elev = 'NaN'
            else:
                elev = float(elev)
        # Can also have a lot of different values if the station moved.
        # Still missing something to detect that and to give info about changes
        # station location. Uses the first value it finds. Will probably not
        # be totally wrong, but isn't the most recent value.
        if 'Werte:' in tester:
            werte_start = header_counter
            # Finds the line where the data starts
        header_counter += 1

    if depth != 'NaN':
        teufe = round((elev - depth), 2)
        # Due to how floating point numbers work, we sometimes run into values
        # like 11.799999999999983 where it should be 11.8 so lets round it to
        # take care of that.
    else:
        teufe = 'NaN'

    if input_type == 'dat':
        seperator = '\s{2,10}'
        deci = '.'
    else:
        seperator = '\s*\;\s*'
        deci = ','

    hydro_tS = pd.read_csv(current_csv,
                           skiprows=werte_start + 1, decimal=deci,
                           sep=seperator, usecols=[0, 1], index_col=0,
                           dayfirst=True, parse_dates=True, engine='python',
                           encoding='cp1252', names=['date', 'level'],
                           na_values='Lücke')
    # Due to the weird format of the csv files, they appear to be enconded as
    # cp1252. If ehyd gets updated at some point in time or this is adapeted
    # to other files, 'encoding='cp1252'' might have to be changed to some more
    # common format.

    # The data sometimes gets read as object, but we need float.
    hydro_tS.level = hydro_tS.level.astype(float)

    # Normalize the whole thing to get rid of hours and minutes.
    # If those are needed, the following line can be removed,
    # but it'll wreak havok with irregular times.
    hydro_tS.index = hydro_tS.index.normalize()

    # get the lowest and the largest date
    min_date = hydro_tS.index.min()
    max_date = hydro_tS.index.max()
    mini_date_1 = str(min_date)
    maxi_date_1 = str(max_date)
    mini_date = mini_date_1[0:10]
    maxi_date = maxi_date_1[0:10]
    # hardcoded to get rid of the hours and seconds.
    # Might fail if anything in the date format changes.

    min_year = min_date.year
    max_year = max_date.year
    data_years = max_year - min_year

    # Check if there is a gap in the index, which can cause issues with some
    # further procsessing. First we need to find the frequency of the data.
    # We also need to get rid of the hours of the day, else days with multiple
    # measurements will wreak havoc.
    firstdate = hydro_tS.index[0]
    seconddate = hydro_tS.index[1]
    datedelta = seconddate - firstdate
    # Pandas timedelta. Seems like it defaults to days, but just to make sure:
    dayinterval_1 = datedelta.days
    # Results in an int with the number of days between two days.
    # 1=daily timeseries; 28-31=monthly
    # However, some csv files can havechanging intervals. Let's do a few more
    # tests to find out, by probing the interval at the end and in the middle.
    lastdate = hydro_tS.index[-1]
    second_lastdate = hydro_tS.index[-2]
    datedelta = lastdate - second_lastdate
    dayinterval_2 = datedelta.days
    middate = hydro_tS.index[len(hydro_tS.index) // 2]
    smiddate = hydro_tS.index[len(hydro_tS.index) // 2 - 1]
    datedelta = middate - smiddate
    dayinterval_3 = datedelta.days

    if dayinterval_1 == dayinterval_2 == dayinterval_3 == 1:
        TS_freq = 'D'
        # hydro_tS = hydro_tS.asfreq(TS_freq)

    elif min(dayinterval_1, dayinterval_2, dayinterval_3) > 1:
        if min(dayinterval_1, dayinterval_2, dayinterval_3) > 27:
            TS_freq = 'MS'
            # hydro_tS = hydro_tS.asfreq(TS_freq)
        else:
            TS_freq = 'MS'
            # hydro_tS = hydro_tS.asfreq(TS_freq)
            print('Station', HZB, 'has irregular monthly times! \n',
                  'Check the index before doing calculations on it.')
            data_error = 'Irregular_measure_times_M'

    else:
        TS_freq = 'D'
        if input_type == 'dat':
            hydro_tS = hydro_tS.resample(TS_freq).mean()
            print('Station', HZB, 'has multiples measurements per day. \n',
                  'Resampled to daily.')
        else:
            print('Station', HZB, 'has irregular measurement times! \n',
                  'Check the index before doing calculations on it.')
        data_error = 'Irregular_measure_times_D'
    # The commented out
    # hydro_tS = hydro_tS.asfreq(TS_freq)
    # lines can resample it to the frequency it apparently has.
    # Will pad missing dates and insert NaN as a value,
    # which will then be taken care of by the stuff below.

    # Built a empty date range with the same start, end and frequency as the
    # orignal data and get its length:
    test_dates = pd.date_range(mini_date, maxi_date, freq=TS_freq)
    test_length = len(test_dates)

    # Get the length of the real data and compare it. If it differs, there must
    # be a gap in the data.
    real_length = len(hydro_tS)
    # Counts everything, including NaN.
    lengthdifference = test_length - real_length

    if lengthdifference != 0:
        if input_type == 'csv':
            hydro_tS = hydro_tS[~hydro_tS.index.duplicated()]
            # Get rid of duplicate entries, keeping the first one. For data that
            # has many measurements per day, this is not a good idea. ehyd data
            # should have only one per day, so this deals with some rare errors,
            # but for the raw data, this can be problematic.
            # the ~ is apparently a reversal of the booleans in that duplicated.
            # see
            # https://stackoverflow.com/questions/13035764/remove-rows-with-duplicate-indices-pandas-dataframe-and-timeseries
            print('Two measurements at one day. first measurement deleted')
        data_error = 'double_measurement'
    if lengthdifference > 4:
        # Apparently, there is some issues around 1945 (war?) where total
        # months are missing, including dates.
        data_error = 'gap_data'
        print('there is a gap in the data')
        print('lengthdifference')
        print(lengthdifference)
    if data_years < 5:
        # Data that is too short can't reliably be used for many statistics.
        data_error = 'short_data'
        print('time series very short')
    if min_year > 2010:
        data_error = 'short_data'
        print('time series very short')
    else:
        # count the NaNs:
        real_count = hydro_tS.level.count()  # counts only valid numbers
        NaN_number = real_length - real_count
        NaN_number = float(NaN_number)
        percent_data = real_length / 100
        ten_percent = percent_data * 10
        if NaN_number > ten_percent:
            data_error = '10+percent_gap'
            print('10 percent of data missing')

        # Count how many NaNs there are following each other
        consecutive_NaNs = hydro_tS.level.isna().astype(int).groupby(
            hydro_tS.level.notna().astype(int).cumsum()).sum().max()

        if TS_freq == 'D' and consecutive_NaNs > 14:
            data_error = '14+dayGap'
            print('more than 14 consecutive NaN in daily data')
        if TS_freq == 'MS' and consecutive_NaNs > 3:
            data_error = '3+monthsGap'
            print('more than 3 consecutive NaN in monthly data')

        if interpolate == 'True':
            # Get rid of the NaN in the dataset.
            # This is just a crude interpolation.
            # For data with just a few, this shouldn't be an issue, but if
            # data_error = '10+percent_gap', '3+monthsGap' or '14+dayGap'
            # this is probably not a valid approach.
            hydro_tS.level = hydro_tS.level.interpolate()

    if output_type == 'df' or write_csv == 'True':
        output_header = pd.MultiIndex.from_product(
            [[datatype], [station_name], [HZB], [HD_num],
             [DBMS_num], [catchment_name], [catchment_symbol],
             [subcatchment], [region_name], [province], [operator],
             [catchment_size], [lat], [lon], [station_move],
             [elev], [depth], [teufe], [data_error], [meta_error]],
            names=['datatype', 'station_name', 'HZB', 'HD_num',
                   'DBMS_num', 'catchment_name', 'catchment_symbol',
                   'subcatchment', 'region_name', 'province', 'operator',
                   'catchment_size', 'lat', 'lon', 'station_move',
                   'elev', 'depth', 'teufe', 'data_error', 'meta_error'])
        hydro_tS.columns = output_header
        output = hydro_tS
    if write_csv == 'True':
        filename_out = str('%s.csv' % (HZB))
        hydro_tS.to_csv(filename_out, sep=';')

    if output_type == 'dict':
        output = {'data_error': data_error, 'meta_error': meta_error,
                  'station_name': station_name, 'catchment_name': catchment_name,
                  'catchment_symbol': catchment_symbol,
                  'subcatchment': subcatchment, 'region_name': region_name, 'HZB': HZB,
                  'HD_num': HD_num, 'DBMS_num': DBMS_num, 'province': province,
                  'operator': operator, 'catchment_size': catchment_size,
                  'lat': lat, 'lon': lon, 'elev': elev, 'depth': depth,
                  'teufe': teufe, 'station_move': station_move,
                  'datatype': datatype, 'timeseries': hydro_tS}

    return output
