import contextlib
import threading
import time
import unittest

import requests
import uvicorn
from uvicorn.config import Config

# from ytclip_server.app import app
from ytclip_server.version import VERSION

APP_NAME = "ytclip_server.app:app"
MY_IP = "127.0.0.1"
PORT = 4422  # Arbitrarily chosen.


# Surprisingly uvicorn does allow graceful shutdowns, making testing hard.
# This class is the stack overflow answer to work around this limitiation.
# Note: Running this in python 3.8 and below will cause the console to spew
# scary warnings during test runs:
#   ValueError: set_wakeup_fd only works in main thread
class ServerWithShutdown(uvicorn.Server):
    """Adds a shutdown method to the uvicorn server."""

    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        """Runs the server in a thread and allows operations to be applied on it."""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


server = ServerWithShutdown(
    config=Config(APP_NAME, host=MY_IP, port=PORT, log_level="info", use_colors=False)
)


class YtclipServerTester(unittest.TestCase):
    """Tester for the ytclip-server."""

    # @unittest.skip("Skip for now")
    def test_platform_executable(self) -> None:
        """Opens up the ytclip-server and tests that the version returned is correct."""
        with server.run_in_thread():
            time.sleep(1)
            version = requests.get(f"http://{MY_IP}:{PORT}/version").text
            self.assertEqual(VERSION, version)


if __name__ == "__main__":
    unittest.main()
