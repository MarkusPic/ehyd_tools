# eHYD Tools
Diverse tools to export and analyse the >10a rain time series from the [https://ehyd.gv.at](https://ehyd.gv.at) platform


If you are interested in a heavy rain analysis like on *Kostra*, take a look at my other python package 
[https://github.com/maxipi/intensity_duration_frequency_analysis](https://github.com/maxipi/intensity_duration_frequency_analysis) which is compatible with this package.

# Install

See the python packages requirements in the 'requirements.txt'. (those packages will get installed during the installing process)

To install the packages via github, [git](https://git-scm.com/) must be installed first.

Otherwise download the package manually via your browser and replace git+xxx.git with the path to the unzipped folder.

I recommend to use Anaconda to install python on Windows and the [Anaconda](https://www.anaconda.com/download/) Prompt for the commandline tool.

## Fresh install

The script is written in Python3.

```
pip install git+https://github.com/maxipi/ehyd_tools.git
```

To install the package only for the local user account, add ```--user``` to the install command.

## Update package

To update the package, add ```--upgrade``` to the install command.

```
pip install git+https://github.com/maxipi/ehyd_tools.git --upgrade
```

## Install without git

First download the package as a zip with the green download button above:

Then unzip the folder.

Now you can install the package with the local files

```
pip install <PATH_TO_FOLDER>\ehyd_tools-master
```

# Usage

To start the script use following commands in the terminal/Anaconda Prompt

Windows:
```python -m ehyd_tools```

Unix-Like:
```ehyd_tools```

## Commandline tool 

> ehyd_tools -h

```
usage: ehyd_tools [-h] [-id ID] [--input INPUT] [--add_gaps] [--to_csv]
                  [--max10a] [--start START] [--end END] [--plot]
                  [--statistics] [--meta] [--unix]

optional arguments:
  -h, --help     show this help message and exit
  -id ID         the id number for the station from the ehyd.gv.at platform
  --input INPUT  path to the rain input file including the filename
  --add_gaps     get the gaps in the series as a csv table
  --to_csv       save the data to the current directory
  --max10a       consider only 10 years with the most availability
  --start START  custom start time, Format="YYYY-MM-DD"
  --end END      custom end time, Format="YYYY-MM-DD"
  --plot         plot the data
  --statistics   creates a txt file with basic statistics (sum, max & min)
  --meta         add the txt file with the meta data of the ehyd data
  --unix         export the csv files with a "," as separator and a "." as
                 decimal sign.
```

## Example


### Example 1

```ehyd_tools -id 100180 --to_csv --max10a --add_gaps```

The results will be:

First the name of the station will be printed to the terminal.

```You choose the station: "Tschagguns" with the id: "100180".```

Because of the ```--max10a``` argument, the series will get a new start and end time base on the maximum availability.

```Data was clipped to start="1982-04-30" and end="1992-04-30".```

The standard filename of the output-files starts with *ehyd_\<ID\>*.

All the files will be created in the current directory.

With the ```--add_gaps``` argument, a csv file of the gaps in the series with the name *ehyd_\<ID\>_gaps.csv* will be created.

With the ```--to_csv``` argument, a csv file of the series with the name *ehyd_\<ID\>.csv* will be created.

After the command above two files will be created:

> ehyd_100180.csv
>
> ehyd_100180_gaps.csv


### Example 2

```ehyd_tools -id 100180 --plot```

With the ```--plot``` argument, a png file of the series bar plot with the name *ehyd_\<ID\>_plot.png* will be created.

For data series longer than 15 years, annual sums, otherwise monthly sums, are used.

After the command above these file will be created:

> ehyd_100180_plot.png

![Regenhöhenlinien](example/ehyd_100180_plot.png)

### Example 3

```ehyd_tools -id 100180 --meta --statistics```

With the ```--meta``` argument, a txt file containing the meta data with the name *ehyd_\<ID\>_meta.txt* will be created.

With the ```--statistics``` argument, a txt file containing the statistics of the series with the name *ehyd_\<ID\>_stats.txt* will be created.

After the command above these two files will be created:


> ehyd_100180_meta.txt

```
Messstelle:                ;Tschagguns
HZB-Nummer:                ;100180
HD-Nummer:                 ;HD8000018
DBMS-Nummer:               ;8000018
Sachgebiet:                ;NLV
Dienststelle:              ;HD-Vorarlberg
Messstellenbetreiber:      ;Hydrographischer Dienst
H�he:
 g�ltig seit:              ;H�he [m �.A.]:
  01.08.1921               ;681
Geographische Koordinaten (Referenzellipsoid: Bessel 1841):
 g�ltig seit:              ;L�nge (Grad,Min,Sek):    ;Breite  (Grad,Min,Sek):
  01.08.1921               ;09 54 57                 ;47 04 03
Zugeordnete Messcodes:
 g�ltig seit: ;g�ltig bis:  ;Messcode:                           ;Entstehungsart:
  01.01.1953;   30.03.2004;  Nh/Schwimmer (Heber);                digitalisiert
  30.03.2004;              ; Nh/elekt.Waage, 500 cm�, beh.;       Datensammler -> DF�
Ursprungszeitreihe:        ;Niederschlag,K,,,0,O,Z,0,,,
Transformation:            ;Summe
Summenintervall:           ;1 Minute
Exportzeitreihe:           ;Abgeleitete Intervallzeitreihe
                           ;Niederschlag,I,Sum,E,12,M,Z,0,,,
Exportqualit�t:            ;MAXQUAL (2)
Exportzeitraum:            ;Beginn der Datenaufzeichnung; bis ;01.01.2016 00:00
Hinweis:                   ;Der Intervallwert gilt bis zum n�chsten Zeitpunkt mit einem Wert oder L�cke
Hinweis:                   ;ACHTUNG: Aufeinanderfolgende gleiche Werte von 0 und L�cke sind jeweils zu einem l�ngeren Intervall zusammengefasst
Hinweis:                   ;Werte aus (teilweise) ungepr�ften Rohdaten
Werteformat:               ;3 Nachkommastellen
Einheit:                   ;mm
```

> ehyd_100180_stats.txt

```
The annual totals of the data series serve as the data basis.
The following statistics were analyzed:

The maximum is 1438 mm and was in the year 2012.
The minimum is 0 mm and was in the year 2016.
The mean is 1090 mm.
```


## The stations

|id      |                      station|
|--------|-----------------------------|
|100180  |                   Tschagguns|
|100370  |                    Thüringen|
|100446  |                     Lustenau|
|100479  |                     Dornbirn|
|100776  |                      Bregenz|
|101303  |         Leutasch-Kirchplatzl|
|101816  |                 Ladis-Neuegg|
|102772  |                     Kelchsau|
|103143  |  St. Johann in Tirol-Almdorf|
|103895  |                    Eugendorf|
|104604  |                      Schlägl|
|104877  |                  Linz-Urfahr|
|105445  |                  Vöcklabruck|
|105528  |                         Wels|
|105908  |                      Flachau|
|106112  |                       Liezen|
|106252  |                    Wildalpen|
|106435  |       Klaus an der Pyhrnbahn|
|106559  |                        Steyr|
|106856  |      Weitersfelden-Ritzenedt|
|107029  |                  Lunz am See|
|107284  |                         Melk|
|107854  |                   Hollabrunn|
|108118  |    Wien (Botanischer Garten)|
|108456  |                   Gutenstein|
|108563  |                      Naglern|
|109280  |       Waidhofen an der Thaya|
|109918  |                  Neunkirchen|
|110064  |                   Gattendorf|
|110312  |                         Karl|
|110734  |                   Eisenstadt|
|111112  |                     Oberwart|
|111435  |                         Alpl|
|111716  |                    Judenburg|
|112086  |                 Graz-Andritz|
|112391  |       St.Peter am Ottersbach|
|112995  |             Ried im Innkreis|
|113001  |                      Sillian|
|113050  |           Matrei in Osttirol|
|113548  |                       Afritz|
|113670  |                      Waidegg|
|114561  |                   Klagenfurt|
|114702  |                    Wolfsberg|
|115055  |                   Kendlbruck|
|115642  |                    St.Pölten|
|120022  |                Hall in Tirol|