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

run this command in the core_hms_final
for easy access our code, basically let us set it up for you
all you need to run is the ./setup.sh file in Gitbash
# Please note this only works on Gitbash

```bash
    ./setup.sh
```

this file will basically setup the environment the way we had it in development 
well hopefully.

# if you get an error running docker with ./setup.sh file

this is expected since you possibly running this in windows

then take the manual road
suppose your env and all your files were not setup by the ./setup.sh file 
then follow the next steps

# outside the core_hms_final folder

```plaintext
├── where you cloned the repository
    └── core_hms_final
```

1. Run this to create a python environment
```bash
    python -m venv hms_venv
```

2.install requirements by running this code

```bash
    pip install -r requirements.txt
```

NB:Ignore

```bash
    pip freeze > requirements.txt
```

creating a new nextjs app

```bash
    npx create-next-app@latest hms-web
```

docker-compose up -d --build
docker-compose down
// open terminal in the docker container
docker exec -it hms_core /bin/sh

// to invoke daphne
daphne daphne.asgi:application

// uvicorn server
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
