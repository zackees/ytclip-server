"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import argparse
import datetime
import os
import shutil
import signal
import subprocess
import sys
import time
import traceback
from threading import Lock, Timer
from typing import Dict, Tuple

from flask import Flask, Response, request, send_from_directory
from flask_executor import Executor  # type: ignore

# TODO: Why is this necessary?!?!
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ytclip_server"))
from version import VERSION

ALLOW_SHUTDOWN = False
DEFAULT_PORT = 80
DEFAULT_EXECUTOR_MAX_WORKERS = 32

STARTUP_DATETIME = datetime.datetime.now()

HERE = os.path.dirname(__file__)
TEMP_DIR = os.path.join(HERE, "temp")

STATE_PROCESSING = "processing"
STATE_FINISHED = "finished"
STATE_ERROR = "error"

# 4 hours of time before the mp4 is expired.
GARGABE_EXPIRATION_SECONDS = 60 * 60 * 4

active_tokens: Dict[str, str] = {}
active_tokens_mutex = Lock()

# Generate temp directory to do work in.
if os.path.exists(TEMP_DIR):
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
os.makedirs(TEMP_DIR, exist_ok=True)


def file_age(filepath: str) -> float:
    """Return the age of a file."""
    return (
        datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
    ).total_seconds()


def gabage_collect() -> None:
    """Garbage collect old files."""
    for filename in os.listdir(TEMP_DIR):
        if filename.endswith(".mp4"):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                file_age_seconds = file_age(file_path)
                if file_age_seconds > GARGABE_EXPIRATION_SECONDS:
                    try:
                        basename = os.path.basename(file_path)
                        token = os.path.splitext(basename)[0]
                        with active_tokens_mutex:
                            if token in active_tokens:
                                del active_tokens[token]
                        os.remove(file_path)
                    except Exception:  # pylint: disable=broad-except
                        log_error(traceback.format_exc())


# Note, app must be instantiated here because the functions
# below bind to it.
app = Flask(__name__)
app.config["EXECUTOR_MAX_WORKERS"] = int(
    os.environ.get("EXECUTOR_MAX_WORKERS", DEFAULT_EXECUTOR_MAX_WORKERS)
)
executor = Executor(app)
garbage_collection_thread = Timer(GARGABE_EXPIRATION_SECONDS / 2, gabage_collect)


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


def run_ytclip(url: str, start: str, end: str, token: str) -> None:
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
        with active_tokens_mutex:
            active_tokens[token] = STATE_FINISHED
    else:
        with active_tokens_mutex:
            active_tokens[token] = STATE_ERROR


@app.route("/", methods=["GET"])
def api_default() -> Response:
    """Returns the contents of the index.html file."""
    content = get_file("index.html")
    return Response(content, mimetype="text/html")


@app.route("/preview.jpg", methods=["GET"])
def api_preview() -> Response:
    """Returns the contents of the preview.jpg file."""
    content = get_file("preview.jpg")
    return Response(content, mimetype="image/jpeg")


@app.route("/info")
def api_info() -> Tuple[str, int, dict]:
    """Returns the current time and the number of seconds since the server started."""
    now_time = datetime.datetime.now()
    headers = {"content-type": "text/plain; charset=utf-8"}
    msg = "running\n"
    msg += "Example: localhost/clip\n"
    msg += "VERSION: " + VERSION + "\n"
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
        with active_tokens_mutex:
            active_tokens[token] = STATE_PROCESSING
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
    with active_tokens_mutex:
        status = active_tokens.get(token, None)
    if status is None:
        return "not found", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_FINISHED:
        return "ready for download", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_PROCESSING:
        return "still processing", 200, {"content-type": "text/plain; charset=utf-8"}
    if status == STATE_ERROR:
        return "error aborted", 200, {"content-type": "text/plain; charset=utf-8"}
    return "unknown", 200, {"content-type": "text/plain; charset=utf-8"}


@app.route("/clip/download/<token>", methods=["GET"])
def api_clip_download(token) -> Response:
    """Download the clip if it's ready."""
    with active_tokens_mutex:
        status = active_tokens.get(token, None)
    if status is None:
        return Response("not found", status=404, mimetype="text/plain; charset=utf-8")
    if not status:
        return Response("still processing", status=200, mimetype="text/plain; charset=utf-8")
    # Download file to requester
    name = f"{token}.mp4"
    return send_from_directory(TEMP_DIR, name, as_attachment=True)


@app.route("/version", methods=["GET"])
def api_version() -> Response:
    """Api endpoint for getting the version."""
    return Response(f"{VERSION}", status=200, mimetype="text/plain; charset=utf-8")


@app.route("/shutdown", methods=["GET"])
def api_clip_shutdown() -> Response:
    """Api endpoint for terminating the process."""

    def kill_process():
        """Kill the process."""
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)

    if not ALLOW_SHUTDOWN:
        return Response("shutdown not allowed", status=403, mimetype="text/plain; charset=utf-8")
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        func = kill_process
    executor.submit(func)
    return Response("shutdown", status=200, mimetype="text/plain; charset=utf-8")


def main() -> None:
    """Run the flask app."""
    global ALLOW_SHUTDOWN  # pylint: disable=global-statement
    parser = argparse.ArgumentParser(description="ytclip-server")
    parser.add_argument("--port", type=int, default=None, help="port to listen on")
    args = parser.parse_args()
    port = args.port or int(os.environ.get("FLASK_PORT", DEFAULT_PORT))
    ALLOW_SHUTDOWN = bool(int(os.environ.get("ALLOW_SHUTDOWN", "0")))
    # Gracefully shutdown the flask app on SIGINT
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)


if __name__ == "__main__":
    main()
