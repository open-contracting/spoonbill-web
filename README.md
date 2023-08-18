# spoonbill-web
A web frontend to convert OCDS data from JSON to Excel/CSV

## Development

```shell
git clone git@github.com:open-contracting/spoonbill-web.git
cd spoonbill-web
```

### Installation

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

### Tests

Replace PostgreSQL connection details, as needed.

```shell
env PYTHONWARNINGS=error MEDIA_ROOT=tmp/ FILE_UPLOAD_TEMP_DIR=tmp/ pytest --cov core --cov spoonbill_web --no-migrations
```

### Run backend application

```shell
docker-compose up -d redis
./manage.py makemigrations
./manage.py migrate
./manage.py runserver
```

### Run frontend application

```shell
cd frontend
npx vue-cli-service serve
```

You might need to change `VUE_APP_API_URL` and `VUE_APP_WEBSOCKET_URL` in `frontend/.env` from `localhost` to `127.0.0.1`.

### Celery

Start celery worker:

```shell
celery -A spoonbill_web worker -l INFO --concurrency=2
```

Start celery beat:

```shell
celery -A spoonbill_web beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Pre-Commit

### Installation

```shell
pip install pre-commit
```

### Install the git hook scripts

```shell
pre-commit install
```

### Edit a pre-commit configuration

Configuration placed in file `.pre-commit-config.yaml`

[More about pre-commit](https://pre-commit.com/)

## Internationalization

### Django

Extract messages:

```shell
./manage.py makemessages -a
```

Push to Transifex:

```shell
tx push -s -t
```

Pull from Transifex:

```shell
tx pull -a
```

Compile messages:

```shell
django-admin compilemessages
```

### Vue

Change into the `frontend/` directory:

```shell
cd frontend
```

Extract messages:

```shell
npm run gettext-extract
```

Push and pull messages from Transifex as above.
