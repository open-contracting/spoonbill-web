FROM python:3.7-alpine

ARG USER=spoonbill

# Install dependencies required for psycopg2 python package
RUN apk update && apk add libpq && apk add --update sudo
RUN apk update && apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev libffi-dev rust cargo g++

RUN adduser -D $USER \
        && echo "$USER ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USER \
        && chmod 0440 /etc/sudoers.d/$USER

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Remove dependencies only required for psycopg2 build
RUN apk del .build-deps
RUN sudo chown -R $USER:$USER /usr/src/app

EXPOSE 8000

USER spoonbill
CMD ["gunicorn", "spoonbill_web.wsgi", "0:8000"]
