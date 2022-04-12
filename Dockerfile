# FROM ubuntu:22.04
FROM python:3.10-slim-bullseye

# Might be necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Setup the image
#RUN apt-get update
# Ubuntu:22.04 uses python 3.10
#RUN apt-get install -y python-is-python3 python3-pip

WORKDIR /app

# Install all the dependencies as it's own layer.
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Add requirements file and install.
COPY . .

RUN python -m pip install -e .

# Expose the port and then launch the app.
EXPOSE 80

# Very important to note that gunicorn[gthreads] is installed because we
# want to share the cache between all threads. Therefore the workers are
# set to 1 and the threads are set to a multiple of that.
CMD ["gunicorn", "--bind=0.0.0.0:80", "--worker-tmp-dir", "/dev/shm", "--workers=1", "--threads=5", "ytclip_server.app:app"]