# Follow These to safely run this application

1.setting up your environment
please dont be in the core folder

```plaintext
├── core_hms_final
    └── api
        ├── admin.py
        ├── models.py
        ├── urls.py
        ├── views.py
        └── wsgi.py
    ├── core
        ├── setting.py
        ├── urls.py
        └── wsgi.py
    ├── README.md
    ├── Dockerfile
    ├── entrypoint.sh
    ├── manage.py
    ├── setup.py
    └── requirements.txt

HMS-app/
├── backend/
│   ├── core/
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

```plaintext
run this command in the core_hms_final
for easy access our code, basically let us set it up for you
all you need to run is the ./setup.sh file in Gitbash

```

Sure, let's go through the steps to fix the errors and set up your Django project with Docker.

### Setting Up Your Environment

1. **Ensure you're not in the `core` folder**:

   - Your project structure should look like this:

     ```plaintext
     ├── core_hms_final
         └── api
             ├── admin.py
             ├── models.py
             ├── urls.py
             ├── views.py
             └── wsgi.py
         ├── core
             ├── setting.py
             ├── urls.py
             └── wsgi.py
         ├── README.md
         ├── Dockerfile
         ├── entrypoint.sh
         ├── manage.py
         ├── setup.py
         └── requirements.txt
     ```

2. **Run the setup script**:
   - If you're using Gitbash, run:

     ```bash
     ./setup.sh
     ```

   - This script sets up the environment as it was in development.

### Manual Setup (if `setup.sh` fails)

1. **Create a Python virtual environment**:

   ```bash
   python -m venv hms_venv
   ```

2. **Rename `core_hms_final` to `core`**:
   - This is for a cleaner structure.

3. **Change directory to `core`**:

   ```bash
   cd core
   ```

4. **Install requirements**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Clear any running Docker containers**:

   ```bash
   docker-compose down
   ```

6. **Build and run the Docker containers**:

   ```bash
   docker-compose up --build -d
   ```

### Handling `entrypoint.sh` Errors

1. **Check for errors in `entrypoint.sh`**:
   - If the script wasn't copied correctly, you might need to handle migrations manually.

2. **Run migrations**:

   ```bash
   python manage.py makemigrations
   ```

3. **Delete old migration files (except `__init__.py`)**:
   - Navigate to:

     ```plaintext
     ├── api
         └── migrations
     ```

   - Delete all files except `__init__.py`.

4. **Run migrations again**:

   ```bash
   python manage.py migrate
   ```

5. **Run the application**:

   ```bash
   docker-compose up -d
   ```

### Final Steps

1. **Create a superuser**:

   ```bash
   python manage.py createsuperuser
   ```


   - Use your student number as the username for simplicity.

2. **Add sites to the Settings.py

```python
    SITE_ID = 10
```

5. **Access the local server**:
   - Open your browser and go to `localhost:8000/admin/` to log into the admin side.

7. **Check API documentation for database requests**.

### Additional Commands Please ignore

- **Create a new Next.js app**:

  ```bash
  npx create-next-app@latest hms-web
  ```

- **Docker commands**:

  ```bash
  docker-compose up -d --build
  docker-compose down
  docker exec -it hms_core /bin/sh
  ```

- **Run Daphne server**:

  ```bash

  daphne daphne.asgi:application
  ```

- **Run Uvicorn server**:

  ```bash
  uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
  ```
