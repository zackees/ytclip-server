#!/usr/bin/sh
set -e
cd $( dirname ${BASH_SOURCE[0]})
pip install -e .
export FLASK_APP=ytclip_server/app.py
export FLASK_ENV=production
python3 -m flask run --host=0.0.0.0 --port=80