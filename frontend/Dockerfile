FROM node:20.15.1 AS base

WORKDIR /code

COPY package.json .
COPY package-lock.json .

RUN npm install

COPY . .

FROM base AS dev

ARG VITE_GOOGLE_CLIENT_ID

ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

CMD ["npm", "run", "dev"]

FROM base AS builder

ARG VITE_GOOGLE_CLIENT_ID

RUN npm run build

FROM nginx:1.25 AS deploy

COPY --from=builder /code/nginx.conf /etc/nginx/templates/default.conf.template

COPY --from=builder /code/dist/client /usr/share/nginx/html
