FROM node:16 as build-stage-vue

WORKDIR /workdir

COPY package*.json ./
RUN npm install

COPY . .

ARG VUE_APP_API_URL
ARG VUE_APP_WEBSOCKET_URL
ARG VUE_APP_SENTRY_DSN
ENV VUE_APP_API_URL ${VUE_APP_API_URL:-http://localhost/api/}
ENV VUE_APP_WEBSOCKET_URL ${VUE_APP_WEBSOCKET_URL:-ws://localhost/api/ws}
ENV VUE_APP_SENTRY_DSN ${VUE_APP_SENTRY_DSN}
ENV SENTRY_ENVIRONMENT ${SENTRY_ENVIRONMENT}
RUN npm run gettext-compile locale/*/lang.po || true
RUN VUE_APP_API_URL=${VUE_APP_API_URL} \
    VUE_APP_WEBSOCKET_URL=${VUE_APP_WEBSOCKET_URL} \
    VUE_APP_SENTRY_DSN=${VUE_APP_SENTRY_DSN} \
    npm run build

FROM nginxinc/nginx-unprivileged:latest as production-stage
USER root
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build-stage-vue --chown=nginx:root /workdir/dist /usr/share/nginx/html/static

# Must match the settings.MEDIA_ROOT default value.
RUN mkdir -p /data/media && chown -R nginx:root /data/media

USER nginx
