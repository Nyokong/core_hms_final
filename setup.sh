#!/bin/bash

mv ./core_hms_final ./core
# go outside the directory
cd ..
# 1. Create the new folder named 'core'
mkdir core

# 2. Copy all files and folders from the current directory to the 'core' directory
# 1. Create the new folder named 'core' (if it doesn't already exist)
if [ ! -d "./core" ]; then
    mkdir ./core
    echo "Created 'core' directory."
else
    echo "'core' directory already exists."
fi

cd core_hms_final

# 2. Copy all files and folders from the current directory to the 'core' directory
# Make sure not to copy 'core' into itself
cp -r ./* ../core/

cd ..

# 3. Remove the original files (but not 'core' itself)
echo "Now trying to delete core_hms_final."
# find . -mindepth 1 -maxdepth 1 ! -name 'core' -exec rm -rf {} +

# Step 1: Create a virtual environment
python -m venv hms_venv

source hms_venv/Scripts/activate

# Check if a virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment is not activated. Please activate your environment first."
    exit 1
fi

echo "Virtual environment is activated."
# Continue with your setup steps
cd core

echo "All files copied to 'core' and original directory cleaned up."

# Step 8: Copy files to a specific directory
# cp docker-compose.yml ../docker-compose.yml

# docker-compose up -d

# 3. Remove the original files (but not 'core' itself)
# find . -mindepth 1 -maxdepth 1 ! -name 'core' -exec rm -rf {} +

# # Check if Docker is running
# if ! docker info > /dev/null 2>&1; then
#     echo "Docker is not running. Please start Docker."
#     exit 1
# fi

# echo "Docker is running."
# # Continue with your setup steps
# step 0 configure the core folder

# Step 3: Upgrade pip
pip install --upgrade pip

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 6: Run Django migrations
# python manage.py migrate

# Step 7: Collect static files
# python manage.py collectstatic --noinput

# Step 10: Run the Django development server
# python manage.py runserver
docker-compose up
