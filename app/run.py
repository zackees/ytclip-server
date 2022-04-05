"""
    Runs the app.py file in the current directory. Will auto update if git repo updates changes.
"""


import os
import subprocess
import time
from datetime import datetime

HERE = os.path.abspath(os.path.dirname(__file__))

# Every 60 minutes
_TIME_BEFORE_RECHECK = 60 * 60
# _TIME_BEFORE_RECHECK = 10


def _check_repo() -> bool:
    """Check if the repo has changed."""
    cmd = ["git", "diff", "--quiet", "HEAD"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()
    return proc.returncode == 0


def main() -> None:
    """Main entry point."""
    # Start off by updating to the latest version of the repo.
    subprocess.call(["git", "pull"], cwd=HERE)
    # Setup the environment
    env = {"FLASK_APP": "app/app.py", "FLASK_ENV": "development"}
    env.update(os.environ)
    # Start the flask app
    cmd = ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
    flask_proc = subprocess.Popen(cmd, env=env, cwd=os.path.dirname(HERE))

    while True:
        time.sleep(_TIME_BEFORE_RECHECK)
        if _check_repo():
            print(f"Changes in the repo have been detected at {datetime.now()}")
            # The repo has changed so it and the flask app need to be updated.
            print("Killing the running flask task")
            flask_proc.kill()
            flask_proc.wait()
            print("Updating the repo")
            cmd = ["git", "pull"]
            subprocess.call(cmd, cwd=HERE)
            print("Restarting the flask app.")
            flask_proc = subprocess.Popen(cmd, env=env, cwd=HERE)


if __name__ == "__main__":
    main()
