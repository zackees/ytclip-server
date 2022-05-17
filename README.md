# ytclip-server

[![Actions Status](https://github.com/zackees/ytclip-server/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/ytclip-server/workflows/Win_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/ytclip-server/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_ubuntu.yml)


Docker http server running [ytclip](https://github.com/zackees/ytclip)

# Demo

  * `pip install ytclip-server`
  * `ytclip-server --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

# Demo from github

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `pip install -e .`
  * `run_dev.sh` (Browser will open up automatically)

# Docker Production test

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `docker-compose up`
  * Now open up `http://127.0.0.1:80/`

# Full Tests + linting

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `tox`