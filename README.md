
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
 docker-compose logs -t -f --tail 30 'web'
 docker-compose logs -t -f --tail 30 'celery'
 docker-compose logs -t -f --tail 30 'celery-beat'
 docker-compose logs -t -f --tail 30 'redis'
> ```