__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ehyd-tools',
    version='0.1dev3',
    packages=['ehyd_tools'],
    url='https://github.com/MarkusPic/ehyd_tools',
    license='MIT',
    author='Markus Pichler',
    author_email='markus.pichler@tugraz.at',
    description='Various tools for exporting and analyzing >10a rain time-series from the '
                '"ehyd.gv.at" platform of the Austian government.',
    scripts=['bin/ehyd_tools'],
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
