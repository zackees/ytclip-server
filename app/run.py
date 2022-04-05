"""
    Runs the app.py file in the current directory. Will auto update if git repo updates changes.
"""


import os
import subprocess
import time
from datetime import datetime

import flask

HERE = os.path.abspath(os.path.dirname(__file__))

# Every 60 minutes
# _TIME_BEFORE_RECHECK = 60 * 60
_TIME_BEFORE_RECHECK = 10

def main() -> None:
    """Main entry point."""
    # Start off by updating to the latest version of the repo.
    subprocess.call(["git", "pull"], cwd=HERE)
    # Setup the environment
    env = {"FLASK_APP": "app/app.py", "FLASK_ENV": "development"}
    env.update(os.environ)
    # Start the flask app
    cmd = ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
    try:
        flask_proc = subprocess.Popen(cmd, env=env, cwd=os.path.dirname(HERE))
        while True:
            time.sleep(_TIME_BEFORE_RECHECK)
            subprocess.call(["git", "pull"], cwd=HERE)
    finally:
        flask_proc.terminate()


if __name__ == "__main__":
    main()
