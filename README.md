# eHYD Tools
Diverse tools to export and analyse the >10a rain time series from the [https://ehyd.gv.at]() platform


If you are interested in a heavy rain analysis based on *Kostra*, take a look at my other python package 
[https://github.com/maxipi/intensity_duration_frequency_analysis]() which is compatible with this package.

# Install

See the python packages requirements in the 'requirements.txt'.

To install the packages via github, git must be installed first. (see [https://git-scm.com/]())

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
ehyd_tools --export csv --id 100180 --path .
ehyd_tools --export csv --max10years --id 100180 --path .
```

pip3 install /home/markus/PycharmProjects/ehyd_tools --upgrade --user