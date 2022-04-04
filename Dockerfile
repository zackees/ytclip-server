FROM ubuntu:18.04

COPY ./app.py /app.py

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

RUN python -m pip install ytclip
RUN python -m pip install flask

EXPOSE 80
CMD ["python", "./app.py"]