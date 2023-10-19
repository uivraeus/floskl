#!/bin/bash

set -euo pipefail

venvpath=.venv
python -m venv $venvpath && source $venvpath/bin/activate && pip install -r ./requirements.txt

echo
echo "Python environment for web app prepared at: $venvpath"
