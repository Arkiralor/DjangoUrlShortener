#!/bin/bash

python -m pip install pip-tools
pip-compile --output-file=./requirements.txt requirements.in
python -m pip install -r requirements.txt