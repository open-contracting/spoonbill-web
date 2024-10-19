# spoonbill-web

A web frontend to convert OCDS data from JSON to Excel/CSV

## Install requirememnts

```shell
pip install -r requirements_dev.txt
pre-commit install
```

```shell
cd frontend
npm install
```

## Run tests

```shell
coverage run --source=core,spoonbill_web -m pytest -W error --no-migrations
```

```shell
cd frontend
npx vue-cli-service lint
npx vue-cli-service test:unit
```

## Run servers

```shell
./manage.py migrate
./manage.py runserver
```

```shell
cd frontend
npx vue-cli-service serve
```

## Run workers

Start celery worker:

```shell
celery -A core worker -l INFO --concurrency=2
```

Start celery beat:

```shell
celery -A core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

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
npx gettext-extract --removeHTMLWhitespaces --output web-app-ui.pot src/main.js $(find src -type f -name '*.vue')
```

Push and pull messages from Transifex as above.

Compile messages:

```shell
npx gettext-compile --output src/translations/translations.json <filenames>
```
