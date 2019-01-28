__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='ehyd_tools',
    version='0.1',
    packages=find_packages(),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.json', '*.', '*.png', '*.pdf', '*.csv', '*.tex','*.xslx'],
    },
    url='https://github.com/MarkusPic/ehyd_tools',
    license='MIT',
    author='pichler',
    author_email='markus.pichler@tugraz.at',
    description='Diverse tools to export and analyse the >10a rain series from the ehyd.gv.at platform',
    scripts=['bin/ehyd_tools'],
    install_requires=requirements,
)
