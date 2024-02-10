FROM node:20.11.0 as base

WORKDIR /code

COPY package.json .
COPY package-lock.json .

RUN npm install

COPY . .

FROM base as dev

ARG VITE_GOOGLE_CLIENT_ID

ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID

CMD ["npm", "run", "dev"]

FROM base as builder

RUN npm run build

FROM nginx:1.25 as deploy

COPY --from=builder /code/nginx.conf /etc/nginx/templates/default.conf.template

COPY --from=builder /code/dist/client /usr/share/nginx/html
