FROM ubuntu:22.04

# Might be necessary.
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Setup the image
RUN apt-get update
# Ubuntu:22.04 uses python 3.10
RUN apt-get install -y python-is-python3 python3-pip

# Add requirements file and install.
COPY ./requirements.txt /requirements.txt
# Install requirements
RUN pip3 install -r requirements.txt

# Copy Application files.
COPY ./app .

# Expose the port and then launch the app.
EXPOSE 80

ENV FLASK_APP=ytclip-server/app.py
ENV FLASK_ENV=production

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=80"]
