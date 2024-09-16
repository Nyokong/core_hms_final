# Follow These to safely run this application

1.setting up your environment
please dont be in the core folder

```plaintext
├── DjangoMainFolder
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
    └── requirements.txt
```

run this command in the DjangoMainFolder

```bash
    python -m venv hms-venv
```

2.install requirements

```bash
    pip install -r requirements.txt
```

NB:Ignore

```bash
    pip freeze > requirements.txt
```

docker-compose up -d --build
docker-compose down
// open terminal in the docker container
docker exec -it hms_core /bin/sh

// to invoke daphne
daphne daphne.asgi:application

// uvicorn server
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
