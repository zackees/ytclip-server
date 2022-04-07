# ytclip-server

Docker http server running [ytclip](https://github.com/zackees/ytclip)

# Docker Production test

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `docker-compose up`
  * Now open up `http://127.0.0.1:5128/`

# Demo

  * `pip install ytclip-server`
  * `ytclip-server --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

# Full Tests

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `tox`