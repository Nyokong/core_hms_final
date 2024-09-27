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

2. for easy nice looking structure rename this core_hms_final to

# now core_hms_final is just core

3. change directory

```bash
    cd core
```

4.install requirements by running this code

```bash
    pip install -r requirements.txt
```
5. your app should have everything setup now

run docker-compose down if you want to clear any running container on docker

```bash
    docker-compose down
```

6. run the app on docker, you might need to run some migrations manually if docker gets an error with entrypoint.sh

but just for safety put "-d" at the end to tell docker to give you your terminal once its done

```bash
    docker-compose up --build -d
```

7.check for entrypoint.sh errors

if you have entrypoint.sh errors this means the applications didnt copy entrypoint.sh into our environment
but this is not a train smash lets move on

8. Running Migrations

```bash
    python manage.py makemigrations
```

any potential issues lies with how django does migrations you might be required to go into 

```plaintext
├── api
    └── migrations
```

Delete anything you see except __init__.py this one is required for python


9. Run Migrate

```bash
    python manage.py makemigrations
```

10. at this point if no issues are there just run the application on docker

```bash
    docker-compose up -d 
```

11. Your Server should be running by now every major error is solved

12. Create a super user to log into the django admin account

```bash
    python manage.py createsuperuser
```

13. you will be asked for a username for a new super user please use your student number

we can technically use any thing you want but a student number saves you hasle of future errors

14. Now you are logged in the local Server Localhost:8000

you can say localhost:8000/admin/ in the browser url to log into the admin side

15. to make any database requests please look at our API documentation

# you have reached the end of the README.md

.
.
.
.
.
.
.
.
.
.
thanks you

NB:Ignore for Collaborators

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
