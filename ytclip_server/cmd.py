"""ytclip-server command line tool."""

import os
import sys


def main() -> None:
    """Just launch ytclip_server from the command line."""
    os.system("uvicorn ytclip_server.app:app --no-use-colors --port 80 --host 0.0.0.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
