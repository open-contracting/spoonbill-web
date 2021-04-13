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
python manage.py makemigrations && python manage.py migrate
python manage.py runserver
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


## Internationalization and Transifex

### Generate pot files

```shell
python manage.py makemessages --all --keep-pot
```

### Push pot files to transifex

```shell
tx push -st
```

### Pull translations

```shell
tx pull -a
```
