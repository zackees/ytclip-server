FROM ubuntu:18.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Setup the image
RUN apt-get update
RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y python3.8 python3-pip

# Add requirements file and install.
COPY ./requirements.txt /requirements.txt
# Install requirements
RUN pip3 install -r requirements.txt

# Copy Application files.
COPY ./app.py /app.py
COPY ./index.html /index.html

# Expose the port and then launch the app.
EXPOSE 80

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_PORT=80

# CMD ["flask", "run"]
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
#CMD ["python", "-m", "http.server", "80"]