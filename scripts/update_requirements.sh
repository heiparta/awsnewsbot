#!/usr/bin/env bash
set -euo pipefail
set -x

VENV=$(mktemp -d)
echo "Creating virtualenv to $VENV"
python3 -m venv $VENV

set +u
source $VENV/bin/activate
set -u
which pip
pip install -r requirements.in

pip freeze > requirements.txt
source deactivate
rm -rf $VENV