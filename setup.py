from setuptools import setup, find_packages

setup(
    name='lib.py',
    version='0.1',
    packages=find_packages(),
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.json', '*.', '*.png', '*.pdf', '*.csv', '*.tex','*.xslx'],
    },
    url='',
    license='',
    author='pichler',
    author_email='markus.pichler@tugraz.at',
    description='Diverse tools to export and analyse the >10a rain series from the ehyd.gv.at platform',
    scripts=['bin/ehyd_tools'],
)
