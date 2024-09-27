```bash

    pip install -r requirements.txt

```

// install from requirements
pip install -r requirements.txt
pip freeze > requirements.txt

docker-compose up --build -d

docker-compose down

// open terminal in the docker container
docker exec -it hms_core /bin/sh

// to invoke daphne
daphne daphne.asgi:application

// uvicorn server
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload

// uvicorn server
uvicorn core.asgi:application --port 8000 --log-level debug --reload