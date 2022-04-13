# ytclip-server

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