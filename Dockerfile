FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
      gettext \
   && rm -rf /var/lib/apt/lists/*

RUN groupadd -r runner && useradd --no-log-init -r -g runner runner

# Must match the settings.FILE_UPLOAD_TEMP_DIR default value.
RUN mkdir -p /data/tmp && chown -R runner:runner /data/tmp
# Must match the settings.MEDIA_ROOT default value.
RUN mkdir -p /data/media && chown -R runner:runner /data/media
# Must match the settings.DATAREGISTRY_MEDIA_ROOT default value.
RUN mkdir -p /data/exporter && chown -R runner:runner /data/exporter

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workdir
USER runner:runner
COPY --chown=runner:runner . .

ENV DJANGO_ENV=production
ENV WEB_CONCURRENCY=2

RUN python manage.py compilemessages
RUN python manage.py collectstatic --noinput -v2

EXPOSE 8000
CMD ["gunicorn", "spoonbill_web.wsgi", "--bind", "0.0.0.0:8000", "--worker-tmp-dir", "/dev/shm", "--threads", "2", "--name", "spoonbill-web"]
