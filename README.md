# Hawa-ko-reporter 

## Setting up development environment 
```bash 
docker-compose up -d --build
```
```bash
 sudo docker-compose exec web python manage.py migrate
```

Once the build is complete, navigate to http://localhost:1337 to ensure the app works as expected. You should see the following text:
```json
{"message": "Welcome to Hawa-ko-reporter API!"}
```

## Viewing logs
 ```bash
 docker-compose logs 'web'
 docker-compose logs 'celery'
 docker-compose logs 'celery-beat'
 docker-compose logs 'redis'
> ```