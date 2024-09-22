FROM python:3.12.4-alpine

WORKDIR /usr/src/app

# prevent python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# ensure python output is sent directly to the terminal 
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY ./requirements.txt /usr/src/app/requirements.txt

RUN pip install -r requirements.txt

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