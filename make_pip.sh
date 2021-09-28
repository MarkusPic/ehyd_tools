#!/usr/bin/env bash

python3 _copy_readme.py

SCRIPTPATH=$(dirname "$BASH_SOURCE")
cd $SCRIPTPATH

python3 -m build
python3 -m twine upload dist/*