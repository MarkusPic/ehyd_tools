# eHYD Tools
Diverse tools to export and analyse the >10a rain time series from the [https://ehyd.gv.at](https://ehyd.gv.at) platform


If you are interested in a heavy rain analysis based on *Kostra*, take a look at my other python package 
[https://github.com/maxipi/intensity_duration_frequency_analysis](https://github.com/maxipi/intensity_duration_frequency_analysis) which is compatible with this package.

# Install

See the python packages requirements in the 'requirements.txt'.

To install the packages via github, git must be installed first. (see [https://git-scm.com/](https://git-scm.com/))

Otherwise download the package manually via your browser and replace git+xxx.git with the path to the unzipped folder.

## Fresh install

```
pip3 install git+https://github.com/maxipi/ehyd_tools.git
```

## Update package

```
pip3 install git+https://github.com/maxipi/ehyd_tools.git --upgrade
```

# Usage

# Commandline tool 

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
