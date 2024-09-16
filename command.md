pip install -r requirements.txt
pip freeze > requirements.txt
docker-compose up -d --build
docker-compose down
// open terminal in the docker container
docker exec -it hms_core /bin/sh

// to invoke daphne
daphne daphne.asgi:application

// uvicorn server
uvicorn core.asgi:application --port 8000 --workers 4 --log-level debug --reload
