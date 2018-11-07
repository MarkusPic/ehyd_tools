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

# Usage

To start the script use following commands in the terminal/Anaconda Prompt

Windows:
```python -m ehyd_tools```

Unix-Like:
```ehyd_tools```

## Commandline tool 

```
usage: ehyd_tools [-h] [-id ID] [-input INPUT] [--add_gaps] [-export EXPORT]
                  [--to_csv] [--max10a] [-start START] [-end END] [--plot]

optional arguments:
  -h, --help      show this help message and exit
  -id ID          the id number for the station from the ehyd.gv.at platform
  -input INPUT    path to the rain input file including the filename
  --add_gaps      get the gaps in the series as a csv table
  -export EXPORT  path to the rain input file
  --to_csv        save the data to the current directory
  --max10a        consider only 10 years with the most availability
  -start START    custom start time, Format="YYYY-MM-DD"
  -end END        custom end time, Format="YYYY-MM-DD"
  --plot          plot the data
```

## Example

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

> ehyd_100180_gaps.csv

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