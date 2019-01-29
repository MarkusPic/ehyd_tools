__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from setuptools import setup

setup(
    name='ehyd_tools',
    version='0.1',
    packages=['ehyd_tools'],
    url='https://github.com/MarkusPic/ehyd_tools',
    license='MIT',
    author='Markus Pichler',
    author_email='markus.pichler@tugraz.at',
    description='Diverse tools to export and analyse the >10a rain series from the ehyd.gv.at platform',
    scripts=['bin/ehyd_tools'],
    install_requires=['numpy', 'pandas', 'matplotlib', 'requests'],
)
