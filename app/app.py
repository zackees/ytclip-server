"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""

import datetime
import os
import shutil
import subprocess
import traceback
from typing import Tuple

from flask import Flask, Response, request, send_from_directory
from flask_executor import Executor

DEFAULT_PORT = 80

STARTUP_DATETIME = datetime.datetime.now()

HERE = os.path.dirname(__file__)
TEMP_DIR = os.path.join(HERE, "temp")

STATE_PROCESSING = "processing"
STATE_FINISHED = "finished"
STATE_ERROR = "error"

active_tokens = {}

# Generate temp directory to do work in.
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Note, app must be instantiated here because the functions
# below bind to it.
app = Flask(__name__)
executor = Executor(app)


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


def run_ytclip(url: str, start: str, end: str, token: str) -> str:
    """Return the string name of the file that was created."""
    print(f"{url} {start} {end}")
    cmd = [
        "ytclip",
        url,
        "--start_timestamp",
        start,
        "--end_timestamp",
        end,
        "--outname",
        token,
    ]

    subprocess.call(cmd, cwd=TEMP_DIR)
    if os.path.exists(os.path.join(TEMP_DIR, f"{token}.mp4")):
        active_tokens[token] = STATE_FINISHED
    else:
        active_tokens[token] = STATE_ERROR


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
        token = os.urandom(16).hex()
        active_tokens[token] = STATE_PROCESSING
        # TODO: Break this off into a thread.
        task = lambda: run_ytclip(url=url, start=start, end=end, token=token)
        executor.submit(task)
        return f"{token}", 200, {"content-type": "text/plain; charset=utf-8"}
    except Exception as exc:  # pylint: disable=broad-except
        traceback.print_exc()
        log_error(f"{exc}")
        return "failed", 500, {"content-type": "text/plain; charset=utf-8"}


@app.route("/clip/status/<token>", methods=["GET"])
def api_clip_status(token) -> Tuple[str, int, dict]:
    """Api endpoint to running the command."""
    status = active_tokens.get(token, None)
    if status is None:
        return "not found", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_FINISHED:
        return "ready for download", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_PROCESSING:
        return "still processing", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_ERROR:
        return "error aborted", 200, {"content-type": "text/plain; charset=utf-8"}


@app.route("/clip/download/<token>", methods=["GET"])
def api_clip_download(token) -> Tuple[str, int, dict]:
    """Download the clip if it's ready."""
    status = active_tokens.get(token, None)
    if status is None:
        return "not found", 404, {"content-type": "text/plain; charset=utf-8"}
    if not status:
        return f"still processing", 200, {"content-type": "text/plain; charset=utf-8"}
    # Download file to requester
    name = f"{token}.mp4"
    return send_from_directory(TEMP_DIR, name, as_attachment=True)


def main() -> None:
    """Run the flask app."""
    port = int(os.environ.get("FLASK_PORT", DEFAULT_PORT))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
