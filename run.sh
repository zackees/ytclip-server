#!/usr/bin/sh
set -e
cd $( dirname ${BASH_SOURCE[0]})
pip install -e .
python3 ytclip_server/app.py