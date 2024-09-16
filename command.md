pip install -r requirements.txt
pip freeze > requirements.txt
docker-compose up -d --build
docker-compose down
// open terminal in the docker container
docker exec -it hms_core /bin/sh
