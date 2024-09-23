# Navigate to the directory containing package.json
Set-Location -Path "C:\path\to\theme\static_src"

# Start the Tailwind CSS development server
Start-Process "npm" -ArgumentList "run dev"

# Wait for a few seconds to ensure the CSS server starts properly
Start-Sleep -Seconds 5

# Navigate to the theme folder
Set-Location -Path ".."

# Navigate back to the root project folder
Set-Location -Path ".."

# Start the Django development server
python manage.py runserver 0.0.0.0:8000
