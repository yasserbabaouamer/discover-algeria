# Base image
FROM python:3.11-slim-buster

# Update the os environment variable to not delay logs
ENV PYTHONBUFFERED = 1

WORKDIR /discoveralgeria

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    libmariadb-dev-compat \
    default-libmysqlclient-dev \
    build-essential

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Copy the project files to the image
COPY . .

# run on 0.0.0.0 to make the application available from outside the container
CMD python manage.py runserver 0.0.0.0:8000
