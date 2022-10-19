# ytclip-server

[![Actions Status](https://github.com/zackees/ytclip-server/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/ytclip-server/workflows/Win_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/ytclip-server/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/ytclip-server/actions/workflows/push_ubuntu.yml)


Docker http server running [ytclip](https://github.com/zackees/ytclip).

![image](https://user-images.githubusercontent.com/6856673/196817552-1442f477-6251-4da0-b726-c9e86ed80fd4.png)

This repo has been tested with DigitalOcean and Render.com zero-config docker apps. Fork the repo then use the repo, the Docker app will be detected automatically.


# Docker

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `docker-compose up`
  * Now open up `http://127.0.0.1:80/`

# Non docker

## Using pip

  * `pip install ytclip-server`
  * `ytclip-server --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

## Using github

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `pip install -e .`
  * `run_dev.sh` (Browser will open up automatically)

# Full Tests + linting

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `tox`
