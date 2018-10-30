# ehyd_tools
Diverse tools to export and analyse the >10a rain time series from the [https://ehyd.gv.at]() platform


If you are interested in a heavy rain analysis based on *Kostra*, take a look at my other python package 
[https://github.com/maxipi/kostra]() which is compatible with this package.

# Install

See the python packages requirements in the 'requirements.txt'.

## Fresh install

```
sudo -H pip3 install git+https://github.com/maxipi/ehyd_tools.git
```

## Update package

```
sudo -H pip3 install --upgrade git+https://github.com/maxipi/ehyd_tools.git
```

# Usage

# Commandline tool 

```
ehyd_tools --export csv --id 100180 --path .
ehyd_tools --export csv --max10years --id 100180 --path .
```