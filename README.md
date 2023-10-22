# floskl
Flask blog demo

## WIP

```shell
docker-compose up -d
./prep-venv.sh && source .venv/bin/activate
flask --app floskl init-db
flask --app floskl run
gunicorn --config gunicorn_config.py
```

