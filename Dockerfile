FROM python:3.12.4-alpine

WORKDIR /usr/src/app

# prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# ensure python output is sent directly to the terminal 
ENV PYTHONUNBUFFERED 1

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

RUN python -m pip install --upgrade pip setuptools
RUN pip install --upgrade pip setuptools wheel
RUN pip install --upgrade pip

# Run the remove_module.py script to remove the specified module
RUN python remove_module.py

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Install nodejs and npm
RUN apk add --no-cache nodejs npm

# Set the working directory
WORKDIR /usr/src/app

# Copy the application files
COPY . .

# Verify the contents of the directory
RUN ls -al /usr/src/app/theme/static_src

# Install npm dependencies
WORKDIR /usr/src/app/theme/static_src
RUN npm install
RUN npm run build:css

# Collect static files
WORKDIR /usr/src/app
RUN python manage.py tailwind install
RUN python manage.py collectstatic --noinput

# Verify the installation of django-tailwind
RUN pip show django-tailwind

COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# eveyrthing will copied
COPY . /usr/src/app/ 

# this will run everytime the container starts
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]