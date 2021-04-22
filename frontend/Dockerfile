FROM node:10 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VUE_APP_API_URL
ARG VUE_APP_WEBSOCKET_URL
ARG VUE_APP_SENTRY_DSN
ARG SENTRY_ENVIRONMENT
ENV VUE_APP_API_URL ${VUE_APP_API_URL:-http://localhost/api/}
ENV VUE_APP_WEBSOCKET_URL ${VUE_APP_WEBSOCKET_URL:-ws://localhost/api/ws}
ENV VUE_APP_SENTRY_DSN ${VUE_APP_SENTRY_DSN}
ENV SENTRY_ENVIRONMENT ${SENTRY_ENVIRONMENT}
RUN npm run gettext-compile locale/*/lang.po || true
RUN VUE_APP_API_URL=${VUE_APP_API_URL} \
    VUE_APP_WEBSOCKET_URL=${VUE_APP_WEBSOCKET_URL} \
    VUE_APP_SENTRY_DSN=${VUE_APP_SENTRY_DSN} \
    SENTRY_ENVIRONMENT=${SENTRY_ENVIRONMENT} \
    npm run build

FROM nginx:stable
WORKDIR /app
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/ /app/
