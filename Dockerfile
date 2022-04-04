FROM python:3.8

ADD server.py .

RUN pip install ytclip flask

CMD ["python", "server.py"]