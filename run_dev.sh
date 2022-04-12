#!/usr/bin/sh
set -e
cd $( dirname ${BASH_SOURCE[0]})
uvicorn ytclip_server.app:app --no-use-colors --reload --port 80 --host 0.0.0.0