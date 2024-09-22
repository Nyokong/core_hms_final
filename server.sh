#!/bin/bash

# Navigate to the directory containing package.json
cd /theme/static_src || exit

# Start the Tailwind CSS development server
npm run dev &

# Wait for a few seconds to ensure the CSS server starts properly
sleep 5

# Navigate to the theme folder
cd .. || exit

# Navigate back to the root project folder
cd .. || exit

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
