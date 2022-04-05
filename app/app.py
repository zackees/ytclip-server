"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""

import datetime
import os
import subprocess
import traceback
from typing import Tuple

from flask import Flask, Response, request

DEFAULT_PORT = 80

STARTUP_DATETIME = datetime.datetime.now()

HERE = os.path.dirname(__file__)

# Note, app must be instantiated here because the functions
# below bind to it.
app = Flask(__name__)


def get_file(filename):  # pragma: no cover
    """Get the contents of a file."""
    try:
        src = os.path.join(HERE, filename)
        # Specify binary mode to avoid decoding errors
        return open(src, mode="rb").read()  # pytype: disable=unspecified-encoding
    except IOError as exc:
        return str(exc)


def log_error(msg: str) -> None:
    """Logs an error to the print stream."""
    print(msg)


def run_ytclip(url: str, start: str, end: str) -> str:
    """Return the string name of the file that was created."""
    print(f"{url} {start} {end}")
    outname = "test/out.mp4"
    cmd = [
        "ytclip",
        url,
        "--start_timestamp",
        start,
        "--end_timestamp",
        end,
        "--outname",
        outname,
    ]
    subprocess.check_output(cmd)
    return outname


@app.route("/", methods=["GET"])
def api_default():  # pragma: no cover
    """Returns the contents of the index.html file."""
    content = get_file("index.html")
    return Response(content, mimetype="text/html")


@app.route("/info")
def api_info() -> Tuple[str, int, dict]:
    """Returns the current time and the number of seconds since the server started."""
    now_time = datetime.datetime.now()
    headers = {"content-type": "text/plain; charset=utf-8"}
    msg = "running\n"
    msg += "Example: localhost/clip\n"
    msg += f"Launched at         {STARTUP_DATETIME}"
    msg += f"\nCurrent utc time:   {datetime.datetime.utcnow()}"
    msg += f"\nCurrent local time: {now_time}"
    msg += f"\nRequest headers: {request.headers}\n"
    return msg, 200, headers


@app.route("/clip", methods=["GET", "POST", "PUT", "DELETE"])
def api_clip() -> Tuple[str, int, dict]:
    """Api endpoint to running the command."""
    # print(request)
    try:
        args = dict(request.form.items())
        args.update(dict(request.args.items()))
        url = args["url"]
        start = args["start"]
        end = args["end"]
    except Exception as err:  # pylint: disable=broad-except
        traceback.print_exc()
        log_error(f"{err}")
        return "invalid request", 400, {"content-type": "text/plain; charset=utf-8"}
    try:
        finished_file = run_ytclip(url=url, start=start, end=end)
        return f"{finished_file}", 200, {"content-type": "text/plain; charset=utf-8"}
    except Exception as exc:  # pylint: disable=broad-except
        traceback.print_exc()
        log_error(f"{exc}")
        return "failed", 500, {"content-type": "text/plain; charset=utf-8"}


def main() -> None:
    """Run the flask app."""
    port = int(os.environ.get("FLASK_PORT", DEFAULT_PORT))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
