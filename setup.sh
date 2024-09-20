#!/bin/bash

# step 0 configure the core folder
cd ..
mv ./core_hms_final ./core

# Step 1: Create a virtual environment
python3 -m venv hms_venv

# Step 2: Activate the virtual environment
source hms_venv/bin/activate

# go into core
cd core

# Step 3: Upgrade pip
pip install --upgrade pip

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Change directory to the Django project directory
# cd my_django_project

# Step 6: Run Django migrations
python manage.py migrate

# Step 7: Collect static files
python manage.py collectstatic --noinput

# Step 8: Copy files to a specific directory
cp docker-compose.yml ../docker-compose.yml

# Step 9: Change back to the original directory
# cd core

# Step 10: Run the Django development server
# python manage.py runserver
docker-compose up
