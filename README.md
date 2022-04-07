# spoonbill-web
A web frontend to convert OCDS data from JSON to Excel/CSV

## Backend installation

```shell
docker-compose build app
docker-compose up
```

Application will be available on http://localhost:8000


## Development

```shell
git clone git@github.com:open-contracting/spoonbill-web.git
cd spoonbill-web
```

### Tests outside Docker

Replace PostgreSQL connection details, as needed.

```shell
env PYTHONWARNINGS=error POSTGRES_DB=spoonbill_web POSTGRES_USER=username POSTGRES_PASSWORD= MEDIA_ROOT=tmp/ FILE_UPLOAD_TEMP_DIR=tmp/ pytest --cov core --cov spoonbill_web --no-migrations
```

### Installation use direnv

```shell
direnv allow
pip install -r requirements_dev.txt
```

### Installation without direnv

```shell
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_dev.txt
```

### Run application

```shell
docker-compose up -d postgres redis
./manage.py makemigrations
./manage.py migrate
./manage.py runserver
```

### Celery

* Up celery worker

```shell
celery -A spoonbill_web worker -l INFO --concurrency=2
```

* Up celery beat
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
./manage.py makemessages --all --keep-pot
```

Push to Transifex:

```shell
tx push -st
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
