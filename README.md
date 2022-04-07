# ytclip-server

Docker http server running [ytclip](https://github.com/zackees/ytclip)

Simply bring up the service with `docker-compose up`


# Demo

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `pip install -e .`
  * `ytclip_server --port 1234`
  * Now open up `http://127.0.0.1:1234` in a browser.

# Full Tests

  * `git clone https://github.com/zackees/ytclip-server`
  * `cd ytclip-server`
  * `tox`