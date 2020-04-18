© [Institute of Urban Water Management and Landscape Water Engineering](https://www.tugraz.at), [Graz University of Technology](https://www.tugraz.at/home/) and [Markus Pichler](mailto:markus.pichler@tugraz.at)

# eHYD Tools

[![license](https://img.shields.io/github/license/markuspic/ehyd_tools.svg?style=flat)](https://github.com/MarkusPic/ehyd_tools/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ehyd_tools.svg)](https://pypi.python.org/pypi/ehyd-tools)

Various tools for exporting and analyzing >10a rain time-series from the [ehyd.gv.at](https://ehyd.gv.at) platform of the Austian government.

If you are interested in a statistical heavy rain analysis like on *(Ö)Kostra*, take a look at my other python package [intensity_duration_frequency_analysis](https://github.com/MarkusPic/intensity_duration_frequency_analysis) which is compatible with this package.

# Install

The script is written in Python3. (use a version > 3.5)

## Windows

You have to install python (i.e. the original python from the [website](https://www.python.org/downloads/)).

The following commands show the usage for Linux/Unix systems. 

To use these features on Windows you have to add ```python -m``` before each command 
and you have to add the path to your python binary to the environment variables [^path1].

[^path1]: https://geek-university.com/python/add-python-to-the-windows-path/

There is also an option during the installation to add python to the PATH automatically. [^path2]

[^path2]: https://datatofish.com/add-python-to-windows-path/

![python_install](https://datatofish.com/wp-content/uploads/2018/10/0001_add_Python_to_Path.png)

## Linux/Unix

Python is pre-installed on most operating systems (as you probably knew).

## Required python packages

Packages required for this program will be installed with pip during the installation process and can be seen in the 'requirements.txt' file.

## Fresh install

```bash
pip install ehyd-tools
```

Add the following tags to the command for special options:

- ```--user```: To install the package only for the local user account (no admin rights needed)
- ```--upgrade```: To update the package

# Usage

To start the script use following commands in the terminal/Prompt

```ehyd_tools```

## Commandline tool 

With the `-h` (help) flag you can see the complete functionality of the tool.

```bash
ehyd_tools -h
```

> ```
> usage: __main__.py [-h] [-id ID] [--input INPUT] [--max10a] [--start START]
>                    [--end END] [--add_gaps] [--to_csv] [--to_parquet] [--plot]
>                    [--statistics] [--meta] [--unix]
> 
> optional arguments:
>   -h, --help     show this help message and exit
>   -id ID         the id number for the station from the ehyd.gv.at platform
>   --input INPUT  path to the rain input file including the filename
>   --max10a       consider only 10 years with the most availability (for
>                  clipping the data)
>   --start START  custom start time (Format="YYYY-MM-DD") for clipping the data
>   --end END      custom end time (Format="YYYY-MM-DD") for clipping the data
>   --add_gaps     save a gaps-table as a csv-file
>   --to_csv       save the time-series as csv-file (to the current directory if
>                  the id is used or in the directory of the input-file)
>   --to_parquet   save the time-series as parquet-file (to the current
>                  directory if the id is used or in the directory of the input-
>                  file) - parquet is a much faster as csv to read and write
>   --plot         save a bar-plot with monthly sums and availability as a png-
>                  file
>   --statistics   save the basic statistics (sum, max & min) as a txt-file
>   --meta         save the meta-data presented in ehyd as a txt-file
>   --unix         export the csv files with a "," as separator and a "." as
>                  decimal sign (otherwise ";" as separator and a "," as decimal
>                  sign will be used)
> ```

## Examples

[Example Jupyter notebooks for the commandline](example/example_commandline.ipynb)

[Example Jupyter notebooks for the python api](example/example_python_api.ipynb)

[Example python skript](example/example_python_api.py)

### Example Files

[CSV-Data of the rain series](example/ehyd_112086.csv)

[Data-gaps in the series](example/ehyd_112086_gaps.csv)

[Meta-data of the series](example/ehyd_112086_meta.txt)


### Example Plot

![Regenhöhenlinien](example/ehyd_112086_plot.png)


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