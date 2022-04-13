cd $( dirname ${BASH_SOURCE[0]})
python make_venv.py
source activate.sh
python -m pip install -r requirements.txt
python -m pip install -r requirements.testing.txt