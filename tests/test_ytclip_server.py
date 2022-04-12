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
PORT = 4422


class Server(uvicorn.Server):
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


config = Config(APP_NAME, host=MY_IP, port=PORT, log_level="info", use_colors=False)
server = Server(config=config)


class YtclipServerTester(unittest.TestCase):
    """Tester for the ytclip-server."""

    # @unittest.skip("Skip for now")
    def test_platform_executable(self) -> None:
        """Opens up the ytclip-server and test that its running after one second."""
        with server.run_in_thread():
            time.sleep(1)
            version = requests.get(f"http://{MY_IP}:{PORT}/version").text
            self.assertEqual(VERSION, version)


if __name__ == "__main__":
    unittest.main()
