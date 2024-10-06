FROM python:3.12.4-alpine

# set root directory
WORKDIR /django

# prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# ensure python output is sent directly to the terminal 
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /django

# RUN apk update && add postgresql-dev gcc musl-dev

# Install dependencies
RUN apk update && apk add --no-cache \
    ffmpeg \
    gcc \
    g++ \
    libffi-dev \
    musl-dev \
    postgresql-dev \
    linux-headers \
    nodejs \
    npm

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Install nodejs and npm
RUN apk add --no-cache nodejs npm
USER root
# Copy the application files
COPY . .

WORKDIR /django
RUN python manage.py collectstatic --noinput
# Verify the installation of django-tailwind
# RUN pip show django-tailwind

# Ensure the entrypoint script is executable
WORKDIR /django
COPY entrypoint.sh /django/entrypoint.sh
RUN chmod +x /django/entrypoint.sh

ENTRYPOINT ["/django/entrypoint.sh"]

