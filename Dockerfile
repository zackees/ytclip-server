FROM python:3.8-slim-buster
COPY . .
RUN pip install ytclip flask
EXPOSE 80
CMD ["python", "./server.py"]