FROM python:3.12 as base

WORKDIR /code

COPY . .

FROM base as dev

RUN pip install -e .

FROM base as deploy

RUN pip install .
