# start from base
FROM ubuntu:18.04

COPY ./app.py /app.py
COPY ./requirements.txt /requirements.txt

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

RUN pip install ytclip flask

EXPOSE 80
CMD ["python", "./app.py"]