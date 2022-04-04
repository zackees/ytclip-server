FROM ubuntu:20.04

# Setup the image
RUN apt-get update
RUN apt-get install -y python-is-python3 python3-pip

# Add requirements file and install.
COPY ./requirements.txt /requirements.txt
# Install requirements
RUN python -m pip install -r requirements.txt

# Copy Application files.
COPY ./app.py /app.py

# Expose the port and then launch the app.
EXPOSE 80
CMD ["python", "./app.py"]