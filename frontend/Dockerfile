FROM node:10 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG VUE_APP_API_URL
ARG VUE_APP_WEBSOCKET_URL
ENV VUE_APP_API_URL ${VUE_APP_API_URL:-http://localhost:8000}
ENV VUE_APP_WEBSOCKET_URL ${VUE_APP_WEBSOCKET_URL:-ws://localhost:8000/ws/api/}
RUN npm run gettext-compile locale/es/lang.po
RUN VUE_APP_API_URL=${VUE_APP_API_URL} VUE_APP_WEBSOCKET_URL=${VUE_APP_WEBSOCKET_URL} npm run build

FROM nginx:stable
WORKDIR /app
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/ /app/
