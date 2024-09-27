#!/bin/ash

# clear python cache
rm -rf __pycache__

# start migrations
echo "Make database migrations"
python manage.py makemigrations

echo "Apply database migrations"
python manage.py migrate


# # Navigate to the directory containing package.json
# echo "Navigate to the directory containing package.json"
# cd /theme/static_src || exit

# echo "Start the Tailwind CSS development server"
# # Start the Tailwind CSS development server
# npm run dev &

# # Wait for a few seconds to ensure the CSS server starts properly
# echo "Wait for a few seconds to ensure the CSS server starts properly"
# sleep 5

# # Navigate to the theme folder
# echo "Navigate to the theme folder"
# cd .. || exit

# # Navigate back to the root project folder
# echo "Navigate back to the root project folder"
# cd .. || exit

# # Start the Django development server
# echo "Start the Django development server"
# python manage.py runserver 0.0.0.0:8000

exec "$@"
