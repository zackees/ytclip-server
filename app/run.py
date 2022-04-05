"""
    Runs the app.py file in the current directory. Will auto update if git repo updates changes.
"""


import os
import subprocess
import time

HERE = os.path.dirname(__file__)

# Every 60 minutes
# _TIME_BEFORE_RECHECK = 60 * 60
_TIME_BEFORE_RECHECK = 10


def _check_repo() -> bool:
    """Check if the repo has changed."""
    cmd = ["git", "diff", "--quiet", "HEAD"]
    proc = subprocess.Popen(cmd, cwd=HERE)
    proc.wait()
    return proc.returncode == 0


def main() -> None:
    """Main entry point."""
    env = {"FLASK_APP": "app.py", "FLASK_ENV": "development"}
    env.update(os.environ)
    cmd = ["flask", "run", "--host", "0.0.0.0", "--port", "80"]
    flask_proc = subprocess.Popen(cmd, env=env, cwd=HERE)

    while True:
        time.sleep(_TIME_BEFORE_RECHECK)
        if _check_repo():
            flask_proc.kill()
            flask_proc.wait()
            # force a git pull
            cmd = ["git", "pull"]
            subprocess.call(cmd, cwd=HERE)
            flask_proc = subprocess.Popen(cmd, env=env, cwd=HERE)


if __name__ == "__main__":
    main()
