
import datetime
import os
from typing import Tuple
from flask import Flask, request, Response
import traceback

import subprocess

DEFAULT_PORT = 80

STARTUP_DATETIME = datetime.datetime.now()

HERE = os.path.dirname(__file__)

# Note, app must be instantiated here because the functions
# below bind to it.
app = Flask(__name__)


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(HERE, filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)


def log_error(s: str) -> None:
    print(s)


def run_ytclip(url: str, start: str, end: str) -> str:
    """Return the string name of the file that was created."""
    print(f"{url} {start} {end}")
    outname = "test/out.mp4"
    cmd = ["ytclip", url, "--start_timestamp", start, "--end_timestamp", end, "--outname", outname]
    subprocess.check_output(cmd)
    return outname


@app.route('/', methods=['GET'])
def html():  # pragma: no cover
    content = get_file('index.html')
    return Response(content, mimetype="text/html")


@app.route("/info")
def apiDefault() -> Tuple[str, int, dict]:
    now_time = datetime.datetime.now()
    headers = {"content-type": "text/plain; charset=utf-8"}
    msg = "running\n"
    msg += f"Example: localhost/clip\n"
    msg += f"Launched at         {STARTUP_DATETIME}"
    msg += f"\nCurrent utc time:   {datetime.datetime.utcnow()}"
    msg += f"\nCurrent local time: {now_time}"
    msg += f"\nRequest headers: {request.headers}\n"
    return msg, 200, headers


@app.route("/clip", methods=["GET", "POST", "PUT", "DELETE"])
def apiClip() -> Tuple[str, int, dict]:
    # print(request)
    try:
        args = {k: v for k, v in request.form.items()}
        args.update({k: v for k, v in request.args.items()})
        url = args["url"]
        start = args["start"]
        end = args["end"]
    except Exception as e:
        traceback.print_exc()
        log_error(f"{e}")
        return f"invalid request", 400, {"content-type": "text/plain; charset=utf-8"}
    try:
        finished_file = run_ytclip(url=url, start=start, end=end)
        return f"{finished_file}", 200, {"content-type": "text/plain; charset=utf-8"}
    except Exception as e:
        traceback.print_exc()
        log_error(f"{e}")
        return f"failed", 500, {"content-type": "text/plain; charset=utf-8"}



def dev_main():
    port = int(os.environ.get("FLASK_PORT", DEFAULT_PORT))
    app.run(port=port)


if __name__ == "__main__":
    dev_main()
