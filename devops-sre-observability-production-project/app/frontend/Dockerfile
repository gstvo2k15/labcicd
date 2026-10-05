FROM node:22-alpine AS build
WORKDIR /src
COPY app/frontend/package.json .
RUN npm install
COPY app/frontend/ .
RUN npm run build
FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=build /src/dist /usr/share/nginx/html
COPY app/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ || exit 1
