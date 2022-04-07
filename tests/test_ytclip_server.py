import os
import subprocess
import time
import unittest

import requests
from ytclip_server.version import VERSION

MY_IP = "127.0.0.1"
PORT = 4421


class YtclipServerTester(unittest.TestCase):
    """Tester for the ytclip-server."""

    # @unittest.skip("Skip for now")
    def test_platform_executable(self) -> None:
        """Opens up the ytclip-server and test that its running after one second."""
        env = {"ALLOW_SHUTDOWN": "1"}
        env.update(os.environ)
        proc = subprocess.Popen(f"ytclip-server --port {PORT}", shell=True, env=env)
        try:
            time.sleep(2)
            self.assertIsNone(proc.poll())
            self.assertEqual(VERSION, requests.get(f"http://{MY_IP}:{PORT}/version").text)
            requests.get(f"http://{MY_IP}:{PORT}/shutdown")
            proc.wait(timeout=10)
        finally:
            proc.terminate()


if __name__ == "__main__":
    unittest.main()
