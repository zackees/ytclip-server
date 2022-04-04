FROM python:3.8-slim-buster
COPY . .
RUN pip install ytclip flask
EXPOSE 5000
CMD ["python", "./server.py"]