"""
    Flask app for the ytclip command line tool. Serves an index.html at port 80. Clipping
    api is located at /clip
"""
import datetime
import os
import shutil
import subprocess
import threading
import time
import traceback

# import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Timer
from typing import Dict

from fastapi import FastAPI
from fastapi.responses import (
    FileResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles

from ytclip_server.version import VERSION

executor = ThreadPoolExecutor(max_workers=8)

DEFAULT_PORT = 80
DEFAULT_EXECUTOR_MAX_WORKERS = 32

HERE = os.path.dirname(__file__)
TEMP_DIR = os.path.join(HERE, "temp")

STATE_PROCESSING = "processing"
STATE_FINISHED = "finished"
STATE_ERROR = "error"


app = FastAPI()

# 4 hours of time before the mp4 is expired.
GARGABE_EXPIRATION_SECONDS = 60 * 60 * 4

active_tokens: Dict[str, str] = {}
active_tokens_mutex = Lock()
STARTUP_DATETIME = datetime.datetime.now()


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


garbage_collection_thread = Timer(GARGABE_EXPIRATION_SECONDS / 2, gabage_collect)
garbage_collection_thread.start()


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

    proc = subprocess.Popen(cmd, cwd=TEMP_DIR)  # pylint: disable=consider-using-with
    while proc.poll() is None:
        time.sleep(0.1)  # be very nice to other threads.
    if os.path.exists(os.path.join(TEMP_DIR, f"{token}.mp4")):
        with active_tokens_mutex:
            active_tokens[token] = STATE_FINISHED
    else:
        with active_tokens_mutex:
            active_tokens[token] = STATE_ERROR


def get_current_thread_id() -> int:
    """Return the current thread id."""
    ident = threading.current_thread().ident
    if ident is None:
        return -1
    return int(ident)


# Mount all the static files.
app.mount("/www", StaticFiles(directory=os.path.join(HERE, "www")), "www")

# Redirect to index.html
@app.get("/")
async def index() -> FileResponse:
    """Returns index.html file"""
    return RedirectResponse(url="/www/index.html")


# Redirect to favicon.ico
@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    """Returns favico file."""
    return RedirectResponse(url="/www/favicon.ico")


@app.get("/version")
async def api_version() -> PlainTextResponse:
    """Api endpoint for getting the version."""
    return PlainTextResponse(VERSION)


@app.get("/info")
async def api_info() -> PlainTextResponse:
    """Returns the current time and the number of seconds since the server started."""
    now_time = datetime.datetime.now()
    msg = "running\n"
    msg += "Example: localhost/clip\n"
    msg += "VERSION: " + VERSION + "\n"
    msg += f"Launched at         {STARTUP_DATETIME}\n"
    msg += f"Current utc time:   {datetime.datetime.utcnow()}\n"
    msg += f"Current local time: {now_time}\n"
    msg += f"Process ID: { os.getpid()}\n"
    msg += f"Thread ID: { get_current_thread_id() }\n"
    return PlainTextResponse(content=msg)


@app.get("/clip")
async def api_clip(start: str, end: str, url: str) -> PlainTextResponse:
    """Api endpoint to running the command."""
    # print(request)
    try:
        token = os.urandom(16).hex()
        with active_tokens_mutex:
            active_tokens[token] = STATE_PROCESSING
        task = lambda: run_ytclip(url=url, start=start, end=end, token=token)
        executor.submit(task)
        return PlainTextResponse(token, status_code=200)
    except Exception as exc:  # pylint: disable=broad-except
        traceback.print_exc()
        log_error(f"{exc}")
        return PlainTextResponse(f"error: {exc}", status_code=500)


@app.get("/clip/status/{token}")
async def api_clip_status(token: str) -> PlainTextResponse:
    """Non blocking method to check the status of a clip."""
    with active_tokens_mutex:
        status = active_tokens.get(token, None)
    if status is None:
        return PlainTextResponse(content="token not found", status_code=404)
    if status == STATE_FINISHED:
        return PlainTextResponse(content="ready for download", status_code=202)
    if status == STATE_PROCESSING:
        return PlainTextResponse(content="still processing", status_code=202)
    if status == STATE_ERROR:
        return PlainTextResponse(content="error aborted", status_code=500)
    return PlainTextResponse(content="unexpected state", status_code=500)


@app.get("/clip/download/{token}")
async def api_clip_download(token) -> Response:
    """Download the clip if it's ready."""
    with active_tokens_mutex:
        status = active_tokens.get(token, None)
    if status is None:
        return Response(status_code=404)
    if not status:
        return Response(content="still processing", status_code=202)
    # Download file to requester
    finished_file = os.path.join(TEMP_DIR, f"{token}.mp4")
    return FileResponse(finished_file)
