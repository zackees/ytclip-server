curl -X GET https://raw.githubusercontent.com/zackees/make_venv/main/make_venv.py | python
source activate.sh
python -m pip install -r requirements.txt
python -m pip install -r requirements.testing.txt